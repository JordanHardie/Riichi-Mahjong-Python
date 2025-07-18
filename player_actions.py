from typing import List
from models import Player
from enums import DiscardType, Melds
from tile_utils import sort_tiles, find_melds

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

def display_calls(player: Player) -> str:
    if not player.calls:
        return ""
    
    call_display = " | Calls: "
    for i, call in enumerate(player.calls):
        if i > 0:
            call_display += ", "
        call_display += f"{call['call_type'].name}({'-'.join(call['tiles'])})"
    
    return call_display