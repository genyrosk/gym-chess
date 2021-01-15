import time
from copy import copy

import numpy as np
from gym_chess import ChessEnvV1
from gym_chess.test.utils import run_test_funcs


def test_benchmark():
    env = ChessEnvV1(opponent="none", log=False)

    num_episodes = 10
    num_steps = 50
    total_steps = 0
    start = time.time()

    for e in range(num_episodes):
        env.reset()
        for step in range(num_steps):
            total_steps += 1

            actions = env.get_possible_actions()
            if not actions:
                break

            idx = np.random.choice(np.arange(len(actions)))
            action = actions[idx]
            state, reward, done, info = env.step(action)

            if done:
                break

    end = time.time()
    diff = end - start

    print("Total time (s)", diff)
    print("Total episodes", num_episodes)
    print("Total steps", total_steps)
    print("Time per episode (s)", diff / num_episodes)
    print("Time per step (s)", diff / total_steps)

    # assert that it's less than 100 seconds
    assert diff < 100


# Total time (s) 54.72057318687439
# Total episodes 10
# Total steps 500
# Time per episode (s) 5.472057318687439
# Time per step (s) 0.10944114637374878


if __name__ == "__main__":
    run_test_funcs(__name__)
