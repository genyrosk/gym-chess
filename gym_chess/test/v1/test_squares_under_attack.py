from copy import copy

import numpy as np
from gym_chess.envs import ChessEnvV1
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
    env = ChessEnvV1(opponent="none", initial_state=BOARD)
    moves = env.get_possible_moves(attack=True)
    env.render_moves(moves)
    expected_moves = set([(5, 5), (5, 4), (5, 1), (5, 7), (3, 3), (5, 6), (5, 3), (3, 5), (5, 2)])
    assert set([tuple(move[1]) for move in moves]) == expected_moves


# Knight basic movements
def test_knight_moves():
    BOARD = copy(BASIC_BOARD)
    BOARD[4, 4] = KNIGHT_ID
    env = ChessEnvV1(opponent="none", initial_state=BOARD)
    moves = env.get_possible_moves(attack=True, skip_pawns=True)
    env.render_moves(moves)
    expected_moves = set([(6, 5), (2, 3), (6, 3), (5, 6), (3, 6), (3, 2), (2, 5), (5, 2)])
    assert set([tuple(move[1]) for move in moves]) == expected_moves


# Bishop basic movements
def test_bishop_moves():
    BOARD = copy(BASIC_BOARD)
    BOARD[4, 4] = BISHOP_ID
    env = ChessEnvV1(opponent="none", initial_state=BOARD)
    moves = env.get_possible_moves(attack=True, skip_pawns=True)
    env.render_moves(moves)
    expected_moves = set([(6, 2), (5, 5), (6, 6), (3, 3), (5, 3), (3, 5)])
    assert set([tuple(move[1]) for move in moves]) == expected_moves


# Rook basic movements
def test_rook_moves():
    BOARD = copy(BASIC_BOARD)
    BOARD[4, 4] = ROOK_ID
    env = ChessEnvV1(opponent="none", initial_state=BOARD)
    moves = env.get_possible_moves(attack=True, skip_pawns=True)
    env.render_moves(moves)
    expected_moves = set(
        [(4, 0), (3, 4), (4, 3), (5, 4), (4, 6), (6, 4), (4, 2), (4, 5), (4, 1), (4, 7)]
    )
    assert set([tuple(move[1]) for move in moves]) == expected_moves


# Queen basic movements
def test_queen_moves():
    BOARD = copy(BASIC_BOARD)
    BOARD[4, 4] = QUEEN_ID
    env = ChessEnvV1(opponent="none", initial_state=BOARD)
    moves = env.get_possible_moves(attack=True, skip_pawns=True)
    env.render_moves(moves)
    expected_moves = set(
        [
            (6, 2),
            (4, 0),
            (5, 5),
            (3, 4),
            (4, 3),
            (5, 4),
            (4, 6),
            (6, 6),
            (6, 4),
            (4, 2),
            (4, 5),
            (3, 3),
            (5, 3),
            (4, 1),
            (4, 7),
            (3, 5),
        ]
    )
    assert set([tuple(move[1]) for move in moves]) == expected_moves


# King basic movements
def test_king_moves():
    BOARD = copy(BASIC_BOARD)
    BOARD[4, 4] = KING_ID
    env = ChessEnvV1(opponent="none", initial_state=BOARD)
    moves = env.get_possible_moves(attack=True, skip_pawns=True)
    env.render_moves(moves)
    expected_moves = set([(5, 5), (3, 4), (4, 3), (5, 4), (4, 5), (3, 3), (5, 3), (3, 5)])
    assert set([tuple(move[1]) for move in moves]) == expected_moves


if __name__ == "__main__":
    run_test_funcs(__name__)
