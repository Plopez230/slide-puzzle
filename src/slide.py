from search import Problem, best_first_graph_search
import pygame
from pygame.locals import *
import sys
import math
from copy import deepcopy
import random

class SlidePuzzleState:

    def __init__(self, rows=4, cols=4):
        self.rows = rows
        self.cols = cols
        self.init_puzzle()

    def init_puzzle(self):
        piece = 0
        self.puzzle = []
        for row in range(self.rows):
            puzzle_row = []
            for col in range(self.cols):
                puzzle_row.append(piece)
                piece += 1
            self.puzzle.append(puzzle_row)
        self.position = {'row': 0, 'col': 0}

    def shuffle(self):
        for _ in range(self.rows * int (self.cols * 2)):
            actions = self.actions()
            action = random.choice(actions)
            self.result(action)

    def actions(self):
        action_list = []
        if self.position['col'] > 0:
            action_list.append('right')
        if self.position['col'] < self.cols - 1:
            action_list.append('left')
        if self.position['row'] > 0:
            action_list.append('down')
        if self.position['row'] < self.rows - 1:
            action_list.append('up')
        return action_list

    def result(self, action):
        if not action in self.actions():
            return False
        new_position = {
            'row': self.position['row'],
            'col': self.position['col']
            }
        if action == 'up':
            new_position['row'] += 1
        if action == 'down':
            new_position['row'] -= 1
        if action == 'left':
            new_position['col'] += 1
        if action == 'right':
            new_position['col'] -= 1
        self.puzzle[self.position['row']][self.position['col']] = \
            self.puzzle[new_position['row']][new_position['col']]
        self.puzzle[new_position['row']][new_position['col']] = 0
        self.position['row'] = new_position['row']
        self.position['col'] = new_position['col']
        return True
    
    def h(self):
        distance = 0
        for row in range(self.rows):
            for col in range(self.cols):
                piece = self.puzzle[row][col]
                d = 0
                d += abs(int(piece / self.cols) - row)
                d += abs(piece % self.cols - col)
                distance += d
        return distance
    
    def __lt__(self, other):
        return self.__hash__() < other.__hash__()
    
    def __eq__(self, other):
        return self.__hash__() == other.__hash__() \
            and self.position['row'] == other.position['row'] \
            and self.position['col'] == other.position['col']

    def __hash__(self):
        hash = ""
        for row in range(self.rows):
            for col in range(self.cols):
                hash = f"{hash}{str(self.puzzle[row][col])}"
        hash = int(hash)
        return hash

class SlidePuzzleProblem(Problem):

    def __init__(self, initial, goal=None):
        super().__init__(initial, goal)

    def actions(self, state):
        return state.actions()

    def result(self, state, action):
        new_state = deepcopy(state)
        new_state.result(action)
        return new_state

    def goal_test(self, state):
        piece = 0
        for row in range(state.rows):
            for col in range(state.cols):
                if not state.puzzle[row][col] == piece:
                    return False
                piece += 1
        return True

    def path_cost(self, c, state1, action, state2):
        return c + 1

    def value(self, state):
        raise NotImplementedError

class Game:

    def __init__(self, image_path, rows=3, cols=4):
        self.image_path = image_path
        self.state = SlidePuzzleState(rows, cols)
        self.state.shuffle()
        self.image = pygame.image.load(self.image_path)
        self.height = self.image.get_height()
        self.width = self.image.get_width()
        pygame.display.set_mode((self.width, self.height), 0, 32)
        pygame.display.set_caption("Slide puzzle")
        self._clock = pygame.time.Clock()
        self.action_queue = []
        self.sleep = 0

    def solve(self):
        problem = SlidePuzzleProblem(self.state)
        pygame.display.set_caption("Slide puzzle SOLVING")
        result = best_first_graph_search(
            problem, 
            lambda n: n.path_cost + n.state.h()
        ).solution()
        pygame.display.set_caption("Slide puzzle")
        result.reverse()
        self.action_queue.extend(result)

    def handle_event(self, event):
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == K_UP:
                self.action_queue.append("up")
            if event.key == K_DOWN:
                self.action_queue.append("down")
            if event.key == K_LEFT:
                self.action_queue.append("left")
            if event.key == K_RIGHT:
                self.action_queue.append("right")
            if event.key == K_s:
                self.solve()
            if event.key == K_h:
                self.state.shuffle()

    def loop(self):
        while True:
            self._clock.tick(0)
            delta_time = self._clock.get_time()
            self.update(delta_time)
            pygame.display.get_surface().fill((0, 100, 150))
            self.draw(pygame.display.get_surface())
            pygame.display.update()
            for event in pygame.event.get():
                self.handle_event(event)

    def update(self, delta_time):
        self.sleep -= delta_time
        if self.sleep < 0:
            if self.action_queue:
                self.state.result(self.action_queue.pop())
                self.sleep = 100

    def draw(self, surface):
        size = (
            math.ceil(self.width / self.state.cols),
            math.ceil(self.height / self.state.rows),
        )
        for row in range(self.state.rows):
            for col in range(self.state.cols):
                piece = self.state.puzzle[row][col]
                if piece == 0:
                    continue
                position = (
                    col * self.width / self.state.cols,
                    row * self.height / self.state.rows
                    )
                origin = (
                    piece % self.state.cols * self.width / self.state.cols,
                    int(piece / self.state.cols) * self.height / self.state.rows
                )
                rect = pygame.Rect(origin, size)
                surface.blit(self.image, position, rect)

if __name__ == '__main__':
    game = Game(
        "./assets/angkor-wat.jpg",
        rows = 3, 
        cols = 5
        )
    game.loop()
