import pygame
import sys

from settings import *
from level import Level


class Game:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Farming Simulator")
        self.clock = pygame.time.Clock()

        self.level = Level()

    def run(self):
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.level.save_game()
                    pygame.quit()
                    sys.exit()
            dt = self.clock.tick() / 1000
            self.level.run(dt)
            pygame.display.update()


if __name__ == '__main__':
    game = Game()
    game.run()
