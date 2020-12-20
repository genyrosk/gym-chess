import numpy as np
from copy import copy

from gym_chess.envs import ChessEnvV2
from gym_chess.envs.chess_v2 import (
    KING_ID,
    QUEEN_ID,
    ROOK_ID,
    BISHOP_ID,
    KNIGHT_ID,
    PAWN_ID,
)


# Blank board
BASIC_BOARD = np.array([[0] * 8] * 8, dtype=np.int8)
BASIC_BOARD[3, 3] = -PAWN_ID
BASIC_BOARD[2, 4] = -PAWN_ID
BASIC_BOARD[3, 5] = -PAWN_ID

# King capture movements
BOARD = copy(BASIC_BOARD)
BOARD[4, 4] = KING_ID
env = ChessEnvV2(opponent="none", initial_state=BOARD)
moves = env.get_possible_moves()
env.render_moves(moves)
king_is_checked = env.king_is_checked()
print("king_is_checked", king_is_checked)

# King capture movements
BOARD = copy(BASIC_BOARD)
BOARD[3, 4] = KING_ID
env = ChessEnvV2(opponent="none", initial_state=BOARD)
moves = env.get_possible_moves()
env.render_moves(moves)
king_is_checked = env.king_is_checked()
print("king_is_checked", king_is_checked)
