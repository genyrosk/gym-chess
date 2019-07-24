import os
import sys
# import time

import numpy as np
from copy import copy
from six import StringIO
from pprint import pprint
from itertools import chain

# import gym
# from gym import spaces, error, utils
# from gym.utils import seeding

class ChessColor:
    def __init__(self, color):
        self.color = color
        self.dual_map = {'BLACK':'WHITE', 'WHITE':'BLACK'}
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return f'<Color: {self.color}>'
    def __eq__(self, other):
        if self.color == other.color:
            return True
        else:
            return False
    def __invert__(self):
        return ChessColor(self.dual_map[self.color])

class BlackColor(ChessColor):
    def __init__(self):
        super().__init__('BLACK')
class WhiteColor(ChessColor):
    def __init__(self):
        super().__init__('WHITE')

BLACK = BlackColor()
WHITE = WhiteColor()

print(BLACK)
print(~BLACK)

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


class ChessPieceMeta(type):
    def __call__(cls, *args, **kwargs):
        class_object = type.__call__(cls, *args, **kwargs)
        if not hasattr(class_object, 'icons'):
            raise NotImplementedError(f'ChessPiece subclass {cls} requires '\
                                      f'an `icons` attribute')
        return class_object

class ChessPiece(metaclass=ChessPieceMeta):
    def __init__(self, color, square):
        self.total_moves = 0
        self.color = color
        self.square = square
        self.possible_moves = []
        self.scope = []
        self.history = []
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        if self.color == WHITE:
            return self.icons[0]
        else:
            return self.icons[1]

class Pawn(ChessPiece):
    def __init__(self, color, square):
        super().__init__(color, square)
        self.icons = ['♟', '♙']
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
    def __init__(self, color, square):
        self.can_castle = True
        self.has_castled = False
        self.icons = ['♜', '♖']
        super().__init__(color, square)
    @property
    def moves(self):
        return [UP_ITER, DOWN_ITER, LEFT_ITER, RIGHT_ITER]
    @property
    def attacks(self):
        return self.moves


class Knight(ChessPiece):
    def __init__(self):
        self.icons = ['♞', '♘']
        super().__init__(color, square)
    @property
    def moves(self):
        return [
            UP_UP_RIGHT, UP_RIGHT_RIGHT, UP_UP_LEFT, UP_LEFT_LEFT,
            DOWN_DOWN_LEFT, DOWN_LEFT_LEFT, DOWN_DOWN_RIGHT, DOWN_RIGHT_RIGHT
        ]
    @property
    def attacks(self):
        return self.moves


class Bishop(ChessPiece):
    def __init__(self, color, square):
        self.icons = ['♝', '♗']
        super().__init__(color, square)
    @property
    def moves(self):
        return [UP_LEFT_ITER, UP_RIGHT_ITER, DOWN_LEFT_ITER, DOWN_RIGHT_ITER]
    @property
    def attacks(self):
        return self.moves


class Queen(ChessPiece):
    def __init__(self, color, square):
        self.icons = ['♛', '♕']
        super().__init__(color, square)
    @property
    def moves(self):
        return [
            UP_ITER, DOWN_ITER, LEFT_ITER, RIGHT_ITER,
            UP_LEFT_ITER, UP_RIGHT_ITER, DOWN_LEFT_ITER, DOWN_RIGHT_ITER
        ]
    @property
    def attacks(self):
        return self.moves


class King(ChessPiece):
    def __init__(self, color, square):
        self.is_checked = False
        self.has_castled = False
        self.icons = ['♚', '♔']
        super().__init__(color, square)
    @property
    def moves(self):
        return [
            UP, DOWN, LEFT, RIGHT,
            UP_LEFT, UP_RIGHT, DOWN_LEFT, DOWN_RIGHT
        ]
    @property
    def attacks(self):
        return self.moves

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


class SquareOutsideBoard(Exception):
    pass
class EnemyPiecePresent(Exception):
    pass
class OwnPiecePresent(Exception):
    pass


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
        print(f'---> evalute <square {self.coords}> + <move {move}>', end='')
        new_coords = [
            self.coords[0] + move[0],
            self.coords[1] + move[1],
        ]
        print(' ====', new_coords)
        return Square(*new_coords)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'Square <{self.name}> {self.coords}'


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


class ChessBoard:
    def __init__(self):
        self.turn = WHITE

        self.board = [[Empty(Square(x+y)) for x in LETTERS] for y in NUMBERS]
        self.board[7][5] = Pawn(WHITE, Square(7,5))
        self.board[6][5] = Pawn(BLACK, Square(6,5))
        self.board[5][5] = Pawn(WHITE, Square(5,5))

        self.prev_board = copy(self.board)
        self.next_board = copy(self.board)

    def pieces(self, color=None):
        pieces = [piece for piece in chain(*self.board) if isinstance(piece, ChessPiece)]
        if color:
            pieces = list(filter(lambda x: x.color == color, pieces))
        return pieces

    @staticmethod
    def move_legality_status(self, board, piece, move):
        try:
            new_square = piece.square + move
            print('new_square:', new_square)
        except SquareOutsideBoard:
            print('illegal move', move)
            return 'Outside'

        x, y = new_square.coords
        target_piece = board[x][y]
        if not isinstance(target_piece, Empty):
            assert isinstance(target_piece, ChessPiece), 'square must be either Empty or ChessPiece'
            if target_piece.color == player_color:
                return 'OwnPiecePresent'
            else:
                raise 'EnemyPiecePresent'
        else:
            return 'Empty'

    def calculate_moves(self, player_color, check_king_check=True):
        pieces = self.pieces(color=player_color)
        print(pieces)
        possible_moves = []

        for piece in pieces:
            # color = piece.color
            # curr_square = piece.square
            # all_moves = piece.moves
            diff = piece.moves != piece.attacks

            for iter_move in piece.moves:
                for move in iter_move:

                    status = ChessBoard.move_legality_status(board, piece, move)
                    if status == 'Outside':
                        legal = False
                    elif status == 'OwnPiecePresent':
                        legal = not diff
                    elif status == 'EnemyPiecePresent':
                        legal = False
                    elif status == 'Empty':
                        legal = bool(diff)

                    if legal:
                        if check_king_check:
                            pass
                            # king under attack
                            # ...
                        else:
                            possible_moves.append(move)
                    

            if diff:
                for iter_move in piece.attacks:
                    for move in iter_move:
                        status = ChessBoard.move_legality_status(board, piece, move)
                        if check_king_check:
                            pass
                            # king under attack
                            # ...
                        else:
                            possible_moves.append(move)

            # attack moves
            # -> same stuff except save one extra move on EnemyPiecePresent exception
        return []

    @staticmethod
    def simulate_move(board, move):
        """
            move = {
                from: (x,y),
                to: (x,y),
                piece: ChessPiece,
                move_type: 'attack', 'normal', 'king_check'
            }
        """
        pass

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        s = ''
        for i, row in enumerate(self.board[::-1]):
            s += NUMBERS[::-1][i]
            s += ' | '
            s += ' | '.join([str(x) for x in row])
            s += ' | '
            s += '\n'
        s += '    ' + '   '.join(LETTERS)
        s += '\n'
        return s



chessboard = ChessBoard()
print(chessboard)
print(chessboard.pieces())
print(chessboard.calculate_moves(WHITE))

p1 = Pawn(WHITE, Square(5,5))
p2 = Rook(WHITE, Square(4,4))
print(p1.moves == p1.attacks)
print(p2.moves == p2.attacks)

# for row in chessboard.board:
#     for x in row:
#         print(x.square)

class ChessGame:
    def __init__(self):
        pass
