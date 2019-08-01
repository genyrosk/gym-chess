import os
import sys
# import time

import numpy as np
from six import StringIO
from pprint import pprint
from itertools import chain
from collections import namedtuple
from copy import deepcopy
from collections import defaultdict
from pprint import pprint

# import gym
# from gym import spaces, error, utils
# from gym.utils import seeding

from chess_pieces_v4 import *

sign = lambda x: (1, -1)[x < 0]

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
        print(f'\t\t---> evaluate {self} + <move {move}>', end='')
        row = self.coords[0] + move[0]
        col = self.coords[1] + move[1]
        new_coords = [row, col]
        new_ = Square(*new_coords)
        print(' ==>>', new_)
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
        return f'{self.piece} {self.from_.name}->{self.to_.name}, {self.move_type}'

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
        if state:
            for piece in state:
                self.__setitem__(piece.square.coords, piece.__class__(piece.color))

    def __getitem__(self, args):
        assert isinstance(args, tuple) and len(args) == 2, 'must pass 2 dimensional tuple'
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
    def pieces(self, color=None):
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
            -
        """
        piece_copy = deepcopy(move.piece)
        _from = move.from_.coords
        _to   = move.to_.coords
        print(f'/// SIMULATION >>> {move}')
        print(f'/// FROM >>>')
        self[_from].marked = True
        self[_to] = Marked()
        print(self)
        # changes
        piece_copy.increment_move_counter()
        self[_from] = Empty(_from)
        self[_to] = deepcopy(piece_copy)

    def get_possible_moves(self, player_color, attack_mode=False):
        if attack_mode:
            print('<<<<<<< SIMULATED >>>>>>>')
        print(f'Compute moves for Player {player_color}:')
        if not attack_mode:
            print('')
            print(self)
        pieces = self.get_pieces(player_color)
        possible_moves = []

        for piece in pieces:
            # input()
            print(f'==== {piece} {piece.square}' )
            moves_iter = piece.generate_moves(self.board, attack_mode)
            print('moves generator', moves_iter)
            for move, move_type in moves_iter:
                move_obj = PlayerMove(player_color, piece.square,
                                    piece.square + move, piece, move_type)
                print('...attack_mode:', attack_mode)
                print('...running simulation')
                next_board = deepcopy(self)
                next_board.make_move(move_obj)
                # print(next_board)
                if not attack_mode:
                    try:
                        print('...simulation => get possible moves')
                        _ = next_board.get_possible_moves(~player_color, attack_mode=True)
                        print('... NO King Check ====>>>> save move', move_obj)
                        possible_moves += [move_obj]
                    except KingCheck:
                        pass
        if not attack_mode:
            input()
            print('='*1000)
            possible_moves += self.get_castling_moves(player_color)
        self.possible_moves = possible_moves
        return possible_moves

    def show_moves(self, moves):
        d = defaultdict(list)
        for move in moves:
            d[move.piece].append(move)
        # print(a)
        for piece, moves in d.items():
            demo_board = deepcopy(self)
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
                _ = self.get_possible_moves(~player_color, attack_mode=True)
                # one step
                move_obj = PlayerMove(player_color, king.square, one_step, king, 'castling')
                next_board = deepcopy(self)
                next_board.make_move(move_obj)
                print(next_board)
                _ = next_board.get_possible_moves(~player_color, attack_mode=True)
                # two step
                move_obj = PlayerMove(player_color, king.square, two_step, king, 'castling')
                next_board = deepcopy(self)
                next_board.make_move(move_obj)
                print(next_board)
                _ = next_board.get_possible_moves(~player_color, attack_mode=True)

                # no KingCheck excpetion raised
                castle_type = {3: 'king', 4: 'queen'}[abs(distance)]
                castle_move = CASTLES[castle_type](player_color)
                possible_moves += [castle_move]
            except KingCheck:
                pass
        return possible_moves

# TEST
# b = Board()
# t = (1,2)
# s = b[t]
# print(s)
# s = b[1,2]
# print(s)
# b[1,2] = Pawn(WHITE)
# b[2,2] = Pawn(WHITE)

# b[2,1:4] = [Pawn(WHITE), Pawn(WHITE), Pawn(WHITE)]
#
# print(b)
# pieces = [piece for piece in b if isinstance(piece, ChessPiece)]
# print(pieces)
# state = b.state
# b2 = Board(state=state)
# print(b2)
# sys.exit()

class PlayerHasNoMoves(Exception):
    pass 

class ChessGame:
    def __init__(self):
        self.player_turn = WHITE
        self.board = ChessBoard()
        # self.board[0,:] = [Rook(WHITE), Knight(WHITE), Bishop(WHITE), Queen(WHITE),
        #                     King(WHITE), Empty(), Empty(), Rook(WHITE)]
        # self.board[1,:] = [Pawn(WHITE) for _ in range(8)]
        # self.board[6,:] = [Pawn(BLACK) for _ in range(8)]
        # self.board[7,:] = [Rook(BLACK), Knight(BLACK), Bishop(BLACK), Queen(BLACK),
        #                     King(BLACK), Bishop(BLACK), Knight(BLACK), Rook(BLACK)]
        self.board[4,3] = Rook(WHITE)
        self.board[5,3] = Knight(WHITE)
        self.board[2,3] = Bishop(BLACK)
        self.board[1,2] = Pawn(WHITE)
        self.board[0,1] = King(WHITE)
        self.prev_board = deepcopy(self.board)

    def get_possible_moves(self):
        player_color = self.player_turn
        possible_moves = self.board.get_possible_moves(player_color, attack_mode=False)
        if not possible_moves:
            raise PlayerHasNoMoves()

    def make_move(self, move):
        assert move in self.board.possible_moves, 'ILLEGAL MOVE !!'
        self.prev_board = deepcopy(self.board)
        self.board.make_move(move)
        self.player_turn = ~self.player_turn

    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return self.board.__str__()


class ChessEnv:
    def __init__(self,):
        pass
    def _seed(self, seed=None):
        pass
    def _step(self, action):
        pass
    def _reset(self):
        pass
    def _render(self, mode=['human', 'ansi']):
        pass

separator = '<>'*30 + '\n'

chessgame = ChessGame()
print(chessgame.board.pieces)
# print(chessboard)
# print('\n', separator*2)
#
# print('\nTEST: Retrieving all the pieces on the board', end='\n'+'-'*35 + '\n')
# print('RESULT: pieces:', chessboard.pieces())
print('\n', separator*2)

print('\nTEST: Calculating ALL possible moves', end='\n'+'-'*35 + '\n')
pmoves = chessgame.get_possible_moves()
chessgame.board.show_moves(pmoves)
print('possible moves:', pmoves)
print('\n', separator*2)


# for row in chessboard.board:
#     for x in row:
#         print(x.square)

class ChessGame:
    def __init__(self):
        pass
