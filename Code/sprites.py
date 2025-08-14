import pygame

from settings import *
from random import choice, randint
from utility import Timer


class GenericSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surface, groups, z = LAYERS['main']):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft = pos)
        self.z = z
        self.hitbox = self.rect.copy().inflate((-self.rect.width * 0.2, -self.rect.height * 0.75))


class Interaction(GenericSprite):
    def __init__(self, pos, size, groups, name):
        surf = pygame.Surface(size)
        super().__init__(pos, surf, groups)
        self.name = name


class BarrierBlock(GenericSprite):
    def __init__(self, pos, surf, groups, width, height):
        super().__init__(pos, surf, groups)
        self.hitbox = pygame.Rect(pos, (width, height))


class WaterSprite(GenericSprite):
    def __init__(self, pos, frames, groups):
        # animation setup
        self.frames = frames
        self.frame_index = 0

        # sprite creation
        super().__init__(pos, self.frames[self.frame_index], groups, LAYERS['water'])

    def animate(self, dt):
        self.frame_index += 3 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        self.image = self.frames[int(self.frame_index)]

    def update(self, dt):
        self.animate(dt)


class Tree(GenericSprite):
    def __init__(self, pos, surface, groups, name, player, give_player, add_exp):
        super(). __init__(pos, surface, groups)

        # general
        self.name = name
        if 'large' in name:
            self.size = 'large'
        elif 'small' in name:
            self.size = 'small'
        self.max_health = 6 if 'large' in name else 3
        self.health = 6 if 'large' in name else 3
        self.alive = True
        self.stump_surf = pygame.image.load(f'../Graphics/stumps/{self.size}_stump.png').convert_alpha()
        self.player = player
        self.fruit = 'apple' if 'apple' in self.name else 'orange'

        self.give_player = give_player
        self.add_exp = add_exp

        # fruit
        self.fruit_surf = pygame.image.load(f'../Graphics/fruit/tree_{self.fruit}.png')
        self.fruit_pos = APPLE_NODES[self.size]
        self.fruit_sprites = pygame.sprite.Group()
        self.create_fruit()

        # respawn
        self.days_dead = 0
        self.respawn_time = 4 if self.size == 'large' else 2
        self.tree_image = surface
        self.tree_pos = pos

    def create_fruit(self):
        if self.alive:
            for pos in self.fruit_pos:
                if randint(0, 10) < 3:
                    GenericSprite(((pos[0] + self.rect.left), (pos[1] + self.rect.top)), self.fruit_surf, [self.fruit_sprites, self.groups()[0]], LAYERS['fruit'])

    def damage(self):
        self.health -= 1
        if len(self.fruit_sprites) > 0:
            rand_fruit = choice(self.fruit_sprites.sprites())
            Particle(rand_fruit.rect.topleft, rand_fruit.image, self.groups()[0], LAYERS['fruit'])
            self.give_player(self.fruit, 1)
            self.add_exp(1)
            rand_fruit.kill()

    def check_death(self):
        if self.health <= 0:
            Particle(self.rect.topleft, self.image, self.groups()[0], LAYERS['fruit'], 400)
            self.image = self.stump_surf
            self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
            self.hitbox = self.rect.copy().inflate((-2, -self.rect.height * 0.9))
            self.hitbox.bottom = self.rect.bottom - 40
            if self.player.hitbox.colliderect(self.hitbox):
                facing = self.player.status.split('_')[0]
                if facing == 'up':
                    self.player.hitbox.top = self.hitbox.bottom
                    self.player.rect.center = self.player.hitbox.center
                    self.player.pos.x = self.player.hitbox.centerx
                    self.player.pos.y = self.player.hitbox.centery
                elif facing == 'left':
                    self.player.hitbox.left = self.hitbox.right
                    self.player.rect.center = self.player.hitbox.center
                    self.player.pos.x = self.player.hitbox.centerx
                    self.player.pos.y = self.player.hitbox.centery
                elif facing == 'right':
                    self.player.hitbox.right = self.hitbox.left
                    self.player.rect.center = self.player.hitbox.center
                    self.player.pos.x = self.player.hitbox.centerx
                    self.player.pos.y = self.player.hitbox.centery

            self.alive = False
            if len(self.fruit_sprites.sprites()) > 0:
                for fruit in self.fruit_sprites.sprites():
                    fruit.kill()
            self.give_player('wood log', 1 if self.size == 'small' else 2)
            self.add_exp(2 if self.size == 'small' else 4)

    def reset(self):
        if self.alive and self.health < self.max_health:
            self.health += 1
        if not self.alive:
            self.days_dead += 1
            if self.days_dead >= self.respawn_time:
                self.days_dead = 0
                self.alive = True
                self.health = self.max_health
                self.image = self.tree_image
                self.rect = self.image.get_rect(topleft = self.tree_pos)
                self.hitbox = self.rect.copy().inflate((-self.rect.width * 0.2, -self.rect.height * 0.75))

                self.create_fruit()

    def update(self, dt):
        if self.alive:
            self.check_death()


class Rock(GenericSprite):
    def __init__(self, pos, surface, groups):
        super(). __init__(pos, surface, groups)


class Bush(GenericSprite):
    def __init__(self, pos, surface, groups, name, give_player, add_exp):
        super(). __init__(pos, surface, groups)

        # general
        self.give_player = give_player
        self.add_exp = add_exp
        self.name = name

        # fruit
        self.fruit_image = pygame.image.load(f'../Graphics/fruit/bush_{self.name}.png')
        self.fruit_pos = BUSH_NODES['blueberry']
        self.fruit_sprites = pygame.sprite.Group()
        self.create_fruit()

    def create_fruit(self):
        for pos in self.fruit_pos:
            if randint(0, 10) < 3:
                GenericSprite(((pos[0] + self.rect.left), (pos[1] + self.rect.top)), self.fruit_image,
                              [self.fruit_sprites, self.groups()[0]], LAYERS['fruit'])

    def damage(self):
        if len(self.fruit_sprites) > 0:
            picked_fruit = choice(self.fruit_sprites.sprites())
            Particle(picked_fruit.rect.topleft, picked_fruit.image, self.groups()[0], LAYERS['fruit'])
            self.give_player(self.name, 1)
            self.add_exp(1)
            picked_fruit.kill()


class Particle(GenericSprite):
    def __init__(self, pos, surf, groups, z, duration = 200):
        super().__init__(pos, surf, groups, z)
        self.start_time = pygame.time.get_ticks()
        self.duration = duration

        mask_surf = pygame.mask.from_surface(self.image)
        new_surf = mask_surf.to_surface()
        new_surf.set_colorkey((0, 0, 0))
        self.image = new_surf

    def update(self, dt):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.duration:
            self.kill()


