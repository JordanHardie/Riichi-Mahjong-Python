from utils import *
from enums import *
from call_logic import can_call
from game_manager import setup_game, Player, DiscardedTile, game_state


def update_current_players(current_player: Player | None = None) -> None:
    game_state.previous_player = game_state.current_player
    if current_player is not None:
        game_state.current_player = current_player.seat
    else:
        game_state.current_player = get_next_enum(game_state.current_player)


def _format_calls(calls) -> str:
    """Helper function to format player calls."""
    if not calls:
        return "None"

    formatted_calls = []
    for call in calls:
        call_tiles = " ".join(clarify_tile(tile, 1) for tile in call.tiles)
        formatted_calls.append(call_tiles)

    return " | ".join(formatted_calls)


# Debating on whether or not to put this in utils.
def normalize_tile_input(user_input: str) -> str: 
    honor_input_map = {
        # Winds  
        "e": "1Z", "east": "1Z",
        "s": "2Z", "south": "2Z", 
        "w": "3Z", "west": "3Z",
        "n": "4Z", "north": "4Z",
        # Dragons
        "wh": "5Z", "white": "5Z",
        "g": "6Z", "green": "6Z", 
        "r": "7Z", "red": "7Z"
    }

    normalized_input = user_input.lower().strip()

    if normalized_input in honor_input_map:
        return honor_input_map[normalized_input]

    return user_input.upper()


def display_current_players_status(current_player: Player) -> None:
    # Header with seat and round wind.
    header = f"Seat: {clarify_tile(current_player.seat, 2)} | Round wind: {clarify_tile(game_state.current_round_wind, 2)}"
    send_message(header)

    if current_player.discard_pile:
        discard_tiles = " ".join(clarify_tile(discard.tile, 1) for discard in current_player.discard_pile)
        send_message(f"Your discard pile:\n{discard_tiles}")
    else:
        send_message("Your discard pile:\nEmpty")

    # Hand with drawn tile and calls.
    hand_tiles = " ".join(clarify_tile(tile, 1) for tile in current_player.hand)
    drawn_tile_display = clarify_tile(current_player.drawn_tile, 1) if current_player.drawn_tile else "None"

    calls_display = _format_calls(current_player.calls)

    hand_message = f"Your current hand: {hand_tiles} | {drawn_tile_display} | Calls: {calls_display}"
    send_message(hand_message)


def clarify_tile(tile_or_enum: str | Winds | Dragons, type: int) -> str:
    honor_tiles = {
        # Winds (by enum and by value).
        Winds.TON: ("E", "East"), 1: ("E", "East"),
        Winds.NAN: ("S", "South"), 2: ("S", "South"),
        Winds.SHAA: ("W", "West"), 3: ("W", "West"),
        Winds.PEI: ("N", "North"), 4: ("N", "North"),
        # Dragons (by enum and by value).
        Dragons.HAKU: ("Wh", "White"), 5: ("Wh", "White"),
        Dragons.HATSU: ("G", "Green"), 6: ("G", "Green"),
        Dragons.CHUN: ("R", "Red"), 7: ("R", "Red")
    }

    if isinstance(tile_or_enum, (Winds, Dragons)):
        if tile_or_enum in honor_tiles:
            simple, full = honor_tiles[tile_or_enum]
            return simple if type == 1 else full
        return "Unknown"

    value, _ = extract_tile_values(tile_or_enum)

    if is_number_tile(tile_or_enum):
        return tile_or_enum

    if value in honor_tiles:
        simple, full = honor_tiles[value]
        return simple if type == 1 else full

    return "Unknown"


def discard_tile(player: Player, tile: str, discard_type: DiscardType) -> None:
    discarded_by = player.seat
    discard_pile = player.discard_pile

    discarded_tile = DiscardedTile()
    discarded_tile.tile = tile
    discarded_tile.discarded_by = discarded_by
    discarded_tile.discard_type = discard_type
    discard_pile.append(discarded_tile)

    if discard_type == DiscardType.TEDASHI:
        player.hand.remove(tile)
        player.hand.append(player.drawn_tile)

    # Drawn tile always gets removed.
    player.drawn_tile = ''
    player.hand = sort_tiles(player.hand)


def draw_and_discard_tile(current_player: Player) -> None:
    game_state.turn_number += 1
    drawn_tile = game_state.wall.draw_tile()
    current_player.drawn_tile = drawn_tile

    display_current_players_status(current_player)

    tile_to_discard = send_input("What will you discard?: ")
    tile_to_discard = normalize_tile_input(tile_to_discard)

    while tile_to_discard not in current_player.hand and tile_to_discard != current_player.drawn_tile:
        send_message("Please try again!")
        tile_to_discard = send_input("What will you discard?: ")
        tile_to_discard = normalize_tile_input(tile_to_discard)
    
    if tile_to_discard == drawn_tile:
        discard_tile(current_player, tile_to_discard, DiscardType.TSUMOGIRI)

    else:
        discard_tile(current_player, tile_to_discard, DiscardType.TEDASHI)


def run_game() -> None:
    setup_game()
    draw_and_discard_tile(game_state.get_current_player())
    update_current_players()

    for player in game_state.players:
        # If they are in riichi, they cannot change their hand.
        # They can do concealed kan if it doesn't mess with their waits though.
        # For now I'll just skip that player since I don't really have that setup yet.
        # TODO: Add concealed kan checking for riichi.
        if player.is_in_riichi:
            continue

        calls = can_call(player)

        for call in calls:
            if call.call_type == Calls.NONE:
                continue

run_game()