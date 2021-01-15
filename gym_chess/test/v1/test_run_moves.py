from copy import copy

import numpy as np
from gym_chess import ChessEnvV1
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

# Pawn basic movements
def test_pawn_basic_moves():
    BOARD = copy(BASIC_BOARD)
    BOARD[6, 0] = PAWN_ID
    BOARD[1, 0] = -PAWN_ID
    env = ChessEnvV1(opponent="none", initial_state=BOARD)
    # player_1
    actions = env.get_possible_actions()
    env.step(actions[0])
    # player_2
    actions = env.get_possible_actions()
    env.step(actions[0])
    # player_3
    actions = env.get_possible_actions()
    env.step(actions[0])
    # player_4
    actions = env.get_possible_actions()
    env.step(actions[0])

    EXPECTED_BOARD = copy(BASIC_BOARD)
    EXPECTED_BOARD[4, 0] = PAWN_ID
    EXPECTED_BOARD[3, 0] = -PAWN_ID
    assert (env.state == EXPECTED_BOARD).all()


if __name__ == "__main__":
    run_test_funcs(__name__)
