import pygame
from settings import *


class Transition:
    def __init__(self, reset, player):
        self.display_surface = pygame.display.get_surface()
        self.reset = reset
        self.player = player

        # overlay
        self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.color = 255
        self.speed = -3
        self.shortened_speed = -8

    def play(self):
        self.color += self.speed
        if self.color <= 0:
            self.color = 0
            self.reset()
            self.player.status = 'right_idle'
            self.speed *= -1
        if self.color >= 255:
            self.color = 255
            self.player.sleep = False
            self.speed *= -1
        self.image.fill((self.color, self.color, self.color))
        self.display_surface.blit(self.image, (0, 0), special_flags = pygame.BLEND_RGBA_MULT)

    def shortened_play(self, boat_use):
        self.color += self.shortened_speed
        if self.color <= 0:
            self.color = 0
            self.player.status = 'up_idle'
            if boat_use == 1:
                self.player.pos.x = 10270
                self.player.pos.y = 2491
            elif boat_use == 2:
                self.player.pos.x = 8659
                self.player.pos.y = 3378
            self.player.rect.center = self.player.pos
            self.player.hitbox.center = self.player.pos
            self.shortened_speed *= -1
        if self.color >= 255:
            self.color = 255
            self.player.traveling = False
            self.shortened_speed *= -1
        self.image.fill((self.color, self.color, self.color))
        self.display_surface.blit(self.image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
