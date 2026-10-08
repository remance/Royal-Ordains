import cProfile
from datetime import datetime
from random import choice

import pygame
from pygame import Vector2, Surface, SRCALPHA, Color, Rect, draw, mouse
from pygame.font import Font
from pygame.key import name as pygame_key_name
from pygame.transform import flip

from engine.battle.player_input_battle import key_select_strategy
from engine.constants import *
from engine.uimenu.uimenu import UIMenu, MenuCursor, BoxUI
from engine.utils.common import keyboard_mouse_press_check
from engine.utils.text_making import text_render_with_bg, text_render_with_texture, \
    make_long_text, shorten_number, add_comma_number


class UIOuterBattle(UIMenu):
    def __init__(self, player_cursor_interact=True, has_containers=False):
        """
        Parent class for all battle menu user interface that exist outside of battle camera
        """
        from engine.battle.battle import Battle
        UIMenu.__init__(self, player_cursor_interact=player_cursor_interact, has_containers=has_containers)
        self.battle = Battle.battle
        self.cursor = Battle.battle_cursor  # use battle cursor for battle ui
        self.outer_ui_updater = self.battle.outer_ui_updater
        self.text_popup = self.battle.text_popup
        self.max_description_box_width = int(1000 * self.screen_scale_width)


class ButtonUI(UIOuterBattle):
    def __init__(self, image, layer=11):
        self._layer = layer
        UIOuterBattle.__init__(self)
        self.pos = (0, 0)
        self.image = image
        self.rect = self.image.get_rect(center=self.pos)
        self.mouse_over = False

    def change_pos(self, pos):
        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)


class BattleCursor(UIOuterBattle, MenuCursor):
    def __init__(self, images):
        """Game battle cursor"""
        self._layer = 999999999999  # as high as possible, always blit last
        MenuCursor.__init__(self, images)
        UIOuterBattle.__init__(self)

    def update(self, dt):
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


class ScreenFade(UIOuterBattle):
    def __init__(self):
        self._layer = 99
        UIOuterBattle.__init__(self)
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
            font_size = int(font_size * self.screen_scale_height)
            image_height = int((self.font.size(self.text)[0]) / self.max_text_width)
            if not image_height:  # only one line
                self.text_surface = text_render_with_texture(self.text, self.font,
                                                             self.font_texture[self.use_font_texture])
            else:
                self.text_surface = make_long_text(text, (font_size, font_size), self.font,
                                                   with_texture=(self.font_texture[self.use_font_texture], None),
                                                   specific_width=self.max_text_width, alignment="center")

            self.text_rect = self.text_surface.get_rect(center=self.image.get_rect().center)
            if not text_fade_in:
                self.image.blit(self.text_surface, self.text_rect)
        self.image.set_alpha(self.alpha)

    def update(self, dt):
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


class Command(UIOuterBattle):
    number_respond_text_cache = {}
    number_cooldown_text_cache = {}
    stat_cache = {}

    def __init__(self, call_count_image, air_count_image):
        self._layer = 9
        UIOuterBattle.__init__(self)
        self.character_list = self.battle.character_list
        self.character_portraits = self.battle.character_portraits
        self.number_font = self.game.character_indicator_font
        self.number_text_cache = self.font_text_cache[self.number_font]
        self.image = Surface((800 * self.screen_scale_width, 400 * self.screen_scale_height), SRCALPHA)
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
        self.broken_icon = Surface((100 * self.screen_scale_width, 100 * self.screen_scale_height), SRCALPHA)
        self.supply_text_bg = Surface((240 * self.screen_scale_width, 120 * self.screen_scale_height))
        self.supply_text_bg.blit(self.grand_ui_images["supply"], (0, 0))
        self.supply_text_bg.blit(self.grand_ui_images["supply_reserve"],
                                 self.grand_ui_images["supply_reserve"].get_rect(
                                     bottomleft=(0, self.supply_text_bg.get_height())))
        self.supply_text_bg_rect = self.supply_text_bg.get_rect(topright=(self.image.get_width(), 0))
        draw.rect(self.broken_icon, (0, 0, 0),
                  (30 * self.screen_scale_width, 30 * self.screen_scale_height,
                   10 * self.screen_scale_width, 60 * self.screen_scale_width))
        draw.rect(self.broken_icon, (255, 255, 255),
                  (40 * self.screen_scale_width, 30 * self.screen_scale_height,
                   40 * self.screen_scale_width, 30 * self.screen_scale_width))

        self.air_return_icon = Surface((100 * self.screen_scale_width, 100 * self.screen_scale_height), SRCALPHA)
        draw.circle(self.air_return_icon, (200, 70, 70),
                    (self.air_return_icon.get_width() / 2, self.air_return_icon.get_height() / 2),
                    (self.air_return_icon.get_width() / 2.5), width=int(8 * self.screen_scale_width))

        self.air_active_icon = Surface((100 * self.screen_scale_width, 100 * self.screen_scale_height), SRCALPHA)
        draw.circle(self.air_active_icon, (200, 200, 0),
                    (self.air_active_icon.get_width() / 2, self.air_active_icon.get_height() / 2),
                    (self.air_active_icon.get_width() / 2.5), width=int(8 * self.screen_scale_width))

        self.dead_icon = Surface((100 * self.screen_scale_width, 100 * self.screen_scale_height), SRCALPHA)
        draw.circle(self.dead_icon, (0, 0, 0),
                    (self.dead_icon.get_width() / 2, self.dead_icon.get_height() / 2),
                    (self.dead_icon.get_width() / 2.5))

        self.call_cooldown_icon = Surface((75 * self.screen_scale_width, 75 * self.screen_scale_height), SRCALPHA)
        draw.circle(self.call_cooldown_icon, (0, 0, 0, 200),
                    (self.call_cooldown_icon.get_width() / 2, self.call_cooldown_icon.get_height() / 2),
                    (self.call_cooldown_icon.get_width() / 2))

        self.font = self.game.generic_ui_font
        self.player_air_group_number = [None, None, None, None, None]
        self.air_group_health = [None, None, None, None, None]
        self.air_group_resource = [None, None, None, None, None]
        self.air_bar_width = 100 * self.screen_scale_width
        self.air_bar_height = 15 * self.screen_scale_width
        self.icon_status = {}
        self.leader_call_pool = []
        self.troop_call_pool = []
        self.player_air_group = []
        self.supply_status = ()
        self.leader_call_pool_status = {index: (None, None) for index in range(3)}
        self.troop_call_pool_status = {index: (None, None) for index in range(5)}
        self.call_pool_status = (self.leader_call_pool_status, self.troop_call_pool_status)

        self.base_image = self.image.copy()

        scaled_pos = 150 * self.screen_scale_width
        self.leader_portrait_rect = {index: self.broken_icon.get_rect(center=(scaled_pos + (
                index * 140 * self.screen_scale_width), 50 * self.screen_scale_height)) for index in range(3)}
        scaled_pos = 100 * self.screen_scale_width
        self.ground_portrait_rect = {index: self.broken_icon.get_rect(center=(scaled_pos + (
                index * 140 * self.screen_scale_width), 180 * self.screen_scale_height)) for index in range(5)}
        self.pool_index_rects = [self.leader_portrait_rect, self.ground_portrait_rect]
        self.air_portrait_rect = {index: self.broken_icon.get_rect(center=(scaled_pos + (
                index * 140 * self.screen_scale_width), 300 * self.screen_scale_height)) for index in range(5)}

    def setup(self):
        self.player_team = self.battle.player_team
        self.player_team_stat = self.battle.team_state[self.player_team]
        self.player_enemy_team = self.battle.player_enemy_team
        self.player_air_group = self.player_team_stat["air_group"]
        self.check_air_group = None
        self.supply_status = ()

    def update(self, dt):
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

                image = self.image
                new_supply_status = (shorten_number(int(self.player_team_stat["supply_resource"])),
                                     shorten_number(int(self.player_team_stat["supply_reserve"])))
                if self.supply_status != new_supply_status:
                    self.supply_status = new_supply_status
                    image.blit(self.supply_text_bg, self.supply_text_bg_rect)

                    text = text_render_with_bg(new_supply_status[0], self.number_font)
                    image.blit(text, text.get_rect(topright=self.supply_text_bg_rect.topright))

                    text = text_render_with_bg(new_supply_status[1], self.number_font)
                    image.blit(text, text.get_rect(bottomright=self.supply_text_bg_rect.bottomright))

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
                            image.blit(self.character_portraits[char_id]["mini"]["right"], pool_rect[index])
                            if state[1]:
                                state.append(call_cooldown_status[index])
                            if state[1] or not state[2]:  # can't call because in cooldown or not enough supply
                                image.blit(self.call_cooldown_icon,
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
                                    image.blit(number_text,
                                               number_text.get_rect(center=pool_rect[index].center))

                            if char_number_reserve not in self.number_text_cache:
                                number_text = text_render_with_bg(str(char_number_reserve),
                                                                  self.number_font, o_colour=(200, 200, 100))
                                self.number_text_cache[char_number_reserve] = number_text
                            else:
                                number_text = self.number_text_cache[char_number_reserve]
                            number_rect = number_text.get_rect(
                                midbottom=self.pool_index_rects[pool_index][index].bottomright)
                            image.blit(self.call_count_image,
                                       self.call_count_image.get_rect(center=number_rect.center))
                            image.blit(number_text, number_rect)

                for index, air_group in enumerate(self.player_air_group):
                    # add air unit group
                    portrait_rect = self.air_portrait_rect[index]
                    portrait_rect_bottomleft = portrait_rect.bottomleft

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
                            image.blit(air_group[0].command_icon, portrait_rect)
                        else:  # air group completely dead, blit black circle over
                            image.blit(self.dead_icon, portrait_rect)
                        self.air_group_rect[index] = portrait_rect
                        if check[0]:  # returning
                            image.blit(self.air_return_icon, portrait_rect)
                        elif check[1]:  # active
                            image.blit(self.air_active_icon, portrait_rect)
                        if check[2]:  # number in group change
                            self.player_air_group_number[index] = len(air_group)

                        if len(air_group) not in self.number_text_cache:
                            number_text = text_render_with_bg(str(len(air_group)),
                                                              self.number_font, o_colour=(200, 200, 100))
                            self.number_text_cache[len(air_group)] = number_text
                        else:
                            number_text = self.number_text_cache[len(air_group)]
                        number_rect = number_text.get_rect(midtop=portrait_rect.topleft)
                        image.blit(self.air_count_image,
                                   self.air_count_image.get_rect(center=number_rect.center))
                        image.blit(number_text, number_rect)

                    if self.air_group_health[index] != health_bar_percentage:
                        self.air_group_health[index] = health_bar_percentage
                        image.fill((0, 0, 0), (portrait_rect_bottomleft[0], portrait_rect_bottomleft[1],
                                               self.air_bar_width, self.air_bar_height))
                        image.fill((250, 100, 100), (portrait_rect_bottomleft[0], portrait_rect_bottomleft[1],
                                                     self.air_bar_width * health_bar_percentage[1],
                                                     self.air_bar_height))
                        image.fill((100, 20, 20, 125), (portrait_rect_bottomleft[0], portrait_rect_bottomleft[1],
                                                        self.air_bar_width * health_bar_percentage[0],
                                                        self.air_bar_height))

                    if self.air_group_resource[index] != resource_bar_percentage:
                        self.air_group_resource[index] = resource_bar_percentage
                        self.image.fill((0, 0, 0), (portrait_rect_bottomleft[0],
                                                    portrait_rect_bottomleft[1] + self.air_bar_height,
                                                    self.air_bar_width, self.air_bar_height))
                        self.image.fill((100, 250, 100), (portrait_rect_bottomleft[0],
                                                          portrait_rect_bottomleft[1] + self.air_bar_height,
                                                          self.air_bar_width * resource_bar_percentage[1],
                                                          self.air_bar_height))
                        self.image.fill((20, 100, 20, 125), (portrait_rect_bottomleft[0],
                                                             portrait_rect_bottomleft[1] + self.air_bar_height,
                                                             self.air_bar_width * resource_bar_percentage[0],
                                                             self.air_bar_height))

            if UIMenu.update(self, dt):
                inside_mouse_pos = Vector2(
                    (self.cursor.pos[0] - self.rect.topleft[0]),
                    (self.cursor.pos[1] - self.rect.topleft[1]))
                for index, rect in self.leader_portrait_rect.items():
                    if rect.collidepoint(inside_mouse_pos):
                        if index < len(self.leader_call_pool):
                            character = self.leader_call_pool[index][0]
                            self.popup_description("Call Leader " + str(index + 1),
                                                   self.leader_call_pool[index][1], character)
                            if self.event_press:  # call leader
                                self.battle.call_reinforcement(self.player_team, "leader", index)
                        return

                for index, rect in self.ground_portrait_rect.items():
                    if rect.collidepoint(inside_mouse_pos):
                        if index < len(self.troop_call_pool):
                            character = self.troop_call_pool[index][0]
                            self.popup_description("Call Troop " + str(index + 1),
                                                   self.troop_call_pool[index][1], character)
                            if self.event_press:  # call ground troop
                                self.battle.call_reinforcement(self.player_team, "troop", index)
                            return

                for air_group, rect in self.air_group_rect.items():
                    if rect.collidepoint(inside_mouse_pos):
                        self.popup_description("Call Air " + str(air_group + 1),
                                               None, self.player_air_group[air_group][0].char_id)
                        if self.event:
                            if self.event_press:  # call air group
                                # active or completely dead air group cannot be activated
                                if self.player_air_group_number[air_group]:
                                    self.battle.call_in_air_group(self.player_team, (air_group,),
                                                                  self.battle.team_state[self.player_enemy_team][
                                                                      "start_pos"])
                            elif self.event_alt_press:
                                if (self.player_air_group_number[air_group] and
                                        any([air_character.active for air_character in
                                             self.player_air_group[air_group]])):
                                    # right click on active air group order it to exit the battle
                                    for character in self.player_air_group[air_group]:
                                        if character.alive:
                                            character.issue_commander_order(("back", character.retreat_pos))
                        return

    def popup_description(self, call_shortcut_name, call_remain, character):
        if character not in self.stat_cache:
            grab_text = self.grab_text
            character_data = self.character_list[character]
            char_stat = [grab_text(("ui", "info_header_name")) + grab_text(("character", character, "Name")),
                         grab_text(("ui", "info_header_call_keybind")) +
                         pygame_key_name(self.battle.player_key_bind[call_shortcut_name]),
                         grab_text(("character", character, "Description")),
                         grab_text(("ui", "info_header_class")) + grab_text(
                             ("ui", "class_" + character_data["Class"])),
                         grab_text(("ui", "info_header_supply_cost")) + add_comma_number(
                             character_data["Supply"]),
                         grab_text(("ui", "info_header_call_cooldown")) + str(character_data["Reinforce Time"]),
                         grab_text(("ui", "info_header_call_response")) + str(
                             character_data["Respond Time"])]
        else:
            char_stat = self.stat_cache[character]
        if call_remain:
            char_stat.append(grab_text(("ui", "info_header_call_remain")) + str(call_remain))
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


class FPSCount(UIOuterBattle):
    def __init__(self, parent):
        self._layer = 99999999999999999999999999999999999
        UIOuterBattle.__init__(self, player_cursor_interact=False)
        self.image = Surface((80 * self.screen_scale_width, 40 * self.screen_scale_height), SRCALPHA)
        self.base_image = self.image.copy()
        self.font = self.game.fps_counter_font
        self.clock = parent.clock
        fps_text = self.font.render("60", True, (255, 60, 60))
        self.text_rect = fps_text.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.rect = self.image.get_rect(topleft=(0, 0))

    def update(self, dt):
        """Update current fps"""
        self.image = self.base_image.copy()
        fps = str(int(self.clock.get_fps()))
        fps_text = self.font.render(fps, True, (255, 60, 60))
        self.image.blit(fps_text, self.text_rect)


class BattleScale(UIOuterBattle):
    def __init__(self, pos):
        self._layer = 12
        UIOuterBattle.__init__(self, player_cursor_interact=False)
        self.battle_scale = None
        self.image = Surface((2200 * self.screen_scale_width, 40 * self.screen_scale_height))
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, dt):
        if self.battle_scale != self.battle.battle_scale:
            self.battle_scale = self.battle.battle_scale
            width = self.width
            height = self.height
            if self.battle_scale:
                percent_scale = 0  # start point fo fill colour of team scale
                for team, value in enumerate(self.battle_scale):
                    if value > 0:
                        self.image.fill(team_colour[team],
                                        (width * percent_scale,
                                         0, width, height))
                        percent_scale += value
            else:
                self.image.fill((0, 0, 0), (0, 0, width, height))


class EventNotification(UIOuterBattle):
    event_icons = {}

    def __init__(self, pos):
        self._layer = 5
        UIOuterBattle.__init__(self, player_cursor_interact=False)
        self.font = self.game.medium_generic_ui_font
        self.header_font = self.game.large_generic_ui_font
        self.image = Surface((0 * self.screen_scale_width, 0 * self.screen_scale_height))
        self.event_item_height = 100 * self.screen_scale_height
        self.image.fill((0, 200, 50))
        self.image_width = 800 * self.screen_scale_width
        self.base_image = self.image.copy()
        self.active_events = []
        self.rect = self.image.get_rect(topleft=pos)

    def add_event(self, event):
        self.active_events.append([event, 4])  # each event got shown for 4 second before removed
        if len(self.active_events) < 7:  # update image when add new event that will get shown right away
            self.update_image()

    def update_image(self):
        self.image = Surface((self.image_width,
                              len(self.active_events[:6]) * self.event_item_height), SRCALPHA)
        for index, event in enumerate(self.active_events[:6]):  # show only max 6 items
            event = event[0]
            event_icon = self.event_icons[event[0]]
            self.image.blit(event_icon, event_icon.get_rect(topleft=(0, index * self.event_item_height)))

            event_text = text_render_with_bg(event[1], self.font)
            self.image.blit(event_text, event_text.get_rect(topleft=(100 * self.screen_scale_width,
                                                                     index * self.event_item_height)))

            draw.line(self.image, (0, 0, 0), (0, index * self.event_item_height),
                      (self.image_width, index * self.event_item_height))

    def reset(self):
        self.active_events = []
        self.image = Surface((0 * self.screen_scale_width, 0 * self.screen_scale_height))

    def update(self, dt):
        image_update = False
        for event in tuple(self.active_events[:6]):
            event[1] -= dt
            if event[1] < 0:
                image_update = True
                self.active_events.remove(event)
        if image_update:
            self.update_image()


class BattleHelper(UIOuterBattle):
    def __init__(self, weather_icon_images, helper_ui_image, helper_ui_base_image, helper_images, time_choice_images,
                 time_select_images):
        self._layer = 12
        UIOuterBattle.__init__(self)
        self.font = self.game.battle_timer_font
        self.image = Surface((800 * self.screen_scale_width, 400 * self.screen_scale_height), SRCALPHA)
        self.image.blit(helper_ui_image, helper_ui_image.get_rect(topright=(self.image.get_width(), 0)))

        self.helper_ui_base_image = helper_ui_base_image
        self.helper_ui_base_rect = helper_ui_base_image.get_rect(bottomleft=(0, self.image.get_height()))
        self.time_choice_images = time_choice_images
        self.time_select_images = time_select_images
        self.helper_images = helper_images

        self.base_image = self.image.copy()

        self.base_battle_timer_rect_center = (570 * self.screen_scale_width, 60 * self.screen_scale_height)
        time_choice_pos_x = 380 * self.screen_scale_width
        self.time_choice_rects = (
            time_choice_images[0].get_rect(center=(time_choice_pos_x, 55 * self.screen_scale_height)),
            time_choice_images[1].get_rect(center=(time_choice_pos_x, 110 * self.screen_scale_height)),
            time_choice_images[2].get_rect(center=(time_choice_pos_x, 165 * self.screen_scale_height)),
            time_choice_images[3].get_rect(center=(time_choice_pos_x, 215 * self.screen_scale_height)))

        self.helper_rect = self.helper_images["castle"]["normal"].get_rect(topleft=(50 * self.screen_scale_width, 0))
        self.helper_time_selector_rect = self.helper_images["castle"]["time_1"].get_rect(
            topleft=(150 * self.screen_scale_width, 0))
        self.time_option = 2
        self.time_text = None
        self.weather = None
        self.battle_state = "normal"
        self.battle_name = ""
        self.battle_info_text = ()
        self.weather_icon_images = weather_icon_images

        self.time_choice = (0, 0.5, 1, 3)

        self.rect = self.image.get_rect(topright=(self.screen_width, 0))

    def setup(self):
        self.battle_name = self.battle.battle_name
        self.time_text = None
        self.time_option = 2
        self.battle.game_speed = self.time_choice[self.time_option]
        self.reset_image()

    def battle_end(self, result):
        self.battle_state = result
        self.reset_image()

    def reset_image(self):
        """reset when require change state"""
        self.image = self.base_image.copy()
        image = self.image
        image.blit(self.helper_images[self.battle.player_culture]["time_" + str(self.time_option)],
                   self.helper_time_selector_rect)
        image.blit(self.helper_images[self.battle.player_culture][self.battle_state], self.helper_rect)
        image.blit(self.helper_ui_base_image, self.helper_ui_base_rect)

        for index, rect in enumerate(self.time_choice_rects):
            if index == self.time_option:
                image.blit(self.time_select_images[0], rect)
            else:
                image.blit(self.time_select_images[1], rect)
            image.blit(self.time_choice_images[index], rect)
        if self.weather:
            icon_image = self.weather_icon_images[self.weather]
            image.blit(icon_image,
                       icon_image.get_rect(center=(570 * self.screen_scale_width, 175 * self.screen_scale_height)))

    def update(self, dt):
        """Update battle time"""
        must_reset_image = False
        reset_inside_helper_image = False

        current_weather = self.battle.current_weather.weather_now
        if self.weather != current_weather:
            grab_text = self.grab_text
            self.weather = current_weather
            self.battle_info_text = (self.battle_name,
                                     "",
                                     grab_text(("ui", "info_header_weather")) +
                                     grab_text(("ui", "weather_strength_" + current_weather.split("_")[1])) +
                                     grab_text(("ui", "weather_" + current_weather.split("_")[0])))
            must_reset_image = True

        if UIMenu.update(self, dt):
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))
            helper_mouse_over = False
            for index, rect in enumerate(self.time_choice_rects):
                if rect.collidepoint(inside_mouse_pos):
                    helper_mouse_over = True
                    if self.event_press:
                        self.time_option = index
                        if self.battle.game_speed != self.time_choice[index]:
                            self.battle.game_speed = self.time_choice[index]
                            must_reset_image = True
                    break
            if not helper_mouse_over:
                self.text_popup.popup(("topright", self.rect.bottomright), self.battle_info_text,
                                      width_text_wrapper=self.max_description_box_width)
                self.outer_ui_updater.add(self.text_popup)
        if must_reset_image:
            self.reset_image()

        time_text = datetime.fromtimestamp(self.battle.battle_time).strftime('%M:%S')
        if time_text != self.time_text or must_reset_image or reset_inside_helper_image:
            self.time_text = time_text
            text = text_render_with_bg(time_text, self.font)
            text_bg = Surface((text.get_size()))
            text_bg.fill((213, 209, 210))
            text_bg.blit(text, text.get_rect(topleft=(0, 0)))
            self.image.blit(text_bg, text.get_rect(center=self.base_battle_timer_rect_center))


class TacticalMap(UIOuterBattle):
    def __init__(self, tactic_alert_image):
        self._layer = 10
        UIOuterBattle.__init__(self)
        self.tactic_alert_image = tactic_alert_image
        self.all_team_ally = self.battle.all_team_ally
        self.battle_camera_object_drawer = self.battle.battle_camera_object_drawer
        self.battle_camera = self.battle.camera
        self.player_team = 1
        self.update_timer = 0
        self.map_scale_width = 1
        self.base_image = Surface((2200 * self.screen_scale_width, 200 * self.screen_scale_height), SRCALPHA)
        self.base_image.fill((255, 255, 255, 125))
        self.air_icon_pos_y = 30 * self.screen_scale_height
        self.strategy_alert_pos_y = 80 * self.screen_scale_height
        self.ground_icon_pos_y = 190 * self.screen_scale_height
        self.ground_commander_icon_pos_y = 200 * self.screen_scale_height
        self.camera_border_image = None
        self.image = self.base_image.copy()
        self.image_width = self.image.get_width()
        self.image_height = self.image.get_height()
        self.current_strategy_base_range = None
        self.current_strategy_base_activate_range = None
        self.strategy_line_width = int(20 * self.screen_scale_width)
        self.rect = self.image.get_rect(midtop=(self.screen_width / 2, 0))
        self.strategy_status = []

        self.commander_icon_border = {team: self.make_icon_border(team, colour_modifier=1.5) for
                                      team in team_colour}
        self.icon_width = self.commander_icon_border[1].get_width()
        self.icon_height = self.commander_icon_border[1].get_height()
        self.icon_center = (int(self.icon_width / 2), int(self.icon_height / 2))
        self.empty_command_icon = Surface((self.icon_width, self.icon_height), SRCALPHA)
        draw.circle(self.empty_command_icon, (30, 30, 30), self.icon_center,
                    (self.empty_command_icon.get_width() / 2))
        self.troop_dot_images = {}
        self.commander_health_state = {1: None, 2: None}
        self.commander_icon = {1: None, 2: None}
        for team, colour in team_colour.items():
            dot = Surface((20 * self.screen_scale_width, 20 * self.screen_scale_height))
            dot.fill(colour)
            self.troop_dot_images[team] = dot
        self.character_rect = {}

    def make_icon_border(self, team, colour_modifier=1):
        image = Surface((200 * self.screen_scale_width, 200 * self.screen_scale_height), SRCALPHA)
        if colour_modifier != 1:
            draw.circle(image, [value * colour_modifier if value * colour_modifier <= 255 else 255
                                for value in team_colour[team]], (image.get_width() / 2, image.get_height() / 2),
                        (image.get_width() / 2))
        else:
            draw.circle(image, team_colour[team], (image.get_width() / 2, image.get_height() / 2),
                        (image.get_width() / 2))

        return image

    def setup(self):
        self.commander_health_state = {1: None, 2: None}
        self.commander_icon = {1: None, 2: None}
        self.strategy_status = []
        self.player_team = self.battle.player_team
        self.map_scale_width = self.battle.base_stage_end / self.image_width
        self.camera_border_image = Surface((Default_Screen_Width / self.map_scale_width,
                                            200 * self.screen_scale_height), SRCALPHA)
        draw.rect(self.camera_border_image, (0, 0, 0), (0, 0, self.camera_border_image.get_width(), self.image_height),
                  width=int(15 * self.screen_scale_width))

    def warn_strategy(self, strategy_base_posx):
        """Add bell icon to warn where enemy use strategy"""
        self.battle.add_sound_effect_queue(choice(self.sound_effect_pool["alert"]),
                                           self.battle.base_camera_center_pos, 2000000, 0)
        self.strategy_status.append([strategy_base_posx / self.map_scale_width, 3])

    def update(self, dt):
        """update map"""
        battle = self.battle
        self.update_timer += battle.true_dt
        if self.update_timer > 0.05:
            self.image = self.base_image.copy()
            image = self.image
            map_scale_width = self.map_scale_width
            # Draw camera border
            image.blit(self.camera_border_image, self.camera_border_image.get_rect(
                topleft=(battle.base_camera_left_bound / map_scale_width, 0)))

            # draw commander
            team_commander = battle.team_commander
            for team, character in team_commander.items():
                if character and not character.invisible:
                    scaled_pos = (character.base_pos[0] / map_scale_width, self.ground_commander_icon_pos_y)
                    health_state = round(character.health / character.base_health, 1)
                    if health_state != self.commander_health_state[team]:
                        # circle also indicate health
                        back_icon = self.commander_icon_border[character.team].subsurface((
                            0, self.icon_height - (self.icon_height * health_state),
                            self.icon_width, self.icon_height - (self.icon_height * (1 - health_state))))
                        back_command_icon = self.empty_command_icon.copy()
                        back_command_icon.blit(back_icon, back_icon.get_rect(bottomleft=(0, self.icon_height)))
                        character_icon = character.icon[character.direction]
                        back_command_icon.blit(character_icon, character_icon.get_rect(center=self.icon_center))
                        self.commander_icon[team] = back_command_icon
                    image.blit(self.commander_icon[team], self.commander_icon[team].get_rect(midbottom=scaled_pos))

            # Draw character dots
            air_icon_pos_y = self.air_icon_pos_y
            ground_icon_pos_y = self.ground_icon_pos_y
            for team, character_team in self.all_team_ally.items():
                dot_image = self.troop_dot_images[team]
                for character in character_team:
                    if not character.invisible:
                        if character.character_type == "air":
                            image.blit(dot_image, dot_image.get_rect(midbottom=(
                                character.base_pos[0] / map_scale_width, air_icon_pos_y)))
                        elif not character.is_commander:
                            image.blit(dot_image, dot_image.get_rect(midbottom=(
                                character.base_pos[0] / map_scale_width, ground_icon_pos_y)))

            if battle.player_selected_strategy:
                # draw activation line
                line_start = ((team_commander[self.player_team].base_pos[
                                   0] - self.current_strategy_base_activate_range) /
                              map_scale_width)
                line_end = ((team_commander[self.player_team].base_pos[
                                 0] + self.current_strategy_base_activate_range) /
                            map_scale_width)
                if line_start < 0:
                    line_start = 0
                if line_end > self.image_width:
                    line_end = self.image_width
                draw.line(image, (80, 120, 200),
                          (line_start, 0),
                          (line_start, self.image_height), width=self.strategy_line_width)

                draw.line(image, (80, 120, 200),
                          (line_end, 0),
                          (line_end, self.image_height), width=self.strategy_line_width)

                if battle.player_interact.show_strategy_activate_line:
                    # draw strategy range if player cursor is within activation range, mean strategy can be used
                    line_start = (battle.base_cursor_pos[
                                      0] - self.current_strategy_base_range) / map_scale_width
                    line_end = (battle.base_cursor_pos[
                                    0] + self.current_strategy_base_range) / map_scale_width
                    if line_start < 0:
                        line_start = 0
                    if line_end > self.image_width:
                        line_end = self.image_width

                    draw.line(image, (120, 180, 80),
                              (line_start, 0),
                              (line_start, self.image_height), width=self.strategy_line_width)

                    draw.line(image, (120, 180, 80),
                              (line_end, 0),
                              (line_end, self.image_height), width=self.strategy_line_width)

            if self.strategy_status:
                for status in self.strategy_status:
                    status[1] -= self.update_timer
                    image.blit(self.tactic_alert_image,
                               self.tactic_alert_image.get_rect(center=(status[0],
                                                                        self.strategy_alert_pos_y)))

                    if status[1] <= 0:
                        self.strategy_status.remove(status)

            self.update_timer -= 0.1
        if UIMenu.update(self, dt):
            if self.event_press or self.event_alt_press:
                battle.camera_center_pos[0] = ((self.cursor.pos[0] - self.rect.topleft[0]) * self.map_scale_width *
                                               self.screen_scale_width)
                battle.fix_camera()


class StrategySelect(UIOuterBattle):
    icon_cache = {}
    strategy_text_list_cache = {}

    def __init__(self, pos, strategy_icons, resource_image):
        self._layer = 10
        UIOuterBattle.__init__(self)
        self.strategy_list = self.battle.strategy_list
        self.strategy_icons = strategy_icons
        self.font = self.game.battle_timer_font

        self.number_text_cache = self.font_text_cache[self.font]
        self.update_timer = 0
        self.strategy_status = {}
        self.base_resource_image = resource_image
        self.resource_image_center = (resource_image.get_width() / 2, resource_image.get_height() / 2)
        self.resource_text_rect = resource_image.get_rect(bottomright=(resource_image.get_width(),
                                                                       resource_image.get_height()))
        self.selected_strategy_icon = Surface((150 * self.screen_scale_width, 150 * self.screen_scale_height), SRCALPHA)
        draw.circle(self.selected_strategy_icon, (200, 200, 50),
                    (self.selected_strategy_icon.get_width() / 2, self.selected_strategy_icon.get_height() / 2),
                    (self.selected_strategy_icon.get_width() / 2), width=int(20 * self.screen_scale_width))

        self.cooldown_strategy_icon = Surface((150 * self.screen_scale_width, 150 * self.screen_scale_height), SRCALPHA)
        draw.circle(self.cooldown_strategy_icon, (0, 0, 0, 200),
                    (self.cooldown_strategy_icon.get_width() / 2, self.cooldown_strategy_icon.get_height() / 2),
                    (self.cooldown_strategy_icon.get_width() / 2))

        self.base_image = Surface((1250 * self.screen_scale_width, 150 * self.screen_scale_height), SRCALPHA)
        self.image = self.base_image.copy()
        self.image_width = self.image.get_width()
        self.image_height = self.image.get_height()
        self.rect = self.image.get_rect(midtop=pos)
        self.player_team = 1
        self.player_team_stat = None
        self.current_strategy_resource = None

        self.strategy_rect = {}

    def setup(self):
        self.player_team = self.battle.player_team
        self.player_team_stat = self.battle.team_state[self.player_team]
        self.strategy_status = {}
        self.strategy_rect = {}
        self.image = self.base_image.copy()
        if self.player_team:
            pos_x = 250 * self.screen_scale_width
            for index, strategy in enumerate(self.player_team_stat["strategy_cooldown"]):
                if strategy not in self.strategy_icons:
                    icon_image = self.strategy_icons["default"].copy()
                else:
                    icon_image = self.strategy_icons[strategy].copy()
                rect = icon_image.get_rect(midtop=(pos_x, 0))
                shortcut_text = text_render_with_bg(pygame.key.name(self.battle.player_key_bind[
                                                                        "Strategy " + str(index + 1)]).capitalize(),
                                                    self.font)
                text_rect = shortcut_text.get_rect(bottomright=(icon_image.get_width(), icon_image.get_height()))
                icon_image.blit(shortcut_text, text_rect)
                pos_x += 180 * self.screen_scale_width
                self.strategy_rect[index] = rect
                self.icon_cache[index] = icon_image

    def update(self, dt):
        if self.player_team:
            self.update_timer += self.battle.true_dt
            if self.update_timer > 0.1:
                image = self.image
                current_strategy_resource = int(self.player_team_stat["strategy_resource"])
                if self.current_strategy_resource != current_strategy_resource:
                    self.current_strategy_resource = current_strategy_resource
                    if current_strategy_resource not in self.number_text_cache:
                        text = text_render_with_bg(str(current_strategy_resource), self.font)
                        self.number_text_cache[current_strategy_resource] = text
                    else:
                        text = self.number_text_cache[current_strategy_resource]
                    resource_image = self.base_resource_image.copy()
                    resource_image.blit(text, text.get_rect(center=self.resource_image_center))
                    image.blit(resource_image, self.resource_text_rect)
                for index, strategy in enumerate(self.player_team_stat["strategy_cooldown"]):
                    cooldown = min(self.player_team_stat["strategy_cooldown"][strategy])
                    check = (cooldown, strategy == self.battle.player_selected_strategy)
                    if index not in self.strategy_status or self.strategy_status[index] != check:
                        self.strategy_status[index] = check
                        image.blit(self.icon_cache[index], self.strategy_rect[index])

                        if cooldown:  # in cooldown
                            cooldown = int(cooldown)
                            image.blit(self.cooldown_strategy_icon, self.strategy_rect[index])
                            if cooldown in self.number_text_cache:
                                number_text = self.number_text_cache[cooldown]
                            else:
                                number_text = text_render_with_bg(str(cooldown), self.font,
                                                                  gf_colour=(255, 255, 255),
                                                                  o_colour=(0, 0, 0))
                                self.number_text_cache[cooldown] = number_text
                            image.blit(number_text, number_text.get_rect(center=self.strategy_rect[index].center))
                        elif self.battle.player_selected_strategy and strategy == self.battle.player_selected_strategy:
                            image.blit(self.selected_strategy_icon, self.strategy_rect[index])
                self.update_timer -= 0.1

            if UIMenu.update(self, dt):
                inside_mouse_pos = Vector2(
                    (self.cursor.pos[0] - self.rect.topleft[0]),
                    (self.cursor.pos[1] - self.rect.topleft[1]))
                for index, rect in self.strategy_rect.items():
                    if rect.collidepoint(inside_mouse_pos):
                        this_strategy = tuple(self.player_team_stat["strategy_cooldown"].keys())[index]
                        if this_strategy not in self.strategy_text_list_cache:
                            grab_text = self.grab_text
                            strategy_stat = self.strategy_list[this_strategy]
                            text = (grab_text(("strategy", this_strategy, "Name")),
                                    grab_text(("strategy", this_strategy, "Description")),
                                    grab_text(("ui", "info_header_strategy_cost")) +
                                    str(strategy_stat["Resource Cost"]),
                                    grab_text(("ui", "info_header_activate_range")) +
                                    str(strategy_stat["Activate Range"]),
                                    grab_text(("ui", "info_header_strategy_range")) +
                                    str(strategy_stat["Range"])
                                    )
                            self.strategy_text_list_cache[this_strategy] = text
                        else:
                            text = self.strategy_text_list_cache[this_strategy]
                        self.text_popup.popup(self.rect.bottomleft, text,
                                              width_text_wrapper=self.max_description_box_width)
                        self.outer_ui_updater.add(self.text_popup)
                        if self.event_press:
                            if not min(tuple(self.player_team_stat["strategy_cooldown"].values())[index]):
                                key_select_strategy(self.battle, index)
                        break


class PlayerBattleInteract(UIOuterBattle):
    def __init__(self):
        self._layer = 9999999999999999999
        UIOuterBattle.__init__(self, player_cursor_interact=False)
        self.battle_camera = self.battle.camera
        self.battle_camera_image = self.battle_camera.image
        self.selection_start_pos = Vector2()
        self.current_pos = Vector2()
        self.line_size = int(10 * self.screen_scale_width)
        self.inner_line_size = int(20 * self.screen_scale_width)
        if self.line_size < 1:
            self.line_size = 1
        self.image = None
        self.rect = None
        self.current_strategy_base_range = None
        self.current_strategy_base_activate_range = None
        self.current_strategy_range = None
        self.current_strategy_activate_range = None
        self.strategy_line_top = 500 * self.screen_scale_height
        self.strategy_line_bottom = 2160 * self.screen_scale_height
        self.strategy_line_width = int(20 * self.screen_scale_width)
        self.strategy_line_inner_width = int(self.strategy_line_width / 2)
        self.strategy_line_center = 900 * self.screen_scale_height
        self.show_strategy_activate_line = False

    def reset(self):
        self.current_pos = None
        self.selection_start_pos = None
        self.rect = None

    def update(self, dt):
        self.event_press = False
        self.event_hold = False  # some UI differentiates between press release or holding, if not just use event
        self.event_alt_press = False
        self.event_alt_hold = True
        self.show_strategy_activate_line = False
        battle = self.battle
        if battle.player_team:
            cursor = self.cursor
            if not cursor.mouse_over:
                if cursor.is_alt_select_just_up:  # put alt (right) click first to prioritise it
                    self.event_alt_press = True
                    cursor.is_alt_select_just_up = False  # reset select button to prevent overlap interaction
                elif cursor.is_alt_select_down:
                    self.event_alt_hold = True
                    cursor.is_alt_select_just_down = False  # reset select button to prevent overlap interaction
                elif cursor.is_select_just_up:
                    self.event_press = True
                    cursor.is_select_just_up = False  # reset select button to prevent overlap interaction
                elif cursor.is_select_down:
                    self.event_hold = True
                    cursor.is_select_just_down = False  # reset select button to prevent overlap interaction
                else:  # no mouse activity
                    if battle.player_selected_strategy:
                        camera_image = self.battle_camera_image

                        # draw activation line
                        commander = battle.team_commander[battle.player_team]
                        if commander:
                            line_start = (commander.pos[0] - self.current_strategy_activate_range) - (
                                    battle.shown_camera_center_pos[0] - self.battle_camera.camera_w_center)
                            line_end = (commander.pos[0] + self.current_strategy_activate_range) - (
                                    battle.shown_camera_center_pos[0] - self.battle_camera.camera_w_center)
                            if line_start > 0:
                                draw.line(camera_image, (80, 120, 200),
                                          (line_start, self.strategy_line_top),
                                          (line_start, self.strategy_line_bottom), width=self.strategy_line_width)
                                draw.line(camera_image, (20, 70, 50),
                                          (line_start, self.strategy_line_top),
                                          (line_start, self.strategy_line_bottom), width=self.strategy_line_inner_width)
                            if line_end > 0:
                                draw.line(camera_image, (80, 120, 200),
                                          (line_end, self.strategy_line_top),
                                          (line_end, self.strategy_line_bottom), width=self.strategy_line_width)
                                draw.line(camera_image, (20, 70, 50),
                                          (line_end, self.strategy_line_top),
                                          (line_end, self.strategy_line_bottom), width=self.strategy_line_inner_width)

                            if not self.current_strategy_base_activate_range or \
                                    (abs(commander.base_pos[0] - battle.base_cursor_pos[0]) <
                                     self.current_strategy_base_activate_range):
                                self.show_strategy_activate_line = True

                                # draw strategy range if player cursor is within activation range, mean strategy can be used
                                # or strategy has no activation range, which mean activate only from commander
                                if not self.current_strategy_base_activate_range:
                                    pos_to_use = commander.pos[0]
                                else:
                                    pos_to_use = battle.cursor_pos[0]
                                line_start = (pos_to_use - self.current_strategy_range) - (
                                        battle.shown_camera_center_pos[0] - self.battle_camera.camera_w_center)
                                line_end = (pos_to_use + self.current_strategy_range) - (
                                        battle.shown_camera_center_pos[0] - self.battle_camera.camera_w_center)

                                if line_start > 0:
                                    draw.line(camera_image, (120, 180, 80),
                                              (line_start, self.strategy_line_top),
                                              (line_start, self.strategy_line_bottom), width=self.strategy_line_width)
                                    draw.line(camera_image, (70, 20, 50),
                                              (line_start, self.strategy_line_top),
                                              (line_start, self.strategy_line_bottom),
                                              width=self.strategy_line_inner_width)
                                if line_end > 0:
                                    draw.line(camera_image, (120, 180, 80),
                                              (line_start, self.strategy_line_center),
                                              (line_end, self.strategy_line_center), width=self.strategy_line_width)

                                    draw.line(camera_image, (120, 180, 80),
                                              (line_end, self.strategy_line_top),
                                              (line_end, self.strategy_line_bottom), width=self.strategy_line_width)
                                    draw.line(camera_image, (70, 20, 50),
                                              (line_end, self.strategy_line_top),
                                              (line_end, self.strategy_line_bottom),
                                              width=self.strategy_line_inner_width)

            if self.event_press:
                if battle.player_selected_strategy:
                    # deactivate strategy when there is one selected
                    battle.player_selected_strategy = None
                elif battle.player_commander:
                    # order to move to area, no attack at all until reach
                    battle.player_commander.issue_commander_order(("move", battle.base_cursor_pos[0]))

            elif self.event_alt_press:  # right click order selected leader to do something
                if battle.player_selected_strategy:
                    # has strategy selected, prioritise activate strategy for this input
                    if battle.activate_strategy(battle.player_team, battle.player_selected_strategy,
                                                battle.base_cursor_pos[0]):
                        # successfully activate strategy
                        battle.player_selected_strategy = None
                elif battle.player_commander:
                    # order to move and attack enemy in range along the way
                    battle.player_commander.issue_commander_order(("attack", battle.base_cursor_pos[0]))


class BattleResult(UIOuterBattle, BoxUI):
    def __init__(self):
        self._layer = 999999999998  # 1 less layer than mouse but higher than all others
        UIOuterBattle.__init__(self)
        BoxUI.__init__(self, (0, 0),
                       (2400 * self.screen_scale_width, 1500 * self.screen_scale_height), self.battle.screen)

        self.character_portraits = self.battle.character_portraits
        self.image.fill((200, 255, 200))

        self.base_image = self.image.copy()
        self.font = self.game.medium_generic_ui_font
        self.header_font = self.game.preset_name_font
        self.result_showing = False

        self.result_text_pos_y = {"total": 700 * self.screen_scale_width,
                                  "loss": 900 * self.screen_scale_width,
                                  "supply": 1100 * self.screen_scale_width}

    def show_result(self):
        self.image = self.base_image.copy()
        # Always assume that main army of team 1 and 2 exist
        if self.battle.team_state[1]["main_army"]:
            portrait = self.character_portraits[self.battle.team_state[1]["main_army"].commander_id]["character_ui"]
            self.image.blit(portrait,
                            portrait.get_rect(center=(1000 * self.screen_scale_width, 250 * self.screen_scale_height)))

        if self.battle.team_state[2]["main_army"]:
            # flip portrait to face left
            portrait = flip(
                self.character_portraits[self.battle.team_state[2]["main_army"].commander_id]["character_ui"], True,
                False)
            self.image.blit(portrait,
                            portrait.get_rect(center=(1900 * self.screen_scale_width, 250 * self.screen_scale_height)))

        result_text = self.grab_text(("ui", "result_text_lose"))
        if self.battle.winner_team == 1:
            result_text = self.grab_text(("ui", "result_text_win"))
        text_surface = self.header_font.render(self.grab_text(("ui", "result_text_team")) + " 1 " + result_text, True,
                                               (0, 0, 0))
        text_rect = text_surface.get_rect(topleft=(850 * self.screen_scale_width, 550 * self.screen_scale_height))
        self.image.blit(text_surface, text_rect)

        result_text = self.grab_text(("ui", "result_text_lose"))
        if self.battle.winner_team == 2:
            result_text = self.grab_text(("ui", "result_text_win"))
        text_surface = self.header_font.render(self.grab_text(("ui", "result_text_team")) + " 2 " + result_text, True,
                                               (0, 0, 0))
        text_rect = text_surface.get_rect(topleft=(1750 * self.screen_scale_width, 550 * self.screen_scale_height))
        self.image.blit(text_surface, text_rect)

        for key, value in self.result_text_pos_y.items():
            text_surface = self.header_font.render(self.grab_text(("ui", "result_text_" + key)), True, (0, 0, 0))
            text_rect = text_surface.get_rect(topleft=(60 * self.screen_scale_width, value))
            self.image.blit(text_surface, text_rect)

            if key == "total":
                text_surface = self.header_font.render(str(self.battle.team_deployed[1]), True, (0, 0, 0))
                text_rect = text_surface.get_rect(topleft=(850 * self.screen_scale_width, value))
                self.image.blit(text_surface, text_rect)

                text_surface = self.header_font.render(str(self.battle.team_deployed[2]), True, (0, 0, 0))
                text_rect = text_surface.get_rect(topleft=(1750 * self.screen_scale_width, value))
                self.image.blit(text_surface, text_rect)
            elif key == "loss":
                text_surface = self.header_font.render(str(self.battle.team_loss[1]), True, (0, 0, 0))
                text_rect = text_surface.get_rect(topleft=(850 * self.screen_scale_width, value))
                self.image.blit(text_surface, text_rect)

                text_surface = self.header_font.render(str(self.battle.team_loss[2]), True, (0, 0, 0))
                text_rect = text_surface.get_rect(topleft=(1750 * self.screen_scale_width, value))
                self.image.blit(text_surface, text_rect)
            elif key == "supply":
                remain_supply = int(
                    self.battle.team_state[1]["supply_resource"] + self.battle.team_state[1]["supply_reserve"])
                diff = str(int(remain_supply - self.battle.team_state[1]["total_supply"]))
                if "-" not in diff:
                    diff = "+" + diff
                text_surface = self.header_font.render(str(remain_supply) + " (" + diff + ")", True, (0, 0, 0))
                text_rect = text_surface.get_rect(topleft=(850 * self.screen_scale_width, value))
                self.image.blit(text_surface, text_rect)

                remain_supply = int(
                    self.battle.team_state[2]["supply_resource"] + self.battle.team_state[2]["supply_reserve"])
                diff = str(int(remain_supply - self.battle.team_state[2]["total_supply"]))
                if "-" not in diff:
                    diff = "+" + diff
                text_surface = self.header_font.render(str(remain_supply) + " (" + diff + ")", True, (0, 0, 0))
                text_rect = text_surface.get_rect(topleft=(1750 * self.screen_scale_width, value))
                self.image.blit(text_surface, text_rect)


class Profiler(cProfile.Profile, UIOuterBattle):

    def __init__(self):
        UIOuterBattle.__init__(self, player_cursor_interact=False)
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
