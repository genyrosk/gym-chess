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
BASIC_BOARD[3, 4] = -PAWN_ID
BASIC_BOARD[3, 5] = -PAWN_ID
BASIC_BOARD[6, 3] = PAWN_ID
BASIC_BOARD[6, 4] = PAWN_ID
BASIC_BOARD[6, 5] = PAWN_ID

# Pawn capture movements
BOARD = copy(BASIC_BOARD)
BOARD[4, 4] = PAWN_ID
env = ChessEnvV2(opponent="none", initial_state=BOARD)
moves = env.get_possible_moves()
env.render_moves(moves)

# Knight capture movements
BOARD = copy(BASIC_BOARD)
BOARD[5, 3] = KNIGHT_ID
env = ChessEnvV2(opponent="none", initial_state=BOARD)
moves = env.get_possible_moves()
env.render_moves(moves)

# Bishop capture movements
BOARD = copy(BASIC_BOARD)
BOARD[5, 3] = BISHOP_ID
env = ChessEnvV2(opponent="none", initial_state=BOARD)
moves = env.get_possible_moves()
env.render_moves(moves)

# Rook capture movements
BOARD = copy(BASIC_BOARD)
BOARD[5, 3] = ROOK_ID
env = ChessEnvV2(opponent="none", initial_state=BOARD)
moves = env.get_possible_moves()
env.render_moves(moves)

# Queen capture movements
BOARD = copy(BASIC_BOARD)
BOARD[5, 3] = QUEEN_ID
env = ChessEnvV2(opponent="none", initial_state=BOARD)
moves = env.get_possible_moves()
env.render_moves(moves)

# King capture movements
BOARD = copy(BASIC_BOARD)
BOARD[4, 3] = KING_ID
env = ChessEnvV2(opponent="none", initial_state=BOARD)
moves = env.get_possible_moves()
env.render_moves(moves)
