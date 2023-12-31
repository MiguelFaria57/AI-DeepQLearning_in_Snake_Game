import torch
import random
import numpy as np
from collections import deque
from game import SnakeGameAI, Direction, Point
from model import Linear_QNet, QTrainer
import helper
import time


MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.002

MAX_GAMES = 500

class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.7 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)


    def get_state(self, game):
        head = game.snake[0]
        point_l = Point(head.x - 20, head.y)
        point_r = Point(head.x + 20, head.y)
        point_u = Point(head.x, head.y - 20)
        point_d = Point(head.x, head.y + 20)
        
        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        state = [
            # Danger straight
            (dir_r and game.is_collision(point_r)) or 
            (dir_l and game.is_collision(point_l)) or 
            (dir_u and game.is_collision(point_u)) or 
            (dir_d and game.is_collision(point_d)),

            # Danger right
            (dir_u and game.is_collision(point_r)) or 
            (dir_d and game.is_collision(point_l)) or 
            (dir_l and game.is_collision(point_u)) or 
            (dir_r and game.is_collision(point_d)),

            # Danger left
            (dir_d and game.is_collision(point_r)) or 
            (dir_u and game.is_collision(point_l)) or 
            (dir_r and game.is_collision(point_u)) or 
            (dir_l and game.is_collision(point_d)),
            
            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            
            # Food location 
            game.food.x < game.head.x,  # food left
            game.food.x > game.head.x,  # food right
            game.food.y < game.head.y,  # food up
            game.food.y > game.head.y  # food down
            ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        #for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitations
        #self.epsilon = 80 - self.n_games

        # Test increase the number of iterations where it can occur exploration (100, 150, 200) (can be beneficial)
        #self.epsilon = numIterations - self.n_games # from iteration numIterations, only chooses exploitation
        self.epsilon = 100 - self.n_games

        # Test having always a percentage of choosing exploration (1%, 5%, 10%) (isn't beneficial)
        #if self.n_games <= 100-(200*(probability/100)):
        #    self.epsilon = 100 - self.n_games # random choosing between exploration and exploitation
        #else:
        #    self.epsilon = 200*(probability/100) # probability% of choosing exploration
        '''if self.n_games <= 100-(200*(5/100)):
            self.epsilon = 100 - self.n_games # random choosing between exploration and exploitation
        else:
            self.epsilon = 200*(5/100) # probability% of choosing exploration'''

        final_move = [0,0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move


def train():
    plot_scores = []
    plot_mean_scores = []
    plot_rewards = []
    plot_mean_rewards = []
    total_score = 0
    total_reward = 0
    sum_rewards = 0
    record = 0

    agent = Agent()
    game = SnakeGameAI()

    start_time = 0
    while agent.n_games < MAX_GAMES:
    #while True:
        # get old state
        state_old = agent.get_state(game)

        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)
        sum_rewards += reward

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            end_time = time.time()
            total_time = round(end_time - start_time, 5)

            # train long memory, plot result
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = round(total_score / agent.n_games, 5)
            plot_mean_scores.append(mean_score)
            helper.plotScores(plot_scores, plot_mean_scores)

            plot_rewards.append(sum_rewards)
            total_reward += sum_rewards
            mean_reward = round(total_reward / agent.n_games, 5)
            plot_mean_rewards.append(mean_reward)
            helper.plotRewards(plot_rewards, plot_mean_rewards)
            sum_rewards = round(sum_rewards, 5)

            helper.saveResults("goingAgainstItselfPenalty_1.csv", [score, mean_score, sum_rewards, mean_reward, total_time])
            sum_rewards = 0
            start_time = time.time()



if __name__ == '__main__':
    train()