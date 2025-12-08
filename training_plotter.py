import matplotlib.pyplot as plt
import json


def plot_results(data):
    episode_rewards = [sum(step["reward"] for step in ep) for ep in data]

    plt.plot(episode_rewards)
    plt.title("Episode Total Reward")
    plt.xlabel("Episode")
    plt.ylabel("Total Reward")
    plt.show()


if __name__ == "__main__":
    info_file = r"logs/abc.json"
    with open(info_file, "r") as f:
        data = json.load(f)
    plot_results(data)
