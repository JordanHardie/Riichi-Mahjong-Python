from typing import List, Tuple, Optional, TypeVar
from enum import Enum
from models import GameState, Player
from enums import Winds, CallTypes
from tile_utils import parse_tile, sort_tiles

# Generic type for enums
T = TypeVar('T', bound=Enum)

def increment_turn(game_state: GameState) -> None:
    game_state.turn += 1

def increment_round(game_state: GameState) -> None:
    game_state.round += 1

def next_enum(_enum: T) -> T:
    members = list(type(_enum))
    index = members.index(_enum)
    return members[(index + 1) % len(members)]

def get_current_player(game_state: GameState) -> Optional[Player]:
    players = game_state.players
    current_player = None

    for player in players:
        if player.seat == game_state.current_player:
            current_player = player
            break

    return current_player

def can_call_pon(hand: List[str], discarded_tile: str) -> bool:
    """Check if player can call pon on the discarded tile."""
    if not discarded_tile:
        return False
    
    # Count how many of the discarded tile we have in hand
    count = hand.count(discarded_tile)
    return count >= 2

def can_call_chii(hand: List[str], discarded_tile: str, caller_seat: Winds, discarder_seat: Winds) -> bool:
    """Check if player can call chii on the discarded tile (only from kamicha - previous player)."""
    if not discarded_tile:
        return False
    
    # Chii can only be called from kamicha (previous player in turn order)
    if not is_kamicha(caller_seat, discarder_seat):
        return False
    
    # Only works on number tiles, not honors
    suit, value = parse_tile(discarded_tile)
    if suit not in ('M', 'P', 'S') or value == 0:  # Red 5 treated as 5
        return False
    
    actual_value = 5 if value == 0 else value
    
    # Check for possible sequences
    sequences = [
        [actual_value - 2, actual_value - 1],  # X-2, X-1, [X]
        [actual_value - 1, actual_value + 1],  # X-1, [X], X+1
        [actual_value + 1, actual_value + 2],  # [X], X+1, X+2
    ]
    
    for seq in sequences:
        if all(1 <= val <= 9 for val in seq):  # Valid tile values
            needed_tiles = [f"{val}{suit}" for val in seq]
            if all(tile in hand for tile in needed_tiles):
                return True
    
    return False

def can_call_kan(hand: List[str], discarded_tile: str, calls: List[dict]) -> Tuple[bool, bool, bool]:
    """Check if player can call kan. Returns (can_open_kan, can_add_kan, can_closed_kan)."""
    can_open_kan = False
    can_add_kan = False
    can_closed_kan = False
    
    if discarded_tile:
        # Check for open kan (daiminkan)
        count = hand.count(discarded_tile)
        if count == 3:
            can_open_kan = True
    
    # Check for added kan (shouminkan) - adding to existing pon
    for call in calls:
        if call["call_type"] == CallTypes.PON:
            pon_tiles = call["tiles"]
            if pon_tiles and pon_tiles[0] in hand:
                can_add_kan = True
                break
    
    # Check for closed kan (ankan) - 4 identical tiles in hand
    tile_counts = {}
    for tile in hand:
        tile_counts[tile] = tile_counts.get(tile, 0) + 1
    
    for tile, count in tile_counts.items():
        if count == 4:
            can_closed_kan = True
            break
    
    return can_open_kan, can_add_kan, can_closed_kan

def is_kamicha(caller_seat: Winds, discarder_seat: Winds) -> bool:
    """Check if the discarder is the kamicha (previous player) of the caller."""
    wind_order = [Winds.EAST, Winds.SOUTH, Winds.WEST, Winds.NORTH]
    caller_index = wind_order.index(caller_seat)
    kamicha_index = (caller_index - 1) % len(wind_order)
    return wind_order[kamicha_index] == discarder_seat

def make_call(player: Player, call_type: CallTypes, discarded_tile: str, discarder: Player, specific_tile: str = "") -> bool:
    """Make a call and update player's hand and calls."""
    if call_type == CallTypes.PON:
        # Remove 2 copies from hand, add the discarded tile
        tiles_to_remove = [discarded_tile, discarded_tile]
        if all(tile in player.hand for tile in tiles_to_remove):
            for tile in tiles_to_remove:
                player.hand.remove(tile)
            
            call_tiles = [discarded_tile, discarded_tile, discarded_tile]
            call_info = {
                "tiles": call_tiles,
                "call_type": CallTypes.PON,
                "called_from": discarder.seat,
                "called_tile": discarded_tile
            }
            player.calls.append(call_info)
            player.called_tiles.extend(call_tiles)
            player.menzenchin = False
            
            # Remove the discarded tile from discarder's discards
            if discarder.discards:
                discarder.discards.pop()
            
            return True
    
    elif call_type == CallTypes.CHII:
        # Find which sequence to make
        suit, value = parse_tile(discarded_tile)
        actual_value = 5 if value == 0 else value
        
        sequences = [
            [actual_value - 2, actual_value - 1],  # X-2, X-1, [X]
            [actual_value - 1, actual_value + 1],  # X-1, [X], X+1
            [actual_value + 1, actual_value + 2],  # [X], X+1, X+2
        ]
        
        for seq in sequences:
            if all(1 <= val <= 9 for val in seq):
                needed_tiles = [f"{val}{suit}" for val in seq]
                if all(tile in player.hand for tile in needed_tiles):
                    # Remove needed tiles from hand
                    for tile in needed_tiles:
                        player.hand.remove(tile)
                    
                    # Create the sequence with the called tile
                    call_tiles = sorted(needed_tiles + [discarded_tile])
                    call_info = {
                        "tiles": call_tiles,
                        "call_type": CallTypes.CHII,
                        "called_from": discarder.seat,
                        "called_tile": discarded_tile
                    }
                    player.calls.append(call_info)
                    player.called_tiles.extend(call_tiles)
                    player.menzenchin = False
                    
                    # Remove the discarded tile from discarder's discards
                    if discarder.discards:
                        discarder.discards.pop()
                    
                    return True
    
    elif call_type == CallTypes.OPEN_KAN:
        # Remove 3 copies from hand, add the discarded tile
        tiles_to_remove = [discarded_tile, discarded_tile, discarded_tile]
        if all(tile in player.hand for tile in tiles_to_remove):
            for tile in tiles_to_remove:
                player.hand.remove(tile)
            
            call_tiles = [discarded_tile, discarded_tile, discarded_tile, discarded_tile]
            call_info = {
                "tiles": call_tiles,
                "call_type": CallTypes.OPEN_KAN,
                "called_from": discarder.seat,
                "called_tile": discarded_tile
            }
            player.calls.append(call_info)
            player.called_tiles.extend(call_tiles)
            player.menzenchin = False
            
            # Remove the discarded tile from discarder's discards
            if discarder.discards:
                discarder.discards.pop()
            
            return True
    
    elif call_type == CallTypes.CLOSED_KAN:
        # Remove 4 copies from hand (closed kan)
        kan_tile = specific_tile if specific_tile else discarded_tile
        tiles_to_remove = [kan_tile, kan_tile, kan_tile, kan_tile]
        if all(tile in player.hand for tile in tiles_to_remove):
            for tile in tiles_to_remove:
                player.hand.remove(tile)
            
            call_tiles = [kan_tile, kan_tile, kan_tile, kan_tile]
            call_info = {
                "tiles": call_tiles,
                "call_type": CallTypes.CLOSED_KAN,
                "called_from": player.seat,  # Self since it's closed
                "called_tile": kan_tile
            }
            player.calls.append(call_info)
            player.called_tiles.extend(call_tiles)
            # menzenchin stays True for closed kan
            
            return True
    
    elif call_type == CallTypes.ADDED_KAN:
        # Find the pon to upgrade
        for call in player.calls:
            if call["call_type"] == CallTypes.PON:
                pon_tile = call["tiles"][0]
                if pon_tile in player.hand:
                    # Remove the tile from hand
                    player.hand.remove(pon_tile)
                    
                    # Update the call to added quad
                    call["call_type"] = CallTypes.ADDED_KAN
                    call["tiles"].append(pon_tile)
                    player.called_tiles.append(pon_tile)
                    
                    return True
    
    return False

def get_closed_kan_options(hand: List[str]) -> List[str]:
    tile_counts = {}
    for tile in hand:
        tile_counts[tile] = tile_counts.get(tile, 0) + 1
    
    kan_options = []
    for tile, count in tile_counts.items():
        if count == 4:
            kan_options.append(tile)
    
    return kan_options