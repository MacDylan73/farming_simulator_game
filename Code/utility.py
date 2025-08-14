import pygame
from os import walk


def import_folder(path, scale = True):
    surface_list = []

    for _,  __, animation_list in walk(path):
        for animation in animation_list:
            # obtains image
            full_path = path + '/' + animation
            img_surf = pygame.image.load(full_path).convert_alpha()

            # scaling each image
            if scale:
                img_rect = img_surf.get_rect()
                img_surf = pygame.transform.scale(img_surf, (img_rect.width * 3, img_rect.height * 3))
            # add to list
            surface_list.append(img_surf)
    return surface_list


def import_folder_dictionary(path):
    surface_dict = {}
    for _, _, img_files in walk(path):
        for img in img_files:
            full_path = path + '/' + img
            img_surf = pygame.image.load(full_path).convert_alpha()
            surface_dict[img.split('.')[0]] = img_surf

    return surface_dict


class Timer:
    def __init__(self, duration, function = None):
        self.duration = duration
        self.function = function
        self.active = False
        self.start_time = 0

    def activate(self):
        self.active = True
        self.start_time = pygame.time.get_ticks()

    def deactivate(self):
        self.active = False
        # self.start_time = 0

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.duration:
            if self.function and self.start_time != 0:
                self.function()
                self.start_time = 0
            self.deactivate()

