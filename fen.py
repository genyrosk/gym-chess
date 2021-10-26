PIECES = ["K", "Q", "R", "N", "B", "P", "k", "q", "r", "n", "b", "p"]
EMPTY = "."


def convert_to_fen(
    board,
    active_player="w",
    white_can_catsle_kingside=True,
    white_can_castle_queenside=True,
    black_can_castle_kingside=True,
    black_can_castle_queenside=True,
    en_passant_target=None,
    total_full_moves=0,
    half_moves_since_last_capture=1,
):
    fen_board = ""
    empty_count = 0
    for i, row in enumerate(board):
        for square in row:
            if square in PIECES:
                if empty_count > 0:
                    fen_board += str(empty_count)
                    empty_count = 0
                fen_board += square
            else:
                empty_count += 1
        if empty_count > 0:
            fen_board += str(empty_count)
            empty_count = 0
        if i < 7:
            fen_board += "/"

    fen_active_player = active_player

    fen_castle = (
        ("K" if white_can_catsle_kingside else "")
        + ("Q" if white_can_castle_queenside else "")
        + ("k" if black_can_castle_kingside else "")
        + ("q" if black_can_castle_queenside else "")
    )

    fen_en_passant = en_passant_target if en_passant_target else "-"

    fen_state = f"{fen_board} {fen_active_player} {fen_castle} {fen_en_passant} {total_full_moves} {half_moves_since_last_capture}"

    return fen_state


def convert_from_fen(fen_state):
    (
        fen_board,
        fen_active_player,
        fen_castle,
        fen_en_passant_target,
        fen_total_full_moves,
        fen_half_moves_since_last_capture,
    ) = fen_state.split(" ")

    total_full_moves = int(fen_total_full_moves)
    half_moves_since_last_capture = int(fen_half_moves_since_last_capture)
    en_passant_target = None

    if fen_en_passant_target != "-":
        en_passant_target = fen_en_passant_target
        assert len(fen_en_passant_target) == 2

    white_can_catsle_kingside = "K" in fen_castle
    white_can_castle_queenside = "Q" in fen_castle
    black_can_castle_kingside = "k" in fen_castle
    black_can_castle_queenside = "q" in fen_castle

    active_player = fen_active_player

    board = []
    for fen_row in fen_board.split("/"):
        row = []
        for place in fen_row:
            if place in PIECES:
                row.append(place)
            else:
                skip = int(place)
                row += ["."] * skip
        board.append(row)

    return (
        board,
        active_player,
        white_can_catsle_kingside,
        white_can_castle_queenside,
        black_can_castle_kingside,
        black_can_castle_queenside,
        en_passant_target,
        total_full_moves,
        half_moves_since_last_capture,
    )


# initial state
board = [
    ["r", "n", "b", "q", "k", "b", "n", "r"],
    ["p"] * 8,
    ["."] * 8,
    ["."] * 8,
    ["."] * 8,
    ["."] * 8,
    ["P"] * 8,
    ["R", "N", "B", "Q", "K", "B", "N", "R"],
]
test = convert_to_fen(
    board,
    active_player="w",
    white_can_catsle_kingside=True,
    white_can_castle_queenside=True,
    black_can_castle_kingside=True,
    black_can_castle_queenside=True,
    en_passant_target=None,
    total_full_moves=0,
    half_moves_since_last_capture=1,
)

initial_fen_state = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

print(test)
print(initial_fen_state)

state = convert_from_fen(initial_fen_state)
print(convert_to_fen(*state))
