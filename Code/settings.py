from pygame import Vector2

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

TILE_SIZE = 64


LAYERS = {
    'water': 0,
    'ground': 1,
    'soil': 2,
    'soil water': 3,
    'rain floor': 4,
    'house bottom': 5,
    'ground plant': 6,
    'main': 7,
    'house top': 8,
    'fruit': 9,
    'rain drops': 10
}

PLAYER_TOOL_OFFSET = {
    'left': Vector2(-38, 30),
    'right': Vector2(38, 30),
    'up': Vector2(0, -20),
    'down': Vector2(0, 40)
}


APPLE_NODES = {
    'small': [(12, 46), (0, 0), (18, 9), (1, 24)],
    'large': [(14, 45), (12, 13), (36, 21), (48, 42), (57, 6), (63, 31)]
}


BUSH_NODES = {
    'blueberry': [(2, 12), (-6, 2), (-11, 9), (13, 2)]
}


GROW_SPEEDS = {
    'wheat': 1,
    'tomato': .8,
    'beetroot': 1.2
}


PLANT_EXP = {
    'wheat': 12,
    'tomato': 15,
    'beetroot': 9
}


PLANT_Y_OFFSETS = {
    'wheat': -11,
    'tomato': -15,
    'beetroot': -16
}


LEVEL_EXP = {
    1: 0,
    2: 10,
    3: 25,
    4: 50,
    5: 100,
    6: 200,
    7: 350,
    8: 500,
    9: 750,
    10: 1100,
    11: 1500,
}

SEED_PRICES = {
    'wheat': 7,
    'tomato': 10,
    'beetroot': 6
}


SELL_PRICES = {
    'wood log': 4,
    'apple': 2,
    'wheat': 10,
    'tomato': 12,
    'blueberry': 3,
    'beetroot': 7,
    'orange': 3,
    'grape': 5
}
