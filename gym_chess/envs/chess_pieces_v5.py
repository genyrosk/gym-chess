import os
import sys
import numpy as np
from copy import deepcopy
from gym_chess.envs.utils import verboseprint, gucci_print

cli_white = "93m"
cli_black = "92m"

class ChessColor:
    cli_colors = {'BLACK': cli_black, 'WHITE': cli_white}
    dual_map = {'BLACK':'WHITE', 'WHITE':'BLACK'}
    def __init__(self, color, cli_color=None):
        self.color = color
        self.cli_color = self.cli_colors[color]
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return f"<\033[{self.cli_color}{self.color}\033[0m>"
    def __eq__(self, other):
        if self.color == other.color:
            return True
        else:
            return False
    def __invert__(self):
        return ChessColor(self.dual_map[self.color])
    def hash(self):
        return self.color

BLACK = ChessColor('BLACK', cli_black)
WHITE = ChessColor('WHITE', cli_white)


class Move:
    def __init__(self, move_coords, iterable=False):
        self.move_coords =  np.array(move_coords)
        self.iterable = iterable
        self.has_moved = False
    def __iter__(self):
        self.has_moved = False
        self.n = 0
        return self
    def __next__(self):
        if self.iterable:
            self.n += 1
            return self.move_coords * self.n
            # return [
            #     self.move_coords[0]*self.n,
            #     self.move_coords[1]*self.n
            # ]
        else:
            if not self.has_moved:
                self.has_moved = True
                return self.move_coords
            else:
                raise StopIteration()

class PawnAttackEnPassant:
    def __init__(self, color, piece, from_, to_, target):
        self.color = color
        self.piece = piece
        self.from_ = from_
        self.to_ = to_
        self.target = target

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

# # one time
# UP = Move([1,0])
# DOWN = Move([-1,0])
# LEFT = Move([0,-1])
# RIGHT = Move([0,1])
# UP_LEFT = Move([1,-1])
# UP_RIGHT = Move([1,1])
# DOWN_LEFT = Move([-1,-1])
# DOWN_RIGHT = Move([-1,1])
#
# # repeatable
# UP_ITER = Move([1,0], iterable=True)
# DOWN_ITER = Move([-1,0], iterable=True)
# LEFT_ITER = Move([0,-1], iterable=True)
# RIGHT_ITER = Move([0,1], iterable=True)
# UP_LEFT_ITER = Move([1,-1], iterable=True)
# UP_RIGHT_ITER = Move([1,1], iterable=True)
# DOWN_LEFT_ITER = Move([-1,-1], iterable=True)
# DOWN_RIGHT_ITER = Move([-1,1], iterable=True)
#
# # special pawn
# TWO_UP = Move([2,0])
# TWO_DOWN = Move([-2,0])
#
# # knight
# UP_UP_RIGHT = Move([2,1])
# UP_RIGHT_RIGHT = Move([1,2])
# UP_UP_LEFT = Move([2,-1])
# UP_LEFT_LEFT = Move([1,-2])
# DOWN_DOWN_LEFT = Move([-2,-1])
# DOWN_LEFT_LEFT = Move([-1,-2])
# DOWN_DOWN_RIGHT = Move([-2,1])
# DOWN_RIGHT_RIGHT = Move([-1,2])


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
        self.marked = False
        self.attacked = False
        #
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        s1, s2 = ' ', ' '
        if self.marked:
            s1, s2 = '<', '>'
        if self.attacked:
            s1, s2 = '+', '+'
        if self.color == WHITE:
            if not os.getenv('CLI_COLOR', True):
                return f"{s1}{self.icons[0]}{s2}"
            return f"\033[{cli_white}{s1}{self.icons[0]}{s2}\033[0m"
        else:
            if not os.getenv('CLI_COLOR', True):
                return f"{s1}{self.icons[1]}{s2}"
            return f"\033[{cli_black}{s1}{self.icons[0]}{s2}\033[0m"
    def copy(self):
        cp = self.__class__(self.color)
        cp.total_moves = self.total_moves
        return cp
    @property
    def moves(self):
        return self.move_types
    @property
    def attacks(self):
        return self.moves

    def mark_attacked(self):
        self_copy = deepcopy(self)
        self_copy.attacked = True
        return self_copy
    def mark(self):
        self_copy = deepcopy(self)
        self_copy.marked = True
        return self_copy
    def unmark(self):
        self_copy = deepcopy(self)
        self_copy.marked = False
        self_copy.attacked = False
        return self_copy

    def increment_move_counter(self):
        self.total_moves += 1

    def assess_move_to(self, target_square):
        # empty square
        if isinstance(target_square, Empty):
            return True, 'move'
        # quick check
        assert isinstance(target_square, ChessPiece), \
                    'square must be either Empty or ChessPiece'
        # own piece
        if target_square.color == self.color:
            return False, 'own_piece'
        # enemy king
        elif isinstance(target_square, King): # and target_piece.color != self.color:
            return False, 'king_check'
        # enemy piece
        else:
            return True, 'capture'

    # @profile
    def generate_moves(self, chessboard, attack_mode=False):
        for iter_move in self.moves:
            for move in iter_move:
                # input()
                # if attack_mode:
                #     print(f'\t >>> For {self} {self.square} analyse move {move}, [attack_mode: {attack_mode}]')
                # else:
                #     print(f'>>> TRY {self} {self.square} analyse move {move}, [attack_mode: {attack_mode}]')
                try:
                    new_square = tuple(self.square + move)
                    if (new_square[0] > 7 or new_square[0] < 0 or
                        new_square[1] > 7 or new_square[1] < 0):
                        raise SquareOutsideBoard
                    target_piece = chessboard[new_square]
                    # print(self.square)
                    # print(move)
                    # print(new_square)
                    # print(target_piece)
                    legal, move_type = self.assess_move_to(target_piece)

                    if not attack_mode:
                        print(new_square)
                        print(legal, move_type)
                    # verboseprint('assessment ==>', legal, move_type)
                    if attack_mode and move_type == 'king_check':
                        print('\t\t => king check')
                        raise KingCheck()

                    if legal:
                        # verboseprint('move is LEGAL => yield', l=2)
                        # print('\t\t => legal')
                        yield move, move_type
                        if move_type == 'capture':
                            # print('\t\t => capture')
                            break
                    else:
                        # print('\t\t => illegal')
                        break
                except SquareOutsideBoard:
                    # print('\t\t => outisde board')
                    break
        return

class Pawn(ChessPiece):
    def __init__(self, color):
        super().__init__(color)
        self.icons = ['♟', '♙']
        self.move_types = None
    @property
    def moves(self):
        UP = Move([1,0])
        DOWN = Move([-1,0])
        TWO_UP = Move([2,0])
        TWO_DOWN = Move([-2,0])
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
        UP_LEFT = Move([1,-1])
        UP_RIGHT = Move([1,1])
        DOWN_LEFT = Move([-1,-1])
        DOWN_RIGHT = Move([-1,1])
        if self.color == WHITE:
            return [UP_LEFT, UP_RIGHT]
        else:
            return [DOWN_LEFT, DOWN_RIGHT]

    def assess_move_to(self, target_square):
        if isinstance(target_square, Empty):
            return True, 'move'
        else:
            return False, None

    def assess_attack_on(self, target_square):
        if (isinstance(target_square, ChessPiece) and
            target_square.color != self.color):
            if isinstance(target_square, King):
                return False, 'king_check'
            else:
                return True, 'capture'
        else:
            return False, None

    def generate_moves(self, chessboard, attack_mode=False):
        for move in super().generate_moves(chessboard, attack_mode):
            yield move
        for iter_move in self.attacks:
            for move in iter_move:
                # input()
                # verboseprint(f'\n\t >>> For {self} {self.square} analyse move {move}', l=2)
                try:
                    new_square = tuple(self.square + move)
                    if (new_square[0] > 7 or new_square[0] < 0 or
                        new_square[1] > 7 or new_square[1] < 0):
                        raise SquareOutsideBoard
                    target_piece = chessboard[new_square]
                    legal, move_type = self.assess_attack_on(target_piece)
                    # verboseprint('assessment ==>', legal, move_type, l=2)
                    if attack_mode and move_type == 'king_check':
                        raise KingCheck()
                    if legal:
                        # verboseprint('move is LEGAL => yield', l=2)
                        yield move, move_type
                        if move_type == 'capture':
                            break
                    else:
                        break
                except SquareOutsideBoard:
                    break

class Rook(ChessPiece):
    def __init__(self, color):
        UP_ITER = Move([1,0], iterable=True)
        DOWN_ITER = Move([-1,0], iterable=True)
        LEFT_ITER = Move([0,-1], iterable=True)
        RIGHT_ITER = Move([0,1], iterable=True)
        UP_LEFT_ITER = Move([1,-1], iterable=True)
        UP_RIGHT_ITER = Move([1,1], iterable=True)
        DOWN_LEFT_ITER = Move([-1,-1], iterable=True)
        DOWN_RIGHT_ITER = Move([-1,1], iterable=True)
        self.can_castle = True
        self.has_castled = False
        self.icons = ['♜', '♖']
        self.move_types = [UP_ITER, DOWN_ITER, LEFT_ITER, RIGHT_ITER]
        super().__init__(color)

class Knight(ChessPiece):
    def __init__(self, color):
        UP_UP_RIGHT = Move([2,1])
        UP_RIGHT_RIGHT = Move([1,2])
        UP_UP_LEFT = Move([2,-1])
        UP_LEFT_LEFT = Move([1,-2])
        DOWN_DOWN_LEFT = Move([-2,-1])
        DOWN_LEFT_LEFT = Move([-1,-2])
        DOWN_DOWN_RIGHT = Move([-2,1])
        DOWN_RIGHT_RIGHT = Move([-1,2])
        self.icons = ['♞', '♘']
        self.move_types = [
            UP_UP_RIGHT, UP_RIGHT_RIGHT, UP_UP_LEFT, UP_LEFT_LEFT,
            DOWN_DOWN_LEFT, DOWN_LEFT_LEFT, DOWN_DOWN_RIGHT, DOWN_RIGHT_RIGHT
        ]
        super().__init__(color)

class Bishop(ChessPiece):
    def __init__(self, color):
        UP_ITER = Move([1,0], iterable=True)
        DOWN_ITER = Move([-1,0], iterable=True)
        LEFT_ITER = Move([0,-1], iterable=True)
        RIGHT_ITER = Move([0,1], iterable=True)
        UP_LEFT_ITER = Move([1,-1], iterable=True)
        UP_RIGHT_ITER = Move([1,1], iterable=True)
        DOWN_LEFT_ITER = Move([-1,-1], iterable=True)
        DOWN_RIGHT_ITER = Move([-1,1], iterable=True)
        self.icons = ['♝', '♗']
        self.move_types = [UP_LEFT_ITER, UP_RIGHT_ITER, DOWN_LEFT_ITER, DOWN_RIGHT_ITER]
        super().__init__(color)

class Queen(ChessPiece):
    def __init__(self, color):
        UP_ITER = Move([1,0], iterable=True)
        DOWN_ITER = Move([-1,0], iterable=True)
        LEFT_ITER = Move([0,-1], iterable=True)
        RIGHT_ITER = Move([0,1], iterable=True)
        UP_LEFT_ITER = Move([1,-1], iterable=True)
        UP_RIGHT_ITER = Move([1,1], iterable=True)
        DOWN_LEFT_ITER = Move([-1,-1], iterable=True)
        DOWN_RIGHT_ITER = Move([-1,1], iterable=True)
        self.icons = ['♛', '♕']
        self.move_types = [
            UP_ITER, DOWN_ITER, LEFT_ITER, RIGHT_ITER,
            UP_LEFT_ITER, UP_RIGHT_ITER, DOWN_LEFT_ITER, DOWN_RIGHT_ITER
        ]
        super().__init__(color)

class King(ChessPiece):
    def __init__(self, color):
        UP = Move([1,0])
        DOWN = Move([-1,0])
        LEFT = Move([0,-1])
        RIGHT = Move([0,1])
        UP_LEFT = Move([1,-1])
        UP_RIGHT = Move([1,1])
        DOWN_LEFT = Move([-1,-1])
        DOWN_RIGHT = Move([-1,1])
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
    def mark_attacked(self):
        return Marked()

class Marked:
    def __init__(self, marker='X'):
        self.marker = marker
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return self.marker

class LogicException(Exception):
    pass
class SquareOutsideBoard(LogicException):
    pass
class EnemyPiecePresent(LogicException):
    pass
class OwnPiecePresent(LogicException):
    pass
class KingCheck(LogicException):
    pass

class GameEvent(Exception):
    pass
class PlayerHasNoMoves(GameEvent):
    def __init__(self, player):
        self.player = player
class PlayerWins(GameEvent):
    def __init__(self, player):
        self.player = player
class DrawByStalemate(GameEvent):
    pass
class DrawByAgreement(GameEvent):
    pass
