from chess_v5 import *
import numpy as np
import os
import sys

def test_moves():
    board = ChessBoard()
    board[4,3] = Rook(WHITE)
    board[5,3] = Knight(WHITE)
    board[2,3] = Bishop(BLACK)
    board[1,2] = Pawn(WHITE)
    board[0,1] = King(WHITE)
    print(board)

    moves = board.get_possible_moves(WHITE)
    board.show_moves(moves)

# test_moves()


def test_moves_2():
    board = ChessBoard()
    board[4,3] = Rook(WHITE)
    board[5,3] = Knight(WHITE)
    board[2,3] = Bishop(BLACK)
    board[1,2] = Pawn(WHITE)
    board[0,1] = King(WHITE)
    print(board)

    pieces = board.get_pieces(WHITE)
    for piece in pieces:
        print(f'==== {piece} {piece.square}.{Square.coords_to_name(piece.square)}')
        moves_iter = piece.generate_moves(self.board, attack_mode)

# test_moves_2()

def test_moves_3():
    board = ChessBoard()
    board[4,3] = Rook(WHITE)
    board[5,3] = Knight(WHITE)
    board[2,3] = Bishop(BLACK)
    board[1,2] = Pawn(WHITE)
    board[0,1] = King(WHITE)
    player_color = WHITE
    print(board)

    pieces = board.get_pieces(player_color)
    for piece in pieces:
        print(f'Piece coords: {piece} {piece.square}.{Square.coords_to_name(piece.square)}')
        moves_iter = piece.generate_moves(board, attack_mode=False)
        possible_moves = []
        for move, move_type in moves_iter:
            move_tup = PlayerMove(player_color, piece.square, piece.square + move, piece, move_type)
            possible_moves.append(move_tup)
        for m in possible_moves:
            print(m)
        board.show_moves(possible_moves)

# test_moves_3()
# sys.exit()

def test_moves_4():
    board = ChessBoard()
    board[4,3] = Rook(WHITE)
    board[5,3] = Knight(WHITE)
    board[2,3] = Bishop(BLACK)
    board[1,2] = Pawn(WHITE)
    board[0,1] = King(WHITE)
    player_color = WHITE
    print(board)

    coords = [1,2]
    _ = board[1,2]
    print(_)
    _ = board[coords]
    print(_)
    _ = board[tuple(coords)]
    print(_)
    _ = board[np.array(coords)]
    print(_)

# test_moves_4()


def test_moves_5():
    board = ChessBoard()
    board[4,3] = Rook(WHITE)
    board[5,3] = Knight(WHITE)
    board[2,3] = Bishop(BLACK)
    board[1,2] = Pawn(WHITE)
    board[0,1] = King(WHITE)
    player_color = WHITE
    print(board)

    coords = np.array([7,7])
    board[7,7] = Queen(WHITE)
    board[7,7] = board[7,7].mark()
    print(board)
    # board[coords] = Queen(WHITE)
    # print(board)
    tup = tuple(coords)
    board[tup] = Queen(WHITE)
    board[tup] = board[tup].mark()
    print(board)
    # board[np.array(coords)] = Queen(WHITE)
    # print(board)

# test_moves_5()

def test_moves_6():
    board = ChessBoard()
    board[0,1] = King(BLACK)
    board[0,0] = Rook(BLACK)
    board[1,1] = Pawn(BLACK)
    board[1,0] = Pawn(BLACK)
    board[0,2] = Knight(BLACK)
    board[2,3] = Bishop(WHITE)
    print(board)

    moves = board.get_possible_moves(BLACK)
    board.show_moves(moves)

# test_moves_6()



def test_moves_7():
    board = ChessBoard()
    board[6,4] = King(BLACK)
    board[4,3] = Bishop(BLACK)
    board[3,4] = King(WHITE)
    print(board)

    moves = board.get_possible_moves(WHITE)
    print(moves)
    board.show_moves(moves)

test_moves_7()


#
# TESTS:
# - pawn attacks != moves
# - every other piece -> attacks == moves
# - ~BLACK == WHITE
# - moves outside board are illegal
# - moves on own piece are illegal
# - moves under check are illegal
# - moves that provoke check are illegal
# - mate conditions return no moves
# - square + move => new square
# - square + move => outside board are illegal
# - pieces stop iterating after encountering obstacle
# - castling can't happen if squares in between or king are checked
#  - pawns can move 2 squares up only in first move
# - pawns can detect *en-passant* conditions
# - castling can't happen if either piece has moved
# - a piece can capture an enemy piece
# - two boards are equal if the disposition of their pieces is equal
# - two boards with the same disposition have the same state except for certain pieces attributes
# - capturing a piece adds it to the "basket"
# - assigning multiple pieces to a slice of the board
# - deepcopy of the board is != from the original
# - Pawn, Rook, Bishop, Knight, King, Queen moves
# - move types: `capture`, `move`, `castling`, `king_check`
#
#
