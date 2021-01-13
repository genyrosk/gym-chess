import gym
import gym_chess
from pprint import pprint

env = gym.make("ChessVsRandomBot-v1")


def available_moves():
    state = env.state
    moves_white = env.get_possible_moves(player="WHITE")
    moves_black = env.get_possible_moves(player="BLACK")
    pprint(moves_white)
    pprint(moves_black)

    # Player 1 moves
    for move in moves_white:
        env.render_moves([move])

    # Player 2 moves
    for move in moves_black:
        env.render_moves([move])


if __name__ == "__main__":
    available_moves()
