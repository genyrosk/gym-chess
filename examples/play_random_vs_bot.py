import sys
import random
import numpy as np

import gym
import gym_chess

env = gym.make('ChessVsRandomBot-v0', log=False)

#
# Play against random bot
#
num_episodes = 5
num_steps_per_episode = 50

collected_rewards = []

import time
s = time.time()
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
		# moves = [m for m in moves if m['type'] == 'castling']
		# print(moves)

		if len(moves) == 0:
			a = env.resign_action()
			print('@'*15, 'PLAYER RESIGNED', '@'*15)
		else:
			m = random.choice(moves)
			a = env.move_to_actions(m)
			# print('{:6s}'.format(env.convert_coords(m)), end=' ')

		# perform action
		state, reward, done, __ = env.step(a)
		total_reward += reward

	collected_rewards.append(total_reward)
e = time.time()
print('time', e-s)
print('\n')
print('#'*40)
print('#'*40)
print('#'*40)
print("\nAVERAGE SCORE: ", sum(collected_rewards) / num_episodes)
