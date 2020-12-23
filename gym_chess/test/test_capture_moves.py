from copy import copy

import numpy as np
from gym_chess.envs import ChessEnvV2
from gym_chess.envs.chess_v2 import (
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
BASIC_BOARD[3, 3] = -PAWN_ID
BASIC_BOARD[3, 4] = -PAWN_ID
BASIC_BOARD[3, 5] = -PAWN_ID
BASIC_BOARD[6, 3] = PAWN_ID
BASIC_BOARD[6, 4] = PAWN_ID
BASIC_BOARD[6, 5] = PAWN_ID


# Pawn capture movements
def test_pawn_capture_moves():
    BOARD = copy(BASIC_BOARD)
    BOARD[4, 4] = PAWN_ID
    env = ChessEnvV2(opponent="none", initial_state=BOARD)
    moves = env.get_possible_moves()
    env.render_moves(moves)
    expected_moves = set([(5, 5), (4, 3), (5, 4), (4, 5), (3, 3), (5, 3), (3, 5)])
    assert set([tuple(move[1]) for move in moves]) == expected_moves


# Knight capture movements
def test_knight_capture_moves():
    BOARD = copy(BASIC_BOARD)
    BOARD[5, 3] = KNIGHT_ID
    env = ChessEnvV2(opponent="none", initial_state=BOARD)
    moves = env.get_possible_moves()
    env.render_moves(moves)
    expected_moves = set(
        [
            (4, 4),
            (7, 4),
            (5, 5),
            (3, 4),
            (4, 3),
            (6, 1),
            (5, 4),
            (4, 5),
            (7, 2),
            (3, 2),
            (4, 1),
        ]
    )
    assert set([tuple(move[1]) for move in moves]) == expected_moves


# Bishop capture movements
def test_bishop_capture_moves():
    BOARD = copy(BASIC_BOARD)
    BOARD[5, 3] = BISHOP_ID
    env = ChessEnvV2(opponent="none", initial_state=BOARD)
    moves = env.get_possible_moves()
    env.render_moves(moves)
    expected_moves = set(
        [
            (4, 4),
            (6, 2),
            (5, 5),
            (7, 1),
            (4, 3),
            (3, 1),
            (5, 4),
            (2, 0),
            (4, 2),
            (4, 5),
            (3, 5),
        ]
    )
    assert set([tuple(move[1]) for move in moves]) == expected_moves


# Rook capture movements
def test_rook_capture_moves():
    BOARD = copy(BASIC_BOARD)
    BOARD[5, 3] = ROOK_ID
    env = ChessEnvV2(opponent="none", initial_state=BOARD)
    moves = env.get_possible_moves()
    env.render_moves(moves)
    expected_moves = set(
        [
            (4, 4),
            (5, 5),
            (4, 3),
            (5, 4),
            (5, 1),
            (5, 7),
            (4, 5),
            (3, 3),
            (5, 0),
            (5, 6),
            (5, 2),
        ]
    )
    assert set([tuple(move[1]) for move in moves]) == expected_moves


# Queen capture movements
def test_queen_capture_moves():
    BOARD = copy(BASIC_BOARD)
    BOARD[5, 3] = QUEEN_ID
    env = ChessEnvV2(opponent="none", initial_state=BOARD)
    moves = env.get_possible_moves()
    env.render_moves(moves)
    expected_moves = set(
        [
            (4, 4),
            (6, 2),
            (5, 5),
            (7, 1),
            (4, 3),
            (3, 1),
            (5, 4),
            (2, 0),
            (5, 1),
            (5, 7),
            (4, 2),
            (4, 5),
            (3, 3),
            (5, 0),
            (5, 6),
            (3, 5),
            (5, 2),
        ]
    )
    assert set([tuple(move[1]) for move in moves]) == expected_moves


# King capture movements
def test_king_capture_moves():
    BOARD = copy(BASIC_BOARD)
    BOARD[4, 3] = KING_ID
    env = ChessEnvV2(opponent="none", initial_state=BOARD)
    moves = env.get_possible_moves()
    env.render_moves(moves)
    expected_moves = set(
        [(4, 4), (5, 5), (3, 4), (5, 4), (4, 5), (3, 3), (5, 3), (3, 2), (5, 2)]
    )
    assert set([tuple(move[1]) for move in moves]) == expected_moves


if __name__ == "__main__":
    run_test_funcs(__name__)
