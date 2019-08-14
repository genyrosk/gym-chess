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

    def __init__(self, *args):
        if len(args) == 1:
            self._name = args[0]
            self.name = self._name
        elif len(args) == 2:
            self._coords = (args[0], args[1])
            self.coords = self._coords
        else:
            raise Exception('1 or 2 args pls')

    @classmethod
    def coords_to_name(cls, coords):
        return cls.LETTERS[coords[1]] + cls.NUMBERS[coords[0]]

    @classmethod
    def name_to_coords(cls, name):
        return [
            cls.NUMBERS.index(name[1]),
            cls.LETTERS.index(name[0])
        ]

    @property
    def coords(self):
        try:
            return self._coords
        except AttributeError:
            self._coords = self.name_to_coords(self.name)
            return self._coords

    @coords.setter
    def coords(self, value):
        if len(value) != 2:
            raise ValueError('coordinates must be len() == 2 !')
        if value[0] not in list(range(8)) or value[1] not in list(range(8)):
            raise SquareOutsideBoard('coordinates must be 2 integers between 0 and 7')
        self._coords = value
        self._name = self.coords_to_name(self._coords)

    @property
    def name(self):
        try:
            return self._name
        except AttributeError:
            # self._name = self.LETTERS[self._coords[0]] + self.NUMBERS[self._coords[0]]
            self._name = self.coords_to_name(self._coords)
            return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError('name must be a string dammit !')
        self._name = value
        self._coords = self.name_to_coords(self._name)

    def __add__(self, move):
        assert isinstance(move, list)
        # verboseprint(f'\t\t---> evaluate {self} + <move {move}>', end='', l=2)
        row = self.coords[0] + move[0]
        col = self.coords[1] + move[1]
        new_coords = [row, col]
        new_ = Square(*new_coords)
        # verboseprint(' ==>>', new_, l=2)
        return new_

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'<{self.name}> {self.coords}'


class PlayerMove(namedtuple('PlayerMove',
                ['player', 'from_', 'to_', 'piece', 'move_type'])):
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return f'<{self.piece} {self.from_.name}->{self.to_.name} {self.move_type}>'

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
                self.__setitem__(piece.square.coords, piece.__class__(piece.color))

    def __getitem__(self, args):
        assert isinstance(args, tuple) and len(args) == 2, 'must pass 2 dimensional tuple'
        simulated = self.simulated_board[args]
        if simulated:
            # print('args: ', args, ' =>> simulated:', simulated)
            return simulated
        else:
            return  self.board[args]

    def __setitem__(self, args, value):
        assert isinstance(args, tuple) and len(args) == 2, 'must pass 2 dimensional tuple'
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
                self.board[row,col].square = Square(row, col)
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
            x = self.__getitem__((row, col))
            return x
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
        return [_ for _ in self.pieces if _.color == color]

    @property
    def state(self):
        return self.pieces

    def make_move(self, move):
        """
            Args:
                move: <PlayerMove>

            TODO:
            - pawn to Queen conversion
            - castling implementation
            - en-passant
        """
        piece_copy = deepcopy(move.piece) ## <=== COPY
        from_ = move.from_.coords
        to_   = move.to_.coords
        piece_copy.increment_move_counter()
        self[from_] = Empty(from_)
        self[to_] = piece_copy  ## <=== COPY

    def reset_simulation(self):
        self.simulated_board = np.zeros((8,8), dtype=np.dtype(object))

    def simulate_move(self, move):
        self.reset_simulation()
        from_ = move.from_.coords
        to_   = move.to_.coords
        piece_copy = deepcopy(move.piece)
        piece_copy.square = Square(*to_)
        self.simulated_board[from_] = Empty()
        self.simulated_board[to_] = piece_copy
        # TODO:
        # en-passant
        # pawn-queen conversion
        # castling

    def get_possible_moves(self, player_color):
        # print('player_color ->', player_color)
        possible_moves = self._get_possible_moves(player_color, attack_mode=False)
        self.possible_moves = possible_moves
        return possible_moves

    def _get_possible_moves(self, player_color, attack_mode=False):
        # print('!!! attack_mode ->', attack_mode)
        # if attack_mode:
        #     verboseprint('<<<<<<< SIMULATED >>>>>>>', l=2)
        # verboseprint(f'Compute moves for Player {player_color}:', l=2)
        # if not attack_mode:
        #     print('')
        #     print(self)
        pieces = self.get_pieces(player_color)
        possible_moves = []

        for piece in pieces:
            # input()
            # print(f'==== {piece} {piece.square}')
            moves_iter = piece.generate_moves(self.board, attack_mode)
            # verboseprint('moves generator', moves_iter)
            for move, move_type in moves_iter:
                # if not attack_mode:
                    # print('!!! attack_mode ->', attack_mode)
                move_obj = PlayerMove(player_color, piece.square,
                                    piece.square + move, piece, move_type)
                # verboseprint('...attack_mode:', attack_mode)
                # verboseprint('...running simulation')
                # next_board = deepcopy(self)
                # next_board = ChessBoard(self.state)
                # next_board.make_move(move_obj)
                # print(next_board)
                if not attack_mode:
                    # print(move_obj)
                    try:
                        self.simulate_move(move_obj)
                        _ = self._get_possible_moves(~player_color, attack_mode=True)

                        # next_board = ChessBoard(self.state)
                        # next_board.make_move(move_obj)
                        # _ = next_board._get_possible_moves(~player_color, attack_mode=True)

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
        # print(a)
        for piece, moves in d.items():
            # demo_board = deepcopy(self)
            demo_board = ChessBoard(self.state)
            for move in moves:
                demo_board[move.from_.coords] = demo_board[move.from_.coords].mark()
                demo_board[move.to_.coords] = demo_board[move.to_.coords].mark_attacked()
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
            distance = rook.square.coords[1] - king.square.coords[1]
            print('distance:', distance)
            _sign = sign(distance)
            one_step = king.square + [0, _sign*1]
            two_step = king.square + [0, _sign*2]
            if (not isinstance(self[one_step.coords], Empty) and
                not isinstance(self[two_step.coords], Empty)):
               continue
            if king.color == WHITE:
                a = king.square.coords[0] == 0
                b = rook.square.coords[0] in [0,7]
                c = rook.square.coords[1] in [0,7]
                print(a, b, c)
                continue
            if king.color == WHITE and not (
                    king.square.coords[0] == 0 and
                    rook.square.coords[0] in [0,7] and
                    rook.square.coords[1] in [0,7]):
                continue
            elif king.color == BLACK and not (
                    king.square.coords[0] == 7 and
                    rook.square.coords[0] in [0,7] and
                    rook.square.coords[1] in [0,7]):
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
        # self.board[4,3] = Rook(WHITE)
        # self.board[5,3] = Knight(WHITE)
        # self.board[2,3] = Bishop(BLACK)
        # self.board[1,2] = Pawn(WHITE)
        # self.board[0,1] = King(WHITE)
        # self.prev_board = deepcopy(self.board)

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
        # self.prev_board = deepcopy(self.board)
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
        except (DrawByStalemate, DrawByAgreement):
            self.total_reward += 0
            self.done = True
        except PlayerWins as e:
            # dtermine player color
            print('player wins !')
            self.total_reward += -1
            self.done = True

        # Copmuter
        try:
            moves = self.game.get_possible_moves()
            self.game.make_move(random.choice(moves))
        except (DrawByStalemate, DrawByAgreement):
            self.total_reward += 0
            self.done = True
        except PlayerWins as e:
            # dtermine player color
            print('player wins !')
            self.total_reward += -1
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


# import random
# import time
# separator = '<>'*30 + '\n'
#
# s = time.time()
# for j in range(5):
#     env = ChessEnv()
#     for i in range(50):
#         moves = env.game.get_possible_moves()
#         state, reward, done, _ = env.step(random.choice(moves))
#         if done:
#             break
# e = time.time()
# print('time', e-s)
# sys.exit()

# import random
# import time
# s = time.time()
# for j in range(5):
#     g = ChessGame()
#     for i in range(50):
#         # player 1
#         try:
#             moves = g.get_possible_moves()
#             g.make_move(random.choice(moves))
#             # print('')
#             # print(b)
#             # player 2
#             moves = g.get_possible_moves()
#             g.make_move(random.choice(moves))
#             # print('')
#             # print(b)
#         except (DrawByAgreement, PlayerWins):
#             pass
# e = time.time()
# print('time', e-s)
# sys.exit()

# import random
# import time
# s = time.time()
# for j in range(5):
#     g = ChessGame()
#     b = g.board
#     for i in range(50):
#         input()
#
#         try:
#             # player 1
#             moves = b.get_possible_moves(WHITE)
#             print(moves)
#             m = random.choice(moves)
#             print('MOVE CHOSEN:', m)
#             b.make_move(m)
#             print('')
#             print(b)
#             # player 2
#             moves = b.get_possible_moves(BLACK)
#             print(moves)
#             m = random.choice(moves)
#             print('MOVE CHOSEN:', m)
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
