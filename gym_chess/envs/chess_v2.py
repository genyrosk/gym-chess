import os
import sys
# import time

from copy import copy
from six import StringIO
from pprint import pprint

# import gym
# from gym import spaces, error, utils
# from gym.utils import seeding
import numpy as np

class ChessColor:
    def __init__(self, color):
        self.color = color
    def __eq__(self, other):
        if self.color == other.color:
            return True
        else:
            return False
class BlackColor(ChessColor):
    def __init__(self):
        super().__init__('BLACK')
class WhiteColor(ChessColor):
    def __init__(self):
        super().__init__('WHITE')

BLACK = BlackColor()
WHITE = WhiteColor()

class Move:
    def __init__(self, move_coords, iterable=False):
        self.move_coords =  move_coords
        self.iterable = iterable
        self.has_moved = False
    def __iter__(self):
        return self
    def __next__(self):
        if self.iterable:
            return self.move_coords
        else:
            if not self.has_moved:
                self.has_moved = True
                return self.move_coords
            else:
                raise StopIteration()

# one time
UP = Move([1,0])
DOWN = Move([-1,0])
LEFT = Move([0,-1])
RIGHT = Move([0,1])
UP_LEFT = Move([1,-1])
UP_RIGHT = Move([1,1])
DOWN_LEFT = Move([-1,-1])
DOWN_RIGHT = Move([-1,1])

# repeatable
UP_ITER = Move([1,0])
DOWN_ITER = Move([-1,0])
LEFT_ITER = Move([0,-1])
RIGHT_ITER = Move([0,1])
UP_LEFT_ITER = Move([1,-1])
UP_RIGHT_ITER = Move([1,1])
DOWN_LEFT_ITER = Move([-1,-1])
DOWN_RIGHT_ITER = Move([-1,1])

# special pawn
TWO_UP = Move([2,0])
TWO_DOWN = Move([-2,0])

# knight
UP_UP_RIGHT = Move([2,1])
UP_RIGHT_RIGHT = Move([1,2])
UP_UP_LEFT = Move([2,-1])
UP_LEFT_LEFT = Move([1,-2])
DOWN_DOWN_LEFT = Move([-2,-1])
DOWN_LEFT_LEFT = Move([-1,-2])
DOWN_DOWN_RIGHT = Move([-2,1])
DOWN_RIGHT_RIGHT = Move([-1,2])


class ChessPiece:
    def __init__(self, color, square):
        self.total_moves = 0
        self.color = color
        self.square = square
        self.possible_moves = []
        self.squares_attacked = []
        self.history = []

class Pawn(ChessPiece):
    def __init__(self, color, square):
        super().__init__(color, square)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        if self.color == WHITE:
            return '♟'
        else:
            return '♙'

    @property
    def moves(self):
        if self.color == WHITE:
            if self.total_moves == 0:
                return [UP, TWO_UP]
            else:
                return [UP]
        else:
            if self.total_moves == 0:
                return [DOWN, TWO_DOWN]
            else:
                return [DOWN]

    @property
    def attacks(self):
        if self.color == WHITE:
            return [UP_LEFT, UP_RIGHT]
        else:
            return [DOWN_LEFT, DOWN_RIGHT]


class Rook(ChessPiece):
    def __init__(self):
        self.has_castled = False

class Knight(ChessPiece):
    def __init__(self):
        self.is_checked

class Bishop(ChessPiece):
    def __init__(self):
        pass

class Queen(ChessPiece):
    def __init__(self):
        pass

class King(ChessPiece):
    def __init__(self):
        self.is_checked = False
        self.has_castled = False

class CastlingMove:
    pass
class KingCastling(CastlingMove):
    pass
class QueenCastling(CastlingMove):
    pass


class Empty:
    def __init__(self, square):
        self.square = square
        self.attacked_by = []

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '.'


class Square:
    LETTERS = list('abcdefgh')
    NUMBERS = list('12345678')

    def __init__(self, *args):
        if len(args) == 1:
            self._name = args[0]
        elif len(args) == 2:
            self._coords = (args[0], args[1])
        else:
            raise Exception('1 or 2 args pls')

    @property
    def coords(self):
        try:
            return self._coords
        except AttributeError:
            self._coords = self.name_to_coords(self.name)
            return self._coords

    @classmethod
    def coords_to_name(cls, coords):
        return cls.LETTERS[coords[1]] + cls.NUMBERS[coords[0]]

    @classmethod
    def name_to_coords(cls, name):
        return [
            cls.NUMBERS.index(name[1]),
            cls.LETTERS.index(name[0])
        ]

    @coords.setter
    def coords(self, value):
        if len(value) != 2:
            raise Exception('coordinates must be len() == 2 !')
        if value[0] not in list(range(8)) or value[1] not in list(range(8)):
            raise Exception('coordinates must be 2 integers between 0 and 7')
        self._coords = value
        self._name = self.coords_to_name(self._coords)

    @property
    def name(self):
        try:
            return self._name
        except AttributeError:
            self._name = self.LETTERS[self._coords[0]] + self.NUMBERS[self._coords[0]]
            return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise Exception('name must be a string dammit !')
        self._name = value
        self._coords = self.name_to_coords(self._name)

    def __add__(self, move):
        if isinstance(move, list):
            print('horrray !!')
        print('current square', self.coords, '+ move', move)
        new_coords = [
            self.coords[0] + move[0],
            self.coords[1] + move[1],
        ]
        print('new square ===>>>', new_coords)
        return Square(*new_coords)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'Square: {self.coords}, {self.name}'

#
# class ChessSquares(dict):
#     def __init__(self):
#         pass
#
#     def __setitem__(self, key, value):
#         # Remove any previous connections with these values
#         if key in self:
#             del self[key]
#         if value in self:
#             del self[value]
#         dict.__setitem__(self, key, value)
#         dict.__setitem__(self, value, key)
#
#     def __delitem__(self, key):
#         dict.__delitem__(self, self[key])
#         dict.__delitem__(self, key)
#
#     def __len__(self):
#         """Returns the number of connections"""
#         return dict.__len__(self) // 2

LETTERS = 'abcdefgh'
NUMBERS = '12345678'

from itertools import chain

class ChessBoard:
    def __init__(self):
        self.board = [[Empty(Square(x+y)) for x in LETTERS] for y in NUMBERS]
        self.board[1][1] = Pawn(WHITE, Square(0,1))

    def pieces(self):
        return [piece for piece in chain(*self.board) if isinstance(piece, ChessPiece)]

    def calculate_moves(self):
        pieces = self.pieces()
        for piece in pieces:
            color = piece.color
            curr_square = piece.square
            all_moves = piece.moves
            for iter_move in all_moves:
                for move in iter_move:
                    print(move)
                    print(type(move))
                    print(curr_square + move)

                    # try: except: SquareOutsideBoard => exit
                    # EnemyPiecePresent or OwnPiecePresent => exit
                    # king under attack
            # attack moves
            # -> same stuff except save one extra move on EnemyPiecePresent exception
        return []

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        s = ''
        for row in self.board[::-1]:
            s += ' | '.join([str(x) for x in row])
            s += '\n'
        return s



chessboard = ChessBoard()
print(chessboard)
print(chessboard.pieces())
print(chessboard.calculate_moves())
# for row in chessboard.board:
#     for x in row:
#         print(x.square)

class ChessGame:
    def __init__(self):
        pass
