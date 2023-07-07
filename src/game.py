import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np


CATCH_BONUS = 10 # reward += 10
COLLISION_PENALTY = 10 # reward -= 10
TIME_PENALTY = 0.01 # reward -= difference_of_frames * TIME_PENALTY
HITS_ITSELF_PENALTY = 0.01 # reward = -HITS_ITSELF_PENALTY * (percentage_of_res * (height or width) - difference_between_body_parts)
HITS_ITSELF_GAP = 0.4 # percentage of resolution that gives the minimum gap between the snake body parts where it starts to give penalty

pygame.init()
font = pygame.font.Font('arial.ttf', 25)
# font = pygame.font.SysFont('arial', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)

BLOCK_SIZE = 20
SPEED = 200


class SnakeGameAI:

    def __init__(self, w=640, h=480):
        self.last_frame = 0

        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.last_frame = 0

        # init game state
        self.direction = Direction.RIGHT

        self.head = Point(self.w / 2, self.h / 2)
        self.snake = [self.head,
                      Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)]

        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0

    def _place_food(self):
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def play_step(self, action):
        self.frame_iteration += 1
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # 2. move
        self._move(action)  # update the head
        self.snake.insert(0, self.head)

        # 3. check if game over
        # give penalty if the snake is going against itself anf for time between catches
        reward = self.detect_colision()
        #print("Reward after detect_colision: ", reward)

        #reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
            game_over = True
            reward -= COLLISION_PENALTY
            reward -= (self.frame_iteration - self.last_frame) * TIME_PENALTY # give penalty for time between collisions
            self.last_frame = self.frame_iteration

            #print("Reward after collision: ", reward)
            return reward, game_over, self.score

        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            reward += CATCH_BONUS
            reward -= (self.frame_iteration - self.last_frame) * TIME_PENALTY # give penalty for time between catches
            self.last_frame = self.frame_iteration

            #print("Reward after catch: ", reward)
            self._place_food()
        else:
            self.snake.pop()

        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)

        # 6. return game over and score
        #print("Reward: ", reward)
        return reward, game_over, self.score

    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # hits boundary
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        # hits itself
        if pt in self.snake[1:]:
            return True

        return False

    # detect if the snake is going against its body
    def detect_colision(self):
        reward = 0
        #print("---------- self.direction: ", self.direction)

        auxH = (HITS_ITSELF_GAP * self.h) + 1
        auxW = (HITS_ITSELF_GAP * self.w) + 1
        for pt in self.snake[1:]:
            #print("     self.head.x: ", self.head.x, " | self.head.y: ", self.head.y)
            #print("     pt.x: ", pt.x, " | pt.y: ", pt.y)
            if self.direction == Direction.UP and pt.x == self.head.x and pt.y < self.head.y:
                #print("DIRECTION: UP")
                #print("HEAD POS: x: ", self.head.x, " , y: ", self.head.y)
                #print("BODY POS: x: ", pt.x, " y: ", pt.y)
                if (self.head.y - pt.y) <= (HITS_ITSELF_GAP * self.h):
                    if (self.head.y - pt.y) < auxH:
                        auxH = self.head.y - pt.y
                        reward = -HITS_ITSELF_PENALTY * (HITS_ITSELF_GAP * self.h - (self.head.y - pt.y))
                        #print("Before Reward: ", reward)
            elif self.direction == Direction.DOWN and pt.x == self.head.x and pt.y > self.head.y:
                #print("DIRECTION: DOWN")
                #print("HEAD POS: x: ", self.head.x, " , y: ", self.head.y)
                #print("BODY POS: x: ", pt.x, " y: ", pt.y)
                if (pt.y - self.head.y) <= (HITS_ITSELF_GAP * self.h):
                    if (pt.y - self.head.y) < auxH:
                        auxH = pt.y - self.head.y
                        reward = -HITS_ITSELF_PENALTY * (HITS_ITSELF_GAP * self.h - (pt.y - self.head.y))
                        #print("Before Reward: ", reward)
            elif self.direction == Direction.RIGHT and pt.y == self.head.y and pt.x > self.head.x:
                #print("DIRECTION: RIGHT")
                #print("HEAD POS: x: ", self.head.x, " , y: ", self.head.y)
                #print("BODY POS: x: ", pt.x, " y: ", pt.y)
                if (pt.x - self.head.x) <= (HITS_ITSELF_GAP * self.w):
                    if (pt.x - self.head.x) < auxW:
                        auxW = pt.x - self.head.x
                        reward = -HITS_ITSELF_PENALTY * (HITS_ITSELF_GAP * self.w - (pt.x - self.head.x))
                        #print("Before Reward: ", reward)
            elif self.direction == Direction.LEFT and pt.y == self.head.y and pt.x < self.head.x:
                #print("DIRECTION: LEFT")
                #print("HEAD POS: x: ", self.head.x, " , y: ", self.head.y)
                #print("BODY POS: x: ", pt.x, " y: ", pt.y)
                if (self.head.x - pt.x) <= (HITS_ITSELF_GAP * self.w):
                    if (self.head.x - pt.x) < auxW:
                        auxW = self.head.x - pt.x
                        reward = -HITS_ITSELF_PENALTY * (HITS_ITSELF_GAP * self.w - (self.head.x - pt.x))
                        #print("Before Reward: ", reward)

        # print("detect_colision reward: ", reward)
        return reward

    def _update_ui(self):
        self.display.fill(BLACK)

        for pt in self.snake:
            if (pt != self.head):
                pygame.draw.rect(self.display, WHITE, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, (
            0.9 * (pt.x / 640) * 255, 0.9 * (pt.y / 480) * 255, 0.9 * (pt.x / 640) * (pt.y / 480) * 255),
                             pygame.Rect(pt.x + 1, pt.y + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2))
            pygame.draw.rect(self.display,
                             ((1 - (pt.x / 640)) * 255, (1 - (pt.y / 480)) * 255, (pt.x / 640) * (pt.y / 480) * 255),
                             pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))

        if (self.direction == Direction.UP):
            pygame.draw.rect(self.display, WHITE, pygame.Rect(self.head.x + 4, self.head.y + 4, 4, 4))
            pygame.draw.rect(self.display, WHITE, pygame.Rect(self.head.x + 12, self.head.y + 4, 4, 4))
            pygame.draw.rect(self.display, RED, pygame.Rect(self.head.x + 9, self.head.y - 5, 2, 6))
        elif (self.direction == Direction.DOWN):
            pygame.draw.rect(self.display, WHITE, pygame.Rect(self.head.x + 4, self.head.y + 12, 4, 4))
            pygame.draw.rect(self.display, WHITE, pygame.Rect(self.head.x + 12, self.head.y + 12, 4, 4))
            pygame.draw.rect(self.display, RED, pygame.Rect(self.head.x + 9, self.head.y + 19, 2, 6))
        elif (self.direction == Direction.RIGHT):
            pygame.draw.rect(self.display, WHITE, pygame.Rect(self.head.x + 12, self.head.y + 4, 4, 4))
            pygame.draw.rect(self.display, WHITE, pygame.Rect(self.head.x + 12, self.head.y + 12, 4, 4))
            pygame.draw.rect(self.display, RED, pygame.Rect(self.head.x + 19, self.head.y + 9, 6, 2))
        else:
            pygame.draw.rect(self.display, WHITE, pygame.Rect(self.head.x + 4, self.head.y + 4, 4, 4))
            pygame.draw.rect(self.display, WHITE, pygame.Rect(self.head.x + 4, self.head.y + 12, 4, 4))
            pygame.draw.rect(self.display, RED, pygame.Rect(self.head.x - 1, self.head.y + 9, 6, 2))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def _move(self, action):
        # [straight, right, left]

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx]  # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]  # right turn r -> d -> l -> u
        else:  # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]  # left turn r -> u -> l -> d

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)