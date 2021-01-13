import gym
import gym_chess

env = gym.make("ChessVsRandomBot-v1")


def make_move():
    state = env.state
    player = 1
    actions = [env.move_to_action(move) for move in env.possible_moves]
    print(env.possible_moves)
    print(actions)

    for a in actions:
        state, reward, done, _ = env.step(a)
        _ = env.reset()


if __name__ == "__main__":
    make_move()
