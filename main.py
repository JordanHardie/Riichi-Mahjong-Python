import random
from models import GameState, Player
from enums import Winds, CallTypes, DiscardType
from tile_utils import generate_tiles, sort_tiles
from wall_utils import draw_tiles_from_wall, get_last_discarded_tile
from game_logic import (
    increment_turn, next_enum, get_current_player, can_call_pon, 
    can_call_chii, can_call_kan, make_call, get_closed_kan_options
)
from player_actions import discard_tile, display_calls
from ui import send_message, input_message

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