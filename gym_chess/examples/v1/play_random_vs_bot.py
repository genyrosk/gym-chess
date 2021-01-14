import sys
import random

import gym
import gym_chess

env = gym.make("ChessVsRandomBot-v1")

#
# Play against random bot
#
num_episodes = 2
num_steps = 50

collected_rewards = []

for i in range(num_episodes):
    initial_state = env.reset()
    print("\n", "=" * 10, "NEW GAME", "=" * 10)
    env.render()
    total_reward = 0

    for j in range(num_steps):
        moves = env.possible_moves
        m = random.choice(moves)
        a = env.move_to_action(m)

        # perform action
        state, reward, done, _ = env.step(a)
        total_reward += reward

        if done:
            print(">" * 5, "GAME", i, "REWARD:", total_reward)
            break

    collected_rewards.append(total_reward)

print("\n")
print("#" * 40)
print("#" * 40)
print("#" * 40)
print("\nAVERAGE SCORE: ", sum(collected_rewards) / num_episodes)
