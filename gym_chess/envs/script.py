LETTERS = 'abcdefgh'
NUMBERS = '12345678'

a = [[x+y for x in LETTERS] for y in NUMBERS]
print(a)


class Demo:

    def __init__(self):
        pass

    @classmethod
    def sth(cls):
        print('class method')

    def sth_else(self):
        self.sth()

d = Demo()
d.sth_else()
