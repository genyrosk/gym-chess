from copy import copy

import numpy as np
from gym_chess import ChessEnvV2
from gym_chess.envs.chess_v1 import (
    KING_ID,
    QUEEN_ID,
    ROOK_ID,
    BISHOP_ID,
    KNIGHT_ID,
    PAWN_ID,
)
from gym_chess.test.utils import run_test_funcs


# Blank board
BASIC_BOARD = np.array([[0] * 8] * 8, dtype=np.int8)
BASIC_BOARD[3, 2] = -PAWN_ID
BASIC_BOARD[3, 3] = -PAWN_ID
BASIC_BOARD[3, 4] = -PAWN_ID
BASIC_BOARD[3, 5] = -PAWN_ID
BASIC_BOARD[3, 6] = -PAWN_ID
BASIC_BOARD[6, 2] = PAWN_ID
BASIC_BOARD[6, 3] = PAWN_ID
BASIC_BOARD[6, 4] = PAWN_ID
BASIC_BOARD[6, 5] = PAWN_ID
BASIC_BOARD[6, 6] = PAWN_ID


# Pawn basic movements
def test_pawn_moves():
    BOARD = copy(BASIC_BOARD)
    BOARD[4, 4] = PAWN_ID
    env = ChessEnvV2(opponent="none", initial_board=BOARD)
    moves = env.get_possible_moves(attack=True)
    env.render_moves(moves)
    expected_attacks = set([(5, 5), (5, 4), (5, 1), (5, 7), (3, 3), (5, 6), (5, 3), (3, 5), (5, 2)])
    squares_attacked = set([tuple(move[1]) for move in moves])
    print(squares_attacked)
    assert squares_attacked == expected_attacks


# Knight basic movements
def test_knight_moves():
    BOARD = copy(BASIC_BOARD)
    BOARD[4, 4] = KNIGHT_ID
    env = ChessEnvV2(opponent="none", initial_board=BOARD)
    moves = env.get_possible_moves(attack=True)
    env.render_moves(moves)
    expected_attacks = set(
        [
            (5, 5),
            (6, 5),
            (5, 4),
            (5, 1),
            (5, 7),
            (2, 3),
            (6, 3),
            (5, 6),
            (3, 6),
            (5, 3),
            (3, 2),
            (2, 5),
            (5, 2),
        ]
    )
    squares_attacked = set([tuple(move[1]) for move in moves])
    print(squares_attacked)
    assert squares_attacked == expected_attacks


# Bishop basic movements
def test_bishop_moves():
    BOARD = copy(BASIC_BOARD)
    BOARD[4, 4] = BISHOP_ID
    env = ChessEnvV2(opponent="none", initial_board=BOARD)
    moves = env.get_possible_moves(attack=True)
    env.render_moves(moves)
    expected_attacks = set(
        [
            (3, 3),
            (3, 5),
            (5, 3),
            (6, 2),
            (5, 5),
            (6, 6),
            (5, 3),
            (5, 1),
            (5, 4),
            (5, 2),
            (5, 5),
            (5, 3),
            (5, 6),
            (5, 4),
            (5, 7),
            (5, 5),
        ]
    )
    squares_attacked = set([tuple(move[1]) for move in moves])
    assert squares_attacked == expected_attacks


# Rook basic movements
def test_rook_moves():
    BOARD = copy(BASIC_BOARD)
    BOARD[4, 4] = ROOK_ID
    env = ChessEnvV2(opponent="none", initial_board=BOARD)
    moves = env.get_possible_moves(attack=True)
    env.render_moves(moves)
    expected_attacks = set(
        [
            (4, 0),
            (5, 5),
            (3, 4),
            (4, 3),
            (5, 4),
            (4, 6),
            (6, 4),
            (4, 2),
            (5, 1),
            (5, 7),
            (4, 5),
            (5, 6),
            (5, 3),
            (4, 1),
            (4, 7),
            (5, 2),
        ]
    )
    squares_attacked = set([tuple(move[1]) for move in moves])
    print(squares_attacked)
    assert squares_attacked == expected_attacks


# Queen basic movements
def test_queen_moves():
    BOARD = copy(BASIC_BOARD)
    BOARD[4, 4] = QUEEN_ID
    env = ChessEnvV2(opponent="none", initial_board=BOARD)
    moves = env.get_possible_moves(attack=True)
    env.render_moves(moves)
    expected_attacks = set(
        [
            (4, 0),
            (3, 4),
            (4, 3),
            (5, 4),
            (4, 6),
            (5, 1),
            (5, 7),
            (6, 2),
            (4, 2),
            (4, 5),
            (3, 3),
            (5, 6),
            (5, 3),
            (6, 4),
            (4, 1),
            (4, 7),
            (3, 5),
            (5, 2),
            (5, 5),
            (6, 6),
        ]
    )
    squares_attacked = set([tuple(move[1]) for move in moves])
    print(squares_attacked)
    assert squares_attacked == expected_attacks


# King basic movements
def test_king_moves():
    BOARD = copy(BASIC_BOARD)
    BOARD[4, 4] = KING_ID
    env = ChessEnvV2(opponent="none", initial_board=BOARD)
    moves = env.get_possible_moves(attack=True)
    env.render_moves(moves)
    expected_attacks = set(
        [
            (5, 5),
            (3, 4),
            (4, 3),
            (5, 4),
            (5, 1),
            (5, 7),
            (4, 5),
            (3, 3),
            (5, 6),
            (5, 3),
            (3, 5),
            (5, 2),
        ]
    )
    squares_attacked = set([tuple(move[1]) for move in moves])
    print(squares_attacked)
    assert squares_attacked == expected_attacks


if __name__ == "__main__":
    run_test_funcs(__name__)
