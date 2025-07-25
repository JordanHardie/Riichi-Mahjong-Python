def send_message(message:str) -> None:
    print(f"\n{message}")

def send_input(_input:str) -> str:
    return input(f"\n{_input}")

def format_tile_name(value: int, suit: int | str) -> str:
    if suit == 1:
        return f"{value}M"
    elif suit == 2:
        return f"{value}P"
    elif suit == 3:
        return f"{value}S"
    else:
        return f"{value}Z"