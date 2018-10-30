from setuptools import setup
import sys

if sys.version_info < (3, 5):
	raise Exception('Only Python 3.5 and above is supported.')
setup(
	name='gym_chess',
	version='0.0.1',
	packages=['gym_chess', 'gym_chess_examples'],
	install_requires=['gym',
		'pprint',
		'numpy'
		]
)
