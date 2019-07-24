import os
import sys
# import time

import numpy as np
from copy import copy
from six import StringIO
from pprint import pprint
from itertools import chain
from collections import namedtuple

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

# TEST:
# print(BLACK)
# print(~BLACK)

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
class KingCheck(Exception):
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
        print(' ==>>', new_coords)
        return Square(*new_coords)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'Square <{self.name}> {self.coords}'


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


class Board:
    LETTERS = 'abcdefgh'
    NUMBERS = '12345678'

    def __init__(self):
        self.board = [[Empty(Square(x+y)) for x in self.LETTERS] for y in self.NUMBERS]
        self.max = 64

    def __getitem__(self, args):
        assert isinstance(args, tuple) and len(args) == 2, 'must pass 2 dimensional tuple'
        return  self.board[args[0]][args[1]]

    def __setitem__(self, args, value):
        assert isinstance(args, tuple) and len(args) == 2, 'must pass 2 dimensional tuple'
        self.board[args[0]][args[1]] = value

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n < self.max:
            x = self.n // 8
            y = self.n % 8
            self.n += 1
            return self[x,y]
        else:
            raise StopIteration

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



# TEST
# b = Board()
# t = (1,2)
# s = b[t]
# print(s)
# s = b[1,2]
# print(s)
# b[1,2] = Pawn(WHITE, Square(1,2))
# print(b)
# pieces = [piece for piece in b if isinstance(piece, ChessPiece)]
# print(pieces)
# sys.exit()

class ChessBoard:
    def __init__(self):
        self.turn = WHITE

        self.board = Board()
        self.board[7,5] = Pawn(WHITE, Square(7,5))
        self.board[6,5] = Pawn(BLACK, Square(6,5))
        self.board[3,3] = Pawn(WHITE, Square(3,3))

        self.prev_board = copy(self.board)
        self.next_board = copy(self.board)

    def pieces(self, color=None):
        return ChessBoard._pieces(self.board, color=color)

    @staticmethod
    def _pieces(board, color=None):
        pieces = [piece for piece in board if isinstance(piece, ChessPiece)]
        print(board)
        print('..originally -->', pieces)
        if color:
            pieces = [x for x in pieces if x.color == color]
        return pieces

    @staticmethod
    def move_status(board, piece, move):
        try:
            new_square = piece.square + move
            print('new_square:', new_square)
            x, y = new_square.coords
            target_piece = board[x,y]

            if not isinstance(target_piece, Empty):
                assert isinstance(target_piece, ChessPiece), 'square must be either Empty or ChessPiece'
                if target_piece.color == piece.color:
                    return 'OwnPiece'
                elif isinstance(target_piece, King) and target_piece.color != player_color:
                    return 'EnemyKing'
                else:
                    return 'EnemyPiece'
            else:
                return 'Empty'

        except SquareOutsideBoard:
            print('illegal move', move)
            return 'Outside'

    def get_possible_moves(self, player_color, attack_mode=False):
        # player_color = self.turn
        return ChessBoard._get_possible_moves(copy(self.board), player_color, attack_mode=False)

    @staticmethod
    def _get_possible_moves(board, player_color, attack_mode=False):
        pieces = ChessBoard._pieces(board, color=player_color)
        print('... pieces ->', pieces)
        possible_moves = []

        for piece in pieces:
            # color = piece.color
            # curr_square = piece.square
            # all_moves = piece.moves
            is_pawn = piece.moves != piece.attacks
            is_pawn_2 = isinstance(piece, Pawn)
            assert is_pawn == is_pawn_2, 'WTF'

            for iter_move in piece.moves:
                for move in iter_move:
                    enemy_king_check = False
                    status = ChessBoard.move_status(board, piece, move)

                    if status in ['Outside' ,'OwnPiece']:
                        legal = False

                    elif status == 'EnemyPiece':
                        legal = bool(not is_pawn) # pawns can't capture on a `move`
                        move_type = 'attack'

                    elif status == 'EnemyKing':
                        legal = False
                        move_type = 'king_check'
                        if attack_mode and not is_pawn:
                            raise KingCheck()

                    elif status == 'Empty':
                        legal = not bool(is_pawn and attack_mode)
                        move_type = 'normal'

                    # => move is legal
                    if legal:
                        move_obj = PlayerMove(
                            player_color,
                            piece.square,
                            piece.square + move,
                            piece,
                            move_type
                        )
                        print(move_obj)
                        if not attack_mode:
                            next_board = ChessBoard.simulate_move(copy(board), move_obj)
                            print('back in time =============')
                            print(board)
                            try:
                                _ = ChessBoard.get_possible_moves(next_board, player_color, attack_mode=False)
                                possible_moves.append(move_obj)
                            except KingCheck:
                                pass
                        else:
                            possible_moves.append(move_obj)

            # calculate attack moves for pawn separetly
            if is_pawn:
                for iter_move in piece.attacks:
                    for move in iter_move:
                        status = ChessBoard.move_status(board, piece, move)
                        if status in ['Outside' ,'OwnPiece', 'Empty']:
                            legal = False

                        elif status == 'EnemyPiece':
                            legal = True
                            move_type = 'attack'

                        elif status == 'EnemyKing':
                            legal = False
                            move_type = 'king_check'
                            if attack_mode:
                                raise KingCheck()

                        # => move is legal
                        if legal:
                            move_obj = PlayerMove(
                                player_color,
                                piece.square,
                                piece.square + move,
                                piece,
                                move_type
                            )
                            if not attack_mode:
                                next_board = ChessBoard.simulate_move(copy(board), move_obj)
                                print('back in time =============')
                                print(board)
                                try:
                                    _ = ChessBoard.get_possible_moves(next_board, player_color, attack_mode=False)
                                    possible_moves.append(move_obj)
                                except KingCheck:
                                    pass
                            else:
                                possible_moves.append(move_obj)
        # DONE
        return possible_moves

    @staticmethod
    def simulate_move(board, move):
        """
            move = (
                player: player_color,
                from: Square(x,y),
                to: Square(x,y),
                piece: ChessPiece,
                move_type: 'attack' || 'normal' || 'king_check'
            )
        """
        print('... --? simulation')
        _from = move.from_.coords
        _to   = move.to_.coords
        piece = copy(move.piece)
        piece.square = Square(*_to)
        # change board
        board[_from] = Empty(_from)
        board[_to] = piece
        print(board)
        return board

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.board.__str__()



chessboard = ChessBoard()
print(chessboard)
print('pieces:', chessboard.pieces())
print('possible moves:', chessboard.get_possible_moves(WHITE))

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
