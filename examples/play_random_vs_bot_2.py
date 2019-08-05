import sys
import time
import random

import gym
import gym_chess

env = gym.make('ChessVsRandomBot-v0', log=False)

#
# Play against random bot
#
num_episodes = 5
num_steps_per_episode = 50
collected_rewards = []

s = time.time()
for i in range(num_episodes):
    initial_state = env.reset()
    print('\n'*2,'<'*5, '='*10, 'NEW GAME', '='*10, '>'*5)
    total_reward = 0
    done = False

    for j in range(num_steps_per_episode):
        if done:
            print('>'*10, 'TOTAL GAME ', i, 'REWARD =', total_reward)
            break

        moves = env.game.get_possible_moves()
        m = random.choice(moves)
        state, reward, done, _ = env.step(m)
        total_reward += reward

    collected_rewards.append(total_reward)
e = time.time()
print('time', e-s)
print('\n')
print('#'*40)
print('#'*40)
print('#'*40)
print("\nAVERAGE SCORE: ", sum(collected_rewards) / num_episodes)
