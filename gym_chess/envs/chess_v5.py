import os
import sys
import time
import random
# import time

import numpy as np
from six import StringIO
from pprint import pprint
from itertools import chain
from collections import namedtuple
from copy import copy, deepcopy
from collections import defaultdict
from pprint import pprint
import argparse
import gym

# import gym
# from gym import spaces, error, utils
# from gym.utils import seeding

from gym_chess.envs.chess_pieces_v5 import *
from gym_chess.envs.utils import verboseprint, gucci_print

sign = lambda x: (1, -1)[x < 0]

parser = argparse.ArgumentParser(description='demo')
parser.add_argument('--verbose',
    type=int, default=0, metavar='v',
    help='verbosity level (default: 0, also 1 or 2)'
)
args = parser.parse_args()
os.environ['verbose'] = str(args.verbose)


class Square:
    LETTERS = list('abcdefgh')
    NUMBERS = list('12345678')

    @classmethod
    def coords_to_name(cls, coords):
        return cls.LETTERS[coords[1]] + cls.NUMBERS[coords[0]]

    @classmethod
    def name_to_coords(cls, name):
        return [
            cls.NUMBERS.index(name[1]),
            cls.LETTERS.index(name[0])
        ]


class PlayerMove(namedtuple('PlayerMove',
                ['player', 'from_', 'to_', 'piece', 'move_type'])):
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        from_  = Square.coords_to_name(self.from_)
        to_  = Square.coords_to_name(self.to_)
        return f'<{self.piece} {from_}->{to_} {self.move_type}>'
    def __eq__(self, other):
        return all([
            self.player == other.player,
            all(self.from_ == other.from_),
            all(self.to_ == other.to_),
            self.piece == other.piece,
            self.move_type == other.move_type,
        ])

class Surender:
    def __init__(self, player_color):
        self.player = player_color
class DrawOffer:
    def __init__(self, player_color):
        self.player = player_color
class DrawAccept:
    def __init__(self, player_color):
        self.player = player_color

# TEST
# p = PlayerMove(BLACK, (1,1), (0,0), 9, 'asd')
# print(p)
# sys.exit()

class ChessBoard:
    LETTERS = 'abcdefgh'
    NUMBERS = '12345678'

    def __init__(self, state=None):
        self.board = np.array([[Empty() for x in self.LETTERS] for y in self.NUMBERS])
        self.max = 64
        self.simulated_board = np.zeros((8,8), dtype=np.dtype(object))
        if state:
            for piece in state:
                self.__setitem__(tuple(piece.square), piece.__class__(piece.color))

    def __getitem__(self, coords):
        # assert len(coords) == 2, 'value must be 2-dimensional'
        simulated = self.simulated_board[coords[0], coords[1]]
        if simulated:
            # print('args: ', args, ' =>> simulated:', simulated)
            return simulated
        else:
            return  self.board[coords[0], coords[1]]

    # @profile
    def __setitem__(self, args, value):
        # assert isinstance(args, tuple) and len(args) == 2, 'must pass 2 dimensional tuple'
        self.board[args] = value
        rows, cols = args[0], args[1]
        if isinstance(rows, slice):
            rows = list(range(rows.start or 0, rows.stop or 8, rows.step or 1))
        else:
            rows = [rows]
        if isinstance(cols, slice):
            cols = list(range(cols.start or 0, cols.stop or 8, cols.step or 1))
        else:
            cols = [cols]
        # set figures' square attribute
        for row in rows:
            for col in cols:
                self.board[row,col].square = np.array([row, col])
                # x = self.board[row,col]

    def __eq__(self, other):
        if len(self.pieces) != len(other.pieces):
            return False
        for sq1, sq2 in zip(iter(self), iter(other)):
            if sq1.__class__ != sq2.__class__ or sq1.color !=  sq2.color:
                return False
        return True

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n < self.max:
            row = self.n // 8
            col = self.n % 8
            self.n += 1
            return self.__getitem__((row, col))
        else:
            raise StopIteration

    def __repr__(self):
        return self.__str__()
    def __str__(self):
        s = ''
        for i, row in enumerate(self.board[::-1]):
            s += self.NUMBERS[::-1][i]
            s += ' |'
            s += '|'.join([f'{str(x):^3s}' for x in row])
            s += '| '
            s += '\n'
        s += '    ' + '   '.join(self.LETTERS)
        s += '\n'
        return s

    @property
    def pieces(self):
        return [_ for _ in self.__iter__() if isinstance(_, ChessPiece)]

    def get_pieces(self, color):
        pieces = []
        for i in range(8):
            for j in range(8):
                p = self.__getitem__((i, j))
                if isinstance(p, ChessPiece) and p.color == color:
                    pieces.append(p)
        return pieces

    @property
    def state(self):
        return self.pieces

    # @profile
    def make_move(self, move):
        """
            Args:
                move: <PlayerMove>

            TODO:
            - pawn to Queen conversion
            - castling implementation
            - en-passant
        """
        from_ = move.from_
        to_   = move.to_
        move.piece.increment_move_counter()
        self[tuple(from_)] = Empty()
        self[tuple(to_)]   = move.piece  ## <=== COPY

    def reset_simulation(self):
        self.simulated_board = np.zeros((8,8), dtype=np.dtype(object))

    # @profile
    def simulate_move(self, move):
        self.reset_simulation()
        from_ = move.from_
        to_   = move.to_
        piece_copy = move.piece.copy()
        piece_copy.square = to_
        self.simulated_board[tuple(from_)] = Empty()
        self.simulated_board[tuple(to_)] = piece_copy
        # TODO:
        # en-passant
        # pawn-queen conversion
        # castling

    def get_possible_moves(self, player_color):
        possible_moves = self._get_possible_moves(player_color, attack_mode=False)
        self.possible_moves = possible_moves
        return possible_moves

    # @profile
    def _get_possible_moves(self, player_color, attack_mode=False):
        pieces = self.get_pieces(player_color)
        possible_moves = []

        for piece in pieces:
            moves_iter = piece.generate_moves(self, attack_mode)
            for move, move_type in moves_iter:
                move_obj = PlayerMove(player_color, piece.square,
                                    piece.square + move, piece, move_type)
                if not attack_mode:
                    try:
                        self.simulate_move(move_obj)
                        _ = self._get_possible_moves(~player_color, attack_mode=True)
                        possible_moves += [move_obj]
                    except KingCheck:
                        pass
                    finally:
                        self.reset_simulation()
        # if not attack_mode:
        #     gucci_print('CASTLING', gang=3)
        #     possible_moves += self.get_castling_moves(player_color)
        return possible_moves

    def show_moves(self, moves):
        moves = [move for move in moves if isinstance(move, PlayerMove)]
        d = defaultdict(list)
        for move in moves:
            d[move.piece].append(move)
        for piece, moves in d.items():
            # demo_board = deepcopy(self)
            demo_board = ChessBoard(self.state)
            for move in moves:
                from_ = tuple(move.from_)
                to_ = tuple(move.to_)
                demo_board[from_] = demo_board[from_].mark()
                demo_board[to_]   = demo_board[to_].mark_attacked()
            print(demo_board)

    def get_castling_moves(self, player_color):
        # Castling:
        # ---------
        # rook is present
        # rook hasn't moved and is on it's original square
        # king hasn't moved and is on it's original square
        # space in between is unoccupied
        # king's isn't under check
        # 2 squares left/right from king aren't under check
        possible_moves = []
        pieces = self.get_pieces(player_color)
        try:
            rooks = [_ for _ in pieces if isinstance(_, Rook)]
            king = [_ for _ in pieces if isinstance(_, King)][0]
        except:
            return []
        print(rooks, king)
        for rook in rooks:
            print(rook, rook.square)
            if not (rook.total_moves == king.total_moves == 0):
                continue
            # check if king/rook are on original squares ? (for starting
            # states which are different from default starting state)
            distance = rook.square[1] - king.square[1]
            print('distance:', distance)
            _sign = sign(distance)
            step = np.array([0, _sign])
            one_step = king.square + step
            two_step = king.square + step*2
            if (not isinstance(self[one_step], Empty) and
                not isinstance(self[two_step], Empty)):
               continue
            if king.color == WHITE:
                a = king.square[0] == 0
                b = rook.square[0] in [0,7]
                c = rook.square[1] in [0,7]
                print(a, b, c)
                continue
            if king.color == WHITE and not (
                    king.square[0] == 0 and
                    rook.square[0] in [0,7] and
                    rook.square[1] in [0,7]):
                continue
            elif king.color == BLACK and not (
                    king.square[0] == 7 and
                    rook.square[0] in [0,7] and
                    rook.square[1] in [0,7]):
                continue
            try:
                # is King checked ?
                print(self)
                _ = self._get_possible_moves(~player_color, attack_mode=True)
                # one step
                move_obj = PlayerMove(player_color, king.square, one_step, king, 'castling')
                # next_board = deepcopy(self)
                next_board = ChessBoard(self.state)
                next_board.make_move(move_obj)
                print(next_board)
                _ = next_board._get_possible_moves(~player_color, attack_mode=True)
                # two step
                move_obj = PlayerMove(player_color, king.square, two_step, king, 'castling')
                # next_board = deepcopy(self)
                next_board = ChessBoard(self.state)
                next_board.make_move(move_obj)
                print(next_board)
                _ = next_board._get_possible_moves(~player_color, attack_mode=True)

                # no KingCheck excpetion raised
                castle_type = {3: 'king', 4: 'queen'}[abs(distance)]
                castle_move = CASTLES[castle_type](player_color)
                possible_moves += [castle_move]
            except KingCheck:
                pass
        return possible_moves


class ChessGame:
    def __init__(self):
        self.total_turns= 0
        self.player_turn = WHITE
        self.draw_offered = {'WHITE': False, 'BLACK': False}
        self.board = ChessBoard()
        self.board[0,:] = [Rook(WHITE), Knight(WHITE), Bishop(WHITE), Queen(WHITE),
                            King(WHITE),  Bishop(WHITE), Knight(WHITE), Rook(WHITE)]
        self.board[1,:] = [Pawn(WHITE) for _ in range(8)]
        self.board[6,:] = [Pawn(BLACK) for _ in range(8)]
        self.board[7,:] = [Rook(BLACK), Knight(BLACK), Bishop(BLACK), Queen(BLACK),
                            King(BLACK), Bishop(BLACK), Knight(BLACK), Rook(BLACK)]

    def get_possible_moves(self):
        player_color = self.player_turn
        possible_moves = self.board.get_possible_moves(player_color)
        if not possible_moves:
            try:
                _ = self.board._get_possible_moves(~player_color, attack_mode=True)
            except KingCheck:
                print(f'Player {~player_color} wins ! Fatality !')
                raise PlayerWins(~player_color)
            else:
                print(f'Stalemate ! {player_color} fucked up !')
                raise DrawByStalemate()

        if self.draw_offered[self.player_turn.hash()]:
            self.draw_offered[self.player_turn.hash()] = False
            possible_moves += [DrawAccept(player_color)]
        # possible_moves += [Surender(player_color)]
        return possible_moves

    def make_move(self, move, offer_draw=False):
        assert move.player == self.player_turn, 'WRONG PLAYER MOVE !!'
        assert move in self.board.possible_moves, 'ILLEGAL MOVE !!'
        if offer_draw:
            self.draw_offered[move.player.hash()] = True
        if isinstance(move, DrawAccept):
            raise DrawByAgreement()
        if isinstance(move, Surender):
            print('Player surrendered LOL')
            raise PlayerWins(~self.player_turn)
        self.board.make_move(move)
        self.player_turn = ~self.player_turn
        if move.player == WHITE:
            self.total_turns += 1

    def __repr__(self):
        return self.__str__()
    def __str__(self):
        s = f'TOTAL TURNS: {self.total_turns}\n'
        s += f'PLAYER TURN: {self.player_turn}\n'
        s += f'DRAW OFFERED: {self.draw_offered[(~self.player_turn).hash()]}\n'
        s += self.board.__str__()
        return s


class ChessEnv(gym.Env):
    def __init__(self, player_color='white', opponent=None, log=None):
        self.color = player_color
        self.total_steps = 0
        self.max_steps = 150
        self.total_reward = 0
        self.done = False
        self.game = ChessGame()
        self.precomputed_moves = None

    def seed(self, seed=None):
        pass

    def step(self, action, offer_draw=False):
        """Run one timestep of the environment's dynamics. When end of episode
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
        self.done = False

        try:
            self.game.make_move(action)
            black_moves = self.game.get_possible_moves()
        except PlayerWins as e:
            self.total_reward += -1
            self.done = True
        except (DrawByStalemate, DrawByAgreement):
            self.total_reward += 0
            self.done = True

        # Computer
        if not self.done:
            try:
                self.game.make_move(random.choice(black_moves))
                self.precomputed_moves = self.game.get_possible_moves()
            except PlayerWins as e:
                self.total_reward += -1
                self.done = True
            except (DrawByStalemate, DrawByAgreement):
                self.total_reward += 0
                self.done = True

        self.total_steps += 1
        state = self.game.board.board
        info = {'state': state}
        return state, self.total_reward, self.done, info

    def reset(self):
        """Resets the state of the environment, returning an initial observation.
		Outputs
        -------
        observation : the initial observation of the space. (Initial reward is assumed to be 0.)
		"""
        self.game = ChessGame()
        return self.game.board.board

    def render(self, mode='human'):
        outfile = StringIO() if mode == 'ansi' else sys.stdout
        s = f'total_steps: {self.total_steps}\n'
        s += f'total_reward: {self.total_reward}\n'
        s += str(self.game)
        outfile.write(s)
        if mode != 'human':
            return outfile

    def get_possible_moves(self):
        return self.precomputed_moves

# import random
# g = ChessGame()
# b = g.board
# print(b)
# moves = b.get_possible_moves(WHITE)
# print(moves)
# b.show_moves(moves)
# b.make_move(random.choice(moves))
# print(b)
# moves = b.get_possible_moves(BLACK)
# print(moves)
# b.show_moves(moves)
# b.make_move(random.choice(moves))

# import traceback
# def log_traceback(ex):
#     tb_lines = traceback.format_exception(ex.__class__, ex, ex.__traceback__)
#     tb_text = ''.join(tb_lines)
#     # I'll let you implement the ExceptionLogger class,
#     # and the timestamping.
#     print(tb_text)
#
#
# import random
# import time
# separator = '<>'*30 + '\n'
#
# s = time.time()
# for j in range(5):
#     env = ChessEnv()
#     for i in range(50):
#         try:
#             moves = env.game.get_possible_moves()
#             state, reward, done, _ = env.step(random.choice(moves))
#         except Exception as e:
#             log_traceback(e)
#             break
#         if done:
#             print(f'Game {j} ended in turn {i}')
#             break
# e = time.time()
# print('time', e-s)
# sys.exit()
#
import random
import time
s = time.time()
for j in range(5):
    g = ChessGame()
    for i in range(50):
        # player 1
        try:
            moves = g.get_possible_moves()
            g.make_move(random.choice(moves))
            # print('')
            # print(b)
            # player 2
            moves = g.get_possible_moves()
            g.make_move(random.choice(moves))
            # print('')
            # print(b)
        except (DrawByAgreement, PlayerWins):
            print(f'Game {j} ended in turn {i}')
            break
    print(g)
e = time.time()
print('time', e-s)
sys.exit()

# import random
# import time
# s = time.time()
# for j in range(5):
#     g = ChessGame()
#     b = g.board
#     for i in range(50):
#         # input()
#         print(f'\nTURN {i}')
#         print('='*30)
#         print('\n')
#         try:
#             # player 1
#             moves = b.get_possible_moves(WHITE)
#             print(moves)
#             m = random.choice(moves)
#             print('MOVE CHOSEN:', m)
#             b.show_moves([m])
#             b.make_move(m)
#             print('')
#             print(b)
#             # player 2
#             moves = b.get_possible_moves(BLACK)
#             print(moves)
#             m = random.choice(moves)
#             print('MOVE CHOSEN:', m)
#             b.show_moves([m])
#             b.make_move(m)
#             print('')
#             print(b)
#         except (DrawByAgreement, PlayerWins):
#             pass
# e = time.time()
# print('time', e-s)
# sys.exit()
# print('\nTEST: Calculating ALL possible moves', end='\n'+'-'*35 + '\n')


# for row in chessboard.board:
#     for x in row:
#         print(x.square)
