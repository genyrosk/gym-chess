from copy import copy

import numpy as np
from gym_chess import ChessEnvV2
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
BASIC_BOARD[2, 4] = -PAWN_ID
BASIC_BOARD[3, 5] = -PAWN_ID


# King capture movements
def test_king_moves_1():
    BOARD = copy(BASIC_BOARD)
    BOARD[4, 4] = KING_ID
    BOARD[0, 0] = ROOK_ID
    env = ChessEnvV2(opponent="none", initial_board=BOARD)
    moves = env.get_possible_moves()
    env.render_moves(moves)
    king_is_checked = env.white_king_is_checked
    expected_attacks = set([(5, 5), (3, 4), (4, 3), (5, 4), (4, 5), (5, 3)])
    squares_attacked = set([tuple(move[1]) for move in moves])
    assert squares_attacked == expected_attacks
    assert king_is_checked


# King capture movements
def test_king_moves_2():
    BOARD = copy(BASIC_BOARD)
    BOARD[3, 4] = KING_ID
    env = ChessEnvV2(opponent="none", initial_board=BOARD)
    moves = env.get_possible_moves()
    env.render_moves(moves)
    king_is_checked = env.white_king_is_checked
    expected_attacks = set([(2, 4), (4, 3), (2, 3), (4, 5), (2, 5)])
    squares_attacked = set([tuple(move[1]) for move in moves])
    assert squares_attacked == expected_attacks
    assert not king_is_checked


if __name__ == "__main__":
    run_test_funcs(__name__)
