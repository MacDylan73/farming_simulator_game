import pygame
from settings import *
from pytmx.util_pygame import load_pygame
from utility import import_folder_dictionary, import_folder
from random import choice
from save_manager import SaveLoadSystem


class WaterTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['soil water']


class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['soil']


class SoilLayer:
    def __init__(self, all_sprites, collision_sprites):
        self.all_sprites = all_sprites
        self.collision_sprites = collision_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.plant_sprites = pygame.sprite.Group()


        # graphics
        self.soil_surfaces = import_folder_dictionary('../Graphics/soil/')
        self.water_surfaces = import_folder('../Graphics/soil_water', False)

        # methods
        self.create_soil_grid()
        self.create_hit_rects()

        # save
        self.save = SaveLoadSystem('.txt', '../Game/')

    def create_soil_grid(self):
        ground = pygame.image.load('../Graphics/map/testing5.png')
        h_tiles, v_tiles = ground.get_width() // TILE_SIZE, ground.get_height() // TILE_SIZE
        self.grid = [[[] for col in range(h_tiles)] for row in range(v_tiles)]
        for x, y, _ in load_pygame('../Data/map/prototype3.tmx').get_layer_by_name('Farmable').tiles():
            self.grid[y][x].append('F')

    def create_hit_rects(self):
        self.hit_rects = []
        for index_row, row in enumerate(self.grid):
            for index_column, cell in enumerate(row):
                if 'F' in cell:
                    x = index_column * TILE_SIZE
                    y = index_row * TILE_SIZE
                    rect = pygame.Rect((x, y), (TILE_SIZE, TILE_SIZE))
                    self.hit_rects.append(rect)

    def get_hit(self, point):
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE

                if 'F' in self.grid[y][x]:
                    # remove soil if already exists
                    if 'S' in self.grid[y][x]:
                        graphic_x = x * TILE_SIZE
                        graphic_y = y * TILE_SIZE
                        self.grid[y][x].remove('S')
                        self.create_soil_tiles()
                        if 'P' in self.grid[y][x]:
                            self.grid[y][x].remove('P')
                            for plant_sprite in self.plant_sprites.sprites():
                                if plant_sprite.rect.collidepoint((graphic_x, graphic_y)):
                                    plant_sprite.kill()
                        if 'W' in self.grid[y][x]:
                            self.grid[y][x].remove('W')
                            for water_sprite in self.water_sprites.sprites():
                                if water_sprite.rect.collidepoint((graphic_x, graphic_y)):
                                    water_sprite.kill()
                        if 'wheat' in self.grid[y][x]:
                            self.grid[y][x].remove('wheat')
                        elif 'tomato' in self.grid[y][x]:
                            self.grid[y][x].remove('tomato')
                        elif 'beetroot' in self.grid[y][x]:
                            self.grid[y][x].remove('beetroot')
                    # create soil
                    else:
                        self.grid[y][x].append('S')
                        self.create_soil_tiles()
                        if self.raining:
                            self.water_all()

    def water(self, target):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target):
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE
                if 'W' not in self.grid[y][x]:
                    self.grid[y][x].append('W')

                    pos = soil_sprite.rect.topleft
                    surf = choice(self.water_surfaces)
                    WaterTile(pos, surf, [self.all_sprites, self.water_sprites])

    def water_all(self):
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'S' in cell and 'W' not in cell:
                    cell.append('W')

                    x = index_col * TILE_SIZE
                    y = index_row * TILE_SIZE
                    WaterTile((x, y), choice(self.water_surfaces), [self.all_sprites, self.water_sprites])

    def remove_water(self):
        for sprite in self.water_sprites.sprites():
            sprite.kill()

        for row in self.grid:
            for cell in row:
                if 'W' in cell:
                    cell.remove('W')

    def check_watered(self, pos):
        x = pos[0] // TILE_SIZE
        y = pos[1] // TILE_SIZE
        cell = self.grid[y][x]
        is_watered = 'W' in cell
        return is_watered

    def plant_seed(self, target_pos, selected_seed):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE

                if 'P' not in self.grid[y][x]:
                    self.grid[y][x].append('P')
                    self.grid[y][x].append(selected_seed)

                    Plant(selected_seed, [self.all_sprites, self.plant_sprites, self.collision_sprites], soil_sprite, self.check_watered, 0)

    def create_soil_tiles(self):
        for sprite in self.soil_sprites:
            sprite.kill()
        for index_row, row in enumerate(self.grid):
            for index_column, cell in enumerate(row):
                if 'S' in cell:

                    # check status of surrounding tiles
                    # main
                    t = 'S' in self.grid[index_row - 1][index_column]
                    r = 'S' in row[index_column + 1]
                    l = 'S' in row[index_column - 1]
                    b = 'S' in self.grid[index_row + 1][index_column]

                    # diagonal
                    tl = 'S' in self.grid[index_row - 1][index_column - 1]
                    tr = 'S' in self.grid[index_row - 1][index_column + 1]
                    bl = 'S' in self.grid[index_row + 1][index_column - 1]
                    br = 'S' in self.grid[index_row + 1][index_column + 1]

                    # noting surrounding
                    if not any([t, r, l, b]): soil_type = 'o'

                    # one surrounding tile
                    if t and not any([r, l, b]): soil_type = 'b'
                    if r and not any([t, l, b]): soil_type = 'l'
                    if l and not any([r, t, b]): soil_type = 'r'
                    if b and not any([t, l, r]): soil_type = 't'

                    # two surrounding tiles
                    if l and t and not any([b, r]): soil_type = 'br'
                    if t and r and not any([b, l]): soil_type = 'bl'
                    if r and b and not any([t, l]): soil_type = 'tl'
                    if b and l and not any([t, r]): soil_type = 'tr'

                    if l and r and not any([b, t]): soil_type = 'lr'
                    if b and t and not any([l, r]): soil_type = 'tb'

                    # three surrounding tiles
                    if all([t, l, r]) and not b: soil_type = 'lrb'
                    if all([t, l, b]) and not r: soil_type = 'tbl'
                    if all([t, r, b]) and not l: soil_type = 'tbr'
                    if all([r, b, l]) and not t: soil_type = 'lrt'

                    # three and corners
                    if all([t, l, r, tr or tl]) and not b: soil_type = 'bm'
                    if all([t, l, b, tl or bl]) and not r: soil_type = 'rm'
                    if all([t, r, b, tr or br]) and not l: soil_type = 'lm'
                    if all([b, l, r, br or bl]) and not t: soil_type = 'tm'

                    # all surrounding tiles
                    if all([t, l, r, b]): soil_type = 'x'

                    SoilTile((index_column * TILE_SIZE, index_row * TILE_SIZE), self.soil_surfaces[soil_type], [self.all_sprites, self.soil_sprites])

    def update_plants(self):
        for plant in self.plant_sprites.sprites():
            plant.grow()

    def save_game(self):
        self.save.save_game_data([self.grid], ['soil_grid'])
        for plant in self.plant_sprites.sprites():
            plant.save_game()

    def load_game(self):
        self.grid = self.save.load_game_data(['soil_grid'], [0])
        if not self.grid:
            self.create_soil_grid()
        self.recreate_soil_and_water()

    def recreate_soil_and_water(self):
        self.create_soil_tiles()
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'W' in cell:
                    x = index_col * TILE_SIZE
                    y = index_row * TILE_SIZE
                    WaterTile((x, y), choice(self.water_surfaces), [self.all_sprites, self.water_sprites])
                if 'P' in cell:
                    x = index_col * TILE_SIZE
                    y = index_row * TILE_SIZE
                    for soil_sprite in self.soil_sprites.sprites():
                        if soil_sprite.rect.collidepoint((x, y)):
                            if 'wheat' in cell:
                                Plant('wheat', [self.all_sprites, self.plant_sprites, self.collision_sprites], soil_sprite, self.check_watered, 0)
                            elif 'tomato' in cell:
                                Plant('tomato', [self.all_sprites, self.plant_sprites, self.collision_sprites], soil_sprite, self.check_watered, 0)
                            elif 'beetroot' in cell:
                                Plant('beetroot', [self.all_sprites, self.plant_sprites, self.collision_sprites], soil_sprite, self.check_watered, 0)


class Plant(pygame.sprite.Sprite):
    def __init__(self, plant_type, groups, soil, check_watered, age):
        super(). __init__(groups)
        self.plant_type = plant_type
        self.soil = soil
        self.check_watered = check_watered
        self.frames = import_folder(f'../Graphics/fruit/{self.plant_type}', False)

        # growth
        self.age = age
        self.max_age = len(self.frames) - 1
        if self.age >= self.max_age:
            self.age = self.max_age
            self.harvestable = True
        self.grow_speed = GROW_SPEEDS[self.plant_type]
        self.harvestable = False

        # sprite
        self.image = self.frames[self.age]
        self.y_offset = PLANT_Y_OFFSETS[self.plant_type]
        self.rect = self.image.get_rect(midbottom = soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))
        self.z = LAYERS['ground plant']

    def grow(self):
        if self.check_watered(self.rect.center):
            self.age += self.grow_speed

            if int(self.age) > 0:
                self.z = LAYERS['main']
                self.hitbox = self.rect.copy().inflate((-26, -self.rect.height * 0.4))

            if self.age >= self.max_age:
                self.age = self.max_age
                self.harvestable = True

            self.image = self.frames[int(self.age)]
            self.rect = self.image.get_rect(midbottom = self.soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))
        elif not self.check_watered(self.rect.center) and self.age > 0:
            self.age -= self.grow_speed

    def save_game(self):
        save_data = [self.age, self.plant_type, self.rect]



