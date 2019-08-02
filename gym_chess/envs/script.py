import os
import sys
import argparse

parser = argparse.ArgumentParser(description='demo')
parser.add_argument(
    '--verbose',
    type=int,
    default=0,
    metavar='v',
    help='verbosity level (default: 0, also 1 or 2)'
)


def verboseprint(*a, level=1, **kw):
    os_level = int(os.environ['verbose']) or 0
    print(os_level, level)
    if level <= os_level:
        print(*a, **kw)
# = print if verbose else lambda *a, **k: None

if __name__ == '__main__':
    args = parser.parse_args()
    os.environ['verbose'] = str(args.verbose)
    verboseprint('print this motherfucker', level=1)
