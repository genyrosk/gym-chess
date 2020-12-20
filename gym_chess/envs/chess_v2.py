import os
import sys

# import time

from copy import copy
from six import StringIO
from pprint import pprint
from dataclasses import dataclass

import gym
from gym import spaces, error, utils
from gym.utils import seeding
import numpy as np


EMPTY_SQUARE_ID = 0
KING_ID = 1
QUEEN_ID = 2
ROOK_ID = 3
BISHOP_ID = 4
KNIGHT_ID = 5
PAWN_ID = 6

KING = "king"
QUEEN = "queen"
ROOK = "rook"
BISHOP = "bishop"
KNIGHT = "knight"
PAWN = "pawn"

WHITE_ID = 1
BLACK_ID = -1

WHITE = "white"
BLACK = "black"

KINGS_SIDE = "kinds_side"
QUEENS_SIDE = "queens_side"

RESIGN_WHITE = "resignation_white"
RESIGN_BLACK = "resignation_black"

CONVERT_PAWN_TO_QUEEN_REWARD = 10
PAWN_VALUE = 1
KNIGHT_VALUE = 3
BISHOP_VALUE = 3
ROOK_VALUE = 5
QUEEN_VALUE = 10


@dataclass
class Castle:
    color: str
    side: str


@dataclass
class Piece:
    id: int
    icon: str
    type: str
    color: str
    value: float


PIECES = [
    Piece(icon="♙", color=BLACK, type=PAWN, id=-PAWN_ID, value=PAWN_VALUE),
    Piece(icon="♘", color=BLACK, type=KNIGHT, id=-KNIGHT_ID, value=KNIGHT_VALUE),
    Piece(icon="♗", color=BLACK, type=BISHOP, id=-BISHOP_ID, value=BISHOP_VALUE),
    Piece(icon="♖", color=BLACK, type=ROOK, id=-ROOK_ID, value=ROOK_VALUE),
    Piece(icon="♕", color=BLACK, type=QUEEN, id=-QUEEN_ID, value=QUEEN_VALUE),
    Piece(icon="♔", color=BLACK, type=KING, id=-KING_ID, value=0),
    Piece(icon=".", color=None, type=None, id=EMPTY_SQUARE_ID, value=0),
    Piece(icon="♚", color=WHITE, type=KING, id=KING_ID, value=0),
    Piece(icon="♛", color=WHITE, type=QUEEN, id=QUEEN_ID, value=QUEEN_VALUE),
    Piece(icon="♜", color=WHITE, type=ROOK, id=ROOK_ID, value=ROOK_VALUE),
    Piece(icon="♝", color=WHITE, type=BISHOP, id=BISHOP_ID, value=BISHOP_VALUE),
    Piece(icon="♞", color=WHITE, type=KNIGHT, id=KNIGHT_ID, value=KNIGHT_VALUE),
    Piece(icon="♟", color=WHITE, type=PAWN, id=PAWN_ID, value=PAWN_VALUE),
]

ID_TO_COLOR = {piece.id: piece.color for piece in PIECES}
ID_TO_ICON = {piece.id: piece.icon for piece in PIECES}
ID_TO_TYPE = {piece.id: piece.type for piece in PIECES}
ID_TO_VALUE = {piece.id: piece.value for piece in PIECES}

CASTLE_KINGS_SIDE_WHITE = Castle(color=WHITE, side=KINGS_SIDE)
CASTLE_QUEENS_SIDE_WHITE = Castle(color=WHITE, side=QUEENS_SIDE)
CASTLE_KINGS_SIDE_BLACK = Castle(color=BLACK, side=KINGS_SIDE)
CASTLE_QUEENS_SIDE_BLACK = Castle(color=BLACK, side=QUEENS_SIDE)

DEFAULT_BOARD = np.array(
    [
        [-3, -5, -4, -2, -1, -4, -5, -3],
        [-6, -6, -6, -6, -6, -6, -6, -6],
        [0] * 8,
        [0] * 8,
        [0] * 8,
        [0] * 8,
        [6, 6, 6, 6, 6, 6, 6, 6],
        [3, 5, 4, 2, 1, 4, 5, 3],
    ],
    dtype=np.int8,
)


# AGENT POLICY
# ------------
def make_random_policy(np_random, bot_player):
    def random_policy(env):
        moves = env.get_possible_moves(player=bot_player)
        # No moves left
        if len(moves) == 0:
            return "resign"
        else:
            idx = np.random.choice(np.arange(len(moves)))
            return moves[idx]

    return random_policy


# CHESS GYM ENVIRONMENT CLASS
# ---------------------------
class ChessEnvV2(gym.Env):
    def __init__(
        self,
        player_color=WHITE,
        opponent="random",
        log=True,
        initial_state=DEFAULT_BOARD,
    ):
        # constants
        self.moves_max = 149
        self.log = log
        self.initial_state = initial_state

        # One action (for each board position) x (for each board position),
        # 4 x castles, offer/accept draw and resign
        self.observation_space = spaces.Box(-16, 16, (8, 8))  # board 8x8
        self.action_space = spaces.Discrete(64 * 64 + 4 + 4)

        self.player = player_color  # define player # TODO: implement
        self.player_2 = self.get_other_player(player_color)
        self.opponent = opponent  # define opponent

        # variables
        self.state = None
        self.prev_state = None
        self.done = False
        self.current_player = None
        self.saved_states = {}
        self.repetitions = 0
        self.move_count = 0

        # reset and build state
        self.seed()
        self.reset()

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)

        # Update the random policy if needed
        if isinstance(self.opponent, str):
            if self.opponent == "random":
                self.opponent_policy = make_random_policy(self.np_random, self.player_2)
            elif self.opponent == "none":
                self.opponent_policy = None
            else:
                raise error.Error(f"Unrecognized opponent policy {self.opponent}")
        else:
            self.opponent_policy = self.opponent

        return [seed]

    def reset(self):
        """
        Resets the state of the environment, returning an initial observation.
        Outputs -> observation : the initial observation of the space. (Initial reward is assumed to be 0.)
        """
        self.state = self.initial_state
        self.prev_state = None
        self.done = False
        self.current_player = WHITE
        self.saved_states = {}
        self.repetitions = 0  # 3 repetitions ==> DRAW
        self.move_count = 0
        # TODO: Let the opponent play if it's not the agent's turn
        # if self.player != BLACK:
        #     a = self.opponent_policy(self.state)
        #     HexEnv.make_move(self.state, a, HexEnv.BLACK)
        #     self.to_play = HexEnv.WHITE
        return self.state

    def step(self, action):
        """
        Run one timestep of the environment's dynamics. When end of episode
        is reached, reset() should be called to reset the environment's internal state.

        Input
        -----
        action : an action provided by the environment

        Outputs
        -------
        (observation, reward, done, info)
        observation : agent's observation of the current environment
        reward [Float] : amount of reward due to the previous action
        done : a boolean, indicating whether the episode has ended
        info : a dictionary containing other diagnostic information from the previous action
        """
        # validate action
        assert self.action_space.contains(action), "ACTION ERROR {}".format(action)

        # Game is done
        if self.done:
            return (
                self.state,
                0.0,
                True,
                {"state": self.state, "move_count": self.move_count},
            )
        if self.move_count > self.moves_max:
            return (
                self.state,
                0.0,
                True,
                {"state": self.state, "move_count": self.move_count},
            )

        # make move
        self.state, reward, self.done = self.player_move(action)
        self.switch_player()

        if self.done:
            return self.state, reward, self.done, {"state": self.state}

        # Bot Opponent play
        if self.opponent_policy:
            opponent_move = self.opponent_policy(self)
            opponent_action = self.move_to_action(opponent_move)
            # make move
            self.state, opp_reward, self.done = self.player_move(opponent_action)
            reward -= opp_reward
            self.switch_player()

        # increment count on WHITE
        if self.current_player == WHITE:
            self.move_count += 1

        return self.state, reward, self.done, {"state": self.state}

    def switch_player(self):
        if self.current_player == WHITE:
            self.current_player = BLACK
        else:
            self.current_player = WHITE
        return self.current_player

    @property
    def opponent_player(self):
        if self.current_player == WHITE:
            return BLACK
        return WHITE

    @property
    def current_player_is_white(self):
        return self.current_player == WHITE

    @property
    def current_player_is_black(self):
        return not self.current_player_is_white

    def get_other_player(self, player):
        if player == WHITE:
            return BLACK
        return WHITE

    def player_move(self, action):
        """
        Returns (state, reward, done)
        """
        # Resign
        if self.is_resignation(action):
            return self.state, -100, True
        # Play
        move = self.action_to_move(action)
        new_state, reward = self.next_state(move)
        # TODO: Save current state and keep track of repetitions
        # self.saved_states = ChessEnv.encode_current_state(state, self.saved_states)
        # self.repetitions = max([v for k, v in self.saved_states.items()])
        # 3-fold repetition => DRAW
        # if self.repetitions >= 3:
        # 	return new_state, 0, True
        # Render
        if self.log:
            print(" " * 10, ">" * 10, self.current_player)
            self.render_moves([move], mode="human")
        return new_state, reward, False

    def next_state(self, move):
        """
        Return the next state given a move
        -------
        (next_state, reward)
        """
        new_state = copy(self.state)
        reward = 0

        # TODO: implement castle move
        #

        # Classic move
        _from, _to = move
        piece_to_move = copy(self.state[_from[0], _from[1]])
        captured_piece = copy(self.state[_to[0], _to[1]])
        assert piece_to_move, f"Bad move: {move} - piece is empty"
        new_state[_from[0], _from[1]] = 0
        new_state[_to[0], _to[1]] = piece_to_move

        # Pawn becomes Queen
        # TODO: allow player to choose the piece into which the pawn converts
        if ID_TO_TYPE[piece_to_move] == PAWN:
            if (self.current_player_is_white and _to[0] == 7) or (
                self.current_player_is_black and _to[0] == 0
            ):
                new_state[_to[0], _to[1]] = QUEEN_ID * self.player_to_int(
                    self.current_player
                )
                reward += CONVERT_PAWN_TO_QUEEN_REWARD

        # Reward
        reward += ID_TO_VALUE[captured_piece]

        return new_state, reward

    def state_to_grid(self):
        grid = [[f" {ID_TO_ICON[square]} " for square in row] for row in self.state]
        return grid

    def render_grid(self, grid, mode="human"):
        outfile = StringIO() if mode == "ansi" else sys.stdout
        outfile.write("    ")
        outfile.write("-" * 25)
        outfile.write("\n")
        for i, row in enumerate(grid):
            outfile.write(f" {i+1} | ")
            for square in row:
                outfile.write(square)
            outfile.write("|\n")
        outfile.write("    ")
        outfile.write("-" * 25)
        outfile.write("\n      a  b  c  d  e  f  g  h ")
        outfile.write("\n")
        outfile.write("\n")

        if mode != "human":
            return outfile

    def render(self, mode="human"):
        """Render the playing board"""
        grid = self.state_to_grid()
        self.render_grid(grid, mode=mode)

    def render_moves(self, moves, mode="human"):
        grid = self.state_to_grid()
        for move in moves:
            x0, y0 = move[0][0], move[0][1]
            x1, y1 = move[1][0], move[1][1]
            if len(grid[x0][y0]) < 4:
                grid[x0][y0] = utils.colorize(
                    utils.colorize(grid[x0][y0], "gray"), "white", highlight=True
                )
            if len(grid[x1][y1]) < 4:
                if self.state[x1, y1]:
                    grid[x1][y1] = utils.colorize(
                        utils.colorize(grid[x1][y1], "gray"), "red", highlight=True
                    )
                else:
                    grid[x1][y1] = utils.colorize(
                        utils.colorize(grid[x1][y1], "gray"), "green", highlight=True
                    )
        self.render_grid(grid, mode=mode)

    def move_to_action(self, move):
        if move == CASTLE_KINGS_SIDE_WHITE:
            return 64 * 64
        elif move == CASTLE_QUEENS_SIDE_WHITE:
            return 64 * 64 + 1
        elif move == CASTLE_KINGS_SIDE_BLACK:
            return 64 * 64 + 2
        elif move == CASTLE_QUEENS_SIDE_BLACK:
            return 64 * 64 + 3
        _from = move[0][0] * 8 + move[0][1]
        _to = move[1][0] * 8 + move[1][1]
        return _from * 64 + _to

    def action_to_move(self, action):
        if action >= 64 * 64:
            _action = action - 64 * 64
            if _action == 0:
                return CASTLE_KINGS_SIDE_WHITE
            elif _action == 1:
                return CASTLE_QUEENS_SIDE_WHITE
            elif _action == 2:
                return CASTLE_KINGS_SIDE_BLACK
            elif _action == 3:
                return CASTLE_QUEENS_SIDE_BLACK
        _from, _to = action // 64, action % 64
        x0, y0 = _from // 8, _from % 8
        x1, y1 = _to // 8, _to % 8
        return [np.array([x0, y0], dtype=np.int8), np.array([x1, y1], dtype=np.int8)]

    def get_possible_actions(self):
        moves = self.get_possible_moves(player=self.current_player)
        return [self.move_to_action(move) for move in moves]

    def get_possible_moves(self, player=None, attack=False):
        if player is None:
            player = self.current_player
        moves = []
        for coords, piece_id in np.ndenumerate(self.state):
            coords = np.array(coords, dtype=np.int8)
            if piece_id == 0:
                continue
            color = ID_TO_COLOR[piece_id]
            if color != player:
                continue
            # breakpoint()
            piece_type = ID_TO_TYPE[piece_id]
            if piece_type == KING:
                moves += self.king_moves(player, coords, attack=attack)
            elif piece_type == QUEEN:
                moves += self.queen_moves(player, coords, attack=attack)
            elif piece_type == ROOK:
                moves += self.rook_moves(player, coords, attack=attack)
            elif piece_type == BISHOP:
                moves += self.bishop_moves(player, coords, attack=attack)
            elif piece_type == KNIGHT:
                moves += self.knight_moves(player, coords, attack=attack)
            elif piece_type == PAWN:
                moves += self.pawn_moves(player, coords, attack=attack)

        # TODO: castle moves
        return moves

    def king_moves(self, player, coords, attack=False):
        """KING MOVES"""
        # breakpoint()
        moves = []
        steps = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]
        for step in steps:
            square = coords + np.array(step, dtype=np.int8)
            if attack:
                if self.king_attack(player, square):
                    moves.append([coords, square])
            else:
                if self.king_move(player, square):
                    moves.append([coords, square])
        return moves

    def queen_moves(self, player, coords, attack=False):
        """QUEEN MOVES"""
        # breakpoint()
        moves = []
        moves += self.rook_moves(player, coords, attack=attack)
        moves += self.bishop_moves(player, coords, attack=attack)
        return moves

    def rook_moves(self, player, coords, attack=False):
        """ROOK MOVES"""
        # breakpoint()
        moves = []
        for step in [[-1, 0], [+1, 0], [0, -1], [0, +1]]:
            moves += self.iterativesteps(player, coords, step, attack=attack)
        return moves

    def bishop_moves(self, player, coords, attack=False):
        """BISHOP MOVES"""
        # breakpoint()
        moves = []
        for step in [[-1, -1], [-1, +1], [+1, -1], [+1, +1]]:
            moves += self.iterativesteps(player, coords, step, attack=attack)
        return moves

    def iterativesteps(self, player, coords, step, attack=False):
        """Used to calculate Bishop, Rook and Queen moves"""
        # breakpoint()
        moves = []
        k = 1
        step = np.array(step, dtype=np.int8)
        while True:
            square = coords + k * step
            if attack:
                add_bool, stop_bool = self.attacking_move(player, square)
                if add_bool:
                    moves.append([coords, square])
                if stop_bool:
                    break
                else:
                    k += 1
            else:
                add_bool, stop_bool = self.playable_move(player, square)
                if add_bool:
                    moves.append([coords, square])
                if stop_bool:
                    break
                else:
                    k += 1
        return moves

    def knight_moves(self, player, coords, attack=False):
        """KNIGHT MOVES"""
        # breakpoint()
        moves = []
        steps = [
            [-2, -1],
            [-2, +1],
            [+2, -1],
            [+2, +1],
            [-1, -2],
            [-1, +2],
            [+1, -2],
            [+1, +2],
        ]
        # filter:
        for step in steps:
            square = coords + np.array(step, dtype=np.int8)
            if attack:
                is_playable, _ = self.attacking_move(player, square)
                if is_playable:
                    moves.append([coords, square])
            else:
                is_playable, _ = self.playable_move(player, square)
                if is_playable:
                    moves.append([coords, square])
        return moves

    def pawn_moves(self, player, coords, attack=False):
        """PAWN MOVES"""
        moves = []
        player_int = ChessEnvV2.player_to_int(player)
        attack_squares = [
            coords + np.array([1, -1], dtype=np.int8) * (-player_int),
            coords + np.array([1, +1], dtype=np.int8) * (-player_int),
        ]
        one_step_square = coords + np.array([1, 0], dtype=np.int8) * (-player_int)
        two_step_square = coords + np.array([2, 0], dtype=np.int8) * (-player_int)

        if attack:
            for square in attack_squares:
                if ChessEnvV2.square_is_on_board(
                    square
                ) and not self.is_king_from_player(player, square):
                    moves.append([coords, square])
        else:
            # moves only to empty squares
            x, y = one_step_square
            if ChessEnvV2.square_is_on_board(one_step_square) and self.state[x, y] == 0:
                moves.append([coords, one_step_square])

            x, y = two_step_square
            # breakpoint()
            if ChessEnvV2.square_is_on_board(two_step_square) and (
                (player == WHITE and coords[0] == 6)
                or (player == BLACK and coords[0] == 1)
            ):
                if self.state[x, y] == 0:
                    moves.append([coords, two_step_square])

            # attacks only opponent's pieces
            for square in attack_squares:
                if ChessEnvV2.square_is_on_board(
                    square
                ) and self.is_piece_from_other_player(player, square):
                    moves.append([coords, square])

            # TODO: implement en-passant pawn capture
            #
        return moves

    def castle_moves(self):
        moves = []
        return moves

    def king_move(self, player, square):
        """
        return squares to which the king can move,
        i.e. unattacked squares that can be:
        - empty squares
        - opponent pieces (excluding king)
        If opponent king is encountered, then there's a problem...
        => return <bool> is_playable
        """
        opponent_player = self.get_other_player(player)
        opponent_attacked_squares = self.get_squares_attacked_by_player(opponent_player)

        if not ChessEnvV2.square_is_on_board(square):
            return False
        elif ChessEnvV2.move_is_in_list(square, opponent_attacked_squares):
            return False
        elif self.is_piece_from_player(player, square):
            return False
        elif self.is_king_from_other_player(player, square):
            raise Exception(f"KINGS NEXT TO EACH OTHER ERROR {square}")
        elif self.is_piece_from_other_player(player, square):
            return True
        elif self.state[square[0], square[1]] == 0:  # empty square
            return True
        else:
            raise Exception(f"KING MOVEMENT ERROR {square}")

    def king_attack(self, player, square):
        """
        return all the squares that the king can attack, except:
        - squares outside the board
        If opponent king is encountered, then there's a problem...
        => return <bool> is_playable
        """
        if not ChessEnvV2.square_is_on_board(square):
            return False
        elif self.is_piece_from_player(player, square):
            return True
        elif self.is_king_from_other_player(player, square):
            raise Exception(f"KINGS NEXT TO EACH OTHER ERROR {square}")
        elif self.is_piece_from_other_player(player, square):
            return True
        elif self.state[square[0], square[1]] == 0:  # empty square
            return True
        else:
            raise Exception(f"KING MOVEMENT ERROR {square}")

    def playable_move(self, player, square):
        """
        return squares to which a piece can move
        - empty squares
        - opponent pieces (excluding king)
        => return [<bool> playable, <bool> stop_iteration]
        """
        if not ChessEnvV2.square_is_on_board(square):
            return False, True
        elif self.is_piece_from_player(player, square):
            return False, True
        elif self.is_king_from_other_player(player, square):
            return False, True
        elif self.is_piece_from_other_player(player, square):
            return True, True
        elif self.state[square[0], square[1]] == 0:  # empty square
            return True, False
        else:
            raise Exception(f"PLAYABLE MOVE ERROR {square}")

    def attacking_move(self, player, square):
        """
        return squares that are attacked or defended
        - empty squares
        - opponent pieces (opponent king is ignored)
        - own pieces
        => return [<bool> playable, <bool> stop_iteration]
        """
        # breakpoint()
        if not ChessEnvV2.square_is_on_board(square):
            return False, True
        elif self.is_piece_from_player(player, square):
            return True, True
        elif self.is_king_from_other_player(player, square):
            return True, False
        elif self.is_piece_from_other_player(player, square):
            return True, True
        elif self.state[square[0], square[1]] == 0:  # empty square
            return True, False
        else:
            raise Exception(f"ATTACKING MOVE ERROR {square}")

    def get_squares_attacked_by_player(self, player):
        moves = self.get_possible_moves(player=player, attack=True)
        attacked_squares = [move[1] for move in moves]
        return attacked_squares

    def is_current_player_piece(self, square):
        self.is_piece_from_player(square, self.current_player)

    def is_opponent_piece(self, square):
        self.is_piece_from_player(square, self.opponent_player)

    def is_piece_from_player(self, player, square):
        piece_id = self.state[square[0], square[1]]
        color = ID_TO_COLOR[piece_id]
        return color == player

    def is_piece_from_other_player(self, player, square):
        return self.is_piece_from_player(self.get_other_player(player), square)

    def is_king_from_current_player(self, square):
        self.is_king_from_player(square, self.current_player)

    def is_king_from_opponent_player(self, square):
        self.is_king_from_player(square, self.opponent_player)

    def is_king_from_player(self, player, square):
        piece_id = self.state[square[0], square[1]]
        if ID_TO_TYPE[piece_id] != KING:
            return False
        color = ID_TO_COLOR[piece_id]
        return color == player

    def is_king_from_other_player(self, player, square):
        return self.is_king_from_player(self.get_other_player(player), square)

    # TODO: implement resignation action parsing
    def is_resignation(self, action):
        return False

    @staticmethod
    def move_is_in_list(move, move_list):
        for m in move_list:
            if np.all(move == m):
                return True
        return False

    @staticmethod
    def player_to_int(player):
        if player == WHITE:
            return 1
        return -1

    @staticmethod
    def square_is_on_board(square):
        return not (square[0] < 0 or square[0] > 7 or square[1] < 0 or square[1] > 7)

    def king_is_checked(self, player=None):
        if player is None:
            player = self.current_player
        player_int = ChessEnvV2.player_to_int(player)
        king_id = player_int * KING_ID
        king_pos = np.where(self.state == king_id)
        king_square = [king_pos[0][0], king_pos[1][0]]
        other_player = self.get_other_player(player)
        attacked_squares = self.get_squares_attacked_by_player(other_player)
        return any(np.equal(attacked_squares, king_square).all(1))
