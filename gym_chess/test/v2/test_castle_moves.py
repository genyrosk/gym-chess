from collections import defaultdict
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
    CASTLE_KING_SIDE_WHITE,
    CASTLE_QUEEN_SIDE_WHITE,
)
from gym_chess.test.utils import run_test_funcs


# Blank board
BASIC_BOARD = np.array([[0] * 8] * 8, dtype=np.int8)
BASIC_BOARD[6, 0] = PAWN_ID
BASIC_BOARD[6, 1] = PAWN_ID
BASIC_BOARD[6, 2] = PAWN_ID
BASIC_BOARD[6, 3] = PAWN_ID
BASIC_BOARD[6, 4] = PAWN_ID
BASIC_BOARD[6, 5] = PAWN_ID
BASIC_BOARD[6, 6] = PAWN_ID
BASIC_BOARD[6, 7] = PAWN_ID


# King side castle
def test_king_side_castle():
    BOARD = copy(BASIC_BOARD)
    BOARD[7, 4] = KING_ID
    BOARD[7, 7] = ROOK_ID
    env = ChessEnvV2(opponent="none", initial_board=BOARD)
    moves = env.get_castle_moves(player=env.current_player)
    env.render_moves(moves)
    assert moves == [CASTLE_KING_SIDE_WHITE]


# Queen side castle
def test_queen_side_castle():
    BOARD = copy(BASIC_BOARD)
    BOARD[7, 0] = ROOK_ID
    BOARD[7, 4] = KING_ID
    env = ChessEnvV2(opponent="none", initial_board=BOARD)
    moves = env.get_castle_moves(player=env.current_player)
    env.render_moves(moves)
    assert moves == [CASTLE_QUEEN_SIDE_WHITE]


# Attacked square side castle
# def test_attacked_square_castling_path():
#     BOARD = copy(BASIC_BOARD)
#     BOARD[0, 2] = -ROOK_ID
#     BOARD[6, 2] = 0
#     BOARD[7, 0] = ROOK_ID
#     BOARD[7, 4] = KING_ID
#     env = ChessEnvV2(opponent="none", initial_board=BOARD)

#     opponent = env.get_other_player(env.current_player)
#     moves = env.get_possible_moves(player=opponent, attack=True)
#     env.render_moves(moves)

#     squares_under_attack = env.get_squares_attacked_by_player(env.state, opponent)
#     squares_under_attack_hashmap = defaultdict(lambda: None)
#     for sq in squares_under_attack:
#         squares_under_attack_hashmap[tuple(sq)] = True
#     moves = env.castle_moves(
#         env.current_player, squares_under_attack_hashmap=squares_under_attack_hashmap
#     )
#     env.render_moves(moves)
#     assert moves == []


# King moves
# def test_king_has_moved_castling():
# BOARD = copy(BASIC_BOARD)
# BOARD[7, 0] = ROOK_ID
# BOARD[7, 4] = KING_ID
# env = ChessEnvV2(opponent="none", initial_board=BOARD)
# king_moves = env.king_moves(env.current_player, np.array([7, 4]))
# action = env.move_to_action(king_moves[0])
# env.step(action)
# env.render()
# env.current_player = "white"
# moves = env.castle_moves(env.current_player)
# env.render_moves(moves)
#     assert moves == []


if __name__ == "__main__":
    run_test_funcs(__name__)
