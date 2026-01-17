import cProfile
from datetime import datetime
from operator import itemgetter
from random import choice

import pygame
from pygame import Vector2, Surface, SRCALPHA, Color, Rect, draw, mouse
from pygame.font import Font
from pygame.transform import smoothscale, flip

from engine.battle.player_input_battle import key_select_strategy
from engine.constants import *
from engine.uimenu.uimenu import UIMenu, MenuCursor
from engine.utils.common import keyboard_mouse_press_check
from engine.utils.text_making import text_render_with_bg, text_render_with_texture, \
    make_long_text, change_number, add_comma_number

team_colour = {0: (50, 190, 50), 1: (100, 110, 150), 2: (190, 50, 50)}
follower_type_colour = {0: (70, 70, 180), 1: (100, 200, 100)}  # melee, range


class UIBattle(UIMenu):
    def __init__(self, player_cursor_interact=True, has_containers=False):
        """
        Parent class for all battle menu user interface
        """
        from engine.battle.battle import Battle
        UIMenu.__init__(self, player_cursor_interact=player_cursor_interact, has_containers=has_containers)
        self.battle = Battle.battle
        self.cursor = Battle.battle_cursor  # use battle cursor for battle ui
        self.max_description_box_width = int(1000 * self.screen_scale[0])


class ButtonUI(UIBattle):
    def __init__(self, image, layer=11):
        self._layer = layer
        UIBattle.__init__(self)
        self.pos = (0, 0)
        self.image = image
        self.rect = self.image.get_rect(center=self.pos)
        self.mouse_over = False

    def change_pos(self, pos):
        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)


class BattleCursor(UIBattle, MenuCursor):
    def __init__(self, images):
        """Game battle cursor"""
        self._layer = 999999999999  # as high as possible, always blit last
        MenuCursor.__init__(self, images)
        UIBattle.__init__(self)

    def update(self):
        self.is_select_just_down, self.is_select_down, self.is_select_just_up = keyboard_mouse_press_check(
            mouse, 0, self.is_select_just_down, self.is_select_down, self.is_select_just_up)

        # Alternative select press button, like mouse right
        self.is_alt_select_just_down, self.is_alt_select_down, self.is_alt_select_just_up = keyboard_mouse_press_check(
            mouse, 2, self.is_alt_select_just_down, self.is_alt_select_down, self.is_alt_select_just_up)

        if self.is_select_down:
            self.image = self.images["click"]
        else:
            if self.battle.player_selected_strategy:  # change cursor for strategy
                if self.is_alt_select_down:
                    self.image = self.images["strategy_click"]
                else:
                    self.image = self.images["strategy"]
            else:
                if self.is_alt_select_down:
                    self.image = self.images["click"]
                else:
                    self.image = self.images["normal"]

        self.pos = mouse.get_pos()
        self.mouse_over = False
        if self.shown:
            self.rect.topleft = self.pos


class ScreenFade(UIBattle):
    def __init__(self):
        self._layer = 99
        UIBattle.__init__(self)
        self.font = self.game.screen_fade_font
        self.use_font_texture = "gold"
        self.text = None
        self.rect = self.battle.screen.get_rect()
        self.max_text_width = int(self.screen_size[0] * 0.8)
        self.image = Surface(self.rect.size, SRCALPHA)
        self.alpha = 0
        self.text_alpha = 0
        self.text_delay = 0
        self.fade_speed = 1
        self.text_surface = None
        self.text_rect = None
        self.text_fade_in = False
        self.fade_in_done = False
        self.fade_out = False
        self.done = False

    def reset(self, text=None, font_texture=None, font_size=70, instant_fade=False,
              text_fade_in=False, text_delay=0, fade_speed=1, fade_out=False):
        """
        Reset value for new fading
        @param text: new text
        @param font_texture: font texture name
        @param font_size: font size
        @param instant_fade: no fading animation
        @param text_fade_in: text also need to do fade in animation to appear
        @param text_delay: timer for delay showing text after fade in finish
        @param fade_speed: speed of screen fading
        @param fade_out: also fade out after finish
        """
        self.use_font_texture = font_texture
        self.text_alpha = 255
        self.text_fade_in = True
        if not text_fade_in:
            self.text_fade_in = False
            self.text_alpha = 0
        self.text_delay = text_delay
        if not font_texture:
            self.use_font_texture = "gold"
        if not instant_fade:
            self.alpha = 1  # fade in
        else:  # start with fade almost complete
            self.alpha = 254
        self.fade_speed = 1000 * fade_speed
        self.image = Surface(self.rect.size, SRCALPHA)
        self.image.fill((20, 20, 20))
        self.text = text
        self.text_surface = None
        self.text_rect = None
        self.fade_in_done = False
        self.fade_out = fade_out
        self.done = False
        if self.text:
            font_size = int(font_size * self.screen_scale[1])
            image_height = int((self.font.size(self.text)[0]) / self.max_text_width)
            if not image_height:  # only one line
                self.text_surface = text_render_with_texture(self.text, self.font,
                                                             self.font_texture[self.use_font_texture])
            else:
                # Find new image height, using code from make_long_text
                x, y = (font_size, font_size)
                words = [word.split(" ") for word in
                         str(text).splitlines()]  # 2D array where each row is a list of words
                space = self.font.size(" ")[0]  # the width of a space
                for line in words:
                    for word in line:
                        word_surface = self.font.render(word, True, (0, 0, 0))
                        word_width, word_height = word_surface.get_size()
                        if x + word_width >= self.max_text_width:
                            x = font_size  # reset x
                            y += word_height  # start on new row.
                        x += word_width + space
                    x = font_size  # reset x
                    y += word_height  # start on new row
                self.text_surface = Surface((self.max_text_width, y), SRCALPHA)
                self.text_surface.fill((0, 0, 0, 0))
                make_long_text(self.text_surface, text, (font_size, font_size), self.font,
                               with_texture=(self.font_texture[self.use_font_texture], None),
                               specific_width=self.max_text_width, alignment="center")

            self.text_rect = self.text_surface.get_rect(center=self.image.get_rect().center)
            if not text_fade_in:
                self.image.blit(self.text_surface, self.text_rect)
        self.image.set_alpha(self.alpha)

    def update(self):
        if not self.fade_in_done:  # keep fading
            self.alpha += self.battle.true_dt * self.fade_speed
            if self.alpha >= 255:
                self.alpha = 255
                self.fade_in_done = True
            self.image.set_alpha(self.alpha)
        elif self.text_fade_in and self.text:  # add text when finish fading if any
            if not self.text_delay:
                self.image.blit(self.text_surface, self.text_rect)
                if self.text_alpha:
                    self.text_alpha -= self.battle.true_dt
                    if self.text_alpha < 0:
                        self.text_alpha = 0
        else:
            if self.text_delay:
                self.text_delay -= self.battle.true_dt
                if self.text_delay < 0:
                    self.text_delay = 0
            if not self.text_delay:
                if self.fade_out:
                    self.alpha -= self.battle.true_dt * self.fade_speed
                    if self.alpha <= 0:
                        self.alpha = 0
                        self.done = True
                    self.image.set_alpha(self.alpha)
                else:
                    self.done = True


class Command(UIBattle):
    number_text_cache = {}
    number_respond_text_cache = {}
    number_cooldown_text_cache = {}
    stat_cache = {}

    def __init__(self, call_count_image, air_count_image):
        self._layer = 9
        UIBattle.__init__(self)
        self.character_list = self.battle.character_list
        self.text_popup = self.battle.text_popup
        self.outer_ui_updater = self.battle.outer_ui_updater
        self.character_portraits = self.battle.character_portraits
        self.number_font = self.game.character_indicator_font
        self.image = Surface((800 * self.screen_scale[0], 400 * self.screen_scale[1]), SRCALPHA)
        self.image_width = self.image.get_width()
        self.image.fill((0, 0, 0, 125))
        self.rect = self.image.get_rect(topleft=(0, 0))
        self.update_timer = 0
        self.player_team = 1
        self.player_enemy_team = 2
        self.player_team_stat = None
        self.character_rect = {}
        self.air_group_rect = {}
        self.check_air_group = None

        self.call_count_image = call_count_image
        self.air_count_image = air_count_image
        self.broken_icon = Surface((100 * self.screen_scale[0], 100 * self.screen_scale[1]), SRCALPHA)
        self.supply_text_bg = Surface((120 * self.screen_scale[0], 120 * self.screen_scale[1]))
        self.supply_text_bg_rect = self.supply_text_bg.get_rect(topright=(self.image.get_width(), 0))
        draw.rect(self.broken_icon, (0, 0, 0),
                  (30 * self.screen_scale[0], 30 * self.screen_scale[1],
                   10 * self.screen_scale[0], 60 * self.screen_scale[0]))
        draw.rect(self.broken_icon, (255, 255, 255),
                  (40 * self.screen_scale[0], 30 * self.screen_scale[1],
                   40 * self.screen_scale[0], 30 * self.screen_scale[0]))

        self.air_return_icon = Surface((100 * self.screen_scale[0], 100 * self.screen_scale[1]), SRCALPHA)
        draw.circle(self.air_return_icon, (200, 70, 70),
                    (self.air_return_icon.get_width() / 2, self.air_return_icon.get_height() / 2),
                    (self.air_return_icon.get_width() / 2.5), width=int(8 * self.screen_scale[0]))

        self.air_active_icon = Surface((100 * self.screen_scale[0], 100 * self.screen_scale[1]), SRCALPHA)
        draw.circle(self.air_active_icon, (200, 200, 0),
                    (self.air_active_icon.get_width() / 2, self.air_active_icon.get_height() / 2),
                    (self.air_active_icon.get_width() / 2.5), width=int(8 * self.screen_scale[0]))

        self.dead_icon = Surface((100 * self.screen_scale[0], 100 * self.screen_scale[1]), SRCALPHA)
        draw.circle(self.dead_icon, (0, 0, 0),
                    (self.dead_icon.get_width() / 2, self.dead_icon.get_height() / 2),
                    (self.dead_icon.get_width() / 2.5))

        self.call_cooldown_icon = Surface((75 * self.screen_scale[0], 75 * self.screen_scale[1]), SRCALPHA)
        draw.circle(self.call_cooldown_icon, (0, 0, 0, 200),
                    (self.call_cooldown_icon.get_width() / 2, self.call_cooldown_icon.get_height() / 2),
                    (self.call_cooldown_icon.get_width() / 2))

        self.font = self.game.generic_ui_font
        self.player_air_group_number = [None, None, None, None, None]
        self.air_group_health = [None, None, None, None, None]
        self.air_group_resource = [None, None, None, None, None]
        self.air_bar_width = 100 * self.screen_scale[0]
        self.air_bar_height = 15 * self.screen_scale[0]
        self.icon_status = {}
        self.leader_call_pool = []
        self.troop_call_pool = []
        self.player_air_group = []
        self.supply_status = ()
        self.leader_call_pool_status = {index: (None, None) for index in range(3)}
        self.troop_call_pool_status = {index: (None, None) for index in range(5)}
        self.call_pool_status = (self.leader_call_pool_status, self.troop_call_pool_status)

        self.base_image = self.image.copy()

        scaled_pos = 200 * self.screen_scale[0]
        self.leader_portrait_rect = {index: self.broken_icon.get_rect(center=(scaled_pos + (
                index * 170 * self.screen_scale[0]), 50 * self.screen_scale[1])) for index in range(3)}
        scaled_pos = 100 * self.screen_scale[0]
        self.ground_portrait_rect = {index: self.broken_icon.get_rect(center=(scaled_pos + (
                index * 140 * self.screen_scale[0]), 180 * self.screen_scale[1])) for index in range(5)}
        self.pool_index_rects = [self.leader_portrait_rect, self.ground_portrait_rect]
        self.air_portrait_rect = {index: self.broken_icon.get_rect(center=(scaled_pos + (
                index * 140 * self.screen_scale[0]), 300 * self.screen_scale[1])) for index in range(5)}

    def setup(self):
        self.player_team = self.battle.player_team
        self.player_team_stat = self.battle.team_stat[self.player_team]
        self.player_enemy_team = self.battle.player_enemy_team
        self.player_air_group = self.player_team_stat["air_group"]
        self.check_air_group = None
        self.supply_status = ()

    def update(self):
        if self.player_team:
            self.update_timer += self.battle.true_dt
            if self.update_timer > 0.2:
                self.update_timer -= 0.2

                reset_image = False
                if self.player_team_stat["leader_call_list"][:3] != self.leader_call_pool:
                    self.leader_call_pool = self.player_team_stat["leader_call_list"][:3]
                    reset_image = True
                if self.player_team_stat["troop_call_list"][:5] != self.troop_call_pool:
                    self.troop_call_pool = self.player_team_stat["troop_call_list"][:5]
                    reset_image = True
                if self.player_team_stat["air_group"] != self.check_air_group:
                    self.check_air_group = self.player_team_stat["air_group"].copy()
                    reset_image = True
                if reset_image:
                    self.image = self.base_image.copy()
                    self.air_group_health = [None, None, None, None, None]
                    self.air_group_resource = [None, None, None, None, None]
                    self.player_air_group_number = [None, None, None, None, None]
                    self.leader_call_pool_status = {index: (None, None) for index in range(3)}
                    self.troop_call_pool_status = {index: (None, None) for index in range(5)}
                    self.icon_status = {}
                    self.air_group_rect = {}
                    self.call_pool_status = (self.leader_call_pool_status, self.troop_call_pool_status)
                    self.supply_status = ()

                new_supply_status = (change_number(int(self.player_team_stat["supply_resource"])),
                                     change_number(int(self.player_team_stat["supply_reserve"])))
                if self.supply_status != new_supply_status:
                    self.supply_status = new_supply_status
                    self.image.blit(self.supply_text_bg, self.supply_text_bg_rect)

                    text = text_render_with_bg(new_supply_status[0], self.number_font)
                    self.image.blit(text, text.get_rect(topright=self.supply_text_bg_rect.topright))

                    text = text_render_with_bg(new_supply_status[1], self.number_font)
                    self.image.blit(text, text.get_rect(bottomright=self.supply_text_bg_rect.bottomright))

                for pool_index, pool in enumerate((self.leader_call_pool, self.troop_call_pool)):
                    # add character portrait for calling
                    pool_rect = self.pool_index_rects[pool_index]
                    for index, character in enumerate(pool):
                        if self.player_team == 1:
                            call_cooldown_status = (self.battle.team1_call_leader_cooldown_reinforcement,
                                                    self.battle.team1_call_troop_cooldown_reinforcement)[pool_index]
                        else:
                            call_cooldown_status = (self.battle.team2_call_leader_cooldown_reinforcement,
                                                    self.battle.team2_call_troop_cooldown_reinforcement)[pool_index]
                        pool_status = self.call_pool_status[pool_index]
                        char_id = character[0]
                        char_number_reserve = character[1]
                        char_supply_use = character[2]
                        state = [char_number_reserve, index in call_cooldown_status,
                                 self.player_team_stat["supply_resource"] >= char_supply_use]

                        if pool_status[index] != state:
                            pool_status[index] = state
                            self.image.blit(self.character_portraits[char_id]["command"], pool_rect[index])
                            if state[1]:
                                state.append(call_cooldown_status[index])
                            if state[1] or not state[2]:  # can't call because in cooldown or not enough supply
                                self.image.blit(self.call_cooldown_icon,
                                                self.call_cooldown_icon.get_rect(center=pool_rect[index].center))
                                if state[1]:
                                    number = int(state[3])
                                    if number in self.number_cooldown_text_cache:
                                        number_text = self.number_cooldown_text_cache[number]
                                    else:
                                        number_text = text_render_with_bg(str(number), self.font,
                                                                          gf_colour=(0, 0, 0),
                                                                          o_colour=(255, 255, 255))
                                        self.number_cooldown_text_cache[number] = number_text
                                    self.image.blit(number_text,
                                                    number_text.get_rect(center=pool_rect[index].center))

                            if char_number_reserve not in self.number_text_cache:
                                number_text = text_render_with_bg(str(char_number_reserve),
                                                                  self.number_font, o_colour=(200, 200, 100))
                                self.number_text_cache[char_number_reserve] = number_text
                            else:
                                number_text = self.number_text_cache[char_number_reserve]
                            number_rect = number_text.get_rect(
                                midbottom=self.pool_index_rects[pool_index][index].bottomright)
                            self.image.blit(self.call_count_image,
                                            self.call_count_image.get_rect(center=number_rect.center))
                            self.image.blit(number_text, number_rect)

                for index, air_group in enumerate(self.player_air_group):
                    # add air unit group
                    health_bar_percentage = (0, 0)
                    resource_bar_percentage = (0, 0)
                    if air_group:
                        health_bar_percentage = [character.health / character.base_health for character in air_group]
                        health_bar_percentage = (min(health_bar_percentage), max(health_bar_percentage))
                        resource_bar_percentage = [character.resource / character.base_resource for character in
                                                   air_group]
                        resource_bar_percentage = (min(resource_bar_percentage), max(resource_bar_percentage))

                    check = (air_group and "back" in air_group[0].commander_order,
                             any([air_character.active for air_character in air_group]),
                             len(air_group) != self.player_air_group_number[index])
                    if index not in self.icon_status or self.icon_status[index] != check:
                        self.icon_status[index] = check
                        if air_group:
                            self.image.blit(air_group[0].command_icon, self.air_portrait_rect[index])
                        else:  # air group completely dead, blit black circle over
                            self.image.blit(self.dead_icon, self.air_portrait_rect[index])
                        self.air_group_rect[index] = self.air_portrait_rect[index]
                        if check[0]:  # returning
                            self.image.blit(self.air_return_icon, self.air_portrait_rect[index])
                        elif check[1]:  # active
                            self.image.blit(self.air_active_icon, self.air_portrait_rect[index])
                        if check[2]:  # number in group change
                            self.player_air_group_number[index] = len(air_group)

                        if len(air_group) not in self.number_text_cache:
                            number_text = text_render_with_bg(str(len(air_group)),
                                                              self.number_font, o_colour=(200, 200, 100))
                            self.number_text_cache[len(air_group)] = number_text
                        else:
                            number_text = self.number_text_cache[len(air_group)]
                        number_rect = number_text.get_rect(midtop=self.air_portrait_rect[index].topleft)
                        self.image.blit(self.air_count_image,
                                        self.air_count_image.get_rect(center=number_rect.center))
                        self.image.blit(number_text, number_rect)

                    if self.air_group_health[index] != health_bar_percentage:
                        self.air_group_health[index] = health_bar_percentage
                        self.image.fill((0, 0, 0), (self.air_portrait_rect[index].bottomleft[0],
                                                    self.air_portrait_rect[index].bottomleft[1],
                                                    self.air_bar_width, self.air_bar_height))
                        self.image.fill((250, 100, 100), (self.air_portrait_rect[index].bottomleft[0],
                                                          self.air_portrait_rect[index].bottomleft[1],
                                                          self.air_bar_width * health_bar_percentage[1],
                                                          self.air_bar_height))
                        self.image.fill((100, 20, 20, 125), (self.air_portrait_rect[index].bottomleft[0],
                                                             self.air_portrait_rect[index].bottomleft[1],
                                                             self.air_bar_width * health_bar_percentage[0],
                                                             self.air_bar_height))

                    if self.air_group_resource[index] != resource_bar_percentage:
                        self.air_group_resource[index] = resource_bar_percentage
                        self.image.fill((0, 0, 0), (self.air_portrait_rect[index].bottomleft[0],
                                                    self.air_portrait_rect[index].bottomleft[1] + self.air_bar_height,
                                                    self.air_bar_width, self.air_bar_height))
                        self.image.fill((100, 250, 100), (self.air_portrait_rect[index].bottomleft[0],
                                                          self.air_portrait_rect[index].bottomleft[
                                                              1] + self.air_bar_height,
                                                          self.air_bar_width * resource_bar_percentage[1],
                                                          self.air_bar_height))
                        self.image.fill((20, 100, 20, 125), (self.air_portrait_rect[index].bottomleft[0],
                                                             self.air_portrait_rect[index].bottomleft[
                                                                 1] + self.air_bar_height,
                                                             self.air_bar_width * resource_bar_percentage[0],
                                                             self.air_bar_height))

            UIMenu.update(self)
            if self.mouse_over:
                inside_mouse_pos = Vector2(
                    (self.cursor.pos[0] - self.rect.topleft[0]),
                    (self.cursor.pos[1] - self.rect.topleft[1]))
                for index, rect in self.leader_portrait_rect.items():
                    if rect.collidepoint(inside_mouse_pos):
                        if index < len(self.leader_call_pool):
                            character = self.leader_call_pool[index][0]
                            self.popup_description(self.leader_call_pool[index][1], character)
                            if self.event_press:  # call unit
                                self.battle.call_reinforcement(self.player_team, "leader", index)
                        return

                for index, rect in self.ground_portrait_rect.items():
                    if rect.collidepoint(inside_mouse_pos):
                        if index < len(self.troop_call_pool):
                            character = self.troop_call_pool[index][0]
                            self.popup_description(self.troop_call_pool[index][1], character)
                            if self.event_press:  # call leader
                                self.battle.call_reinforcement(self.player_team, "troop", index)
                            return

                for air_group, rect in self.air_group_rect.items():
                    if rect.collidepoint(inside_mouse_pos):
                        self.popup_description(None, self.player_air_group[air_group][0].char_id)
                        if self.event:
                            if self.event_press:
                                # active or completely dead air group cannot be activated
                                if self.player_air_group_number[air_group]:
                                    self.battle.call_in_air_group(self.player_team, (air_group,),
                                                                  self.battle.team_stat[self.player_enemy_team][
                                                                      "start_pos"])
                            elif self.event_alt_press:
                                if (self.player_air_group_number[air_group] and
                                        any([air_character.active for air_character in
                                             self.player_air_group[air_group]])):
                                    # right click on active air group order it to exit the battle
                                    for character in self.player_air_group[air_group]:
                                        if character.alive:
                                            character.issue_commander_order(("back", character.start_pos))
                        return

    def popup_description(self, call_remain, character):
        if character not in self.stat_cache:
            character_data = self.character_list[character]
            char_stat = [self.localisation.grab_text(("ui", "Name:")) + self.localisation.grab_text(
                ("character", character, "Name")),
                         self.localisation.grab_text(
                             ("ui", "Description:")) + self.localisation.grab_text(
                             ("character", character, "Description")),
                         self.localisation.grab_text(("ui", "Class:")) + self.localisation.grab_text(
                             ("ui", character_data["Class"])),
                         self.localisation.grab_text(("ui", "Supply Cost:")) + add_comma_number(
                             character_data["Supply"]),
                         self.localisation.grab_text(("ui", "Call Cooldown:")) + str(character_data["Reinforce Time"]),
                         self.localisation.grab_text(("ui", "Call Response Time:")) + str(
                             character_data["Respond Time"])]
        else:
            char_stat = self.stat_cache[character]
        if call_remain:
            char_stat.append(self.localisation.grab_text(("ui", "Call Remain:")) + str(call_remain))
        self.text_popup.popup(self.rect.bottomleft, char_stat, width_text_wrapper=self.max_description_box_width)
        self.outer_ui_updater.add(self.text_popup)

    def reset(self):
        self.image = self.base_image.copy()
        self.icon_status = {}
        self.air_group_health = [None, None, None, None, None]
        self.air_group_resource = [None, None, None, None, None]
        self.player_air_group_number = [None, None, None, None, None]
        self.character_rect = {}
        self.air_group_rect = {}


class FPSCount(UIBattle):
    def __init__(self, parent):
        self._layer = 12
        UIBattle.__init__(self, player_cursor_interact=False)
        self.image = Surface((80 * self.screen_scale[0], 80 * self.screen_scale[1]), SRCALPHA)
        self.base_image = self.image.copy()
        self.font = self.game.fps_counter_font
        self.clock = parent.clock
        fps_text = self.font.render("60", True, (255, 60, 60))
        self.text_rect = fps_text.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.rect = self.image.get_rect(topleft=(0, 0))

    def update(self):
        """Update current fps"""
        self.image = self.base_image.copy()
        fps = str(int(self.clock.get_fps()))
        fps_text = self.font.render(fps, True, (255, 60, 60))
        self.image.blit(fps_text, self.text_rect)


class BattleHelper(UIBattle):
    def __init__(self, weather_icon_images, helper_ui_images, time_selector_image, time_choice_images,
                 time_select_images, defeat_images, victory_images):
        self._layer = 12
        UIBattle.__init__(self)
        self.font = self.game.battle_timer_font
        self.image = Surface((800 * self.screen_scale[0], 400 * self.screen_scale[1]), SRCALPHA)
        self.base_image = self.image.copy()
        self.helper_ui_images = helper_ui_images
        self.time_choice_images = time_choice_images
        self.time_select_images = time_select_images
        self.time_selector_image = time_selector_image
        self.defeat_images = defeat_images
        self.victory_images = victory_images

        self.button_rect = {"menu": (), "pause": (), "x1": (), "x2": (), "x3": ()}
        self.base_image = self.image.copy()

        self.image_width = self.image.get_width()
        self.base_battle_scale_image_height = 30 * self.screen_scale[1]
        self.base_battle_timer_rect_topright = (590 * self.screen_scale[0], 100 * self.screen_scale[1])
        time_choice_pos_x = 750 * self.screen_scale[0]
        self.time_choice_rects = (time_choice_images[0].get_rect(center=(time_choice_pos_x, 60 * self.screen_scale[1])),
                                  time_choice_images[1].get_rect(center=(time_choice_pos_x, 120 * self.screen_scale[1])),
                                  time_choice_images[2].get_rect(center=(time_choice_pos_x, 180 * self.screen_scale[1])),
                                  time_choice_images[3].get_rect(center=(time_choice_pos_x, 240 * self.screen_scale[1])),
                                  time_choice_images[4].get_rect(center=(time_choice_pos_x, 300 * self.screen_scale[1])))

        self.time_selector_rects = tuple([self.time_selector_image.get_rect(
            midleft=(670 * self.screen_scale[0], rect.center[1])) for rect in self.time_choice_rects])
        self.battle_scale = None
        self.time_option = 2
        self.alert_state = 0
        self.alert_timer = 0
        self.time_text = None
        self.weather = None
        self.alert_revert = False
        self.weather_icon_images = weather_icon_images

        self.time_choice = (0, 0.5, 1, 2, 3)

        self.rect = self.image.get_rect(topright=(self.screen_width, 0))

    def setup(self):
        self.alert_revert = False
        self.time_text = None
        self.alert_state = 0
        self.alert_timer = 0
        self.time_option = 2
        self.battle.game_speed = self.time_option
        self.add_battle_scale()
        self.true_reset_image()

    def battle_end(self, result):
        pass

    def true_reset_image(self):
        """total reset entire image due to player change game speed, weather change, or setup"""
        self.image = self.base_image.copy()
        self.image.blit(self.time_selector_image, self.time_selector_rects[self.time_option])
        for index, rect in enumerate(self.time_choice_rects):
            if index == self.time_option:
                self.image.blit(self.time_select_images[0], self.time_choice_rects[index])
            else:
                self.image.blit(self.time_select_images[1], self.time_choice_rects[index])
            self.image.blit(self.time_choice_images[index], self.time_choice_rects[index])
        self.image.blit(self.time_selector_image, self.time_selector_rects[self.time_option])

        icon_image = self.weather_icon_images[self.weather.split("_")[0]].copy()
        strength_text = text_render_with_bg(str(int(self.weather.split("_")[1]) + 1), self.font)
        icon_image.blit(strength_text, strength_text.get_rect(bottomright=icon_image.get_size()))
        self.image.blit(icon_image, icon_image.get_rect(topleft=(0, self.base_battle_scale_image_height)))

        self.reset_image()

    def reset_image(self):
        """reset when strategy alert change state"""
        self.image.blit(self.helper_ui_images[self.alert_state], self.helper_ui_images[0].get_rect(topleft=(0, 0)))

    def add_battle_scale(self):
        if self.battle_scale:
            percent_scale = 0  # start point fo fill colour of team scale
            for team, value in enumerate(self.battle_scale):
                if value > 0:
                    self.image.fill(team_colour[team], (self.image_width * percent_scale, 0,
                                                        self.image_width, self.base_battle_scale_image_height))
                    percent_scale += value
        else:
            self.image.fill((0, 0, 0), (0, 0,
                                        self.image_width, self.base_battle_scale_image_height))

    def update(self):
        """Update battle time"""
        must_reset_image = False
        reset_inside_helper_image = False

        if self.weather != self.battle.current_weather.weather_now:
            self.weather = self.battle.current_weather.weather_now
            must_reset_image = True

        UIMenu.update(self)

        if self.event_press:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))
            for index, rect in enumerate(self.time_choice_rects):
                if rect.collidepoint(inside_mouse_pos):
                    self.time_option = index
                    if self.battle.game_speed != self.time_choice[index]:
                        self.battle.game_speed = self.time_choice[index]
                        must_reset_image = True

        if self.alert_timer:
            if self.alert_revert:
                self.alert_timer -= self.battle.true_dt
                if self.alert_timer < 0:
                    self.alert_timer = 0
                    self.alert_revert = False
            else:
                self.alert_timer += self.battle.true_dt
                if self.alert_timer > 0.3:
                    self.alert_timer = 0.3
                    self.alert_revert = True
            alert_state = int(self.alert_timer * 10)
            if self.alert_state != alert_state:
                self.alert_state = alert_state
                if self.alert_state == 3:  # play alert bell sound
                    self.alert_state = 3
                    self.battle.add_sound_effect_queue(choice(self.sound_effect_pool["Alert"]),
                                                       self.battle.camera_pos, 200000, 0)
                if not must_reset_image:  # no need to reset here if will be true reset after
                    reset_inside_helper_image = True
                    self.reset_image()

        if must_reset_image:
            self.true_reset_image()

        time_text = datetime.fromtimestamp(self.battle.battle_time).strftime('%M:%S')
        if time_text != self.time_text or must_reset_image or reset_inside_helper_image:
            self.time_text = time_text
            text = text_render_with_bg(datetime.fromtimestamp(self.battle.battle_time).strftime('%M:%S'), self.font)
            text_bg = Surface((text.get_size()))
            text_bg.blit(text, text.get_rect(topleft=(0, 0)))
            self.image.blit(text_bg, text.get_rect(topright=self.base_battle_timer_rect_topright))

        if self.battle_scale != self.battle.battle_scale or must_reset_image or reset_inside_helper_image:
            self.battle_scale = self.battle.battle_scale
            self.add_battle_scale()


class TacticalMap(UIBattle):
    def __init__(self, tactic_alert_image):
        self._layer = 10
        UIBattle.__init__(self)
        self.tactic_alert_image = tactic_alert_image
        self.all_team_enemy_check = self.battle.all_team_enemy_check
        self.battle_camera_object_drawer = self.battle.battle_camera_object_drawer
        self.battle_camera = self.battle.camera
        self.player_team = 1
        self.update_timer = 0
        self.map_scale_width = 1
        self.base_image = Surface((2200 * self.screen_scale[0], 200 * self.screen_scale[1]), SRCALPHA)
        self.base_image.fill((255, 255, 255, 125))
        self.air_icon_pos_y = 30 * self.screen_scale[1]
        self.strategy_alert_pos_y = 80 * self.screen_scale[1]
        self.ground_icon_pos_y = 190 * self.screen_scale[1]
        self.camera_border_image = None
        self.image = self.base_image.copy()
        self.image_width = self.image.get_width()
        self.image_height = self.image.get_height()
        self.current_strategy_base_range = None
        self.current_strategy_base_activate_range = None
        self.strategy_line_width = int(20 * self.screen_scale[0])
        self.rect = self.image.get_rect(midtop=(self.battle.screen_width / 2, 0))
        self.strategy_status = []

        self.commander_icon_border = {team: self.make_icon_border(team, False, colour_modifier=1.5) for
                                      team in team_colour}
        self.icon_width = self.commander_icon_border[1].get_width()
        self.icon_height = self.commander_icon_border[1].get_height()
        self.icon_center = (self.icon_width / 2, self.icon_height / 2)
        self.empty_command_icon = Surface((self.icon_width, self.icon_height), SRCALPHA)
        draw.circle(self.empty_command_icon, (30, 30, 30), self.icon_center,
                    (self.empty_command_icon.get_width() / 2))
        self.troop_dot_images = {}
        self.commander_health_state = {1: None, 2: None}
        self.commander_icon = {1: None, 2: None}
        for team, colour in team_colour.items():
            dot = Surface((20 * self.screen_scale[0], 20 * self.screen_scale[1]))
            dot.fill(colour)
            self.troop_dot_images[team] = dot
        self.character_rect = {}

    def make_icon_border(self, team, circle, colour_modifier=1):
        if circle:
            image = Surface(circle.get_size(), SRCALPHA)
        else:
            image = Surface((170 * self.screen_scale[0], 170 * self.screen_scale[1]), SRCALPHA)
        if colour_modifier != 1:
            draw.circle(image, [value * colour_modifier if value * colour_modifier <= 255 else 255
                                for value in team_colour[team]], (image.get_width() / 2, image.get_height() / 2),
                        (image.get_width() / 2))
        else:
            draw.circle(image, team_colour[team], (image.get_width() / 2, image.get_height() / 2),
                        (image.get_width() / 2))
        if circle:
            image.blit(circle, circle.get_rect(topleft=(0, 0)))

        return image

    def setup(self):
        self.commander_health_state = {1: None, 2: None}
        self.commander_icon = {1: None, 2: None}
        self.strategy_status = []
        self.player_team = self.battle.player_team
        self.map_scale_width = self.battle.base_stage_end / self.image_width
        self.camera_border_image = Surface((Default_Screen_Width / self.map_scale_width,
                                            200 * self.screen_scale[1]), SRCALPHA)
        draw.rect(self.camera_border_image, (0, 0, 0), (0, 0, self.camera_border_image.get_width(), self.image_height),
                  width=int(15 * self.screen_scale[0]))

    def warn_strategy(self, strategy_base_posx):
        """Add bell icon to warn where enemy use strategy"""
        self.strategy_status.append([strategy_base_posx / self.map_scale_width, 3])
        self.battle.battle_helper_ui.alert_timer = 0.01
        self.battle.battle_helper_ui.alert_revert = False

    def update(self):
        """update map"""
        self.update_timer += self.battle.true_dt
        if self.update_timer > 0.05:
            self.image = self.base_image.copy()

            # Draw camera border
            self.image.blit(self.camera_border_image,
                            self.camera_border_image.get_rect(
                                topleft=(self.battle.base_camera_left / self.map_scale_width, 0)))

            # draw commander
            for team, character in self.battle.team_commander.items():
                if character:

                    scaled_pos = (character.base_pos[0] / self.map_scale_width, self.ground_icon_pos_y)
                    health_state = round(character.health / character.base_health, 1)
                    if health_state != self.commander_health_state[team]:
                        # circle also indicate health
                        back_icon = self.commander_icon_border[character.team].subsurface((
                            0, self.icon_height - (self.icon_height * health_state),
                            self.icon_width, self.icon_height - (self.icon_height * (1 - health_state))))
                        back_command_icon = self.empty_command_icon.copy()
                        back_command_icon.blit(back_icon, back_icon.get_rect(bottomleft=(0, self.icon_height)))
                        back_command_icon.blit(character.icon[character.direction],
                                               character.icon[character.direction].get_rect(center=self.icon_center))
                        self.commander_icon[team] = back_command_icon
                    self.image.blit(self.commander_icon[team], self.commander_icon[team].get_rect(midbottom=scaled_pos))

            # Draw character dots
            for character_team in self.all_team_enemy_check.values():
                for character in character_team:
                    if character in self.battle_camera_object_drawer:
                        team = character.team
                        if character.character_type == "air":
                            if character.active:
                                scaled_pos = (character.base_pos[0] / self.map_scale_width, self.air_icon_pos_y)
                                self.image.blit(self.troop_dot_images[team],
                                                self.troop_dot_images[team].get_rect(midbottom=scaled_pos))
                        elif not character.is_commander:
                            scaled_pos = (character.base_pos[0] / self.map_scale_width, self.ground_icon_pos_y)
                            self.image.blit(self.troop_dot_images[team],
                                            self.troop_dot_images[team].get_rect(midbottom=scaled_pos))

            if self.battle.player_selected_strategy:
                # draw activation line
                line_start = ((self.battle.team_commander[self.player_team].base_pos[
                                   0] - self.current_strategy_base_activate_range) /
                              self.map_scale_width)
                line_end = ((self.battle.team_commander[self.player_team].base_pos[
                                 0] + self.current_strategy_base_activate_range) /
                            self.map_scale_width)
                if line_start < 0:
                    line_start = 0
                if line_end > self.image_width:
                    line_end = self.image_width
                draw.line(self.image, (80, 120, 200),
                          (line_start, 0),
                          (line_start, self.image_height), width=self.strategy_line_width)

                draw.line(self.image, (80, 120, 200),
                          (line_end, 0),
                          (line_end, self.image_height), width=self.strategy_line_width)

                if self.battle.player_battle_interact.show_strategy_activate_line:
                    # draw strategy range if player cursor is within activation range, mean strategy can be used
                    line_start = (self.battle.base_cursor_pos[
                                      0] - self.current_strategy_base_range) / self.map_scale_width
                    line_end = (self.battle.base_cursor_pos[
                                    0] + self.current_strategy_base_range) / self.map_scale_width
                    if line_start < 0:
                        line_start = 0
                    if line_end > self.image_width:
                        line_end = self.image_width

                    draw.line(self.image, (120, 180, 80),
                              (line_start, 0),
                              (line_start, self.image_height), width=self.strategy_line_width)

                    draw.line(self.image, (120, 180, 80),
                              (line_end, 0),
                              (line_end, self.image_height), width=self.strategy_line_width)

            if self.strategy_status:
                for status in self.strategy_status:
                    status[1] -= self.update_timer
                    self.image.blit(self.tactic_alert_image,
                                    self.tactic_alert_image.get_rect(center=(status[0],
                                                                             self.strategy_alert_pos_y)))

                    if status[1] <= 0:
                        self.strategy_status.remove(status)

            self.update_timer -= 0.05
        UIMenu.update(self)

        if self.event_press or self.event_alt_press:
            self.battle.camera_pos[0] = ((self.cursor.pos[0] - self.rect.topleft[0]) * self.map_scale_width *
                                         self.screen_scale[0])
            self.battle.fix_camera()


class StrategySelect(UIBattle):
    icon_cache = {}
    number_text_cache = {}
    strategy_text_cache = {}

    def __init__(self, pos, strategy_icons):
        self._layer = 10
        UIBattle.__init__(self)
        self.text_popup = self.battle.text_popup
        self.outer_ui_updater = self.battle.outer_ui_updater
        self.strategy_icons = strategy_icons
        self.font = self.game.battle_timer_font
        self.update_timer = 0
        self.strategy_status = {}
        self.selected_strategy_icon = Surface((150 * self.screen_scale[0], 150 * self.screen_scale[1]), SRCALPHA)
        draw.circle(self.selected_strategy_icon, (200, 200, 50),
                    (self.selected_strategy_icon.get_width() / 2, self.selected_strategy_icon.get_height() / 2),
                    (self.selected_strategy_icon.get_width() / 2), width=int(20 * self.screen_scale[0]))

        self.cooldown_strategy_icon = Surface((150 * self.screen_scale[0], 150 * self.screen_scale[1]), SRCALPHA)
        draw.circle(self.cooldown_strategy_icon, (0, 0, 0, 200),
                    (self.cooldown_strategy_icon.get_width() / 2, self.cooldown_strategy_icon.get_height() / 2),
                    (self.cooldown_strategy_icon.get_width() / 2))

        self.base_image = Surface((1200 * self.screen_scale[0], 150 * self.screen_scale[1]), SRCALPHA)
        self.base_image.fill((0, 0, 0, 125))
        self.image = self.base_image.copy()
        self.image_width = self.image.get_width()
        self.image_height = self.image.get_height()
        self.rect = self.image.get_rect(midtop=pos)
        self.player_team = 1
        self.player_team_stat = None

        self.strategy_rect = {}

    def setup(self):
        self.player_team = self.battle.player_team
        self.player_team_stat = self.battle.team_stat[self.player_team]
        self.strategy_status = {}
        self.image = self.base_image.copy()
        if self.player_team:
            pos_x = 250 * self.screen_scale[1]
            for index, strategy in enumerate(self.player_team_stat["strategy"]):
                if strategy not in self.strategy_icons:
                    icon_image = self.strategy_icons["Default"].copy()
                else:
                    icon_image = self.strategy_icons[strategy].copy()
                rect = icon_image.get_rect(midtop=(pos_x, 0))
                shortcut_text = text_render_with_bg(pygame.key.name(self.battle.player_key_bind[
                                                                        "Strategy " + str(index + 1)]).capitalize(),
                                                    self.font)
                text_rect = shortcut_text.get_rect(bottomright=(icon_image.get_width(), icon_image.get_height()))
                icon_image.blit(shortcut_text, text_rect)
                pos_x += 180 * self.screen_scale[1]
                self.strategy_rect[index] = rect
                self.icon_cache[index] = icon_image

    def update(self):
        if self.player_team:
            self.update_timer += self.battle.true_dt
            if self.update_timer > 0.1:
                text = text_render_with_bg(str(int(self.player_team_stat["strategy_resource"])),
                                           self.font)
                text_bg = Surface((text.get_size()))
                text_bg.blit(text, text.get_rect(topleft=(0, 0)))
                text_rect = text.get_rect(topleft=(0, 0))
                self.image.blit(text_bg, text_rect)
                for index, strategy in enumerate(self.player_team_stat["strategy"]):
                    cooldown = self.player_team_stat["strategy_cooldown"][index]
                    check = (cooldown, (strategy, index) == self.battle.player_selected_strategy)
                    if index not in self.strategy_status or self.strategy_status[index] != check:
                        self.strategy_status[index] = check
                        self.image.blit(self.icon_cache[index], self.strategy_rect[index])

                        if cooldown:  # in cooldown
                            self.image.blit(self.cooldown_strategy_icon, self.strategy_rect[index])
                            if int(cooldown) in self.number_text_cache:
                                number_text = self.number_text_cache[int(cooldown)]
                            else:
                                number_text = text_render_with_bg(str(int(cooldown)), self.font,
                                                                  gf_colour=(255, 255, 255),
                                                                  o_colour=(0, 0, 0))
                                self.number_text_cache[int(cooldown)] = number_text
                            self.image.blit(number_text, number_text.get_rect(center=self.strategy_rect[index].center))
                        elif self.battle.player_selected_strategy and index == self.battle.player_selected_strategy[1]:
                            self.image.blit(self.selected_strategy_icon, self.strategy_rect[index])
                self.update_timer -= 0.1

            UIMenu.update(self)
            if self.mouse_over:
                inside_mouse_pos = Vector2(
                    (self.cursor.pos[0] - self.rect.topleft[0]),
                    (self.cursor.pos[1] - self.rect.topleft[1]))
                for index, rect in self.strategy_rect.items():
                    if rect.collidepoint(inside_mouse_pos):
                        this_strategy = self.player_team_stat["strategy"][index]
                        if this_strategy not in self.strategy_text_cache:
                            text = (self.localisation.grab_text(("strategy", this_strategy, "Name")),
                                    self.localisation.grab_text(("strategy", this_strategy, "Description")),
                                    self.localisation.grab_text(("ui", "Strategy Cost")) +
                                    str(self.battle.strategy_list[this_strategy]["Resource Cost"]),
                                    self.localisation.grab_text(("ui", "Activate Range")) +
                                    str(self.battle.strategy_list[this_strategy]["Activate Range"]),
                                    self.localisation.grab_text(("ui", "Strategy Range")) +
                                    str(self.battle.strategy_list[this_strategy]["Range"])
                                    )
                            self.strategy_text_cache[this_strategy] = text
                        else:
                            text = self.strategy_text_cache[this_strategy]
                        self.text_popup.popup(self.rect.bottomleft, text,
                                              width_text_wrapper=self.max_description_box_width)
                        self.outer_ui_updater.add(self.text_popup)
                        if self.event_press:
                            if not self.player_team_stat["strategy_cooldown"][index]:
                                key_select_strategy(self.battle, index)
                        break


class PlayerBattleInteract(UIBattle):
    def __init__(self):
        self._layer = 9999999999999999999
        UIBattle.__init__(self, player_cursor_interact=False)
        self.battle_camera = self.battle.camera
        self.selection_start_pos = Vector2()
        self.current_pos = Vector2()
        self.line_size = int(10 * self.screen_scale[0])
        self.inner_line_size = int(20 * self.screen_scale[0])
        if self.line_size < 1:
            self.line_size = 1
        self.image = None
        self.rect = None
        self.current_strategy_base_range = None
        self.current_strategy_base_activate_range = None
        self.current_strategy_range = None
        self.current_strategy_activate_range = None
        self.strategy_line_top = 500 * self.screen_scale[1]
        self.strategy_line_bottom = 2160 * self.screen_scale[1]
        self.strategy_line_width = int(20 * self.screen_scale[0])
        self.strategy_line_inner_width = int(self.strategy_line_width / 2)
        self.strategy_line_center = 900 * self.screen_scale[1]
        self.show_strategy_activate_line = False

    def reset(self):
        self.current_pos = None
        self.selection_start_pos = None
        self.rect = None

    def update(self):
        self.event_press = False
        self.event_hold = False  # some UI differentiates between press release or holding, if not just use event
        self.event_alt_press = False
        self.event_alt_hold = True
        self.show_strategy_activate_line = False
        if self.battle.player_team:
            if not self.cursor.mouse_over:
                if self.cursor.is_alt_select_just_up:  # put alt (right) click first to prioritise it
                    self.event_alt_press = True
                    self.cursor.is_alt_select_just_up = False  # reset select button to prevent overlap interaction
                elif self.cursor.is_alt_select_down:
                    self.event_alt_hold = True
                    self.cursor.is_alt_select_just_down = False  # reset select button to prevent overlap interaction
                elif self.cursor.is_select_just_up:
                    self.event_press = True
                    self.cursor.is_select_just_up = False  # reset select button to prevent overlap interaction
                elif self.cursor.is_select_down:
                    self.event_hold = True
                    self.cursor.is_select_just_down = False  # reset select button to prevent overlap interaction
                else:  # no mouse activity
                    if self.battle.player_selected_strategy:
                        # draw activation line
                        commander = self.battle.team_commander[self.battle.player_team]
                        line_start = (commander.pos[0] - self.current_strategy_activate_range) - (
                                self.battle.shown_camera_pos[0] - self.battle_camera.camera_w_center)
                        line_end = (commander.pos[0] + self.current_strategy_activate_range) - (
                                self.battle.shown_camera_pos[0] - self.battle_camera.camera_w_center)
                        if line_start > 0:
                            draw.line(self.battle.camera.image, (80, 120, 200),
                                      (line_start, self.strategy_line_top),
                                      (line_start, self.strategy_line_bottom), width=self.strategy_line_width)
                            draw.line(self.battle.camera.image, (20, 70, 50),
                                      (line_start, self.strategy_line_top),
                                      (line_start, self.strategy_line_bottom), width=self.strategy_line_inner_width)
                        if line_end > 0:
                            draw.line(self.battle.camera.image, (80, 120, 200),
                                      (line_end, self.strategy_line_top),
                                      (line_end, self.strategy_line_bottom), width=self.strategy_line_width)
                            draw.line(self.battle.camera.image, (20, 70, 50),
                                      (line_end, self.strategy_line_top),
                                      (line_end, self.strategy_line_bottom), width=self.strategy_line_inner_width)

                        if not self.current_strategy_base_activate_range or \
                                (abs(commander.base_pos[0] - self.battle.base_cursor_pos[0]) <
                                 self.current_strategy_base_activate_range):
                            self.show_strategy_activate_line = True

                            # draw strategy range if player cursor is within activation range, mean strategy can be used
                            # or strategy has no activation range, which mean activate only from commander
                            if not self.current_strategy_base_activate_range:
                                pos_to_use = commander.pos[0]
                            else:
                                pos_to_use = self.battle.cursor_pos[0]
                            line_start = (pos_to_use - self.current_strategy_range) - (
                                    self.battle.shown_camera_pos[0] - self.battle_camera.camera_w_center)
                            line_end = (pos_to_use + self.current_strategy_range) - (
                                    self.battle.shown_camera_pos[0] - self.battle_camera.camera_w_center)
                            if line_start > 0:
                                draw.line(self.battle.camera.image, (120, 180, 80),
                                          (line_start, self.strategy_line_top),
                                          (line_start, self.strategy_line_bottom), width=self.strategy_line_width)
                                draw.line(self.battle.camera.image, (70, 20, 50),
                                          (line_start, self.strategy_line_top),
                                          (line_start, self.strategy_line_bottom), width=self.strategy_line_inner_width)
                            if line_end > 0:
                                draw.line(self.battle.camera.image, (120, 180, 80),
                                          (line_start, self.strategy_line_center),
                                          (line_end, self.strategy_line_center), width=self.strategy_line_width)

                                draw.line(self.battle.camera.image, (120, 180, 80),
                                          (line_end, self.strategy_line_top),
                                          (line_end, self.strategy_line_bottom), width=self.strategy_line_width)
                                draw.line(self.battle.camera.image, (70, 20, 50),
                                          (line_end, self.strategy_line_top),
                                          (line_end, self.strategy_line_bottom), width=self.strategy_line_inner_width)

            if self.event_press:
                if self.battle.player_selected_strategy:
                    # deactivate strategy when there is one selected
                    self.battle.player_selected_strategy = None
                elif self.battle.player_commander:
                    # order to move to area, no attack at all until reach
                    self.battle.player_commander.issue_commander_order(("move", self.battle.base_cursor_pos[0]))

            elif self.event_alt_press:  # right click order selected leader to do something
                if self.battle.player_selected_strategy:
                    # has strategy selected, prioritise activate strategy for this input
                    if self.battle.activate_strategy(self.battle.player_team, self.battle.player_selected_strategy[0],
                                                     self.battle.player_selected_strategy[1],
                                                     self.battle.base_cursor_pos[0]):
                        # successfully activate strategy
                        self.battle.player_selected_strategy = None
                elif self.battle.player_commander:
                    # order to move and attack enemy in range along the way
                    self.battle.player_commander.issue_commander_order(("attack", self.battle.base_cursor_pos[0]))


class CharacterCommandIndicator(UIBattle):
    def __init__(self, pos_y, move_image, attack_image):
        self._layer = 9999999999999999998
        UIBattle.__init__(self, player_cursor_interact=False, has_containers=True)
        self.battle_camera_drawer = self.battle.battle_camera_ui_drawer
        self.move_image = move_image.copy()
        self.attack_image = attack_image.copy()
        self.command_dict = {"move": self.move_image, "attack": self.attack_image}
        self.image = self.move_image
        self.pos_y = pos_y * self.screen_scale[1]
        self.rect = self.image.get_rect(center=(0, 0))
        self.check_order = None
        self.leader = None

    def setup(self, leader=None):
        if leader:
            self.leader = leader
            self.move_image.blit(self.leader.icon["right"], self.leader.icon["right"].get_rect(topleft=(0, 0)))
            self.attack_image.blit(self.leader.icon["right"], self.leader.icon["right"].get_rect(topleft=(0, 0)))
            self.battle.battle_effect_updater.add(self)
        else:
            self.battle.battle_effect_updater.remove(self)

    def update(self, dt):
        if self.leader.alive:
            order_check = self.leader.true_commander_order
            if order_check and "stay" not in order_check:  # only show move and attack command
                if self not in self.battle_camera_drawer:
                    self.battle_camera_drawer.add(self)
                if self.check_order != order_check:
                    self.check_order = order_check
                    self.image = self.command_dict[order_check[0]]
                    self.rect.center = (order_check[1] * self.screen_scale[0], self.pos_y)
            else:
                if self in self.battle_camera_drawer:
                    self.battle_camera_drawer.remove(self)

        else:
            if self in self.battle_camera_drawer:
                self.battle_camera_drawer.remove(self)


class CharacterLeaderIndicator(UIBattle):
    indicator_select_image = None
    text_image_cache = {team: {} for team in team_colour}

    def __init__(self, character):
        self._layer = 9999999999999999997
        UIBattle.__init__(self, player_cursor_interact=False, has_containers=True)
        self.character = character
        self.height_adjust = character.sprite_height
        font = self.game.character_indicator_font

        text = "P"

        if character.team == self.battle.player_team:
            self.battle.player_leader_indicators.add(self)

        if text not in self.text_image_cache[self.character.team]:
            self.text_image_cache[self.character.team][text] = {}
            self.base_text_image = text_render_with_bg(text, font, gf_colour=team_colour[self.character.team],
                                                       o_colour=Color("white"))
            self.selected_text_image = text_render_with_bg(text, font, gf_colour=team_colour[self.character.team],
                                                           o_colour=Color("black"))
            self.text_image_cache[self.character.team][text]["normal"] = self.base_text_image
            self.text_image_cache[self.character.team][text]["selected"] = self.selected_text_image
        else:
            self.base_text_image = self.text_image_cache[self.character.team][text]["normal"]
            self.selected_text_image = self.text_image_cache[self.character.team][text]["selected"]

        self.base_pos = None
        self.selected = False
        self.pos_y = 2170 * self.screen_scale[1]
        self.image = Surface((100 * self.screen_scale[0], 100 * self.screen_scale[1]), SRCALPHA)
        self.health = None

        self.image_width = self.image.get_width()
        self.health_bar_height = 15 * self.screen_scale[0]
        self.health_bar = Surface((self.image_width, self.health_bar_height))
        self.follower_bar = Surface((self.image.get_width(), self.health_bar_height))

        self.text_rect = self.base_text_image.get_rect(midtop=(self.image_width / 2, 0))
        self.health_bar_rect = self.health_bar.get_rect(midtop=(self.image_width / 2,
                                                                self.text_rect.midbottom[1]))
        self.image.blit(self.base_text_image, self.text_rect)
        self.image.blit(self.health_bar, self.health_bar_rect)
        self.rect = self.image.get_rect(midbottom=(self.character.pos[0], self.pos_y))

    def update(self, dt):
        if self.base_pos != self.character.base_pos:
            self.base_pos = self.character.base_pos.copy()
            self.rect.midbottom = (self.character.pos[0], self.pos_y)
        if self.health != self.character.health:
            self.health = self.character.health
            self.health_bar.fill((0, 0, 0))
            self.health_bar.fill((150, 50, 50), (0, 0,
                                                 self.image_width * (self.health / self.character.base_health),
                                                 self.health_bar_height))
            self.image.blit(self.health_bar, self.health_bar_rect)


class UIScroll(UIBattle):
    def __init__(self, ui, pos):
        """
        Scroll for any applicable ui
        :param ui: Any ui object, the ui must has max_row_show attribute, layer, and image surface
        :param pos: Starting pos
        :param layer: Surface layer value
        """
        self.ui = ui
        self._layer = self.ui.layer + 2  # always 2 layer higher than the ui and its item
        UIBattle.__init__(self)

        self.ui.scroll = self
        self.height_ui = self.ui.image.get_height()
        self.max_row_show = self.ui.max_row_show
        self.pos = pos
        self.image = Surface((10, self.height_ui))
        self.image.fill((255, 255, 255))
        self.base_image = self.image.copy()
        self.button_colour = (100, 100, 100)
        draw.rect(self.image, self.button_colour, (0, 0, self.image.get_width(), self.height_ui))
        self.rect = self.image.get_rect(topright=self.pos)
        self.current_row = 0
        self.row_size = 0

    def create_new_image(self):
        percent_row = 0
        max_row = 100
        self.image = self.base_image.copy()
        if self.row_size:
            percent_row = self.current_row * 100 / self.row_size
            max_row = (self.current_row + self.max_row_show) * 100 / self.row_size
        max_row = max_row - percent_row
        draw.rect(self.image, self.button_colour,
                  (0, int(self.height_ui * percent_row / 100), self.image.get_width(),
                   int(self.height_ui * max_row / 100)))

    def change_image(self, new_row=None, row_size=None):
        """New row is input of scrolling by user to new row, row_size is changing based on adding more log or clear"""
        if row_size is not None:
            self.row_size = row_size
        if new_row is not None:  # accept from both wheeling scroll and drag scroll bar
            self.current_row = new_row
        self.create_new_image()

    def player_input(self, mouse_pos, mouse_scroll_up=False, mouse_scroll_down=False):
        """Player input update via click or scrolling"""
        if mouse_pos and self.mouse_over:
            mouse_value = (mouse_pos[1] - self.pos[
                1]) * 100 / self.height_ui  # find what percentage of mouse_pos at the scroll bar (0 = top, 100 = bottom)
            if mouse_value > 100:
                mouse_value = 100
            if mouse_value < 0:
                mouse_value = 0
            new_row = int(self.row_size * mouse_value / 100)
            if self.row_size > self.max_row_show and new_row > self.row_size - self.max_row_show:
                new_row = self.row_size - self.max_row_show
            if self.row_size > self.max_row_show:  # only change scroll position in list longer than max length
                self.change_image(new_row)
            return self.current_row


class CharacterInteractPrompt(UIBattle):
    def __init__(self, image):
        """Weak button prompt that indicate player can talk to target"""
        self._layer = 9999999999999999998
        UIBattle.__init__(self, player_cursor_interact=False)
        self.character = None
        self.target = None
        self.target_pos = None
        self.button_image = image
        font = self.game.character_name_talk_prompt_font
        text_surface = text_render_with_bg("Talk", font)
        self.image = Surface((150 * self.screen_scale[0], 55 * self.screen_scale[1]), SRCALPHA)
        text_rect = text_surface.get_rect(midright=self.image.get_rect().midright)
        self.image.blit(text_surface, text_rect)
        self.image.blit(image, image.get_rect(midleft=self.image.get_rect().midleft))

        self.rect = self.image.get_rect(center=(0, 0))

    def add_to_screen(self, character, target, target_pos):
        self.character = character
        self.target_pos = target_pos
        self.target = target
        text_surface = text_render_with_bg(target.name, self.game.character_name_talk_prompt_font)
        self.image = Surface((text_surface.get_width() + self.button_image.get_width() +
                              (10 * self.screen_scale[0]), 55 * self.screen_scale[1]), SRCALPHA)
        text_rect = text_surface.get_rect(midright=self.image.get_rect().midright)
        self.image.blit(text_surface, text_rect)
        self.image.blit(self.button_image, self.button_image.get_rect(midleft=self.image.get_rect().midleft))

        self.rect = self.image.get_rect(midbottom=(self.target_pos[0] * self.screen_scale[0],
                                                   self.target_pos[1] * self.screen_scale[1]))
        if self not in self.battle.battle_camera_ui_drawer:
            self.battle.battle_camera_ui_drawer.add(self)
            self.battle.battle_effect_updater.add(self)

    def update(self, *args):
        if self.target_pos and not 100 < abs(self.character.base_pos[0] - self.target_pos[0]) < 250:
            # check if player move too far from current target prompt
            self.clear()

    def clear(self):
        self.character = None
        self.target = None
        self.target_pos = None
        if self in self.battle.battle_camera_ui_drawer:
            self.battle.battle_camera_ui_drawer.remove(self)
            self.battle.battle_effect_updater.remove(self)


class CharacterSpeechBox(UIBattle):
    images = {}
    simple_font = False

    def __init__(self, character, text, specific_timer=None, player_input_indicator=False, cutscene_event=None,
                 add_log=None, voice=False, font_size=60, max_text_width=800):
        """Speech box that appear from character head"""
        self._layer = 9999999999999999998
        UIBattle.__init__(self, player_cursor_interact=False, has_containers=True)
        font = "talk_font"
        if self.simple_font:
            font = "simple"

        self.font_size = int(font_size * self.screen_scale[1])
        self.font = Font(self.ui_font[font], self.font_size)
        max_text_width *= self.screen_scale[0]

        # Find text height, using code from make_long_text
        start_pos = (0, self.font_size / 3)
        true_max_width = start_pos[0]
        x, y = start_pos[0], start_pos[1]
        words = [word.split(" ") for word in
                 str(text).splitlines()]  # 2D array where each row is a list of words
        space = self.font.size(" ")[0]  # the width of a space
        exceed_max_width = False
        for line in words:
            for word in line:
                word_surface = self.font.render(word, True, (0, 0, 0))
                word_width, word_height = word_surface.get_size()
                if x + word_width >= max_text_width:
                    exceed_max_width = True
                    x = self.font_size  # reset x
                    y += word_height  # start on new row.
                if not exceed_max_width:
                    true_max_width += word_width + space
                x += word_width + space
            x = self.font_size  # reset x
            y += word_height  # start on new row

        self.text_surface = Surface((true_max_width, y), SRCALPHA)

        self.text_surface.fill((224, 224, 224))
        make_long_text(self.text_surface, text, start_pos, self.font)

        start_top = self.images["speech_start_top"]
        start_mid = smoothscale(self.images["speech_start_mid"], (self.images["speech_start_mid"].get_width(),
                                                                  self.text_surface.get_height()))
        start_bottom = self.images["speech_start_bottom"]

        end_top = self.images["speech_end_top"]
        end_mid = smoothscale(self.images["speech_end_mid"], (self.images["speech_end_mid"].get_width(),
                                                              self.text_surface.get_height()))
        end_bottom = self.images["speech_end_bottom"]

        body_top = smoothscale(self.images["speech_body_top"], (self.text_surface.get_width(),
                                                                self.images["speech_body_top"].get_height()))
        body_bottom = smoothscale(self.images["speech_body_bottom"], (self.text_surface.get_width(),
                                                                      self.images["speech_body_bottom"].get_height()))

        self.base_image = Surface((self.text_surface.get_width() + start_top.get_width() + end_top.get_width(),
                                   self.text_surface.get_height() + start_top.get_height() + start_bottom.get_height()),
                                  SRCALPHA)

        start_top_rect = start_top.get_rect(topleft=(0, 0))
        self.base_image.blit(start_top, start_top_rect)

        start_bottom_rect = start_bottom.get_rect(bottomleft=(0, self.base_image.get_height()))
        self.base_image.blit(start_bottom, start_bottom_rect)

        start_mid_rect = start_mid.get_rect(topleft=(0, start_top_rect.height))
        self.base_image.blit(start_mid, start_mid_rect)

        end_top_rect = end_top.get_rect(topright=(self.base_image.get_width(), 0))
        self.base_image.blit(end_top, end_top_rect)

        end_bottom_rect = end_bottom.get_rect(bottomright=(self.base_image.get_width(), self.base_image.get_height()))
        self.base_image.blit(end_bottom, end_bottom_rect)

        end_mid_rect = end_mid.get_rect(topright=(self.base_image.get_width(), end_top_rect.height))
        self.base_image.blit(end_mid, end_mid_rect)

        body_top_rect = body_top.get_rect(topleft=(start_top_rect.width, 0))
        self.base_image.blit(body_top, body_top_rect)

        body_bottom_rect = body_bottom.get_rect(bottomleft=(start_bottom_rect.width, self.base_image.get_height()))
        self.base_image.blit(body_bottom, body_bottom_rect)

        self.right_image = self.base_image.copy()
        self.left_image = flip(self.base_image, 1, 0)

        text_rect = self.text_surface.get_rect(topleft=start_mid_rect.topright)
        self.right_image.blit(self.text_surface, text_rect)

        text_rect = self.text_surface.get_rect(topright=(self.base_image.get_width() - start_mid_rect.topright[0],
                                                         start_mid_rect.topright[1]))
        self.left_image.blit(self.text_surface, text_rect)

        if player_input_indicator:  # add player weak button indicate for closing speech in cutscene
            rect = self.images["button_weak"].get_rect(topleft=(0, text_rect.height * 1.2))
            self.left_image.blit(self.images["button_weak"], rect)

            rect = self.images["button_weak"].get_rect(topright=(self.base_image.get_width(),
                                                                 text_rect.height * 1.2))
            self.right_image.blit(self.images["button_weak"], rect)

        self.character = character
        self.character.speech = self
        self.player_input_indicator = player_input_indicator
        self.cutscene_event = cutscene_event
        self.base_pos = self.character.base_pos.copy()
        self.finish_unfolding = False
        self.current_length = start_top.get_width()

        self.max_length = self.base_image.get_width()  # max length of the body, not counting the end corner

        self.base_image = self.right_image
        self.image = self.base_image.subsurface((0, 0, self.current_length, self.base_image.get_height()))
        self.rect = self.image.get_rect(midleft=self.character.rect.center)

        if voice:
            self.battle.add_sound_effect_queue(choice(self.battle.sound_effect_pool[voice[0]]),
                                               self.battle.camera_pos, voice[1],
                                               voice[2], volume="voice")
        elif voice is False:  # None will play no sound
            self.battle.add_sound_effect_queue(choice(self.battle.sound_effect_pool["Parchment_write"]),
                                               self.battle.camera_pos, 1000,
                                               0, volume="voice")

        if specific_timer:
            self.timer = specific_timer
        else:
            self.timer = 3
            if len(text) > 20:
                self.timer += int(len(text) / 20)
        if add_log:
            self.battle.save_data.save_profile["dialogue log"].append(
                ("(" + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + ")" +
                 " Mission " + self.battle.mission + " " +
                 self.character.name + ": ", add_log))
            if len(self.battle.save_data.save_profile["dialogue log"]) > 500:
                self.battle.save_data.save_profile["dialogue log"] = self.battle.save_data.save_profile["dialogue log"][
                                                                     1:]

    def update(self, dt):
        """Play unfold animation and blit text at the end"""
        direction_left = False
        # always use p1 head to place speak
        head_rect = (
        (self.character.pos[0] + (self.character.current_animation_direction["head"][0] * self.screen_scale[0])),
        (self.character.pos[1] + (self.character.current_animation_direction["head"][1] * self.screen_scale[1])))
        if self.character.direction == "left":  # left direction facing
            if self.character.rect.topleft[0] - (
                    self.battle.shown_camera_pos[0] - self.battle.camera.camera_w_center) < self.base_image.get_width():
                self.base_image = self.right_image
                self.rect = self.image.get_rect(bottomleft=head_rect)
            else:
                # text will exceed screen, go other way
                direction_left = True
                self.base_image = self.left_image
                self.rect = self.image.get_rect(bottomright=head_rect)

        else:  # right direction facing
            if (self.battle.shown_camera_pos[0] + self.battle.camera.camera_w_center) - \
                    self.character.rect.topright[0] < self.base_image.get_width():
                # text will exceed screen, go other way
                direction_left = True
                self.base_image = self.left_image
                self.rect = self.image.get_rect(bottomright=head_rect)
            else:
                self.base_image = self.right_image
                self.rect = self.image.get_rect(bottomleft=head_rect)

        if self.rect.midtop[1] < 0:  # exceed top scene
            self.rect = self.image.get_rect(midtop=(self.rect.midtop[0], 0))

        if self.current_length < self.max_length:  # keep unfolding if not yet reach max length
            self.current_length += self.max_length * dt
            if self.current_length > self.max_length:
                self.current_length = self.max_length
            if direction_left:
                self.image = self.base_image.subsurface((self.max_length - self.current_length, 0,
                                                         self.current_length, self.image.get_height()))
            else:
                self.image = self.base_image.subsurface((0, 0, self.current_length, self.image.get_height()))

        else:  # finish animation, count down timer
            self.timer -= dt
            if self.timer <= 0:
                self.character.speech = None
                self.kill()
                return

        if not self.character.alive:  # kill speech if character die
            self.character.speech = None
            self.kill()
            return


class DamageNumber(UIBattle):
    image_cache = {team: {True: {}, False: {}} for team in team_colour}

    def __init__(self, value, pos, critical, team, move=True):
        self._layer = 9999999999999999997
        UIBattle.__init__(self, has_containers=True)
        self.move = move
        self.timer = 0.5
        if type(value) is str:
            self.timer = 1
        str_value = str(value)
        if str_value not in self.image_cache[team][critical]:
            if critical:
                self.image = text_render_with_bg(str_value, self.game.critical_damage_number_font,
                                                 gf_colour=team_colour[team])
            else:
                self.image = text_render_with_bg(str_value, self.game.damage_number_font,
                                                 gf_colour=team_colour[team])
            self.image_cache[team][critical][str_value] = self.image
        else:
            self.image = self.image_cache[team][critical][str_value]

        self.rect = self.image.get_rect(midbottom=pos)

    def update(self, dt):
        self.timer -= dt
        if self.move:
            self.rect.center = (self.rect.center[0], self.rect.center[1] - (dt * 200))
        if self.timer <= 0:
            self.kill()


#
# class WheelUI(UIBattle):
#     item_sprite_pool = None
#     choice_list_key = {"Down": 1, "Left": 2, "Up": 3, "Right": 4}
#     choice_key = tuple(choice_list_key.keys())
#
#     def __init__(self, images, pos):
#         """Wheel choice ui to select item"""
#         self._layer = 11
#         UIBattle.__init__(self)
#         self.small_font = Font(self.ui_font["main_button"], int(36 * self.screen_scale[1]))
#         self.font = Font(self.ui_font["main_button"], int(52 * self.screen_scale[1]))
#         self.pos = pos
#         self.choice_list = ()
#         self.selected = "Up"
#
#         self.wheel_button_image = images["wheel"]
#         self.wheel_selected_button_image = images["wheel_selected"]
#         self.wheel_text_image = images["wheel_text"]
#
#         self.base_image2 = Surface((self.wheel_button_image.get_width() * 5,
#                                     self.wheel_button_image.get_height() * 4), SRCALPHA)  # empty image
#         self.rect = self.base_image2.get_rect(midtop=self.pos)
#
#         image_center = (self.base_image2.get_width() / 2, self.base_image2.get_height() / 2)
#         self.wheel_image_with_stuff = []
#         self.wheel_selected_image_with_stuff = []
#         self.wheel_rect = []
#         angle_space = 360 / 4
#         angle = 0
#         for wheel_button in range(4):
#             base_target = Vector2(image_center[0] - (image_center[0] / 2 *
#                                                      sin(radians(angle))),
#                                   image_center[1] + (image_center[1] / 1.6 *
#                                                      cos(radians(angle))))
#             angle += angle_space
#
#             self.wheel_image_with_stuff.append(self.wheel_button_image.copy())
#             self.wheel_selected_image_with_stuff.append(self.wheel_selected_button_image.copy())
#             self.wheel_rect.append(self.wheel_button_image.get_rect(center=base_target))
#             self.base_image2.blit(self.wheel_image_with_stuff[wheel_button], self.wheel_rect[wheel_button])
#         self.image = self.base_image2.copy()
#
#     def selection(self, key_input):
#         self.selected = key_input
#         for index, rect in enumerate(self.wheel_rect):
#             if self.selected == self.choice_key[index]:
#                 self.image.blit(self.wheel_selected_image_with_stuff[index], rect)
#             else:
#                 self.image.blit(self.wheel_image_with_stuff[index], rect)
#             if index + 1 <= len(self.choice_list) and self.choice_list[index]:
#                 text_image = self.wheel_text_image.copy()  # blit text again to avoid wheel overlap old text
#                 if self.choice_list[index] in self.command_list.values():  # command
#                     text_surface = self.small_font.render(self.grab_text(("ui", self.choice_list[index])),
#                                                           True,
#                                                           (20, 20, 20))
#                 else:
#                     text_surface = text_render_with_bg(
#                         str(self.battle.player_objects[self.player].item_usage[self.choice_list[index]]),
#                         self.font)  # add item number
#                     self.wheel_image_with_stuff[index].blit(text_surface,
#                                                             text_surface.get_rect(topright=rect.topright))
#                     self.wheel_selected_image_with_stuff[index].blit(text_surface,
#                                                                      text_surface.get_rect(topright=rect.topright))
#
#                     text_surface = self.small_font.render(self.grab_text(("item", self.choice_list[index],
#                                                                           "Name")), True, (20, 20, 20))
#
#                 text_image.blit(text_surface, text_surface.get_rect(center=(text_image.get_width() / 2,
#                                                                             text_image.get_height() / 2)))
#
#                 self.image.blit(text_image, text_image.get_rect(center=self.wheel_rect[index].midbottom))
#
#     def change_text_icon(self, blit_list, item_wheel=False):
#         """Add icon or text to the wheel choice"""
#         self.image = self.base_image2.copy()
#         self.choice_list = blit_list
#         for index, value in enumerate(blit_list):
#             self.wheel_image_with_stuff[index] = self.wheel_button_image.copy()
#             self.wheel_selected_image_with_stuff[index] = self.wheel_selected_button_image.copy()
#             if value:  # Wheel choice with icon at center
#                 surface = self.item_sprite_pool[value]
#                 rect = surface.get_rect(center=(self.wheel_image_with_stuff[index].get_width() / 2,
#                                                 self.wheel_image_with_stuff[index].get_height() / 2))
#
#                 self.wheel_image_with_stuff[index].blit(surface, rect)
#                 self.wheel_selected_image_with_stuff[index].blit(surface, rect)
#
#                 if item_wheel:
#                     number_text_rect = surface.get_rect(center=(self.wheel_image_with_stuff[index].get_width() / 1.3,
#                                                                 self.wheel_image_with_stuff[index].get_height() / 2))
#                     text_surface = text_render_with_bg(str(self.battle.player_objects[self.player].item_usage[value]),
#                                                        self.font)  # add item number
#                     self.wheel_image_with_stuff[index].blit(text_surface,
#                                                             text_surface.get_rect(topright=number_text_rect.center))
#                     self.wheel_selected_image_with_stuff[index].blit(text_surface,
#                                                                      text_surface.get_rect(
#                                                                          topright=number_text_rect.center))
#
#                     text_surface = self.small_font.render(self.grab_text(("item", value, "Name")), True,
#                                                           (20, 20, 20))
#                 else:
#                     text_surface = self.small_font.render(self.grab_text(("ui", value)), True,
#                                                           (20, 20, 20))
#
#                 if self.selected == self.choice_key[index]:
#                     self.image.blit(self.wheel_selected_image_with_stuff[index], self.wheel_rect[index])
#                 else:
#                     self.image.blit(self.wheel_image_with_stuff[index], self.wheel_rect[index])
#                 text_image = self.wheel_text_image.copy()
#                 text_image.blit(text_surface, text_surface.get_rect(center=(text_image.get_width() / 2,
#                                                                             text_image.get_height() / 2)))
#
#                 self.image.blit(text_image, text_image.get_rect(center=self.wheel_rect[index].midbottom))


class Profiler(cProfile.Profile, UIBattle):

    def __init__(self):
        UIBattle.__init__(self, player_cursor_interact=False)
        self.size = (1200, 600)
        self.image = Surface(self.size)
        self.rect = Rect((0, 0, *self.size))
        self.font = Font(self.ui_font["main_button"], 16)
        self._layer = 12
        self.visible = False
        self.empty_image = Surface((0, 0))

    def refresh(self):
        import io
        from pstats import Stats

        # There should be a way to hide/show something using the sprite api but
        # I didn't get it to work so I did this solution instead

        if self.visible:
            self.image = Surface(self.size)
            s_io = io.StringIO()
            stats = Stats(self, stream=s_io)
            stats.sort_stats('tottime').print_stats(20)
            info_str = s_io.getvalue()
            self.enable()  # profiler must be re-enabled after get stats
            self.image.fill(0x112233)
            self.image.blit(self.font.render("press F7 to clear times", True, Color("white")), (0, 0))
            for e, line in enumerate(info_str.split("\n"), 1):
                self.image.blit(self.font.render(line, True, Color("white")), (0, e * 20))
        else:
            self.image = self.empty_image

    def switch_show_hide(self):
        self.visible = not self.visible
        self.refresh()
