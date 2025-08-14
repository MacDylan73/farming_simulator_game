import pygame
import sys

from settings import *
from utility import *
from save_manager import SaveLoadSystem


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, collision_sprites, tree_sprites, bush_sprites, interaction_sprites, soil_layer, save_func):
        super().__init__(group)

        # import player graphics and get status and animation index variables
        self.import_player_graphics()
        self.status = 'down_idle'
        self.animation_index = 0

        # player image
        self.image = self.animations[self.status][self.animation_index]
        self.rect = self.image.get_rect(center = pos)
        self.z = LAYERS['main']

        # movement vectors
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200

        # collision attributes
        self.hitbox = self.rect.inflate((-116, -80))
        self.collision_sprites = collision_sprites

        # timers
        self.timers = {
            'tool use': Timer(1000, self.use_tool),
            'tool switch': Timer(200),
            'seed use': Timer(200, self.use_seed),
            'seed switch': Timer(200),
            'inventory toggle': Timer(165),
            'gather': Timer(200, self.gather)
        }

        # tool
        self.tools = ['hoe', 'axe', 'water']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]

        # seeds
        self.seeds = ['wheat', 'tomato', 'corn', 'eggplant', 'cabbage', 'lettuce', 'cucumber', 'pumpkin', 'cauliflower',
                      'beetroot', 'arracacha', 'tulip', 'star flower']
        self.unlocked_seeds = ['wheat', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.unlocked_seeds[self.seed_index]

        # nature
        self.tree_sprites = tree_sprites
        self.bush_sprites = bush_sprites

        # inventory
        self.inventory_open = False
        self.inventory_dict = {
            'wheat_seeds': 5,
            'tomato_seeds': 5,
            'beetroot_seeds': 0,
            'wood log': 10,
            'wheat': 2,
            'tomato': 2,
            'beetroot': 0,
            'apple': 2,
            'orange': 0,
            'blueberry': 0,
            'grape': 0,
        }
        self.inventory_list = []

        # interaction
        self.interaction_sprites = interaction_sprites
        self.sleep = False
        self.traveling = False
        self.boat_used = 1
        self.soil_layer = soil_layer
        self.trade_menu_toggle = False
        self.quest_toggle = False

        # exp/money
        self.exp = 0
        self.money = 20

        # save
        self.save = SaveLoadSystem('.txt', '../Game/')
        self.save_func = save_func

    def import_player_graphics(self):
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'up_idle': [], 'down_idle': [], 'left_idle': [], 'right_idle': [],
                           'up_hoe': [], 'down_hoe': [], 'left_hoe': [], 'right_hoe': [],
                           'up_axe': [], 'down_axe': [], 'left_axe': [], 'right_axe': [],
                           'up_water': [], 'down_water': [], 'left_water': [], 'right_water': [],}

        for animation in self.animations.keys():
            full_path = '../graphics/character/' + animation
            self.animations[animation] = import_folder(full_path)

    def animate_player(self, dt):
        self.animation_index += 8 * dt
        if self.animation_index > len(self.animations[self.status]):
            self.animation_index = 0
        try:
            self.image = self.animations[self.status][int(self.animation_index)]
        except:
            self.save_func()
            print('A bug has occured, game session saved and closed, please restart')
            pygame.quit()
            sys.exit()

    def get_status(self):
        # if player is idle
        if self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_idle'

        # if player is using a tool
        if self.timers['tool use'].active:
            self.status = self.status.split('_')[0] + '_' + self.selected_tool

    def input(self):
        keys = pygame.key.get_pressed()
        if not self.sleep and not self.traveling:
            if not self.timers['tool use'].active:
                # movement
                if not self.inventory_open and not self.trade_menu_toggle:
                    if keys[pygame.K_w]:
                        self.direction.y = -1
                        self.status = 'up'
                    elif keys[pygame.K_s]:
                        self.direction.y = 1
                        self.status = 'down'
                    else:
                        self.direction.y = 0

                    if keys[pygame.K_a]:
                        self.direction.x = -1
                        self.status = 'left'
                    elif keys[pygame.K_d]:
                        self.direction.x = 1
                        self.status = 'right'
                    else:
                        self.direction.x = 0

                # tool use
                if keys[pygame.K_r] and not self.inventory_open and not self.trade_menu_toggle:
                    self.timers['tool use'].activate()
                    self.direction = pygame.math.Vector2()
                    self.animation_index = 0

                # change tools
                if keys[pygame.K_CAPSLOCK] and not self.timers['tool switch'].active:
                    self.timers['tool switch'].activate()
                    self.tool_index += 1
                    if self.tool_index >= len(self.tools):
                        self.tool_index = 0
                    self.selected_tool = self.tools[self.tool_index]

                # inventory
                if not self.timers['seed use'].active and not self.timers['inventory toggle'].active and not self.trade_menu_toggle:
                    if keys[pygame.K_e]:
                        self.timers['inventory toggle'].activate()
                        if self.inventory_open:
                            self.inventory_open = False
                        elif not self.inventory_open:
                            self.inventory_open = True
                            self.direction = pygame.math.Vector2()

                # gathering
                if not self.timers['seed use'].active and not self.inventory_open and not self.trade_menu_toggle:
                    if keys[pygame.K_g] and not self.timers['gather'].active:
                        self.timers['gather'].activate()

            if not self.timers['seed use'].active:

                # seed use
                if keys[pygame.K_f] and not self.inventory_open and not self.trade_menu_toggle:
                    self.timers['seed use'].activate()

                # seed switch
                if keys[pygame.K_TAB] and not self.timers['seed switch'].active:
                    self.timers['seed switch'].activate()
                    self.seed_index += 1
                    if self.seed_index >= len(self.unlocked_seeds):
                        self.seed_index = 0
                    self.selected_seed = self.unlocked_seeds[self.seed_index]

            # interaction
            if keys[pygame.K_t]:
                collided_interaction_sprite = pygame.sprite.spritecollide(self, self.interaction_sprites, False)
                if collided_interaction_sprite:
                    if collided_interaction_sprite[0].name == 'Bed':
                        self.status = 'left_idle'
                        self.sleep = True
                    if collided_interaction_sprite[0].name == 'Boat1':
                        self.status = 'down_idle'
                        self.boat_used = 1
                        self.traveling = True
                        self.direction = pygame.math.Vector2()
                    if collided_interaction_sprite[0].name == 'Boat2':
                        self.status = 'down_idle'
                        self.boat_used = 2
                        self.traveling = True
                        self.direction = pygame.math.Vector2()
                    if collided_interaction_sprite[0].name == 'Trader' and not self.timers['inventory toggle'].active:
                        self.timers['inventory toggle'].activate()
                        if not self.trade_menu_toggle:
                            self.trade_menu_toggle = True
                            self.direction = pygame.math.Vector2()
                        elif self.trade_menu_toggle:
                            self.trade_menu_toggle = False
                    if collided_interaction_sprite[0].name == 'Quest' and not self.timers['inventory toggle'].active:
                        self.timers['inventory toggle'].activate()
                        if not self.quest_toggle:
                            self.quest_toggle = True
                            self.direction = pygame.math.Vector2()
                        elif self.quest_toggle:
                            self.quest_toggle = False

    def move(self, dt):
        # normalize direction vector
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        # horizontal movement
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')

        # vertical movement
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        if self.direction.x > 0:
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0:
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx
                    if direction == 'vertical':
                        if self.direction.y > 0:
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0:
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery

    def use_tool(self):
        if self.selected_tool == "hoe":
            self.soil_layer.get_hit(self.target_pos)
        if self.selected_tool == "axe":
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()
        if self.selected_tool == "water":
            self.soil_layer.water(self.target_pos)

    def use_seed(self):
        if self.inventory_dict[f'{self.selected_seed}_seeds'] > 0:
            for soil_sprite in self.soil_layer.soil_sprites.sprites():
                if soil_sprite.rect.collidepoint(self.target_pos):
                    x = soil_sprite.rect.x // TILE_SIZE
                    y = soil_sprite.rect.y // TILE_SIZE

                    if 'P' not in self.soil_layer.grid[y][x] and 'S' in self.soil_layer.grid[y][x]:
                        self.soil_layer.plant_seed(self.target_pos, self.selected_seed)
                        self.inventory_dict[f'{self.selected_seed}_seeds'] -= 1

    def gather(self):
        for bush in self.bush_sprites.sprites():
            if bush.rect.collidepoint(self.target_pos):
                bush.damage()

    def get_target_pos(self):
        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def update_inventory(self):
        # add item if not already in
        for key in self.inventory_dict.keys():
            if self.inventory_dict[key] > 0:
                if key not in self.inventory_list:
                    self.inventory_list.append(key)
        # take item out if player has 0
        for item in self.inventory_list:
            if self.inventory_dict[item] <= 0:
                self.inventory_list.remove(item)

    def update(self, dt):
        self.input()
        self.get_status()
        self.update_timers()
        self.update_inventory()
        self.get_target_pos()
        self.move(dt)
        self.animate_player(dt)

    def save_game(self):
        self.save.save_game_data([self.hitbox.center], ['player_pos'])
        self.save.save_game_data([self.money], ['player_money'])
        self.save.save_game_data([self.exp], ['player_exp'])
        self.save.save_game_data([self.inventory_dict], ['player_inventory'])

    def load_game(self):
        self.hitbox.center = self.save.load_game_data(['player_pos'], [(6331, 1304)])
        self.money = self.save.load_game_data(['player_money'], [20])
        self.exp = self.save.load_game_data(['player_exp'], [0])
        self.inventory_dict = self.save.load_game_data(['player_inventory'], [{
            'wheat_seeds': 5,
            'tomato_seeds': 5,
            'beetroot_seeds': 0,
            'wood log': 10,
            'wheat': 2,
            'tomato': 2,
            'beetroot': 0,
            'apple': 2,
            'orange': 0,
            'blueberry': 0,
            'grape': 0
        }])
        self.rect.center = self.hitbox.center
        self.pos.x = self.hitbox.centerx
        self.pos.y = self.hitbox.centery

