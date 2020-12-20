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
BLANK_BOARD = np.array([[0] * 8] * 8, dtype=np.int8)

# Pawn basic movements
BOARD = copy(BLANK_BOARD)
BOARD[6, 0] = PAWN_ID
env = ChessEnvV2(opponent="none", initial_state=BOARD)
moves = env.get_possible_moves()
env.render_moves(moves)

# Knight basic movements
BOARD = copy(BLANK_BOARD)
BOARD[4, 4] = KNIGHT_ID
env = ChessEnvV2(opponent="none", initial_state=BOARD)
moves = env.get_possible_moves()
env.render_moves(moves)

# Bishop basic movements
BOARD = copy(BLANK_BOARD)
BOARD[4, 4] = BISHOP_ID
env = ChessEnvV2(opponent="none", initial_state=BOARD)
moves = env.get_possible_moves()
env.render_moves(moves)

# Rook basic movements
BOARD = copy(BLANK_BOARD)
BOARD[4, 4] = ROOK_ID
env = ChessEnvV2(opponent="none", initial_state=BOARD)
moves = env.get_possible_moves()
env.render_moves(moves)

# Queen basic movements
BOARD = copy(BLANK_BOARD)
BOARD[4, 4] = QUEEN_ID
env = ChessEnvV2(opponent="none", initial_state=BOARD)
moves = env.get_possible_moves()
env.render_moves(moves)

# King basic movements
BOARD = copy(BLANK_BOARD)
BOARD[4, 4] = KING_ID
env = ChessEnvV2(opponent="none", initial_state=BOARD)
moves = env.get_possible_moves()
env.render_moves(moves)
