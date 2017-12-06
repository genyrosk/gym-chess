import sys
import numpy as np
import random 
from pprint import pprint
import random

import gym
import gym_chess

env = gym.make('ChessVsRandomBot-v0')

num_episodes = 1
num_steps_per_episode = 200

collected_rewards = []

def test_available_moves():
	state = env.state
	moves_p1 = env.get_possible_moves(state, 1)
	moves_p2 = env.get_possible_moves(state, -1)
	pprint(moves_p1)
	pprint(moves_p2)

	# no actions left -> resign
	if len(moves_p1) == 0:
		print('resigning is the only move...')
		resign_action = env.resign()

	# chess coordinates Player 1
	for m in moves_p1:
		print(env.convert_coords(m))

	# chess coordinates Player 2
	for m in moves_p2:
		print(env.convert_coords(m))

	# Player 1 moves
	for piece in set([m['piece_id'] for m in moves_p1]):
		env.render_moves(state, piece, moves_p1, mode='human')

	# Player 2 moves
	for piece in set([m['piece_id'] for m in moves_p2]):
		env.render_moves(state, piece, moves_p2, mode='human')


def test_make_move():
	state = env.state
	player = 1
	actions = env.get_possible_actions(state, player)
	print(actions)
	for a in actions:
		print(env.action_to_move(a, player))

	for a in actions:
		state, reward, done, __ = env.step(a)
		__ = env.reset()



#
# Play against random bot
#
for i in range(num_episodes):
	initial_state = env.reset()
	print('\n'*2,'<'*5, '='*10, 'NEW GAME', '='*10, '>'*5)
	# env._render()
	# print('<'*5, '-'*10, 'STARTING', '-'*10, '>'*5)

	player = 1
	total_reward = 0
	done = False
	on_move = 1

	for j in range(num_steps_per_episode):
		state = env.state

		board = state['board']
		kr_moves = state['kr_moves']
		captured = state['captured']

		if done:
			print('>'*10, 'TOTAL GAME ', i, 'REWARD =', total_reward)
			break

		moves = env.get_possible_moves(state, player)

		if len(moves) == 0:
			a = env.resign_action()
			print('<'*5, '@'*10, 'PLAYER RESIGNED', '@'*10, '>'*5)
		else:
			m = random.choice(moves)
			a = env.move_to_actions(m)
			# print('{:6s}'.format(env.convert_coords(m)), end=' ')

		# perform action
		state, reward, done, __ = env.step(a)
		total_reward += reward		

	collected_rewards.append(total_reward)

print('\n')
print('#'*40)
print('#'*40)
print('#'*40)
print("\nAVERAGE SCORE: ", sum(collected_rewards) / num_episodes)

