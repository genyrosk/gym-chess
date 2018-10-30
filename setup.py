from setuptools import setup

setup(
	name='gym_chess',
	version='0.0.1',
	packages=['gym_chess', 'gym_chess_examples'],
	install_requires=['gym',
		'pprint',
		'numpy'
		]
)
