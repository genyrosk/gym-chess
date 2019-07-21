p = Pawn(WHITE, 'a2')
for move in p.moves:
    for x in move:
        print(x)
for attack in p.attacks:
    for x in attack:
        print(x)
