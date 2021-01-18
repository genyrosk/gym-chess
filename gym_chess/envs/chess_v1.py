import os
import sys
from collections import defaultdict
from copy import copy
from dataclasses import dataclass
from six import StringIO
from pprint import pprint

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

KING_DESC = "K"
QUEEN_DESC = "Q"
ROOK_DESC = "R"
BISHOP_DESC = "B"
KNIGHT_DESC = "N"
PAWN_DESC = ""

WHITE_ID = 1
BLACK_ID = -1

WHITE = "WHITE"
BLACK = "BLACK"

CONVERT_PAWN_TO_QUEEN_REWARD = 10
PAWN_VALUE = 1
KNIGHT_VALUE = 3
BISHOP_VALUE = 3
ROOK_VALUE = 5
QUEEN_VALUE = 10
WIN_REWARD = 100
LOSS_REWARD = -100
INVALID_ACTION_REWARD = -10
VALID_ACTION_REWARD = 10


@dataclass
class Piece:
    id: int
    icon: str
    desc: str
    type: str
    color: str
    value: float


PIECES = [
    Piece(icon="♙", desc=PAWN_DESC, color=BLACK, type=PAWN, id=-PAWN_ID, value=PAWN_VALUE),
    Piece(icon="♘", desc=KNIGHT_DESC, color=BLACK, type=KNIGHT, id=-KNIGHT_ID, value=KNIGHT_VALUE),
    Piece(icon="♗", desc=BISHOP_DESC, color=BLACK, type=BISHOP, id=-BISHOP_ID, value=BISHOP_VALUE),
    Piece(icon="♖", desc=ROOK_DESC, color=BLACK, type=ROOK, id=-ROOK_ID, value=ROOK_VALUE),
    Piece(icon="♕", desc=QUEEN_DESC, color=BLACK, type=QUEEN, id=-QUEEN_ID, value=QUEEN_VALUE),
    Piece(icon="♔", desc=KING_DESC, color=BLACK, type=KING, id=-KING_ID, value=0),
    Piece(icon=".", desc="", color=None, type=None, id=EMPTY_SQUARE_ID, value=0),
    Piece(icon="♚", desc=KING_DESC, color=WHITE, type=KING, id=KING_ID, value=0),
    Piece(icon="♛", desc=QUEEN_DESC, color=WHITE, type=QUEEN, id=QUEEN_ID, value=QUEEN_VALUE),
    Piece(icon="♜", desc=ROOK_DESC, color=WHITE, type=ROOK, id=ROOK_ID, value=ROOK_VALUE),
    Piece(icon="♝", desc=BISHOP_DESC, color=WHITE, type=BISHOP, id=BISHOP_ID, value=BISHOP_VALUE),
    Piece(icon="♞", desc=KNIGHT_DESC, color=WHITE, type=KNIGHT, id=KNIGHT_ID, value=KNIGHT_VALUE),
    Piece(icon="♟", desc=PAWN_DESC, color=WHITE, type=PAWN, id=PAWN_ID, value=PAWN_VALUE),
]

ID_TO_COLOR = {piece.id: piece.color for piece in PIECES}
ID_TO_ICON = {piece.id: piece.icon for piece in PIECES}
ID_TO_TYPE = {piece.id: piece.type for piece in PIECES}
ID_TO_VALUE = {piece.id: piece.value for piece in PIECES}
ID_TO_DESC = {piece.id: piece.desc for piece in PIECES}

RESIGN = "RESIGN"
CASTLE_KING_SIDE_WHITE = "CASTLE_KING_SIDE_WHITE"
CASTLE_QUEEN_SIDE_WHITE = "CASTLE_QUEEN_SIDE_WHITE"
CASTLE_KING_SIDE_BLACK = "CASTLE_KING_SIDE_BLACK"
CASTLE_QUEEN_SIDE_BLACK = "CASTLE_QUEEN_SIDE_BLACK"
CASTLE_MOVES = [
    CASTLE_KING_SIDE_WHITE,
    CASTLE_QUEEN_SIDE_WHITE,
    CASTLE_KING_SIDE_BLACK,
    CASTLE_QUEEN_SIDE_BLACK,
]

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


def highlight(string, background="white", color="gray"):
    return utils.colorize(utils.colorize(string, color), background, highlight=True)


# AGENT POLICY
# ------------
def make_random_policy(np_random, bot_player):
    def random_policy(env):
        # moves = env.get_possible_moves(player=bot_player)
        moves = env.possible_moves
        # No moves left
        if len(moves) == 0:
            return "resign"
        else:
            idx = np.random.choice(np.arange(len(moves)))
            return moves[idx]

    return random_policy


# CHESS GYM ENVIRONMENT CLASS
# ---------------------------
class ChessEnvV1(gym.Env):
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

        #
        # Observation + Action spaces
        # ---------------------------
        #  Observations: 8x8 board with 6 types of pieces for each player + empty square
        #  Actions: (every board position) x (every board position), 4 castles and resign
        #
        # Note: not every action is legal
        #
        self.observation_space = spaces.Box(-6, 6, (8, 8))
        self.action_space = spaces.Discrete(64 * 64 + 4 + 1)

        self.player = player_color  # define player # TODO: implement
        self.player_2 = self.get_other_player(player_color)
        self.opponent = opponent  # define opponent

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
        self.saved_states = defaultdict(lambda: 0)
        self.repetitions = 0  # 3 repetitions ==> DRAW
        self.move_count = 0
        self.white_king_castle_possible = True
        self.white_queen_castle_possible = True
        self.black_king_castle_possible = True
        self.black_queen_castle_possible = True
        self.white_king_on_the_board = len(np.where(self.state == KING_ID)[0]) != 0
        self.black_king_on_the_board = len(np.where(self.state == -KING_ID)[0]) != 0
        self.possible_moves = self.get_possible_moves(state=self.state, player=WHITE)
        # If player chooses black, make white openent move first
        if self.player == BLACK:
            white_first_move = self.opponent_policy(self)
            white_first_action = self.move_to_action(white_first_move)
            # make move
            # self.state, _, _, _ = self.step(white_first_action)
            self.state, _, _ = self.player_move(white_first_action)
            self.move_count += 1
            self.current_player = BLACK
            self.possible_moves = self.get_possible_moves(state=self.state, player=BLACK)
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

        # action invalid in current state
        if action not in self.possible_actions:
            reward = INVALID_ACTION_REWARD
            return self.state, reward, self.done, self.info

        # Game is done
        if self.done:
            return (
                self.state,
                0.0,
                True,
                self.info,
            )
        if self.move_count > self.moves_max:
            return (
                self.state,
                0.0,
                True,
                self.info,
            )

        # valid action reward
        reward = INVALID_ACTION_REWARD
        # make move
        self.state, move_reward, self.done = self.player_move(action)
        reward += move_reward

        # opponent play
        opponent_player = self.switch_player()
        self.possible_moves = self.get_possible_moves(player=opponent_player)
        # check if there are no possible_moves for opponent
        if not self.possible_moves and self.king_is_checked(
            state=self.state, player=opponent_player
        ):
            self.done = True
            reward += WIN_REWARD
        if self.done:
            return self.state, reward, self.done, self.info

        # Bot Opponent play
        if self.opponent_policy:
            opponent_move = self.opponent_policy(self)
            opponent_action = self.move_to_action(opponent_move)
            # make move
            self.state, opp_reward, self.done = self.player_move(opponent_action)
            agent_player = self.switch_player()
            self.possible_moves = self.get_possible_moves(player=agent_player)
            reward -= opp_reward
            # check if there are no possible_moves for opponent
            if not self.possible_moves and self.king_is_checked(
                state=self.state, player=agent_player
            ):
                self.done = True
                reward += LOSS_REWARD

        # increment count on WHITE
        if self.current_player == WHITE:
            self.move_count += 1

        return self.state, reward, self.done, self.info

    def switch_player(self):
        other_player = self.get_other_player(self.current_player)
        self.current_player = other_player
        return other_player

    @property
    def possible_moves(self):
        return self._possible_moves

    @possible_moves.setter
    def possible_moves(self, moves):
        self._possible_moves = moves

    @property
    def possible_actions(self):
        return [self.move_to_action(m) for m in self.possible_moves]

    @property
    def info(self):
        return dict(
            state=self.state,
            move_count=self.move_count,
        )

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

    def player_can_castle(self, player):
        if player == WHITE:
            return self.white_king_castle_possible and self.white_queen_castle_possible
        else:
            return self.black_king_castle_possible and self.black_queen_castle_possible

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
            return self.state, LOSS_REWARD, True
        # Play
        move = self.action_to_move(action)
        new_state, reward = self.next_state(self.state, self.current_player, move, commit=True)
        # 3-fold repetition => DRAW
        encoded_state = self.encode_state()
        self.saved_states[encoded_state] += 1
        if self.saved_states[encoded_state] >= 3:
            return new_state, reward, True
        # Render
        if self.log:
            print(" " * 10, ">" * 10, self.current_player)
            self.render_moves([move], mode="human")
        return new_state, reward, False

    def next_state(self, state, player, move, commit=False):
        """
        Return the next state given a move
        -------
        (next_state, reward)
        """
        new_state = copy(state)
        reward = 0

        # TODO: implement castle move
        #
        if type(move) is str and move in CASTLE_MOVES:
            new_state = self.run_castle_move(new_state, move)
        elif type(move) is list or tuple:
            # Classic move
            _from, _to = move
            piece_to_move = copy(new_state[_from[0], _from[1]])
            captured_piece = copy(new_state[_to[0], _to[1]])
            assert piece_to_move, f"Bad move: {move} - piece is empty"
            new_state[_from[0], _from[1]] = 0
            new_state[_to[0], _to[1]] = piece_to_move

            # Pawn becomes Queen
            # TODO: allow player to choose the piece into which the pawn converts
            if ID_TO_TYPE[piece_to_move] == PAWN:
                if (player == WHITE and _to[0] == 7) or (player == BLACK and _to[0] == 0):
                    new_state[_to[0], _to[1]] = QUEEN_ID * self.player_to_int(player)
                    reward += CONVERT_PAWN_TO_QUEEN_REWARD

            # Keep track if castling is still possible
            if commit and self.player_can_castle(player):
                if piece_to_move == KING_ID:
                    if player == WHITE:
                        self.white_king_castle_possible = False
                        self.white_queen_castle_possible = False
                    else:
                        self.black_king_castle_possible = False
                        self.black_queen_castle_possible = False
                elif piece_to_move == ROOK_ID:
                    if _from[1] == 0:
                        if player == WHITE:
                            self.white_queen_castle_possible = False
                        else:
                            self.black_queen_castle_possible = False
                    elif _from[1] == 7:
                        if player == WHITE:
                            self.white_king_castle_possible = False
                        else:
                            self.black_king_castle_possible = False

            # Reward
            reward += ID_TO_VALUE[captured_piece]

        return new_state, reward

    def run_castle_move(self, state, move):
        if move == CASTLE_KING_SIDE_WHITE:
            state[7, 4] = EMPTY_SQUARE_ID
            state[7, 5] = ROOK_ID
            state[7, 6] = KING_ID
            state[7, 7] = EMPTY_SQUARE_ID
        elif move == CASTLE_QUEEN_SIDE_WHITE:
            state[7, 0] = EMPTY_SQUARE_ID
            state[7, 1] = EMPTY_SQUARE_ID
            state[7, 2] = KING_ID
            state[7, 3] = ROOK_ID
            state[7, 4] = EMPTY_SQUARE_ID
        elif move == CASTLE_KING_SIDE_BLACK:
            state[0, 4] = EMPTY_SQUARE_ID
            state[0, 5] = -ROOK_ID
            state[0, 6] = -KING_ID
            state[0, 7] = EMPTY_SQUARE_ID
        elif move == CASTLE_QUEEN_SIDE_BLACK:
            state[0, 0] = EMPTY_SQUARE_ID
            state[0, 1] = EMPTY_SQUARE_ID
            state[0, 2] = -KING_ID
            state[0, 3] = -ROOK_ID
            state[0, 4] = EMPTY_SQUARE_ID
        if self.current_player_is_white:
            self.white_king_castle_possible = False
            self.white_queen_castle_possible = False
        else:
            self.black_king_castle_possible = False
            self.black_queen_castle_possible = False
        return state

    def state_to_grid(self):
        grid = [[f" {ID_TO_ICON[square]} " for square in row] for row in self.state]
        return grid

    def render_grid(self, grid, mode="human"):
        outfile = sys.stdout if mode == "human" else StringIO()
        outfile.write("    ")
        outfile.write("-" * 25)
        outfile.write("\n")
        rows = "87654321"
        for i, row in enumerate(grid):
            outfile.write(f" {rows[i]} | ")
            for square in row:
                outfile.write(square)
            outfile.write("|\n")
        outfile.write("    ")
        outfile.write("-" * 25)
        outfile.write("\n      a  b  c  d  e  f  g  h ")
        outfile.write("\n")

        if mode == "string":
            return outfile.getvalue()
        if mode != "human":
            return outfile

    def render(self, mode="human"):
        """Render the playing board"""
        grid = self.state_to_grid()
        out = self.render_grid(grid, mode=mode)
        return out

    def render_moves(self, moves, mode="human"):
        grid = self.state_to_grid()
        for move in moves:
            if type(move) is str and move in CASTLE_MOVES:
                if move == CASTLE_QUEEN_SIDE_WHITE:
                    grid[7][0] = highlight(grid[7][0], background="white")
                    grid[7][1] = highlight(" >>", background="green")
                    grid[7][2] = highlight("> <", background="green")
                    grid[7][3] = highlight("<< ", background="green")
                    grid[7][4] = highlight(grid[7][4], background="white")
                elif move == CASTLE_KING_SIDE_WHITE:
                    grid[7][4] = highlight(grid[7][4], background="white")
                    grid[7][5] = highlight(" >>", background="green")
                    grid[7][6] = highlight("<< ", background="green")
                    grid[7][7] = highlight(grid[7][7], background="white")
                elif move == CASTLE_QUEEN_SIDE_BLACK:
                    grid[0][0] = highlight(grid[0][0], background="white")
                    grid[0][1] = highlight(" >>", background="green")
                    grid[0][2] = highlight("> <", background="green")
                    grid[0][3] = highlight("<< ", background="green")
                    grid[0][4] = highlight(grid[0][4], background="white")
                elif move == CASTLE_KING_SIDE_BLACK:
                    grid[0][4] = highlight(grid[0][4], background="white")
                    grid[0][5] = highlight(" >>", background="green")
                    grid[0][6] = highlight("<< ", background="green")
                    grid[0][7] = highlight(grid[0][7], background="white")
                continue

            x0, y0 = move[0][0], move[0][1]
            x1, y1 = move[1][0], move[1][1]
            if len(grid[x0][y0]) < 4:
                grid[x0][y0] = highlight(grid[x0][y0], background="white")
            if len(grid[x1][y1]) < 4:
                if self.state[x1, y1]:
                    grid[x1][y1] = highlight(grid[x1][y1], background="red")
                else:
                    grid[x1][y1] = highlight(grid[x1][y1], background="green")
        return self.render_grid(grid, mode=mode)

    def move_to_action(self, move):
        if type(move) is list:
            _from = move[0][0] * 8 + move[0][1]
            _to = move[1][0] * 8 + move[1][1]
            return _from * 64 + _to
        if move == CASTLE_KING_SIDE_WHITE:
            return 64 * 64
        elif move == CASTLE_QUEEN_SIDE_WHITE:
            return 64 * 64 + 1
        elif move == CASTLE_KING_SIDE_BLACK:
            return 64 * 64 + 2
        elif move == CASTLE_QUEEN_SIDE_BLACK:
            return 64 * 64 + 3
        elif move == RESIGN:
            return 64 * 64 + 4

    def action_to_move(self, action):
        if action >= 64 * 64:
            _action = action - 64 * 64
            if _action == 0:
                return CASTLE_KING_SIDE_WHITE
            elif _action == 1:
                return CASTLE_QUEEN_SIDE_WHITE
            elif _action == 2:
                return CASTLE_KING_SIDE_BLACK
            elif _action == 3:
                return CASTLE_QUEEN_SIDE_BLACK
            elif _action == 4:
                return RESIGN
        _from, _to = action // 64, action % 64
        x0, y0 = _from // 8, _from % 8
        x1, y1 = _to // 8, _to % 8
        return [np.array([x0, y0], dtype=np.int8), np.array([x1, y1], dtype=np.int8)]

    def move_to_string(self, move):
        if move in [CASTLE_KING_SIDE_WHITE, CASTLE_KING_SIDE_BLACK]:
            return "O-O"
        elif move in [CASTLE_QUEEN_SIDE_WHITE, CASTLE_QUEEN_SIDE_BLACK]:
            return "O-O-O"
        _from, _to = move
        rows = list(reversed("12345678"))
        cols = "abcdefgh"
        piece_id = self.state[_from[0], _from[1]]
        piece_desc = ID_TO_DESC[piece_id]
        capture = self.state[_to[0], _to[1]] != 0
        _from_str = cols[_from[1]] + rows[_from[0]]
        _to_str = cols[_to[1]] + rows[_to[0]]
        string = f"{piece_desc}{_from_str}{'x' if capture else ''}{_to_str}"
        return string

    def get_possible_actions(self):
        moves = self.get_possible_moves(player=self.current_player)
        return [self.move_to_action(move) for move in moves]

    def get_possible_moves(self, state=None, player=None, attack=False, skip_pawns=False):
        if state is None:
            state = self.state
        if player is None:
            player = self.current_player

        squares_under_attack = []
        if not attack:
            opponent_player = self.get_other_player(player)
            squares_under_attack = self.get_squares_attacked_by_player(state, opponent_player)

        squares_under_attack_hashmap = defaultdict(lambda: None)
        for sq in squares_under_attack:
            squares_under_attack_hashmap[tuple(sq)] = True

        moves = []
        for coords, piece_id in np.ndenumerate(state):
            coords = np.array(coords, dtype=np.int8)
            if piece_id == 0:
                continue
            color = ID_TO_COLOR[piece_id]
            if color != player:
                continue
            piece_type = ID_TO_TYPE[piece_id]
            if piece_type == KING:
                moves += self.king_moves(
                    player,
                    coords,
                    state=state,
                    attack=attack,
                    squares_under_attack_hashmap=squares_under_attack_hashmap,
                )
            elif piece_type == QUEEN:
                moves += self.queen_moves(player, coords, state=state, attack=attack)
            elif piece_type == ROOK:
                moves += self.rook_moves(player, coords, state=state, attack=attack)
            elif piece_type == BISHOP:
                moves += self.bishop_moves(player, coords, state=state, attack=attack)
            elif piece_type == KNIGHT:
                moves += self.knight_moves(player, coords, state=state, attack=attack)
            elif piece_type == PAWN and not skip_pawns:
                moves += self.pawn_moves(player, coords, state=state, attack=attack)

        if attack:
            return moves

        if self.player_can_castle(player):
            moves += self.castle_moves(
                player, state=state, squares_under_attack_hashmap=squares_under_attack_hashmap
            )

        # King not present on the board (for testing pruposes)
        if (player == WHITE and not self.white_king_on_the_board) or (
            player == BLACK and not self.black_king_on_the_board
        ):
            return moves

        # Filter out moves that leave the king checked
        def move_leaves_king_checked(move):
            # skip castling moves
            if type(move) is not list:
                return False
            # skip king moves
            if (player == WHITE and state[move[0][0], move[0][1]] == KING_ID) or (
                player == BLACK and state[move[0][0], move[0][1]] == -KING_ID
            ):
                return False
            next_state, _ = self.next_state(state, player, move, commit=False)
            return self.king_is_checked(state=next_state, player=player)

        moves = [move for move in moves if not move_leaves_king_checked(move)]
        return moves

    def king_moves(
        self,
        player,
        coords,
        state=None,
        attack=False,
        squares_under_attack_hashmap=defaultdict(lambda: None),
    ):
        """KING MOVES"""
        if state is None:
            state = self.state
        moves = []
        steps = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]

        if attack:
            for step in steps:
                square = coords + np.array(step, dtype=np.int8)
                if self.king_attack(player, state, square):
                    moves.append([coords, square])
        else:
            for step in steps:
                square = coords + np.array(step, dtype=np.int8)
                if self.king_move(player, state, square, squares_under_attack_hashmap):
                    moves.append([coords, square])
        return moves

    def queen_moves(self, player, coords, state=None, attack=False):
        """QUEEN MOVES"""
        if state is None:
            state = self.state
        moves = []
        moves += self.rook_moves(player, coords, state=state, attack=attack)
        moves += self.bishop_moves(player, coords, state=state, attack=attack)
        return moves

    def rook_moves(self, player, coords, state=None, attack=False):
        """ROOK MOVES"""
        if state is None:
            state = self.state
        moves = []
        for step in [[-1, 0], [+1, 0], [0, -1], [0, +1]]:
            moves += self.iterativesteps(player, state, coords, step, attack=attack)
        return moves

    def bishop_moves(self, player, coords, state=None, attack=False):
        """BISHOP MOVES"""
        if state is None:
            state = self.state
        moves = []
        for step in [[-1, -1], [-1, +1], [+1, -1], [+1, +1]]:
            moves += self.iterativesteps(player, state, coords, step, attack=attack)
        return moves

    def iterativesteps(self, player, state, coords, step, attack=False):
        """Used to calculate Bishop, Rook and Queen moves"""
        moves = []
        k = 1
        step = np.array(step, dtype=np.int8)
        while True:
            square = coords + k * step
            if attack:
                add_bool, stop_bool = self.attacking_move(player, state, square)
                if add_bool:
                    moves.append([coords, square])
                if stop_bool:
                    break
                else:
                    k += 1
            else:
                add_bool, stop_bool = self.playable_move(player, state, square)
                if add_bool:
                    moves.append([coords, square])
                if stop_bool:
                    break
                else:
                    k += 1
        return moves

    def knight_moves(self, player, coords, state=None, attack=False):
        """KNIGHT MOVES"""
        if state is None:
            state = self.state
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
                is_playable, _ = self.attacking_move(player, state, square)
                if is_playable:
                    moves.append([coords, square])
            else:
                is_playable, _ = self.playable_move(player, state, square)
                if is_playable:
                    moves.append([coords, square])
        return moves

    def pawn_moves(self, player, coords, state=None, attack=False):
        """PAWN MOVES"""
        if state is None:
            state = self.state
        moves = []
        player_int = ChessEnvV1.player_to_int(player)
        attack_squares = [
            coords + np.array([1, -1], dtype=np.int8) * (-player_int),
            coords + np.array([1, +1], dtype=np.int8) * (-player_int),
        ]
        one_step_square = coords + np.array([1, 0], dtype=np.int8) * (-player_int)
        two_step_square = coords + np.array([2, 0], dtype=np.int8) * (-player_int)

        if attack:
            for square in attack_squares:
                if ChessEnvV1.square_is_on_board(square) and not self.is_king_from_player(
                    player, state, square
                ):
                    moves.append([coords, square])
        else:
            # moves only to empty squares
            x, y = one_step_square
            if ChessEnvV1.square_is_on_board(one_step_square) and self.state[x, y] == 0:
                moves.append([coords, one_step_square])

            x, y = two_step_square
            if ChessEnvV1.square_is_on_board(two_step_square) and (
                (player == WHITE and coords[0] == 6) or (player == BLACK and coords[0] == 1)
            ):
                if self.state[x, y] == 0:
                    moves.append([coords, two_step_square])

            # attacks only opponent's pieces
            for square in attack_squares:
                if ChessEnvV1.square_is_on_board(square) and self.is_piece_from_other_player(
                    player, state, square
                ):
                    moves.append([coords, square])

            # TODO: implement en-passant pawn capture
            #
        return moves

    def castle_moves(
        self, player, state=None, squares_under_attack_hashmap=defaultdict(lambda: None)
    ):
        if state is None:
            state = self.state
        moves = []
        if player == WHITE:
            # CASTLE_QUEEN_SIDE_WHITE:
            rook = (7, 0)
            empty_3 = (7, 1)
            empty_2 = (7, 2)
            empty_1 = (7, 3)
            king = (7, 4)
            if (
                state[rook] == ROOK_ID
                and state[empty_3] == EMPTY_SQUARE_ID
                and state[empty_2] == EMPTY_SQUARE_ID
                and state[empty_1] == EMPTY_SQUARE_ID
                and state[king] == KING_ID
                and not squares_under_attack_hashmap[king]
                and not squares_under_attack_hashmap[empty_1]
                and not squares_under_attack_hashmap[empty_2]
            ):
                moves.append(CASTLE_QUEEN_SIDE_WHITE)
            # CASTLE_KING_SIDE_WHITE
            king = (7, 4)
            empty_1 = (7, 5)
            empty_2 = (7, 6)
            rook = (7, 7)
            if (
                state[king] == KING_ID
                and state[empty_1] == EMPTY_SQUARE_ID
                and state[empty_2] == EMPTY_SQUARE_ID
                and state[rook] == ROOK_ID
                and not squares_under_attack_hashmap[king]
                and not squares_under_attack_hashmap[empty_1]
                and not squares_under_attack_hashmap[empty_2]
            ):
                moves.append(CASTLE_KING_SIDE_WHITE)
        else:
            # CASTLE_QUEEN_SIDE_BLACK:
            rook = (0, 0)
            empty_3 = (0, 1)
            empty_2 = (0, 2)
            empty_1 = (0, 3)
            king = (0, 4)
            if (
                state[rook] == ROOK_ID
                and state[empty_3] == EMPTY_SQUARE_ID
                and state[empty_2] == EMPTY_SQUARE_ID
                and state[empty_1] == EMPTY_SQUARE_ID
                and state[king] == KING_ID
                and not squares_under_attack_hashmap[king]
                and not squares_under_attack_hashmap[empty_1]
                and not squares_under_attack_hashmap[empty_2]
            ):
                moves.append(CASTLE_QUEEN_SIDE_BLACK)
            # CASTLE_KING_SIDE_BLACK:
            king = (0, 4)
            empty_1 = (0, 5)
            empty_2 = (0, 6)
            rook = (0, 7)
            if (
                state[king] == KING_ID
                and state[empty_1] == EMPTY_SQUARE_ID
                and state[empty_2] == EMPTY_SQUARE_ID
                and state[rook] == ROOK_ID
                and not squares_under_attack_hashmap[king]
                and not squares_under_attack_hashmap[empty_1]
                and not squares_under_attack_hashmap[empty_2]
            ):
                moves.append(CASTLE_KING_SIDE_BLACK)
        return moves

    def king_move(self, player, state, square, squares_under_attack_hashmap):
        """
        return squares to which the king can move,
        i.e. unattacked squares that can be:
        - empty squares
        - opponent pieces (excluding king)
        If opponent king is encountered, then there's a problem...
        => return <bool> is_playable
        """
        if not ChessEnvV1.square_is_on_board(square):
            return False
        elif squares_under_attack_hashmap[tuple(square)]:
            return False
        elif self.is_piece_from_player(player, state, square):
            return False
        elif self.is_king_from_other_player(player, state, square):
            raise Exception(f"KINGS NEXT TO EACH OTHER ERROR {square}")
        elif self.is_piece_from_other_player(player, state, square):
            return True
        elif state[square[0], square[1]] == 0:  # empty square
            return True
        else:
            raise Exception(f"KING MOVEMENT ERROR {square}")

    def king_attack(self, player, state, square):
        """
        return all the squares that the king can attack, except:
        - squares outside the board
        If opponent king is encountered, then there's a problem...
        => return <bool> is_playable
        """
        if not ChessEnvV1.square_is_on_board(square):
            return False
        elif self.is_piece_from_player(player, state, square):
            return True
        elif self.is_king_from_other_player(player, state, square):
            raise Exception(f"KINGS NEXT TO EACH OTHER ERROR {square}")
        elif self.is_piece_from_other_player(player, state, square):
            return True
        elif state[square[0], square[1]] == 0:  # empty square
            return True
        else:
            raise Exception(f"KING MOVEMENT ERROR {square}")

    def playable_move(self, player, state, square):
        """
        return squares to which a piece can move
        - empty squares
        - opponent pieces (excluding king)
        => return [<bool> playable, <bool> stop_iteration]
        """
        if not ChessEnvV1.square_is_on_board(square):
            return False, True
        elif self.is_piece_from_player(player, state, square):
            return False, True
        elif self.is_king_from_other_player(player, state, square):
            return False, True
        elif self.is_piece_from_other_player(player, state, square):
            return True, True
        elif state[square[0], square[1]] == 0:  # empty square
            return True, False
        else:
            print(f"PLAYABLE MOVE ERROR {square}")
            raise Exception(f"PLAYABLE MOVE ERROR {square}")

    def attacking_move(self, player, state, square):
        """
        return squares that are attacked or defended
        - empty squares
        - opponent pieces (opponent king is ignored)
        - own pieces
        => return [<bool> playable, <bool> stop_iteration]
        """
        if not ChessEnvV1.square_is_on_board(square):
            return False, True
        elif self.is_piece_from_player(player, state, square):
            return True, True
        elif self.is_king_from_other_player(player, state, square):
            return True, True
        elif self.is_piece_from_other_player(player, state, square):
            return True, True
        elif state[square[0], square[1]] == 0:  # empty square
            return True, False
        else:
            print(f"ATTACKING MOVE ERROR {square}")
            raise Exception(f"ATTACKING MOVE ERROR {square}")

    def get_squares_attacked_by_player(self, state, player):
        moves = self.get_possible_moves(state=state, player=player, attack=True)
        attacked_squares = [move[1] for move in moves]
        return attacked_squares

    # def is_current_player_piece(self, square):
    #     self.is_piece_from_player(square, self.current_player)

    # def is_opponent_piece(self, square):
    #     self.is_piece_from_player(square, self.opponent_player)

    def is_piece_from_player(self, player, state, square):
        piece_id = state[square[0], square[1]]
        color = ID_TO_COLOR[piece_id]
        return color == player

    def is_piece_from_other_player(self, player, state, square):
        return self.is_piece_from_player(self.get_other_player(player), state, square)

    # def is_king_from_current_player(self, square):
    #     self.is_king_from_player(square, self.current_player)

    # def is_king_from_opponent_player(self, square):
    #     self.is_king_from_player(square, self.opponent_player)

    def is_king_from_player(self, player, state, square):
        piece_id = state[square[0], square[1]]
        if ID_TO_TYPE[piece_id] != KING:
            return False
        color = ID_TO_COLOR[piece_id]
        return color == player

    def is_king_from_other_player(self, player, state, square):
        return self.is_king_from_player(self.get_other_player(player), state, square)

    # TODO: implement resignation action parsing
    def is_resignation(self, action):
        return False

    @staticmethod
    def player_to_int(player):
        if player == WHITE:
            return 1
        return -1

    @staticmethod
    def square_is_on_board(square):
        return not (square[0] < 0 or square[0] > 7 or square[1] < 0 or square[1] > 7)

    def king_is_checked(self, state=None, player=None):
        if state is None:
            state = self.state
        if player is None:
            player = self.current_player
        # King not present on the board (for testing purposes)
        if (player == WHITE and not self.white_king_on_the_board) or (
            player == BLACK and not self.black_king_on_the_board
        ):
            return False
        player_int = ChessEnvV1.player_to_int(player)
        king_id = player_int * KING_ID
        king_pos = np.where(state == king_id)
        king_square = [king_pos[0][0], king_pos[1][0]]
        other_player = self.get_other_player(player)
        attacked_squares = self.get_squares_attacked_by_player(state, other_player)
        if not attacked_squares:
            return False
        return any(np.equal(attacked_squares, king_square).all(1))

    def encode_state(self):
        mapping = "0ABCDEFfedcba"
        encoding = "".join([mapping[val] for val in self.state.ravel()])
        return encoding
