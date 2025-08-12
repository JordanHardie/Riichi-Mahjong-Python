from utils import *
from enums import Calls
from dataclasses import dataclass
from game_manager import Player, game_state


@dataclass
class CallOption:
    call_type: Calls
    tiles_used: list[str]
    kuikae_restrictions: set[str]
    """Kuikae: After making a call, prevents discarding tiles that could have completed that call on the same turn.
    Example:
        - Calling pon on 5-pin → cannot discard 5-pin.
        - Calling chii on 4-sou with 2-3-sou → cannot discard 1-sou or 4-sou.
    """


def is_uniform_list(items: list[str] | list[int]) -> bool:
    """Return True if all elements in the list are identical."""
    return len(set(items)) == 1


def is_same_tiles(tiles: list[str]) -> bool:
    """Check if tiles have the same value and suit."""
    values, suits = extract_tile_list_values(tiles)
    return is_uniform_list(values) and is_uniform_list(suits)


def add_call_option(call_options: list[CallOption], call_type: Calls, tiles_used: list[str], kuikae: set[str]) -> None:
    """Create a CallOption and append it to the list."""
    call_options.append(CallOption(call_type, tiles_used, kuikae))


def get_last_discard() -> str:
    """Retrieve the last tile discarded by the previous player."""
    previous_player_wind = game_state.previous_player

    for player in game_state.players:
        if player.seat == previous_player_wind:
            if not player.discard_pile:
                raise ValueError(f"Player {previous_player_wind} has no discards.")
            return player.discard_pile[-1].tile

    raise ValueError(f"No player found with seat {previous_player_wind}.")


def is_sequence(tiles: list[str]) -> bool:
    tiles = sort_tiles(tiles)
    values, suits = extract_tile_list_values(tiles)

    normalized_values = []
    for v in values:
        if v == 0:
            normalized_values.append(5)
        else:
            normalized_values.append(v)

    if is_uniform_list(suits):
        for i in range(1, len(normalized_values)):
            # This works because we sort the tiles earlier.
            # Regardless of any possible ar
            if values[i] != normalized_values[i - 1] + 1:
                return False

        return True

    else:
        return False


def find_chii_options(hand: list[str], discard: str) -> list[CallOption]:
    """Find all valid chii sequences using the discarded tile, handling red fives correctly."""
    if not is_number_tile(discard):
        return []

    discard_value, suit = extract_tile_values(discard)
    if discard_value == 0:
        discard_value = 5

    hand_tiles = set(hand)
    chii_options: list[CallOption] = []

    for offset in (-2, -1, 0):
        n1, n2 = discard_value + offset, discard_value + offset + 1

        if 1 <= n1 <= 9 and 1 <= n2 <= 9:
            possible_tiles_1 = {f"{n1}{suit}"}
            possible_tiles_2 = {f"{n2}{suit}"}

            if n1 == 5:
                possible_tiles_1.add(f"0{suit}")
            if n2 == 5:
                possible_tiles_2.add(f"0{suit}")

            if hand_tiles & possible_tiles_1 and hand_tiles & possible_tiles_2:
                kuikae: set[str] = set()

                left_tile_val = discard_value - 1
                right_tile_val = discard_value + 1

                if discard_value > 1:
                    possible_left = {f"{left_tile_val}{suit}"}
                    if left_tile_val == 5:
                        possible_left.add(f"0{suit}")
                    if hand_tiles & possible_left:
                        kuikae |= possible_left

                if discard_value < 9:
                    possible_right = {f"{right_tile_val}{suit}"}
                    if right_tile_val == 5:
                        possible_right.add(f"0{suit}")
                    if hand_tiles & possible_right:
                        kuikae |= possible_right

                tiles_used = [next(tile for tile in hand if tile in possible_tiles_1),
                              next(tile for tile in hand if tile in possible_tiles_2)]

                add_call_option(chii_options, Calls.CHII, tiles_used, kuikae)

    return chii_options


def check_kita(player: Player, call_options: list[CallOption]) -> None:
    if game_state.is_three_player and '4Z' in player.hand:
        add_call_option(call_options, Calls.KITA, ['4Z'], set())


def check_set_call(matching_tiles: list[str], last_discard: str, call_options: list[CallOption], call_type: Calls, count_required: int) -> None:
    """Generic check for Pon/Open Kan."""
    if len(matching_tiles) >= count_required:
        meld = [last_discard] * (count_required - 1)
        add_call_option(call_options, call_type, meld, {last_discard})


def check_chii(player: Player, last_discard: str, call_options: list[CallOption]) -> None:
    # Only chii from the player to the left and not in 3-player games.
    if get_next_enum(game_state.previous_player) == game_state.current_player and not game_state.is_three_player:
        call_options.extend(find_chii_options(player.hand, last_discard))


def check_added_kan(player: Player, call_options: list[CallOption]) -> None:
    for call in player.calls:
        if call.call_type == Calls.PON and call.tiles and player.drawn_tile == call.tiles[0]:
            add_call_option(call_options, Calls.ADDED_KAN, [player.drawn_tile], {player.drawn_tile})


def check_closed_kan(player: Player, call_options: list[CallOption]) -> None:
    tile_counts: dict[str, int] = {}
    for tile in player.hand:
        tile_counts[tile] = tile_counts.get(tile, 0) + 1

    for tile, count in tile_counts.items():
        if count >= 4:
            add_call_option(call_options, Calls.CLOSED_KAN, [tile] * 4, set())


def can_call(player: Player) -> list[CallOption]:
    last_discard = get_last_discard()
    call_options: list[CallOption] = []
    matching_tiles = [tile for tile in player.hand if tile == last_discard]

    check_kita(player, call_options)
    check_set_call(matching_tiles, last_discard, call_options, Calls.PON, 2)
    check_chii(player, last_discard, call_options)
    check_set_call(matching_tiles, last_discard, call_options, Calls.OPEN_KAN, 3)
    check_closed_kan(player, call_options)
    check_added_kan(player, call_options)

    return call_options or [CallOption(Calls.NONE, [], set())]
