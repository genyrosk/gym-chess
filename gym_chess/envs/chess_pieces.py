import os
import sys

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
        return f'<\033[{self.cli_color}{self.color}\033[0m>'
    def __eq__(self, other):
        if self.color == other.color:
            return True
        else:
            return False
    def __invert__(self):
        return ChessColor(self.dual_map[self.color])

BLACK = ChessColor('BLACK', cli_black)
WHITE = ChessColor('WHITE', cli_white)


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

class CastlingMove:
    def __init__(self, color):
        self.color = color
class KingCastling(CastlingMove):
    pass
class QueenCastling(CastlingMove):
    pass

CASTLES = {
    'king': KingCastling,
    'queen': QueenCastling
}

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
            raise NotImplementedError(f'ChessPiece subclass {cls} requires `icons`'\
                                      f' -> a len=2 list of piece representations')
        if not hasattr(class_object, 'move_types'):
            raise NotImplementedError(f'ChessPiece subclass {cls} requires '\
                                      f'`move_types` -> a list of possible moves.')
        return class_object

class ChessPiece(metaclass=ChessPieceMeta):
    def __init__(self, color, square=None):
        self.total_moves = 0
        self.color = color
        self.square = square
        self.possible_moves = []
        self.history = []
        #
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        if self.color == WHITE:
            if not os.getenv('CLI_COLOR', True):
                return self.icons[0]
            return f"\033[{cli_white}{self.icons[0]}\033[0m"
        else:
            if not os.getenv('CLI_COLOR', True):
                return self.icons[1]
            return f"\033[{cli_black}{self.icons[0]}\033[0m"
    @property
    def moves(self):
        return self.move_types
    @property
    def attacks(self):
        return self.moves

    def makes_move(self):
        self.total_moves += 1

class Pawn(ChessPiece):
    def __init__(self, color):
        super().__init__(color)
        self.icons = ['♟', '♙']
        self.move_types = None
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
        self.move_types = [UP_ITER, DOWN_ITER, LEFT_ITER, RIGHT_ITER]
        super().__init__(color)


class Knight(ChessPiece):
    def __init__(self, color):
        self.icons = ['♞', '♘']
        self.move_types = [
            UP_UP_RIGHT, UP_RIGHT_RIGHT, UP_UP_LEFT, UP_LEFT_LEFT,
            DOWN_DOWN_LEFT, DOWN_LEFT_LEFT, DOWN_DOWN_RIGHT, DOWN_RIGHT_RIGHT
        ]
        super().__init__(color)


class Bishop(ChessPiece):
    def __init__(self, color):
        self.icons = ['♝', '♗']
        self.move_types = [UP_LEFT_ITER, UP_RIGHT_ITER, DOWN_LEFT_ITER, DOWN_RIGHT_ITER]
        super().__init__(color)


class Queen(ChessPiece):
    def __init__(self, color):
        self.icons = ['♛', '♕']
        self.move_types = [
            UP_ITER, DOWN_ITER, LEFT_ITER, RIGHT_ITER,
            UP_LEFT_ITER, UP_RIGHT_ITER, DOWN_LEFT_ITER, DOWN_RIGHT_ITER
        ]
        super().__init__(color)


class King(ChessPiece):
    def __init__(self, color):
        self.is_checked = False
        self.has_castled = False
        self.icons = ['♚', '♔']
        self.move_types = [
            UP, DOWN, LEFT, RIGHT,
            UP_LEFT, UP_RIGHT, DOWN_LEFT, DOWN_RIGHT
        ]
        super().__init__(color)


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
