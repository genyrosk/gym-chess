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
separator = '<>'*30 + '\n'
cli_white = "93m"
cli_black = "1;32;40m"

class ChessColor:
    def __init__(self, color, cli_color=None):
        self.color = color
        self.cli_color = cli_color
        self.dual_map = {'BLACK':'WHITE', 'WHITE':'BLACK'}
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return f'<\033[{cli_white}{self.color}\033[0m>'
    def __eq__(self, other):
        if self.color == other.color:
            return True
        else:
            return False
    def __invert__(self):
        return ChessColor(self.dual_map[self.color])

class BlackColor(ChessColor):
    def __init__(self):
        super().__init__('BLACK', cli_white)
class WhiteColor(ChessColor):
    def __init__(self):
        super().__init__('WHITE', cli_black)

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
        self.has_moved = False
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
    def __init__(self, color, square=None):
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
            return f"\033[93m{self.icons[0]}\033[0m"
            # return f'\033[0m 0;37;48m {self.icons[0]} \'
        else:
            return f"\033[1;32;40m{self.icons[1]}\033[0m"

class Pawn(ChessPiece):
    def __init__(self, color):
        super().__init__(color)
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
    def __init__(self, color):
        self.can_castle = True
        self.has_castled = False
        self.icons = ['♜', '♖']
        super().__init__(color)
    @property
    def moves(self):
        return [UP_ITER, DOWN_ITER, LEFT_ITER, RIGHT_ITER]
    @property
    def attacks(self):
        return self.moves


class Knight(ChessPiece):
    def __init__(self, color):
        self.icons = ['♞', '♘']
        super().__init__(color)
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
    def __init__(self, color):
        self.icons = ['♝', '♗']
        super().__init__(color)
    @property
    def moves(self):
        return [UP_LEFT_ITER, UP_RIGHT_ITER, DOWN_LEFT_ITER, DOWN_RIGHT_ITER]
    @property
    def attacks(self):
        return self.moves


class Queen(ChessPiece):
    def __init__(self, color):
        self.icons = ['♛', '♕']
        super().__init__(color)
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
    def __init__(self, color):
        self.is_checked = False
        self.has_castled = False
        self.icons = ['♚', '♔']
        super().__init__(color)
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
    def __init__(self, square=None):
        self.square = square
        self.attacked_by = []
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return '.'
class Marked:
    def __init__(self, marker='X'):
        self.marker = marker
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return self.marker


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

    def __init__(self, state=None):
        self.board = np.array([[Empty() for x in self.LETTERS] for y in self.NUMBERS])
        self.max = 64
        if state:
            for piece in state:
                self.__setitem__(piece.square.coords, piece)


    def __getitem__(self, args):
        assert isinstance(args, tuple) and len(args) == 2, 'must pass 2 dimensional tuple'
        return  self.board[args[0]][args[1]]

    def __setitem__(self, args, piece):
        print(args)
        print(type(args))
        assert isinstance(args, tuple) and len(args) == 2, 'must pass 2 dimensional tuple'
        # if
        if isinstance(row, slice):
            row = list(range(row.start or 0, row.stop or -1, row.step or 1))
        else:
            row = [row]
        if isinstance(col, slice):
            col = list(range(col.start or 0, col.stop or -1, col.step or 1))
        else:
            col = [col]

        for 


        row, col = args[0], args[1]
        if isinstance(row, int) and isinstance(col, int):
            piece.square = Square(row, col)
            self.board[row,col] = piece
        else:
            if isinstance(row, slice):
                row = list(range(row.start or 0, row.stop or -1, row.step or 1))
            else:
                row = [row]
            if isinstance(col, slice):
                col = list(range(col.start or 0, col.stop or -1, col.step or 1))
            else:
                col = [col]

            for i, r in enumerate(row):
                for j, c in enumerate(col):
                    print(r, c)
                    piece.square = Square(r, c)
                    self.board[r][c] = piece
        print(row, col)
        piece.square = Square(row, col)
        self.board[row][col] = piece

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
            return self[row, col]
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

    @property
    def pieces(self):
        return [piece for piece in self.__iter__() if isinstance(piece, ChessPiece)]

    @property
    def state(self):
        return self.pieces

    def copy(self):
        return Board(state=self.state)



# TEST
b = Board()
# t = (1,2)
# s = b[t]
# print(s)
# s = b[1,2]
# print(s)
# b[1,2] = Pawn(WHITE)
# b[2,2] = Pawn(WHITE)

b[2:4,4] = [Pawn(WHITE), Pawn(WHITE), Pawn(WHITE)]

print(b)
pieces = [piece for piece in b if isinstance(piece, ChessPiece)]
print(pieces)
state = b.state
b2 = Board(state=state)
print(b2)
sys.exit()

class ChessBoard:
    def __init__(self):
        self.turn = WHITE

        self.board = Board()
        self.board[5,5] = Pawn(WHITE)
        self.board[3,3] = Pawn(WHITE)
        self.board[6,6] = Pawn(BLACK)
        self.prev_board = self.board.copy()

    def pieces(self, color=None):
        return ChessBoard._pieces(self.board, color=color)

    @staticmethod
    def _pieces(board, color=None):
        pieces = [piece for piece in board if isinstance(piece, ChessPiece)]
        print('\nPieces:')
        print('...all      -->', pieces)
        if color:
            pieces = [x for x in pieces if x.color == color]
        print('...filered  -->', pieces)
        return pieces

    @staticmethod
    def move_status(board, piece, move):
        try:
            new_square = piece.square + move
            # print('... new_square:', new_square)
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
        if attack_mode:
            print('<<<<<<< SIMULATED >>>>>>>')
        print(f'Compute moves for Player {player_color}:')
        if not attack_mode:
            print('')
            print(board)
        pieces = ChessBoard._pieces(board, color=player_color)
        possible_moves = []

        for piece in pieces:
            # color = piece.color
            # curr_square = piece.square
            # all_moves = piece.moves
            is_pawn = piece.moves != piece.attacks
            is_pawn_2 = isinstance(piece, Pawn)
            assert is_pawn == is_pawn_2, 'WTF'

            print(f'\t{piece} {piece.square}' )
            for iter_move in piece.moves:
                for move in iter_move:
                    print(f'\n\t >>> For {piece} {piece.square} analyse move {move}' )
                    status = ChessBoard.move_status(board, piece, move)

                    if status in ['Outside' ,'OwnPiece']:
                        legal = False
                        move_type = None

                    elif status == 'EnemyPiece':
                        legal = bool(not is_pawn) # pawns can't capture on a `move`
                        move_type = 'attack'

                    elif status == 'EnemyKing':
                        legal = False
                        move_type = 'king_check'
                        if attack_mode and not is_pawn:
                            raise KingCheck()

                    elif status == 'Empty':
                        legal = bool(is_pawn)
                        move_type = 'normal'

                    print(f'\t\t==>> <move {move}>, legal: {legal}, type: {move_type}')

                    # => move is legal
                    if legal and not attack_mode:
                        print('...move is legal')
                        move_obj = PlayerMove(
                            player_color,
                            piece.square,
                            piece.square + move,
                            piece,
                            move_type
                        )
                        print('...attack_mode:', attack_mode)
                        print('...running simulation')
                        next_board = ChessBoard.simulate_move(board.copy(), move_obj)
                        try:
                            print('...simulation => get possible moves')
                            _ = ChessBoard._get_possible_moves(next_board, ~player_color, attack_mode=True)
                            print('... NO King Check ====>>>> save move', move_obj)
                            possible_moves.append(move_obj)
                        except KingCheck:
                            pass

            # calculate attack moves for pawn separetly
            if is_pawn:
                for iter_move in piece.attacks:
                    for move in iter_move:
                        print(f'\n\t >>> For {piece} {piece.square} analyse move {move}' )

                        status = ChessBoard.move_status(board, piece, move)
                        if status in ['Outside' ,'OwnPiece', 'Empty']:
                            legal = False
                            move_type = None

                        elif status == 'EnemyPiece':
                            legal = True
                            move_type = 'attack'

                        elif status == 'EnemyKing':
                            legal = False
                            move_type = 'king_check'
                            if attack_mode:
                                raise KingCheck()

                        print(f'\t\t==>> <move {move}>, legal: {legal}, type: {move_type}')

                        # => move is legal
                        if legal and not attack_mode:
                            move_obj = PlayerMove(
                                player_color,
                                piece.square,
                                piece.square + move,
                                piece,
                                move_type
                            )
                            print('...attack_mode:', attack_mode)
                            print('...running simulation')
                            next_board = ChessBoard.simulate_move(board.copy(), move_obj)
                            try:
                                print('...simulation => get possible moves')
                                _ = ChessBoard._get_possible_moves(next_board, ~player_color, attack_mode=True)
                                print('... NO King Check ====>>>> save move', move_obj)
                                possible_moves.append(move_obj)
                            except KingCheck:
                                pass
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
        print(f'/// SIMULATION >>> {move}')
        print(f'/// FROM >>>')
        _from = move.from_.coords
        _to   = move.to_.coords

        new_board = copy(board)
        new_board[_to]= Marked()
        print(new_board)

        piece = copy(move.piece)
        piece.square = Square(*_to)
        # change board
        new_board[_from] = Empty(_from)
        new_board[_to] = piece
        # print(f'/// TO >>>')
        # print(board)
        return new_board

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.board.__str__()



chessboard = ChessBoard()
# print(chessboard)
# print('\n', separator*2)
#
# print('\nTEST: Retrieving all the pieces on the board', end='\n'+'-'*35 + '\n')
# print('RESULT: pieces:', chessboard.pieces())
print('\n', separator*2)

print('\nTEST: Calculating ALL possible moves', end='\n'+'-'*35 + '\n')
print('possible moves:', chessboard.get_possible_moves(WHITE))
print('\n', separator*2)

p1 = Pawn(WHITE)
p2 = Rook(WHITE)
print(p1.moves == p1.attacks)
print(p2.moves == p2.attacks)

# for row in chessboard.board:
#     for x in row:
#         print(x.square)

class ChessGame:
    def __init__(self):
        pass
