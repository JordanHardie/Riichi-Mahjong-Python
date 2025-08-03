from utils import *
from enums import Calls
from typing import List
from game_manager import Player, CallOption, DiscardedTile, game_state


def is_uniform_list(list: List[str]) -> bool:
    return len(set(list)) == 1


def is_same_tiles(tiles: List[str]) -> bool:
    tiles = sort_tiles(tiles)
    values, suits = extract_tile_list_values(tiles)

    if is_uniform_list(suits) and is_uniform_list(values):
        return True
    else:
        return False


def add_call_option(call_options: List, _call_type: Calls, _tiles_used: List[str], kuikae: set[str]) -> None:
    option = CallOption(
        call_type=_call_type,
        tiles_used=_tiles_used,
        kuikae_restrictions=kuikae
    )
    call_options.append(option)


def get_last_discard() -> str:
    last_discard: DiscardedTile = DiscardedTile()
    previous_player_wind = game_state.previous_player

    for player in game_state.players:
        if player.seat == previous_player_wind:
            last_discard = player.discard_pile[-1]
            last_tile = last_discard.tile
            return last_tile

    raise ValueError(f"No player found with seat {game_state.previous_player}")


def extract_tile_list_values(tiles: List[str]) -> tuple:
    tiles = sort_tiles(tiles)
    values: List[int] = []
    suits: List[str] = []

    for tile in tiles:
        value, suit = extract_tile_values(tile)
        suits.append(suit)
        values.append(value)

    return values, suits


def is_sequence(tiles: List[str]) -> bool:
    tiles = sort_tiles(tiles)
    values, suits = extract_tile_list_values(tiles)

    if is_uniform_list(suits):
        for i in range(1, len(values)):
            if values[i] != values[i - 1] + 1:
                return False

        return True

    else:
        return False


def find_chii_options(hand: List[str], discard: str) -> List[CallOption]:
    """Find all valid chii sequences using the discarded tile."""

    if not is_number_tile(discard):
        return []

    value, suit = extract_tile_values(discard)
    hand_tiles = set(hand)
    chii_options = []

    # Each offset represents where the discard sits in the sequence.
    # -2: discard is the highest (n-2, n-1, discard)
    # -1: discard is in the middle (n-1, discard, n+1)
    # 0:  discard is the smallest (discard, n+1, n+2)
    for offset in [-2, -1, 0]:
        n1 = value + offset
        n2 = value + offset + 1

        # All numbers must be in 1–9 range.
        if 1 <= n1 <= 9 and 1 <= n2 <= 9:
            tile1 = f"{n1}{suit}"
            tile2 = f"{n2}{suit}"

            # Only add if both required tiles are in the hand.
            if tile1 in hand_tiles and tile2 in hand_tiles:
                kuikae = set()

                left_tile = f"{value - 1}{suit}"
                right_tile = f"{value + 1}{suit}"

                if value > 1 and left_tile in hand_tiles:
                    kuikae.add(left_tile)
                if value < 9 and right_tile in hand_tiles:
                    kuikae.add(right_tile)

                add_call_option(chii_options, Calls.CHII, [tile1, tile2], kuikae)

    return chii_options


def check_kita(player: Player, call_options: List[CallOption]):
    if game_state.is_three_player:
        if '4Z' in player.hand:
            add_call_option(call_options, Calls.KITA, ['4Z'], set())


def check_pon(matching_tiles: List[str], last_discard: str, call_options: List[CallOption]):
    if len(matching_tiles) >= 2:
        meld = [last_discard] * 2
        add_call_option(call_options, Calls.PON, meld, {last_discard})


def check_open_kan(matching_tiles: List[str], last_discard: str, call_options: List[CallOption]):
    if len(matching_tiles) >= 3:
        meld = [last_discard] * 3
        add_call_option(call_options, Calls.OPEN_KAN, meld, {last_discard})


def check_chii(player: Player, last_discard: str, call_options: List[CallOption]):
    # Check for chii. We can only chii off the player to the left of the current player.
    # Chii is also not avalible during 3 player.
    if get_next_enum(game_state.previous_player) == game_state.current_player and not game_state.is_three_player:
        chii_options = find_chii_options(player.hand, last_discard)
        call_options.extend(chii_options)


def check_added_kan(player: Player, call_options: List[CallOption]):
    for call in player.calls:
        if call.call_type == Calls.PON:
            # Check if drawn tile matches the pon tiles.
            if player.drawn_tile == call.tiles[0]:
                tile = [player.drawn_tile]
                add_call_option(call_options, Calls.ADDED_KAN, tile, {player.drawn_tile})


def check_closed_kan(player: Player, call_options: List[CallOption]):
    tile_counts = {}
    for tile in player.hand:
        tile_counts[tile] = tile_counts.get(tile, 0) + 1

    for tile, count in tile_counts.items():
        if count >= 4:
            meld = [tile] * 4
            add_call_option(call_options, Calls.CLOSED_KAN, meld, set())


def can_call(player: Player) -> List[CallOption]:
    last_discard = get_last_discard()
    call_options: List[CallOption] = []

    matching_tiles = []
    for tile in player.hand:
        if tile == last_discard:
            matching_tiles.append(tile)

    check_kita(player, call_options)
    check_pon(matching_tiles, last_discard, call_options)
    check_chii(player, last_discard, call_options)
    check_open_kan(matching_tiles, last_discard, call_options)
    check_closed_kan(player, call_options)
    check_added_kan(player, call_options)

    if call_options:
        return call_options
    else:
        return [CallOption(Calls.NONE, [], set())]