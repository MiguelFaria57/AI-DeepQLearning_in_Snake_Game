import matplotlib.pyplot as plt
from IPython import display

import matplotlib
matplotlib.use("TkAgg")
import csv
import os

plt.ion()

def plotScores(scores, mean_scores):
    f = plt.figure(1)
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Evolution of Scores')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.ylim(ymin=0)
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))
    #plt.show(block=False)
    f.show()
    plt.pause(.1)

def plotRewards(rewards, mean_rewards):
    f = plt.figure(2)
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Evolution of Rewards')
    plt.xlabel('Number of Games')
    plt.ylabel('Reward')
    plt.plot(rewards)
    plt.plot(mean_rewards)
    #plt.ylim(ymin=0)
    plt.text(len(rewards) - 1, rewards[-1], str(rewards[-1]))
    plt.text(len(mean_rewards) - 1, mean_rewards[-1], str(mean_rewards[-1]))
    #plt.show(block=False)
    f.show()
    plt.pause(.1)

def saveResults(fileName, data):
    if not os.path.isfile("results/" + fileName):
        with open("results/" + fileName, 'w', newline='', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow(["score", "mean_score", "sum_rewards", "mean_reward", "total_time"])
            f.close()
    else:
        with open("results/" + fileName, 'a', newline='', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow(data)
            f.close()
