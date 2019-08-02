import os
from itertools import chain, cycle, islice

def verboseprint(*a, l=1, **kw):
    os_level = int(os.environ['verbose']) or 0
    if l <= os_level:
        print(*a, **kw)

def gucci_print(a, gang=5):
    string = ' '.join(a for _ in range(4))
    for i in range(1, gang+1):
        print(string[-i::], string[:-i:])

# gucci_print('HARAMBE')
