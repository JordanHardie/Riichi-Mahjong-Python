import random
from enum import Enum
from typing import Dict, List, Tuple, TypeVar, Optional  

# Generic type for enums
T = TypeVar('T', bound=Enum)

# Constants
COPIES = 4
HAND_SIZE = 13
TILE_NUMBER_MIN = 1
TILE_NUMBER_MAX = 9

DEAD_WALL_SIZE = 14
DORA_INDICATOR_INDEX = 5

class DiscardType(Enum):
    TEDASHI = 1
    """Tedashi refers to discarding a tile already in the hand."""

    TSUMOGIRI = 2
    """Tsumogiri refers to discarding the tile just drawn."""

class Suits(Enum):
    MAN = 1
    """Characters / numbers / manzu"""
    PIN = 2
    """Circles / wheels / pinzu"""
    SOU = 3
    """Bamboo / sticks / souzu"""

class Winds(Enum):
    EAST = 1
    SOUTH = 2
    WEST = 3
    NORTH = 4

class Dragons(Enum):
    WHITE = 5
    GREEN = 6
    RED = 7

class Furiten(Enum):
    NONE = 0
    DISCARD = 1
    TEMPORARY = 2
    PERMANENT = 3

class CallTypes(Enum):
    PON = 1
    CHII = 2
    OPEN_KAN = 3
    CLOSED_KAN = 4
    ADDED_KAN = 5
    KITA = 6

class Melds(Enum):
    NONE = 0
    OPEN_TRIPLET = 1
    """Minkou."""
    CLOSED_TRIPLET = 2
    """Ankou."""
    OPEN_SEQUENCE = 3
    """Minjun."""
    CLOSED_SEQUENCE = 4
    """Anjun."""
    OPEN_QUAD = 5
    """Daiminkan"""
    CLOSED_QUAD = 6
    """Ankan."""
    ADDED_QUAD = 7
    """Shouminkan"""

class GameState:
    def __init__(self):
        self.wall: List[str] = []
        self.dead_wall: List[str] = []
        self.dora: List[str] = []
        self.dora_indicators: List[str] = []

        self.players: List[Player] = []
        self.player_count: int = 4

        self.turn: int = 0
        self.round: int = 0
        self.wind: Winds = Winds.EAST
        self.current_player: Winds = Winds.EAST

class Player:
    def __init__(self):
        self.points: int = 25000
        self.seat: Winds = Winds.EAST

        self.hand: List[str] = []
        self.calls: List[dict] = [] # Structure: {"tiles": [tile_list], "call_type": CallTypes, "called_from": Winds, "called_tile": str}
        self.called_tiles: List[str] = []  # All tiles that have been called (for quick lookup)
        self.discards: List[Dict[str, DiscardType]] = []
        self.drawn_tile: str = ""  # Changed from List[str] to str since there's only one drawn tile

        self.yaku: List[str] = []
        self.tenpai: bool = False
        self.menzenchin: bool = True
        """If menzenchin is true, then the hand is closed."""
        self.furiten: Furiten = Furiten.NONE

def increment_turn(game_state: GameState) -> None:
    game_state.turn += 1

def increment_round(game_state: GameState) -> None:
    game_state.round += 1

def discard_tile(player: Player, tile: str, discard_type: DiscardType) -> None:
    player.discards.append({tile: discard_type})

    # If the player discards a tile in their hand its replaced with the drawn tile.
    if discard_type == DiscardType.TEDASHI:
        if tile in player.hand:
            player.hand.remove(tile)
            if player.drawn_tile:  # Only add if there's a drawn tile
                player.hand.append(player.drawn_tile)
                player.hand = sort_tiles(player.hand)

    # Clear the drawn tile after discarding
    player.drawn_tile = ""

def send_message(message: str) -> None:
    print(f"\n{message}")

def input_message(message: str) -> str:
    return input(f"\n{message}")

def next_enum(_enum: T) -> T:
    members = list(type(_enum))
    index = members.index(_enum)
    return members[(index + 1) % len(members)]

def format_tile(suit: int, value: int) -> str:
    if suit == 1:
        return f"{value}M"
    elif suit == 2:
        return f"{value}P"
    else:
        return f"{value}S"

def parse_tile(tile: str) -> Tuple[str, int]:
    value = int(tile[0])
    suit = tile[1]
    return suit, value

def draw_tiles_from_wall(wall: List[str], amount: int) -> List[str]:
    if amount >= 0:
        tiles = wall[:amount]
        del wall[:amount]
    else:
        tiles = wall[amount:]
        del wall[amount:]
    return tiles

def get_current_player(game_state: GameState) -> Optional[Player]:
    players = game_state.players
    current_player = None

    for player in players:
        if player.seat == game_state.current_player:
            current_player = player
            break

    return current_player

def get_last_discarded_tile(game_state: GameState) -> Tuple[Optional[str], Optional[Player]]:
    """Get the last discarded tile and the player who discarded it."""
    last_tile = None
    last_player = None
    
    for player in game_state.players:
        if player.discards:
            last_tile = list(player.discards[-1].keys())[0]
            last_player = player
    
    return last_tile, last_player

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

def display_calls(player: Player) -> str:
    if not player.calls:
        return ""
    
    call_display = " | Calls: "
    for i, call in enumerate(player.calls):
        if i > 0:
            call_display += ", "
        call_display += f"{call['call_type'].name}({'-'.join(call['tiles'])})"
    
    return call_display
    players = game_state.players
    current_player = None

    for player in players:
        if player.seat == game_state.current_player:
            current_player = player
            break

    return current_player

def sort_tiles(tiles: List[str]) -> List[str]:
    def tile_sort_key(tile: str) -> tuple:
            suit, raw_value = parse_tile(tile)
            value = 5 if raw_value == 0 else raw_value  # Treat '0' as '5' for sorting

            if suit == 'M':  # Man
                return Suits.MAN.value, value
            elif suit == 'P':  # Pin
                return Suits.PIN.value, value
            elif suit == 'S':  # Sou
                return Suits.SOU.value, value
            elif suit == 'Z':  # Honor tiles
                if 1 <= value <= 4:  # Winds
                    return 4, Winds(value).value
                else:  # Dragons
                    return 5, Dragons(value).value
            else:
                raise ValueError(f"Unknown tile suit: {tile}")

    return sorted(tiles, key=tile_sort_key)

def get_dora(game_state: GameState) -> List[str]:
    dora_values = []
    dora_indicators = game_state.dora_indicators

    def loop_back(max_val: int, val: int, min_val: int = 1) -> int:
        if val + 1 < max_val:
            return val + 1
        else:
            return min_val

    for tile in dora_indicators:
        suit, value = parse_tile(tile)
        if suit in ("M", "P", "S"):
            dora_value = loop_back(10, value)
            dora_values.append(f"{dora_value}{suit}")
        elif value <= 4:
            dora_value = loop_back(5, value)
            dora_values.append(f"{dora_value}Z")
        else:
            dora_value = loop_back(8, value, 5)
            dora_values.append(f"{dora_value}Z")

    return dora_values

def find_melds(tiles) -> Optional[Melds]:
    if len(tiles) < 3:
        return Melds.NONE
        
    values = []
    suits = []

    for tile in tiles:
        suit, value = parse_tile(tile)
        values.append(value)
        suits.append(suit)

    # If they suits aren't the same then we can't have a meld (except for sequences which need same suit)
    if len(set(suits)) != 1:
        return Melds.NONE
    
    # Check for quads (4 identical tiles)
    if len(tiles) == 4 and len(set(values)) == 1:
        return Melds.CLOSED_QUAD  # TODO: We need to check for the discard type to determine open vs closed
    
    # Check for triplets (3 identical tiles)
    elif len(tiles) == 3 and len(set(values)) == 1:
        return Melds.CLOSED_TRIPLET  # TODO: We need to check for the discard type to determine open vs closed
    
    # Check for sequences (3 consecutive tiles in same suit)
    elif len(tiles) == 3 and suits[0] in ('M', 'P', 'S'):
        sorted_values = sorted(values)
        if sorted_values[1] == sorted_values[0] + 1 and sorted_values[2] == sorted_values[1] + 1:
            return Melds.CLOSED_SEQUENCE  # TODO: We need to check for the discard type to determine open vs closed
    
    return Melds.NONE

def check_tenpai(hand: List[str]) -> bool:
    # This is a simplified tenpai check - a full implementation would be much more complex
    melds = []
    hand_copy = hand.copy()
    
    # Simple approach: check if we can form melds with most tiles, leaving 1-2 tiles for the pair/wait
    while len(hand_copy) >= 3:
        found_meld = False
        for i in range(len(hand_copy) - 2):
            potential_meld = hand_copy[i:i+3]
            if len(potential_meld) == 3:
                result = find_melds(potential_meld)
                if result != Melds.NONE:
                    melds.append(result)
                    # Remove the tiles used in this meld
                    for tile in potential_meld:
                        hand_copy.remove(tile)
                    found_meld = True
                    break
        
        if not found_meld:
            break
    
    # Check for quads
    i = 0
    while i <= len(hand_copy) - 4:
        potential_quad = hand_copy[i:i+4]
        if len(potential_quad) == 4:
            result = find_melds(potential_quad)
            if result == Melds.CLOSED_QUAD:
                melds.append(result)
                for tile in potential_quad:
                    hand_copy.remove(tile)
                continue
        i += 1
    
    # A rough tenpai check: if we have 4 melds and 1-2 tiles left, we might be in tenpai
    return len(melds) >= 4 and len(hand_copy) <= 2

def generate_tiles(game_state: GameState) -> List[str]:
    tiles = []

    for copy in range(COPIES):
        # While I would like to use the enum, this system works better for skipping the red 5 and the man tiles if in 3P.
        for suit in range(1, 4):
            for tile_number in range(TILE_NUMBER_MIN, TILE_NUMBER_MAX + 1):

                # Suit 1 is man tiles, and we only keep the terminals, skipping the rest.
                if game_state.player_count == 3 and suit == 1 and tile_number not in (1, 9):
                    continue

                # We skip one copy of a five to make it a red five later.
                if tile_number == 5 and copy == 0:
                    continue

                tiles.append(format_tile(suit, tile_number))

        for wind in Winds:
            tiles.append(f"{wind.value}Z")

        for dragon in Dragons:
            tiles.append(f"{dragon.value}Z")

    # Red fives are re-added as value 0
    for suit in range(1, 4):
        # Skip red 5 man in 3 player game
        if game_state.player_count == 3 and suit == 1:
            continue
        tiles.append(format_tile(suit, 0))

    random.shuffle(tiles)
    return tiles

def initialize_game(game_state: GameState) -> None:
    while True:
        try:
            amount_of_players = int(input_message("How many players?: "))
            if amount_of_players in (3, 4):
                break
            else:
                send_message("Please enter 3 or 4 players.")
        except ValueError:
            send_message("Please enter a valid number.")

    game_state.player_count = amount_of_players

    game_state.wall = generate_tiles(game_state)
    game_state.dead_wall = draw_tiles_from_wall(game_state.wall, -DEAD_WALL_SIZE)
    game_state.dora_indicators.append(game_state.dead_wall[DORA_INDICATOR_INDEX])

    winds = [Winds.EAST, Winds.SOUTH, Winds.WEST, Winds.NORTH]
    random.shuffle(winds)

    if amount_of_players == 3:
        winds.remove(Winds.NORTH)

    for _ in range(amount_of_players):
        player = Player()
        seat_wind = winds.pop()  # Use pop() instead of random.choice() and remove()
        player.seat = seat_wind

        player.hand = draw_tiles_from_wall(game_state.wall, HAND_SIZE)
        player.hand = sort_tiles(player.hand)

        game_state.players.append(player)

def run_game() -> None:
    game_state = GameState()

    initialize_game(game_state)

    while game_state.round <= 8:
        display_hand = ""
        current_player = get_current_player(game_state)

        if current_player is None:
            send_message("Error: No current player found")
            break

        # Check if wall is empty
        if not game_state.wall:
            send_message("Wall is empty - game ends")
            break

        # Check for calls before drawing (only East player can call for now)
        last_tile, last_discarder = get_last_discarded_tile(game_state)
        called_tile = False
        
        if last_tile and last_discarder and last_discarder != current_player and current_player.seat == Winds.EAST:
            send_message(f"Last discarded tile: {last_tile}")
            
            # Check what calls are possible
            can_pon = can_call_pon(current_player.hand, last_tile)
            can_chii = can_call_chii(current_player.hand, last_tile, current_player.seat, last_discarder.seat)
            can_open_kan, can_add_kan, can_closed_kan = can_call_kan(current_player.hand, last_tile, current_player.calls)
            
            if can_pon or can_chii or can_open_kan:
                call_options = []
                if can_pon:
                    call_options.append("PON")
                if can_chii:
                    call_options.append("CHII")
                if can_open_kan:
                    call_options.append("KAN")
                
                call_choice = input_message(f"Available calls: {', '.join(call_options)} (or SKIP): ").upper()
                
                if call_choice == "PON" and can_pon:
                    if make_call(current_player, CallTypes.PON, last_tile, last_discarder):
                        send_message(f"Called PON on {last_tile}")
                        called_tile = True
                    else:
                        send_message("Failed to make PON call")
                elif call_choice == "CHII" and can_chii:
                    if make_call(current_player, CallTypes.CHII, last_tile, last_discarder):
                        send_message(f"Called CHII on {last_tile}")
                        called_tile = True
                    else:
                        send_message("Failed to make CHII call")
                elif call_choice == "KAN" and can_open_kan:
                    if make_call(current_player, CallTypes.OPEN_KAN, last_tile, last_discarder):
                        send_message(f"Called KAN on {last_tile}")
                        called_tile = True
                    else:
                        send_message("Failed to make KAN call")

        # Draw tile if no call was made
        if not called_tile:
            drawn_tiles = draw_tiles_from_wall(game_state.wall, 1)
            if drawn_tiles:
                current_player.drawn_tile = drawn_tiles[0]
            else:
                send_message("No tiles left to draw")
                break
        else:
            # After calling (except closed kan), player draws from dead wall for kan or doesn't draw for pon/chii
            if current_player.calls and current_player.calls[-1]["call_type"] in [CallTypes.OPEN_KAN, CallTypes.CLOSED_KAN, CallTypes.ADDED_KAN]:
                # For kan, draw replacement tile (simplified: draw from regular wall)
                drawn_tiles = draw_tiles_from_wall(game_state.wall, 1)
                if drawn_tiles:
                    current_player.drawn_tile = drawn_tiles[0]
            # For pon/chii, no tile is drawn
            
        increment_turn(game_state)

        if current_player.seat == Winds.EAST:
            # Check for closed kan and added kan options during East's turn
            can_open_kan, can_add_kan, can_closed_kan = can_call_kan(current_player.hand, "", current_player.calls)
            
            if can_closed_kan or can_add_kan:
                kan_options = []
                if can_closed_kan:
                    closed_kan_tiles = get_closed_kan_options(current_player.hand)
                    kan_options.extend([f"ANKAN-{tile}" for tile in closed_kan_tiles])
                if can_add_kan:
                    # Find which pon can be upgraded
                    for call in current_player.calls:
                        if call["call_type"] == CallTypes.PON:
                            pon_tile = call["tiles"][0]
                            if pon_tile in current_player.hand:
                                kan_options.append(f"SHOUMINKAN-{pon_tile}")
                
                if kan_options:
                    send_message(f"Available kans: {', '.join(kan_options)} (or SKIP)")
                    kan_choice = input_message("Choose kan or SKIP: ").upper()
                    
                    if kan_choice.startswith("ANKAN-"):
                        kan_tile = kan_choice[6:]  # Remove "ANKAN-" prefix
                        if make_call(current_player, CallTypes.CLOSED_KAN, "", current_player, kan_tile):
                            send_message(f"Called closed KAN on {kan_tile}")
                            # Draw replacement tile
                            drawn_tiles = draw_tiles_from_wall(game_state.wall, 1)
                            if drawn_tiles:
                                current_player.drawn_tile = drawn_tiles[0]
                    elif kan_choice.startswith("SHOUMINKAN-"):
                        kan_tile = kan_choice[11:]  # Remove "SHOUMINKAN-" prefix
                        if make_call(current_player, CallTypes.ADDED_KAN, "", current_player, kan_tile):
                            send_message(f"Called added KAN on {kan_tile}")
                            # Draw replacement tile
                            drawn_tiles = draw_tiles_from_wall(game_state.wall, 1)
                            if drawn_tiles:
                                current_player.drawn_tile = drawn_tiles[0]

            for i, tile in enumerate(current_player.hand):
                if i != len(current_player.hand) - 1:
                    display_hand += f"{tile}, "
                else:
                    display_hand += f"{tile}"

            if current_player.drawn_tile:
                display_hand += f" | {current_player.drawn_tile}"
            
            # Add calls display
            display_hand += display_calls(current_player)

            send_message(display_hand)

            while True:
                tile_to_discard = input_message("What will you discard?: ")
                tile_to_discard = tile_to_discard.upper()

                # We check to see if the discarded tile matches the drawn tile first,
                # Since its more likely the player wants to discard that first rather than anything in their hand.
                if tile_to_discard == current_player.drawn_tile:
                    discard_tile(current_player, tile_to_discard, DiscardType.TSUMOGIRI)
                    break
                elif tile_to_discard in current_player.hand:
                    discard_tile(current_player, tile_to_discard, DiscardType.TEDASHI)
                    break
                else:
                    send_message("Invalid tile. Please try again.")

        else:
            if current_player.drawn_tile:
                discard_tile(current_player, current_player.drawn_tile, DiscardType.TSUMOGIRI)

        game_state.current_player = next_enum(game_state.current_player)

if __name__ == "__main__":
    run_game()