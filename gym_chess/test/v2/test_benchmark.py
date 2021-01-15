import time
from copy import copy

import numpy as np
from gym_chess import ChessEnvV2
from gym_chess.test.utils import run_test_funcs


def test_benchmark():
    env = ChessEnvV2(opponent="none", log=False)

    num_episodes = 10
    num_steps = 100
    total_steps = 0
    start = time.time()

    for e in range(num_episodes):
        env.reset()
        for step in range(num_steps):
            total_steps += 1

            moves = env.possible_moves
            if not moves:
                break

            idx = np.random.choice(np.arange(len(moves)))
            move = moves[idx]
            action = env.move_to_action(move)
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

    # assert that it's less than 10 seconds
    assert diff < 1


# Total time (s) 0.5776240825653076
# Total episodes 10
# Total steps 1851
# Time per episode (s) 0.05776240825653076
# Time per step (s) 0.00031206055243938825


if __name__ == "__main__":
    run_test_funcs(__name__)
