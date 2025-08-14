import pygame
from pytmx.util_pygame import load_pygame

from settings import *
from player import Player
from overlay import Overlay
from sprites import GenericSprite, WaterSprite, Tree, Rock, Bush, BarrierBlock, Interaction, Particle
from utility import *
from transition import Transition
from soil import SoilLayer
from rain import Rain, Sky
from random import randint
from save_manager import SaveLoadSystem


class Level:
    def __init__(self):
        # get display surface from main
        self.display_surface = pygame.display.get_surface()

        # make sprite groups
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.bush_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()

        # soil, interaction, reset
        self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)
        self.setup()
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset_day, self.player)

        # sky
        self.rain = Rain(self.all_sprites)
        self.raining = False
        self.soil_layer.raining = self.raining
        self.sky = Sky()

        # save
        self.save = SaveLoadSystem('.txt', '../Game/')
        self.variables_to_save = [self.raining]
        self.load_game()

    def setup(self):
        path = '../Data/map/prototype3.tmx'
        map_data = load_pygame(path)

        # water
        water_frames = import_folder('../Graphics/water animation')
        for x, y, surf in map_data.get_layer_by_name('Water').tiles():
            WaterSprite((x * TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites)

        # map image
        GenericSprite((0, 0), pygame.image.load('../Graphics/map/testing5.png').convert_alpha(), self.all_sprites, LAYERS['ground'])

        # collision tiles
        for obj in map_data.get_layer_by_name('Collision'):
            BarrierBlock((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites, obj.width, obj.height)

        # player
        for obj in map_data.get_layer_by_name('Player'):
            if obj.name == 'Player':
                self.player = Player(
                    pos = (obj.x, obj.y),
                    group = self.all_sprites,
                    collision_sprites = self.collision_sprites,
                    tree_sprites = self.tree_sprites,
                    bush_sprites = self.bush_sprites,
                    interaction_sprites = self.interaction_sprites,
                    soil_layer = self.soil_layer,
                    save_func = self.save_game
                )
            if obj.name == 'Bed':
                Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)
            if 'Boat' in obj.name:
                Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)
            if obj.name == 'Trader':
                Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)
            if obj.name == 'Quest':
                Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)

        # for obj in map_data.get_layer_by_name('Level Barriers')


        # pathways and lower object layer
        bottom_objects = map_data.get_layer_by_name('Always Bottom')
        for obj in bottom_objects:
            GenericSprite((obj.x, obj.y), obj.image, self.all_sprites, LAYERS['soil'])

        # house floor
        for x, y, surf in map_data.get_layer_by_name('house bottom').tiles():
            GenericSprite((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])

        for x, y, surf in map_data.get_layer_by_name('mats').tiles():
            GenericSprite((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])

        # house walls
        for x, y, surf in map_data.get_layer_by_name('house walls').tiles():
            GenericSprite((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['main'])

        # house floor furniture
        for x, y, surf in map_data.get_layer_by_name('house furnature bottom').tiles():
            GenericSprite((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['main'])

        # house wall furniture
        for x, y, surf in map_data.get_layer_by_name('house furnature top').tiles():
            GenericSprite((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['house top'])

        # trader island objects
        trader_layer = map_data.get_layer_by_name('Trader Objects')
        for obj in trader_layer:
            GenericSprite((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites], LAYERS['main'])

        # trees bushes and rocks
        for obj in map_data.get_layer_by_name('Trees'):
            Tree((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites, self.tree_sprites], obj.name, self.player, self.give_player, self.add_exp)

        for obj in map_data.get_layer_by_name('Bushes'):
            Bush((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites, self.bush_sprites], obj.name, self.give_player, self.add_exp)

        for obj in map_data.get_layer_by_name('Rocks'):
            Rock((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])

    def give_player(self, item, number):
        self.player.inventory_dict[item] += number

    def add_exp(self, amount):
        self.player.exp += amount

    def plant_harvesting(self):
        if self.soil_layer.plant_sprites:
            for plant in self.soil_layer.plant_sprites.sprites():
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    self.give_player(plant.plant_type, 1)
                    self.add_exp(PLANT_EXP[plant.plant_type])
                    plant.kill()
                    Particle(plant.rect.topleft, plant.image, self.all_sprites, LAYERS['main'])
                    x = plant.rect.centerx // TILE_SIZE
                    y = plant.rect.centery // TILE_SIZE
                    self.soil_layer.grid[y][x].remove('P')
                    if 'tomato' in self.soil_layer.grid[y][x]:
                        self.soil_layer.grid[y][x].remove('tomato')
                    if 'wheat' in self.soil_layer.grid[y][x]:
                        self.soil_layer.grid[y][x].remove('wheat')
                    if 'beetroot' in self.soil_layer.grid[y][x]:
                        self.soil_layer.grid[y][x].remove('beetroot')

    def reset_day(self):
        # plants
        self.soil_layer.update_plants()

        # apples/trees
        for tree in self.tree_sprites.sprites():
            tree.reset()
            for apple in tree.fruit_sprites.sprites():
                apple.kill()
            tree.create_fruit()

        # bushes
        for bush in self.bush_sprites:
            for fruit in bush.fruit_sprites.sprites():
                fruit.kill()
            bush.create_fruit()

        # soil
        self.soil_layer.remove_water()

        # randomize rain
        self.raining = randint(0, 10) > 3
        self.soil_layer.raining = self.raining
        if self.raining:
            self.soil_layer.water_all

        # reset day cycle
        self.sky.start_color = [255, 255, 255]
        self.save_game()

    def run(self, dt):
        self.display_surface.fill('#000000')
        self.all_sprites.custom_draw(self.player)
        self.all_sprites.update(dt)
        self.plant_harvesting()

        self.overlay.update_overlay()

        # rain
        if self.raining:
            self.rain.update(self.player)

        # day/night cycle
        self.sky.display(dt)

        # traveling
        if self.player.traveling:
            self.transition.shortened_play(self.player.boat_used)

        # sleeping
        if self.player.sleep:
            self.transition.play()

    def save_game(self):
        # save necessary data from level.py
        self.save.save_game_data([self.raining], ['rain'])
        # save data from soil
        self.soil_layer.save_game()
        self.player.save_game()

    def load_game(self):
        # level
        self.raining = self.save.load_game_data(['rain'], [False])
        self.soil_layer.water_all()
        self.soil_layer.raining = self.raining

        # soil
        self.soil_layer.load_game()
        self.player.load_game()


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - (SCREEN_WIDTH / 2)
        self.offset.y = player.rect.centery - (SCREEN_HEIGHT / 2)

        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key= lambda sprite: sprite.rect.centery):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset

                    self.display_surface.blit(sprite.image, offset_rect)

                    # debug screen
                    # if sprite == player:
                    #     pygame.draw.rect(self.display_surface, 'red', offset_rect, 5)
                    #     hitbox_rect = player.hitbox.copy()
                    #     hitbox_rect.center = offset_rect.center
                    #     pygame.draw.rect(self.display_surface, 'green', hitbox_rect, 5)
                    #     target_pos = offset_rect.center + PLAYER_TOOL_OFFSET[player.status.split('_')[0]]
                    #     pygame.draw.circle(self.display_surface, 'blue', target_pos, 5)
                    # if sprite != player and hasattr(sprite, 'hitbox'):
                    #     pygame.draw.rect(self.display_surface, '#ffff00', sprite.hitbox, 5)





