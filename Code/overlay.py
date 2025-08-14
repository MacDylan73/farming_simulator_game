import pygame

from settings import *
from utility import Timer


class Overlay:
    def __init__(self, player):
        self.display_surface = pygame.display.get_surface()
        self.player = player

        self.inventory_font = pygame.font.Font('../Font/LycheeSoda.ttf', 32, bold=True)
        self.level_font = pygame.font.SysFont('../Font/LycheeSoda.ttf', 38, bold=True)
        self.trade_font = pygame.font.SysFont('../Font/LycheeSoda.ttf', 44)
        self.trade_title_font = pygame.font.SysFont('../Font/LycheeSoda.ttf', 50, bold=True)

        # import graphics
        file_path = '../graphics/overlay/'
        self.tool_surfaces = {tool: pygame.transform.scale(pygame.image.load(f'{file_path}{tool}.png').convert_alpha(), (64, 64)) for tool in player.tools}
        self.seed_surfaces = {seed: pygame.transform.scale(pygame.image.load(f'{file_path}{seed}.png').convert_alpha(), (64, 64)) for seed in player.unlocked_seeds}

        self.item_surfaces = {}
        for key in self.player.inventory_dict.keys():
            self.item_surfaces.update({key: pygame.image.load(f'../Graphics/inventory icons/{key}.png')})

        # inventory attributes
        self.bg_rect = pygame.Rect((260, 80), (835, 580))
        self.tlc = pygame.Rect((300, 120), (80, 80))
        self.trc = pygame.Rect((975, 120), (80, 80))
        self.blc = pygame.Rect((300, 345), (80, 80))
        self.brc = pygame.Rect((975, 345), (80, 80))
        self.grid = [
            pygame.Rect((375, 120), (80, 80)), pygame.Rect((450, 120), (80, 80)), pygame.Rect((525, 120), (80, 80)),
            pygame.Rect((600, 120), (80, 80)), pygame.Rect((675, 120), (80, 80)), pygame.Rect((750, 120), (80, 80)),
            pygame.Rect((825, 120), (80, 80)), pygame.Rect((900, 120), (80, 80)), pygame.Rect((300, 195), (80, 80)),
            pygame.Rect((375, 195), (80, 80)), pygame.Rect((450, 195), (80, 80)), pygame.Rect((525, 195), (80, 80)),
            pygame.Rect((600, 195), (80, 80)), pygame.Rect((675, 195), (80, 80)), pygame.Rect((750, 195), (80, 80)),
            pygame.Rect((825, 195), (80, 80)), pygame.Rect((900, 195), (80, 80)), pygame.Rect((975, 195), (80, 80)),
            pygame.Rect((300, 270), (80, 80)), pygame.Rect((375, 270), (80, 80)), pygame.Rect((450, 270), (80, 80)),
            pygame.Rect((525, 270), (80, 80)), pygame.Rect((600, 270), (80, 80)), pygame.Rect((675, 270), (80, 80)),
            pygame.Rect((750, 270), (80, 80)), pygame.Rect((825, 270), (80, 80)), pygame.Rect((900, 270), (80, 80)),
            pygame.Rect((975, 270), (80, 80)), pygame.Rect((375, 345), (80, 80)), pygame.Rect((450, 345), (80, 80)),
            pygame.Rect((525, 345), (80, 80)), pygame.Rect((600, 345), (80, 80)), pygame.Rect((675, 345), (80, 80)),
            pygame.Rect((750, 345), (80, 80)), pygame.Rect((825, 345), (80, 80)), pygame.Rect((900, 345), (80, 80)),
            ]

        self.icon_positions = [
            (305, 125), (380, 125), (455, 125), (530, 125), (605, 125), (680, 125), (755, 125), (830, 125), (905, 125),
            (980, 125)
        ]
        self.value_positions = [
            (375, 195), (450, 195), (525, 195), (600, 195), (675, 195), (750, 195), (825, 195), (900, 195), (975, 195),
            (1050, 195)
        ]

        # trader attributes
        self.trade_ui_timer = Timer(170)
        self.internal_timer = Timer(150)
        self.sell_indication_timer = Timer(3000)
        self.buy_indication_timer = Timer(3000)
        self.purchase_lock_timer = Timer(3000)
        self.buy_toggle = False
        self.sell_index = 0
        self.buy_index = 0
        self.buyable_items = []
        self.sellable_items = ['wood log', 'apple', 'wheat', 'tomato', 'blueberry', 'beetroot', 'orange', 'grape']
        for value in self.seed_surfaces.keys(): self.buyable_items.append(value)
        self.divide_rect = pygame.Rect(self.bg_rect.left, (self.bg_rect.centery - 1), self.bg_rect.width, 3)
        self.buy_bg = pygame.Rect((self.bg_rect.topleft), (self.bg_rect.width, (self.bg_rect.centery - self.bg_rect.top)))
        self.sell_bg = pygame.Rect((self.divide_rect.bottomleft), (self.bg_rect.width, (self.bg_rect.bottom - self.bg_rect.centery)))
        self.sell_text = self.trade_title_font.render('Sell:', False, '#353738')
        self.buy_text_rect = self.sell_text.get_rect(topleft=((self.bg_rect.left + 6), (self.divide_rect.bottom + 5)))
        self.buy_text = self.trade_title_font.render('Buy:', False, '#353738')
        self.sell_text_rect = self.buy_text.get_rect(topleft=((self.bg_rect.left + 6), (self.bg_rect.top + 5)))
        self.buying_item_pos = ((self.bg_rect.centerx - 32, (self.divide_rect.bottom + self.bg_rect.bottom) / 2))

        self.money_particle_pos = (pygame.Rect(10, 70, 100, 32).centerx, pygame.Rect(10, 70, 100, 32).centery + 40)
        self.bal_change_text = 0

    def make_overlay(self):
        # tool
        tool_overlay_pos = (SCREEN_WIDTH - (SCREEN_WIDTH - 20), (SCREEN_HEIGHT - 100))
        tool_surf = self.tool_surfaces[self.player.selected_tool]
        self.display_surface.blit(tool_surf, tool_overlay_pos)

        # seed
        seed_overlay_pos = (SCREEN_WIDTH - (SCREEN_WIDTH - 60), (SCREEN_HEIGHT - 70))
        seed_surf = self.seed_surfaces[self.player.selected_seed]
        self.display_surface.blit(seed_surf, seed_overlay_pos)

        # inventory
        if self.player.inventory_open:
            # inventory background
            pygame.draw.rect(self.display_surface, '#818b83', self.bg_rect, border_radius=15)
            pygame.draw.rect(self.display_surface, '#f3f4e7', self.bg_rect, 3, border_radius=15)

            # corner slots
            pygame.draw.rect(self.display_surface, '#c1c8b9', self.tlc, border_top_left_radius=15)
            pygame.draw.rect(self.display_surface, '#dce0d2', self.tlc, 5, border_top_left_radius=15)

            pygame.draw.rect(self.display_surface, '#c1c8b9', self.trc, border_top_right_radius=15)
            pygame.draw.rect(self.display_surface, '#dce0d2', self.trc, 5, border_top_right_radius=15)

            pygame.draw.rect(self.display_surface, '#c1c8b9', self.blc, border_bottom_left_radius=15)
            pygame.draw.rect(self.display_surface, '#dce0d2', self.blc, 5, border_bottom_left_radius=15)

            pygame.draw.rect(self.display_surface, '#c1c8b9', self.brc, border_bottom_right_radius=15)
            pygame.draw.rect(self.display_surface, '#dce0d2', self.brc, 5, border_bottom_right_radius=15)

            # central slots
            for rect in self.grid:
                pygame.draw.rect(self.display_surface, '#c1c8b9', rect)
                pygame.draw.rect(self.display_surface, '#dce0d2', rect, 5)

            # items
            index = 0
            for item in self.player.inventory_list:
                self.display_surface.blit(self.item_surfaces[item], self.icon_positions[index])

                # item values
                value = self.inventory_font.render(str(self.player.inventory_dict[item]), False, '#353738')
                value_rect = value.get_rect(bottomright = self.value_positions[index])
                self.display_surface.blit(value, value_rect)

                index += 1

        # money
        money_rect = pygame.Rect(10, 70, 100, 32)
        pygame.draw.rect(self.display_surface, '#c1c8b9', money_rect, border_radius=10)
        pygame.draw.rect(self.display_surface, '#f3f4e7', (10, 70, 100, 32), 3, border_radius=10)
        money_text = self.inventory_font.render(f'${str(self.player.money)}', False, '#353738')
        money_text_rect = money_text.get_rect(center = money_rect.center)
        self.display_surface.blit(money_text, money_text_rect)

    def get_level(self):
        self.exp = self.player.exp
        if 0 <= self.exp < 10:
            self.level = 1
        elif 10 <= self.exp < 25:
            self.level = 2
        elif 25 <= self.exp < 50:
            self.level = 3
        elif 50 <= self.exp < 100:
            self.level = 4
        elif 100 <= self.exp < 200:
            self.level = 5
            if 'beetroot' not in self.player.unlocked_seeds: self.player.unlocked_seeds.append('beetroot')
            file_path = '../graphics/overlay/'
            self.seed_surfaces = {
                seed: pygame.transform.scale(pygame.image.load(f'{file_path}{seed}.png').convert_alpha(), (64, 64)) for
                seed in self.player.unlocked_seeds}
            for value in self.seed_surfaces.keys():
                if value not in self.buyable_items:
                    self.buyable_items.append(value)
        elif 200 <= self.exp < 350:
            self.level = 6
        elif 350 <= self.exp < 500:
            self.level = 7
        elif 500 <= self.exp < 750:
            self.level = 8
        elif 750 <= self.exp < 1100:
            self.level = 9
        elif 1100 <= self.exp < 1500:
            self.level = 10

        self.to_level_exp = LEVEL_EXP[self.level + 1] - LEVEL_EXP[self.level]
        self.lvl_exp_progress = self.exp - LEVEL_EXP[self.level]

        self.bar_exp = self.lvl_exp_progress / self.to_level_exp

    def exp_bar(self):
        self.get_level()
        # exp
        pygame.draw.rect(self.display_surface, '#c1c8b9', (50, 20, 320, 30), border_radius=10)
        pygame.draw.rect(self.display_surface, '#92b6d4', (50, 20, (320 * self.bar_exp), 30), border_radius=10)
        pygame.draw.rect(self.display_surface, "#f3f4e7", (50, 20, 320, 30), 3, 10)

        pygame.draw.rect(self.display_surface, '#92b6d4', (10, 10, 50, 50), border_radius=10)
        pygame.draw.rect(self.display_surface, '#f3f4e7', (10, 10, 50, 50), 3, 10)
        level_text = self.level_font.render(str(self.level), True, '#353738')
        level_text_rect = level_text.get_rect(center = (35, 35))
        self.display_surface.blit(level_text, level_text_rect)

    def trade_ui(self):
        # background
        pygame.draw.rect(self.display_surface, '#818b83', self.bg_rect, border_radius=15)
        if self.buy_toggle:
            pygame.draw.rect(self.display_surface, '#c1c8b9', self.buy_bg, border_top_left_radius=15,
                             border_top_right_radius=15)
            you_have_text_pos = (self.bg_rect.centerx, self.bg_rect.bottom - 20)
            if self.buyable_items[self.buy_index] == 'beetroot' or 'wheat' or 'tomato':
                get_from_inv_text = f"{self.buyable_items[self.buy_index]}_seeds"
            else:
                get_from_inv_text = self.buyable_items[self.buy_index]
            you_have_text = self.trade_font.render(
                f'you have: {self.player.inventory_dict[get_from_inv_text]}', False, '#353738')
            you_have_text_rect = you_have_text.get_rect(center=you_have_text_pos)
        elif not self.buy_toggle:
            pygame.draw.rect(self.display_surface, '#c1c8b9', self.sell_bg, border_bottom_left_radius=15,
                             border_bottom_right_radius=15)
            you_have_text_pos = (self.bg_rect.centerx, self.divide_rect.top - 20)
            you_have_text = self.trade_font.render(
                f'you have: {self.player.inventory_dict[self.sellable_items[self.sell_index]]}', False, '#353738')
            you_have_text_rect = you_have_text.get_rect(center=you_have_text_pos)
        pygame.draw.rect(self.display_surface, "#f3f4e7", self.divide_rect)
        pygame.draw.rect(self.display_surface, '#f3f4e7', self.bg_rect, 3, border_radius=15)

        # content
        self.display_surface.blit(self.sell_text, self.sell_text_rect)
        self.display_surface.blit(self.buy_text, self.buy_text_rect)

        buy_icon = pygame.transform.scale(self.seed_surfaces[self.buyable_items[self.buy_index]], (128, 128))
        buy_icon_rect = buy_icon.get_rect(center = (self.bg_rect.centerx, (self.divide_rect.bottom + self.bg_rect.bottom) / 2))
        buy_item = self.trade_font.render(f'{self.buyable_items[self.buy_index]} seed', False, '#353738')
        buy_item_rect = buy_item.get_rect(midleft=(self.buy_text_rect.left + 50, buy_icon_rect.centery))
        buy_price = self.trade_font.render(f'${SEED_PRICES[self.buyable_items[self.buy_index]]}', False, '#353738')
        buy_price_rect = buy_price.get_rect(midleft=(999, 516))
        self.display_surface.blit(buy_icon, buy_icon_rect)
        self.display_surface.blit(buy_item, buy_item_rect)
        self.display_surface.blit(buy_price, buy_price_rect)

        sell_icon = pygame.transform.scale(self.item_surfaces[self.sellable_items[self.sell_index]], (128, 128))
        sell_icon_rect = sell_icon.get_rect(center=(self.bg_rect.centerx, (self.divide_rect.top + self.bg_rect.top) / 2))
        sell_item = self.trade_font.render(self.sellable_items[self.sell_index], False, '#353738')
        sell_item_rect = sell_item.get_rect(midleft=(self.sell_text_rect.left + 50, sell_icon_rect.centery))
        sell_price = self.trade_font.render(f'${SELL_PRICES[self.sellable_items[self.sell_index]]}', False, '#353738')
        sell_price_rect = buy_price.get_rect(midleft=(999, 224))
        self.display_surface.blit(sell_icon, sell_icon_rect)
        self.display_surface.blit(sell_item, sell_item_rect)
        self.display_surface.blit(sell_price, sell_price_rect)

        self.display_surface.blit(you_have_text, you_have_text_rect)

    def trader_input(self):
        # input
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_UP] or keys[pygame.K_DOWN]) and not self.trade_ui_timer.active:
            self.buy_toggle = not self.buy_toggle
            self.trade_ui_timer.activate()
        if keys[pygame.K_LEFT] and not self.internal_timer.active:
            self.internal_timer.activate()
            if self.buy_toggle:
                self.buy_index -= 1
                if self.buy_index < 0:
                    self.buy_index = len(self.buyable_items) - 1
            elif not self.buy_toggle:
                self.sell_index -= 1
                if self.sell_index < 0:
                    self.sell_index = len(self.sellable_items) - 1
        elif keys[pygame.K_RIGHT] and not self.internal_timer.active:
            self.internal_timer.activate()
            if self.buy_toggle:
                self.buy_index += 1
                if self.buy_index > len(self.buyable_items) - 1:
                    self.buy_index = 0
            elif not self.buy_toggle:
                self.sell_index +=1
                if self.sell_index > len(self.sellable_items) - 1:
                    self.sell_index = 0

        if keys[pygame.K_RETURN] and not self.internal_timer.active:
            self.internal_timer.activate()
            # buying items
            if self.buy_toggle:
                selected_item = f'{self.buyable_items[self.buy_index]}_seeds'
                selected_item_price = SEED_PRICES[self.buyable_items[self.buy_index]]
                if selected_item_price <= self.player.money:
                    if self.buy_indication_timer.active: self.buy_indication_timer.deactivate()
                    if self.purchase_lock_timer.active: self.purchase_lock_timer.deactivate()
                    if self.sell_indication_timer.active: self.sell_indication_timer.deactivate()
                    self.buy_indication_timer.activate()
                    self.show_balance_updates()
                    self.purchase_lock_timer.activate()
                    self.player.inventory_dict[selected_item] += 1
                    self.player.money -= selected_item_price
            # selling items
            elif not self.buy_toggle:
                selected_item = self.sellable_items[self.sell_index]
                selected_item_price = SELL_PRICES[self.sellable_items[self.sell_index]]
                if self.player.inventory_dict[selected_item] > 0:
                    if self.sell_indication_timer.active: self.sell_indication_timer.deactivate()
                    if self.purchase_lock_timer.active: self.purchase_lock_timer.deactivate()
                    self.sell_indication_timer.activate()
                    self.show_balance_updates()
                    self.purchase_lock_timer.activate()
                    self.player.inventory_dict[selected_item] -= 1
                    self.player.exp += 1
                    self.player.money += selected_item_price

    def show_balance_updates(self):
        if self.sell_indication_timer.active:
            if not self.purchase_lock_timer.active:
                self.bal_change_text = self.inventory_font.render(f'${SELL_PRICES[self.sellable_items[self.sell_index]]}', False, (50, 205, 50))
            self.display_surface.blit(self.bal_change_text, self.bal_change_text.get_rect(center=self.money_particle_pos))
        elif self.buy_indication_timer.active:
            if not self.purchase_lock_timer.active:
                self.bal_change_text = self.inventory_font.render(f'${SEED_PRICES[self.buyable_items[self.buy_index]]}', False, (205, 92, 92))
            self.display_surface.blit(self.bal_change_text, self.bal_change_text.get_rect(center=self.money_particle_pos))

    def update_timers(self):
        self.trade_ui_timer.update()
        self.internal_timer.update()
        self.buy_indication_timer.update()
        self.sell_indication_timer.update()
        self.purchase_lock_timer.update()

    def update_overlay(self):
        self.make_overlay()
        self.exp_bar()
        if self.player.trade_menu_toggle:
            self.trader_input()
            self.trade_ui()
            self.update_timers()
            self.show_balance_updates()






