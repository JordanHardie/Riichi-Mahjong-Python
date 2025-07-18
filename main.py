import random
from ui import *
from enums import *
from models import *
from tile_utils import *
from wall_utils import *
from game_logic import *
from player_actions import *

# Constants
HAND_SIZE = 13
DEAD_WALL_SIZE = 14
DORA_INDICATOR_INDEX = 5

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
