import matplotlib.pyplot as plt
import numpy as np

def plot_rewards(episode_rewards, alpha, discount, epsilon, goal=100):
    x = np.linspace(1, len(episode_rewards), len(episode_rewards))
    y = np.array(episode_rewards)

    plt.plot(x, episode_rewards)
    plt.hlines(goal, 0, len(episode_rewards)-1, color="b", linestyles="--")
    plt.title("Reward over the episodes of training")
    plt.xlabel("Episode")
    plt.ylabel("Total Reward")
    plt.text(1,95, f"alpha={alpha}")
    plt.text(1,90, f"discount={discount}")
    plt.text(1,85, f"epsilon={epsilon}")
    plt.grid(True)
    plt.show()

def plot_test_rewards(episode_rewards, test_rewards, alpha, discount, epsilon, goal=100):
    x = np.linspace(1, len(episode_rewards), len(episode_rewards))
    y = np.array(episode_rewards)

    plt.plot(x, episode_rewards)
    plt.plot(x, test_rewards)
    plt.hlines(goal, 0, len(episode_rewards)-1, color="b", linestyles="--")
    plt.title("Reward over the episodes of training")
    plt.xlabel("Episode")
    plt.ylabel("Total Reward")
    plt.text(1,95, f"alpha={alpha}")
    plt.text(1,90, f"discount={discount}")
    plt.text(1,85, f"epsilon={epsilon}")
    plt.grid(True)
    plt.show()
