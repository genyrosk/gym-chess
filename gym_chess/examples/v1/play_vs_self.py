import sys
import time
import random

import numpy as np
import gym
import gym_chess

env = gym.make("ChessVsSelf-v1", log=False)

#
# Play against self
#
num_episodes = 2
num_steps = 100

total_steps = 0
collected_rewards = []
start = time.time()

for i in range(num_episodes):
    initial_state = env.reset()
    print("\n", "=" * 10, "NEW GAME", "=" * 10)
    env.render()
    total_rewards = {"WHITE": 0, "BLACK": 0}

    for j in range(num_steps):
        total_steps += 1
        # white moves
        moves = env.possible_moves
        m = random.choice(moves)
        a = env.move_to_action(m)
        # perform action
        state, reward, done, _ = env.step(a)
        total_rewards["WHITE"] += reward
        if done:
            break

        # black moves
        moves = env.possible_moves
        m = random.choice(moves)
        a = env.move_to_action(m)
        # perform action
        state, reward, done, _ = env.step(a)
        total_rewards["BLACK"] += reward
        if done:
            break

    print(">" * 5, "GAME", i, "REWARD:", total_rewards)
    collected_rewards.append(total_rewards)

end = time.time()
diff = end - start

print("Total time (s)", diff)
print("Total episodes", num_episodes)
print("Total steps", total_steps)
print("Time per episode (s)", diff / num_episodes)
print("Time per step (s)", diff / total_steps)
