p = Pawn(WHITE, 'a2')
for move in p.moves:
    for x in move:
        print(x)
for attack in p.attacks:
    for x in attack:
        print(x)

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
