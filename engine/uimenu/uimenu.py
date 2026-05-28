import types
from copy import deepcopy
from functools import lru_cache
from math import ceil
from random import choice

import pygame
import pyperclip
from pygame import Surface, SRCALPHA, Rect, Color, draw, mouse, Vector2
from pygame.font import Font
from pygame.sprite import Sprite
from pygame.transform import smoothscale, scale

from engine.constants import (Custom_Default_Culture, Default_Showcase_Character_POS,
                              Default_Showcase_Character_air_POS,
                              Default_Showcase_Character, Opposite_Team,
                              Retinue_Leadership_Add_Modifier)
from engine.utils.common import keyboard_mouse_press_check
from engine.utils.data_loading import load_image
from engine.utils.text_making import text_render_with_bg, make_long_text, add_comma_number, calculate_long_text_size

none_type = type(None)


@lru_cache(maxsize=2 ** 8)
def draw_text(text, font, color, ellipsis_length=None):
    # NOTE: this can be very slow. Imagine you have a very long text it has to step down each
    #       character till it find the character length that works.
    #       if this method's performance becomes a big issue try to make a better estimate on the length
    #       and start from there and move up or down in length.
    #
    #       we have cache in place so hopefully it will be enough to save performance.

    if ellipsis_length is not None:
        for i in range(len(text)):
            text_surface = font.render(text[:len(text) - i] + ('...' if i > 0 else ''), True, color)
            if text_surface.get_size()[0] > ellipsis_length:
                continue
            return text_surface
        raise Exception()
    else:
        return font.render(text, True, color)


def make_image_by_frame(frame: Surface, final_size):
    """
        Makes a bigger frame based image out of a frame surface.

        A frame surface is the smallest possible surface of a frame.
        It contains all corners and sides and a pixel in the center.
        The pixel in will be the color of the content of the image.

        It is required that every corner has the same size. If not
        the final image will not look correct.

        And each side must have the same size.
    """

    fs = final_size

    assert frame.get_size()[0] == frame.get_size()[1]

    css = corner_side_size = (frame.get_size()[0] - 1) // 2

    image = Surface(final_size, SRCALPHA)

    # offsets
    # ---
    # if the corners has alpha they can appear to make the final image uneven.
    # that is why we need to adjust the thresholds with some offsets.
    # these offsets are being calculated by check the margins on each side.

    # NOTE/TODO: this is only being implemented on left/right because that is
    #            where we had issues on some image. when we have issues on top/bottom
    #            let us then implement it on it then.
    offsets = o = [0] * 4  # left, up, right, down

    # left margin
    lm = frame.get_size()[0]
    for y in range(frame.get_size()[1]):
        for x in range(lm):
            if frame.get_at((x, y)).a != 0:
                lm = x
                break
    o[0] = -lm

    # right margin
    rm = frame.get_size()[0]
    for y in range(frame.get_size()[1]):
        for x in range(rm):
            if frame.get_at((frame.get_size()[0] - x - 1, y)).a != 0:
                rm = x
                break
    o[2] = rm
    # ---

    # background color
    bc = background_color = frame.get_at((css, css))
    draw.rect(image, bc, (css + o[0], css, fs[0] - css * 2 + o[2] - o[0], fs[1] - css * 2))

    # corners
    image.blit(frame, (0 + o[0], 0), (0, 0, css, css))
    image.blit(frame, (0 + o[0], fs[1] - css), (0, css + 1, css, css * 2 + 1))
    image.blit(frame, (fs[0] - css + o[2], 0), (css + 1, 0, css * 2 + 1, css))
    image.blit(frame, (fs[0] - css + o[2], fs[1] - css), (css + 1, css + 1, css * 2 + 1, css * 2 + 1))

    # sides
    for x in range(css + o[0], fs[0] - css + o[2]):
        image.blit(frame, (x, 0), (css, 0, 1, css))
        image.blit(frame, (x, fs[1] - css), (css, css + 1, 1, css * 2 + 1))
    for y in range(css, fs[1] - css):
        image.blit(frame, (0 + o[0], y), (0, css, css, 1))
        image.blit(frame, (fs[0] - css + o[2], y), (css + 1, css, css * 2 + 1, 1))

    return image


class UIMenu(Sprite):
    containers = None

    def __init__(self, player_cursor_interact=True, has_containers=False, play_sound_when_click=False):
        """
        Parent class for all menu user interface objects

        :param player_cursor_interact: Player can interact (click) with UI in some way
        :param has_containers: Object has group containers to assign
        """
        from engine.game.game import Game
        self.game = Game.game
        self.add_to_ui_menu_updater = self.game.add_to_ui_menu_updater
        self.remove_from_ui_menu_updater = self.game.remove_from_ui_menu_updater
        self.button_sound_channel = self.game.button_sound_channel
        self.sound_effect_pool = self.game.sound_effect_pool
        self.screen_scale_width = Game.screen_scale_width
        self.screen_scale_height = Game.screen_scale_height
        self.data_dir = Game.data_dir
        self.ui_font = Game.ui_font
        self.font_texture = Game.font_texture
        self.screen_rect = Game.screen_rect
        self.screen_size = Game.screen_size
        self.screen_width = self.screen_size[0]
        self.screen_height = self.screen_size[1]
        self.half_screen_width = self.screen_size[0] / 2
        self.half_screen_height = self.screen_size[1] / 2
        self.localisation = Game.localisation
        self.grab_text = self.localisation.grab_text
        self.cursor = Game.cursor
        self.updater = Game.ui_menu_updater
        self.player_interact = player_cursor_interact
        self.play_sound_when_click = play_sound_when_click
        if has_containers:
            Sprite.__init__(self, self.containers)
        else:
            Sprite.__init__(self)
        self.event = False
        self.event_press = False
        self.event_hold = False
        self.event_alt_press = False
        self.event_alt_hold = False
        self.event_middle_mouse_press = False
        self.mouse_over = False
        self.pause = False

    def update(self, dt):
        self.event = False
        self.event_press = False
        self.event_hold = False  # some UI differentiates between press release or holding, if not just use event
        self.event_alt_press = False
        self.event_alt_hold = False
        self.event_middle_mouse_press = False
        self.mouse_over = False
        if self.player_interact and not self.pause:
            if self.rect.collidepoint(self.cursor.pos):
                self.mouse_over = True
                self.cursor.mouse_over = True
                if self.cursor.is_select_just_up:
                    if self.play_sound_when_click:
                        self.button_sound_channel.play(choice(self.sound_effect_pool["button"]))
                        self.button_sound_channel.set_volume(self.game.play_effect_volume)
                    self.event = True
                    self.event_press = True
                    self.cursor.is_select_just_up = False  # reset select button to prevent overlap interaction
                elif self.cursor.is_select_down:
                    self.event = True
                    self.event_hold = True
                    self.cursor.is_select_just_down = False  # reset select button to prevent overlap interaction
                elif self.cursor.is_alt_select_just_up:
                    self.event = True
                    self.event_alt_press = True
                    self.cursor.is_alt_select_just_up = False  # reset select button to prevent overlap interaction
                elif self.cursor.is_alt_select_down:
                    self.event = True
                    self.event_alt_hold = True
                    self.cursor.is_alt_select_just_down = False  # reset select button to prevent overlap interaction
                elif self.cursor.is_middle_mouse_select_just_up:
                    self.event = True
                    self.event_middle_mouse_press = True
                    self.cursor.is_middle_mouse_select_just_up = False  # reset select button to prevent overlap interaction


class UIScroll(UIMenu):
    def __init__(self, ui, pos):
        """
        Scroll for any applicable ui
        :param ui: Any ui object, the ui must has max_row_show attribute, layer, and image surface
        :param pos: Starting pos
        :param layer: Surface layer value
        """
        self.ui = ui
        self._layer = self.ui.layer + 2  # always 2 layer higher than the ui
        UIMenu.__init__(self)

        self.ui.scroll = self
        self.ui_height = self.ui.image.get_height()
        self.max_row_show = self.ui.max_row_show
        self.pos = pos
        self.image = Surface((10, self.ui_height))
        self.image.fill((255, 255, 255))
        self.base_image = self.image.copy()
        self.button_colour = (100, 100, 100)
        draw.rect(self.image, self.button_colour, (0, 0, self.image.get_width(), self.ui_height))
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
                  (0, int(self.ui_height * percent_row / 100), self.image.get_width(),
                   int(self.ui_height * max_row / 100)))

    def change_image(self, new_row=None, row_size=None):
        """New row is input of scrolling by user to new row, row_size is changing based on adding more item or clear"""
        if row_size is not None:
            self.row_size = row_size
        if new_row is not None:  # accept from both wheeling scroll and drag scroll bar
            self.current_row = int(new_row)
        self.create_new_image()

    def update(self, dt):
        """Player input update via click or scrolling"""
        UIMenu.update(self, dt)
        if self.mouse_over and (self.event_hold or self.event_press):
            mouse_value = (self.cursor.pos[1] - self.pos[
                1]) * 100 / self.ui_height  # find what percentage of mouse_pos at the scroll bar (0 = top, 100 = bottom)
            if mouse_value > 100:
                mouse_value = 100
            if mouse_value < 0:
                mouse_value = 0
            new_row = int(self.row_size * mouse_value / 100)
            if self.row_size > self.max_row_show and new_row > self.row_size - self.max_row_show:
                new_row = self.row_size - self.max_row_show
            if self.row_size > self.max_row_show:  # only change scroll position in list longer than max length
                self.change_image(new_row)


class MenuCursor(UIMenu):
    def __init__(self, images):
        """Game menu cursor"""
        self._layer = 9999999999999999999999999999999999999999  # as high as possible, always blit last
        UIMenu.__init__(self, player_cursor_interact=False)
        self.images = images
        self.image = images["normal"]
        self.current_image = "normal"
        self.pos = (0, 0)
        self.is_select_just_down = False
        self.is_select_down = False
        self.is_select_just_up = False
        self.select_up = False

        self.is_alt_select_just_down = False
        self.is_alt_select_down = False
        self.alt_select_up = False
        self.is_alt_select_just_up = False

        self.is_middle_mouse_select_just_down = False
        self.is_middle_mouse_select_down = False
        self.middle_mouse_select_up = False
        self.is_middle_mouse_select_just_up = False

        self.scroll_up = False
        self.scroll_down = False
        self.rect = self.image.get_rect(topleft=self.pos)
        self.shown = True

    def update(self, dt):
        """Update cursor position based on mouse position and mouse button click"""
        self.pos = mouse.get_pos()
        self.rect.topleft = self.pos
        self.mouse_over = False
        self.is_select_just_down, self.is_select_down, self.is_select_just_up = keyboard_mouse_press_check(
            mouse, 0, self.is_select_just_down, self.is_select_down, self.is_select_just_up)

        self.select_up = self.is_select_just_up
        # Alternative select press button, like mouse right
        self.is_alt_select_just_down, self.is_alt_select_down, self.is_alt_select_just_up = keyboard_mouse_press_check(
            mouse, 2, self.is_alt_select_just_down, self.is_alt_select_down, self.is_alt_select_just_up)
        self.alt_select_up = self.is_alt_select_just_up

        # middle mouse button press
        self.is_middle_mouse_select_just_down, self.is_middle_mouse_select_down, self.is_middle_mouse_select_just_up = keyboard_mouse_press_check(
            mouse, 1, self.is_middle_mouse_select_just_down, self.is_middle_mouse_select_down,
            self.is_middle_mouse_select_just_up)
        self.middle_mouse_select_up = self.is_middle_mouse_select_just_up

        if self.is_select_down or self.is_alt_select_down:
            self.image = self.images["click"]
        else:
            self.image = self.images[self.current_image]

        if self.shown:
            self.rect.topleft = self.pos

    def change_image(self, image_name):
        """Change cursor image to whatever input name"""
        self.current_image = image_name


class SliderMenu(UIMenu):
    def __init__(self, bar_images, button_images, pos, value):
        """
        Slider UI that let player click or drag the setting point in the bar
        :param bar_images: List of box image and slider box
        :param button_images: List of button or ball clicked/non-clicked image
        :param pos: Position of the ui sprite
        :param value: Value of the setting
        """
        self._layer = 25
        UIMenu.__init__(self)
        self.pos = pos
        self.image = bar_images[0].copy()
        self.slider_size = bar_images[1].get_width()
        self.difference = (self.image.get_width() - self.slider_size) / 2
        self.value_scale = self.slider_size / 100
        rect = bar_images[1].get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(bar_images[1], rect)
        self.button_image_list = button_images
        self.button_image = self.button_image_list[0]
        self.min_value = self.pos[0] - (self.slider_size / self.value_scale)  # min value position of the scroll bar
        self.max_value = self.pos[0] + (self.slider_size / self.value_scale)  # max value position
        self.value = value
        self.mouse_value = (self.slider_size * value / 100) + self.difference  # convert mouse pos on scroll to value
        self.base_image = self.image.copy()
        button_rect = self.button_image_list[1].get_rect(center=(self.mouse_value, self.image.get_height() / 2))
        self.image.blit(self.button_image, button_rect)
        self.rect = self.image.get_rect(center=self.pos)

    def player_input(self, value_box, forced_value=False):
        """
        Update slider value and position
        :param value_box: UI box that show number value
        :param forced_value: forced number value
        """
        if forced_value is False:
            self.mouse_value = self.cursor.pos[0]
            if self.mouse_value > self.max_value:
                self.mouse_value = self.max_value
            elif self.mouse_value < self.min_value:
                self.mouse_value = self.min_value
            self.value = (self.mouse_value - self.min_value) / 2
        else:  # for revert, cancel or esc in the option menu
            self.value = forced_value
        self.mouse_value = (self.slider_size * self.value / 100) + self.difference
        self.image = self.base_image.copy()
        button_rect = self.button_image_list[1].get_rect(center=(self.mouse_value, self.image.get_height() / 2))
        self.image.blit(self.button_image, button_rect)
        value_box.change_value(self.value)


class InputUI(UIMenu):
    def __init__(self, image, pos):
        self._layer = 40
        UIMenu.__init__(self, player_cursor_interact=False)

        self.pos = pos
        self.image = image
        self.base_image = self.image.copy()
        self.font = Font(self.ui_font["main_button"], int(96 * self.screen_scale_height))
        self.rect = self.image.get_rect(center=self.pos)

    def change_instruction(self, text):
        self.image = self.base_image.copy()
        self.text = text
        text_surface = self.font.render(text, True, (30, 30, 30))
        text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 4))
        self.image.blit(text_surface, text_rect)


class FactionSelector(UIMenu):
    def __init__(self, width_limit, pos, layer=10, is_popup=False, include_random=False, include_free=False,
                 use_culture=False):
        self._layer = layer
        UIMenu.__init__(self)
        self.width_limit = width_limit
        self.pos = pos
        self.is_popup = is_popup
        self.use_culture = use_culture
        if use_culture:
            self.faction_coas = {key: value["small"] for key, value in self.game.sprite_data.culture_coas.items()}

            free_coa = self.faction_coas["free"]
            self.faction_coas.pop("free")
            if include_free:  # add back free coa as the end of dict
                self.faction_coas["free"] = free_coa

            random_coa = self.faction_coas["random"]
            self.faction_coas.pop("random")
            if include_random:  # add back random coa as the last one
                self.faction_coas["random"] = random_coa
        else:  # faction based on campaign
            self.faction_coas = {}
            for faction, data in self.game.map_data.faction_list.items():
                if data["Ruler"]:  # faction with no ruler means not playable
                    self.faction_coas[faction] = self.game.sprite_data.character_portraits[data["Ruler"]]["small"][
                        "right"]

        max_column = int((width_limit * self.screen_scale_width) / (220 * self.screen_scale_width))
        require_row = int(len(self.faction_coas) / max_column)
        rect_per_row = range(1, max_column)
        if not require_row:
            require_row = 1

        self.image = Surface((int(width_limit * self.screen_scale_width),
                              int((300 * require_row) * self.screen_scale_height)), SRCALPHA)
        self.image.fill((100, 100, 100))
        self.base_image = self.image.copy()
        self.faction_coa_rects = {}
        y = 50 * self.screen_scale_height

        rect_placement = [(220 * self.screen_scale_width) * item for item in rect_per_row]
        x_index = 0
        for faction, coa in self.faction_coas.items():
            x = rect_placement[x_index]
            rect = coa.get_rect(midtop=(x, y))
            self.image.blit(coa, rect)
            self.faction_coa_rects[faction] = rect
            x_index += 1
            if x_index == len(rect_placement):
                y = 220 * self.screen_scale_height
                x_index = 0
        self.selected_faction = None

        self.rect = self.image.get_rect(midtop=pos)
        if not self.is_popup:
            if use_culture:
                self.selected_faction = Custom_Default_Culture
                self.change_faction(Custom_Default_Culture)
            else:
                self.selected_faction = self.game.map_data.default_grand_faction
                self.change_faction(self.selected_faction)

    def change_faction(self, new_select_faction):
        self.image = self.base_image.copy()
        for faction, rect in self.faction_coa_rects.items():
            if faction == new_select_faction:
                coa = self.faction_coas[faction].copy()
                draw.circle(coa, (200, 200, 50),
                            (coa.get_width() / 2, coa.get_height() / 2),
                            (coa.get_width() / 2), width=int(12 * self.screen_scale_width))
                self.image.blit(coa, self.faction_coa_rects[faction])
            else:  # unselected old one
                self.image.blit(self.faction_coas[faction], self.faction_coa_rects[faction])
        self.selected_faction = new_select_faction
        if self.game.menu_state == "grand":
            self.game.grand_setup_mini_map.change_faction(new_select_faction,
                                                          {key: value["Control"] for key, value in
                                                           self.game.map_data.region_list.items()})
            self.game.grand_faction_detail.change_faction(new_select_faction)
            self.game.grand_faction_showcase.change_faction(new_select_faction)
        elif self.game.menu_state == "beast":
            self.game.lorebook_showcase_character_selector.add(new_select_faction, None)
        elif self.game.menu_state == "preset":
            self.game.custom_preset_army_setup.change_faction(new_select_faction)

    def update(self, dt):
        UIMenu.update(self, dt)
        if self.mouse_over:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))
            for faction, rect in self.faction_coa_rects.items():
                if rect.collidepoint(inside_mouse_pos):
                    if self.use_culture:
                        self.game.text_popup.popup(self.cursor.rect,
                                                   self.grab_text(("culture", faction, "Name")))
                    else:
                        self.game.text_popup.popup(self.cursor.rect,
                                                   self.grab_text(("faction", faction, "Name")))
                    self.add_to_ui_menu_updater(self.game.text_popup)
                    if self.event_press:
                        self.button_sound_channel.play(choice(self.sound_effect_pool["button"]))
                        self.button_sound_channel.set_volume(self.game.play_effect_volume)
                        if self.is_popup:  # remove popup ui
                            self.remove_from_ui_menu_updater(self)
                            self.selected_faction = faction
                        else:
                            self.change_faction(faction)
                    break

        elif self.cursor.select_up and self.is_popup:  # remove popup ui
            self.remove_from_ui_menu_updater(self)


class CharacterSelector(UIMenu):
    def __init__(self, pos):
        """UI for selecting character for army setup"""
        self._layer = 11
        UIMenu.__init__(self)
        self.scroll = None  # got added later during scroll object __init__
        self.character_portraits = self.game.sprite_data.character_portraits
        self.character_list = self.game.character_list
        self.custom_character_setup = self.game.character_data.custom_character_setup
        self.all_main_exist_characters = self.game.character_data.all_main_exist_characters
        self.image = Surface((int(1300 * self.screen_scale_width), int(1080 * self.screen_scale_height)), SRCALPHA)
        self.image.fill((200, 200, 200))
        self.selected_faction = None
        self.total_row = 0
        self.scroll_total_row = self.total_row + 1
        self.current_row = 0
        self.portrait_rects = []
        self.selector_character_list = []
        self.shown_character_type = None
        temp_rect_image = Surface((int(200 * self.screen_scale_width), int(200 * self.screen_scale_height)))

        self.max_row = 5
        self.max_row_show = 1  # trick the scroller to use additional row instead of total
        self.max_total_character_show = 30

        for y in range(5):
            for x in range(6):
                rect = temp_rect_image.get_rect(center=((150 + (x * 200)) * self.screen_scale_width,
                                                        50 + (y * 200) * self.screen_scale_height))
                self.portrait_rects.append(rect)
                # self.image.blit(temp_rect_image, rect)

        self.rect = self.image.get_rect(midtop=pos)

    def add(self, faction, character_type, exist_unique_check=()):
        selector_character_list = ()
        self.selected_faction = faction
        self.shown_character_type = character_type
        if self.game.menu_state in ("custom", "preset"):
            if character_type in ("commander", "leader", "retinue"):
                selector_character_list = [value for value in
                                           self.custom_character_setup[faction]["ground"]["leader"]["unique"] if value
                                           not in exist_unique_check]
                selector_character_list += [value for value in
                                            self.custom_character_setup["free"]["ground"]["leader"]["unique"] if value
                                            not in exist_unique_check]
                if character_type == "commander":  # exclude leader that cannot be commander
                    selector_character_list = [value for value in selector_character_list
                                               if not self.character_list[value]["No Commander"]]
                selector_character_list += self.custom_character_setup[faction]["ground"]["leader"]["generic"]
            elif character_type == "troop":
                selector_character_list = self.custom_character_setup[faction]["ground"]["troop"]
            elif character_type == "air":
                selector_character_list = self.custom_character_setup[faction]["air"]
        else:
            selector_character_list = self.all_main_exist_characters[faction]
        # sort characters, based on unique leader, common leader, ground troop, air troop
        true_selector_character_list = [item for item in selector_character_list if
                                        self.character_list[item]["Is Leader"] and self.character_list[item][
                                            "Is Unique"]]
        true_selector_character_list += [item for item in selector_character_list if
                                         self.character_list[item]["Is Leader"] and not self.character_list[item][
                                             "Is Unique"]]
        true_selector_character_list += [item for item in selector_character_list if self.character_list[item][
            "Type"] == "ground" and item not in true_selector_character_list]
        true_selector_character_list += [item for item in selector_character_list if self.character_list[item][
            "Type"] == "air" and item not in true_selector_character_list]
        self.selector_character_list = true_selector_character_list

        additional_character = len(self.selector_character_list) - self.max_total_character_show
        if additional_character < 0:
            additional_character = 0
        self.total_row = ceil(additional_character / 6)
        self.scroll_total_row = self.total_row + 1
        self.current_row = 0  # reset showing row
        self.scroll.change_image(self.current_row, self.scroll_total_row)
        self.add_character()

    def add_character(self):
        self.image.fill((200, 200, 200))
        start_index = (self.current_row * 6)
        for index, character in enumerate(self.selector_character_list):
            if index >= start_index:
                shown_index = index - start_index
                if int(shown_index / 6) < self.max_row:
                    if character in self.character_portraits:
                        self.image.blit(self.character_portraits[character]["setup_ui"],
                                        self.portrait_rects[shown_index])
                    else:  # use default instead
                        self.image.blit(self.character_portraits["default"]["setup_ui"],
                                        self.portrait_rects[shown_index])
                else:
                    break

    def update(self, dt):
        UIMenu.update(self, dt)
        if self.mouse_over:
            if self.cursor.scroll_up:
                if self.current_row > 0:
                    self.current_row -= 1
                    self.scroll.change_image(self.current_row, self.scroll_total_row)
                    self.add_character()
            elif self.cursor.scroll_down:
                if self.current_row < self.total_row:
                    self.current_row += 1
                    self.scroll.change_image(self.current_row, self.scroll_total_row)
                    self.add_character()

            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))
            start_index = (self.current_row * 6)
            for index, rect in enumerate(self.portrait_rects):
                if rect.collidepoint(inside_mouse_pos):
                    shown_index = index + start_index
                    if shown_index < len(self.selector_character_list):
                        character_id = self.selector_character_list[shown_index]
                        if self.event_press:
                            self.button_sound_channel.play(choice(self.sound_effect_pool["button"]))
                            self.button_sound_channel.set_volume(self.game.play_effect_volume)
                            if self.game.menu_state == "preset":
                                self.game.custom_preset_army_setup.change_character(
                                    self.game.custom_preset_army_setup.selected_portrait_index[0],
                                    self.game.custom_preset_army_setup.selected_portrait_index[1], character_id)
                            elif self.game.menu_state == "beast":
                                lorebook_showcase_character = self.game.lorebook_showcase_character
                                if lorebook_showcase_character.char_id != character_id:
                                    self.game.all_showcase_characters.remove(lorebook_showcase_character.sub_characters)
                                    self.game.all_showcase_characters.remove(lorebook_showcase_character)
                                    self.remove_from_ui_menu_updater(
                                        (lorebook_showcase_character.sub_characters, lorebook_showcase_character))
                                    for character in lorebook_showcase_character.sub_characters:
                                        character.erase()
                                    self.game.sprite_data.load_character_animation(
                                        set([character_id] + [
                                            item[0] for item in self.character_list[character_id]["Sub Characters"]]))
                                    pos = Default_Showcase_Character_POS
                                    if self.character_list[character_id]["Type"] == "air":
                                        pos = Default_Showcase_Character_air_POS
                                    lorebook_showcase_character.__init__(
                                        0, {"ID": character_id, "POS": pos,
                                            "direction": "right"} | self.character_list[character_id])
                                    self.add_to_ui_menu_updater(lorebook_showcase_character,
                                                                lorebook_showcase_character.sub_characters)
                                    animation_list = list(
                                        self.game.sprite_data.character_animation_data[character_id].keys())
                                    for character in self.character_list[character_id]["Sub Characters"]:
                                        for anim in self.game.sprite_data.character_animation_data[character[0]]:
                                            if anim not in animation_list:
                                                animation_list.append(anim)
                                    animation_list = sorted(animation_list)
                                    self.game.lorebook_showcase_animation_list_box.adapter.__init__(
                                        [[0, key] for key in animation_list if key != "Default"])
                                    self.game.lorebook_character_description_showcase.change_character(character_id)
                                    self.game.lorebook_character_moveset_showcase.change_moveset(character_id, None)
                            return
                        character_data = self.character_list[character_id]
                        if self.shown_character_type != "retinue":
                            char_stat = [self.grab_text(("ui", "info_header_name")) + self.grab_text(
                                ("character", character_id, "Name")) + " (" + str(character_data["Arrive Per Call"]) +
                                         "x" + str(character_data["Capacity"]) + ")",
                                         self.grab_text(("character", character_id, "Description")),
                                         self.grab_text(("ui", "info_header_class")) + self.grab_text(
                                             ("ui", "class_" + character_data["Class"])),
                                         self.grab_text(("ui", "info_header_health")) + add_comma_number(
                                             character_data["Health"]),
                                         self.grab_text(("ui", "info_header_offence")) + str(character_data["Offence"]),
                                         self.grab_text(("ui", "info_header_defence")) + str(character_data["Defence"]),
                                         self.grab_text(("ui", "info_header_speed")) + str(character_data["Speed"]),
                                         self.grab_text(("ui", "info_header_cost")) + add_comma_number(
                                             character_data["Cost"])]

                            if character_data["Leadership"]:
                                char_stat.append(self.grab_text(("ui", "info_header_leadership")) + str(
                                    character_data["Leadership"]))
                            if character_data["Strategy"]:
                                char_stat.append(
                                    self.grab_text(("ui", "info_header_strategy")) + self.grab_text(
                                        ("strategy", character_data["Strategy"], "Name")))
                            if character_data["Supply"]:
                                char_stat.append(
                                    self.grab_text(("ui", "info_header_supply_cost")) + str(character_data["Supply"]))

                            for resistance in (
                                    "Slash", "Crush", "Stab", "Fire", "Water", "Air", "Earth", "Magic", "Poison"):
                                if character_data[resistance + " Resistance"]:
                                    char_stat.append(
                                        self.grab_text(
                                            ("ui", "info_header_" + resistance.lower() + "_resistance")) + str(
                                            int(100 * character_data[resistance + " Resistance"])) + "%")
                            tag_text = ""
                            for prop in character_data["Property"]:
                                prop_text = self.grab_text(("ui", "property_" + prop))
                                if "(" not in prop_text:  # mean tag has no localisation, likely intentional
                                    tag_text += prop_text + ", "
                            if tag_text:
                                tag_text = self.grab_text(("ui", "info_header_property")) + tag_text
                                tag_text = tag_text[:-2]  # remove additional comma
                                char_stat.append(tag_text)
                        else:
                            char_stat = [self.grab_text(("ui", "info_header_name")) + self.grab_text(
                                ("character", character_id, "Name")),
                                         self.grab_text(("character", character_id, "Description")),
                                         self.grab_text(("ui", "info_header_strategy")) + self.grab_text(
                                             ("strategy", character_data["Strategy"], "Name")),
                                         self.grab_text(("ui", "info_header_leadership")) + add_comma_number(
                                             character_data["Leadership"]),
                                         self.grab_text(("ui", "info_header_cost")) + add_comma_number(
                                             character_data["Cost"])]
                        self.game.text_popup.popup(self.cursor.rect, char_stat,
                                                   width_text_wrapper=int(1400 * self.screen_scale_width))
                        self.add_to_ui_menu_updater(self.game.text_popup)
                    break


class CustomTeamSetupUI(UIMenu):
    def __init__(self, team, pos):
        """UI to setup team for custom battle, since it is for custom battle use
        culture instead of faction to setup army"""
        UIMenu.__init__(self)
        self.culture_coas = self.game.sprite_data.culture_coas
        self.font = self.game.preset_name_font
        self.note_font = self.game.note_font
        self.font_width = self.font.size("a")[0]
        self.image = Surface((int(1800 * self.screen_scale_width), int(1400 * self.screen_scale_height)), SRCALPHA)
        self.image.fill((150, 220, 220))

        self.image.blit(self.game.grand_ui_images["gold"],
                        self.game.grand_ui_images["gold"].get_rect(
                            topright=(self.image.get_width() - 50 * self.screen_scale_width,
                                      50 * self.screen_scale_height)))
        self.image.blit(self.game.grand_ui_images["supply"],
                        self.game.grand_ui_images["supply"].get_rect(topleft=(
                            50 * self.screen_scale_width, 50 * self.screen_scale_height)))

        self.circle = Surface((200 * self.screen_scale_width, 200 * self.screen_scale_height), SRCALPHA)
        draw.circle(self.circle, (255, 255, 255),
                    (self.circle.get_width() / 2, self.circle.get_height() / 2),
                    (self.circle.get_width() / 2))

        self.text_box_image = Surface((int(400 * self.screen_scale_width), int(60 * self.screen_scale_height)))
        self.text_box_image.fill((150, 220, 220))

        self.culture_coa_rects = []
        self.cost_text_rects = {"total": 150 * self.screen_scale_height, "warn": 200 * self.screen_scale_height}
        for index, y in enumerate((350, 570, 790, 1010, 1230)):
            self.cost_text_rects[index] = y * self.screen_scale_height
            rect = self.circle.get_rect(center=(500 * self.screen_scale_width, y * self.screen_scale_height))
            self.culture_coa_rects.append(rect)
            self.image.blit(self.circle, rect)
            self.change_cost(index, 0, 0, check_total=False)

        self.cost_warn_text_box = Surface((int(800 * self.screen_scale_width), int(60 * self.screen_scale_height)))
        self.cost_warn_text_box.fill((150, 220, 220))
        self.empty_cost_warn_box = self.cost_warn_text_box.copy()
        text = self.note_font.render(self.grab_text(("ui", "warn_cost_exceed")), True, (30, 30, 30))
        self.cost_warn_text_box.blit(text, text.get_rect(midright=(self.cost_warn_text_box.get_width(),
                                                                   self.cost_warn_text_box.get_height() / 2)))
        self.cost_warn_text_box_rect = self.cost_warn_text_box.get_rect(midright=(self.image.get_width(),
                                                                                  self.cost_text_rects["warn"]))

        self.supply_warn_text_box = Surface((int(800 * self.screen_scale_width), int(60 * self.screen_scale_height)))
        self.supply_warn_text_box.fill((150, 220, 220))
        self.empty_supply_warn_box = self.supply_warn_text_box.copy()
        text = self.note_font.render(self.grab_text(("ui", "warn_supply_exceed")), True, (30, 30, 30))
        self.supply_warn_text_box.blit(text, text.get_rect(midleft=(0,
                                                                     self.supply_warn_text_box.get_height() / 2)))
        self.supply_warn_text_box_rect = self.supply_warn_text_box.get_rect(midleft=(0, self.cost_text_rects["warn"]))

        self.rect = self.image.get_rect(center=pos)
        self.total_gold = 0
        self.total_supply = 0
        self.team = team

        self.player_control_rect = self.circle.get_rect(
            center=((self.image.get_width() / 2), 150 * self.screen_scale_width))
        self.change_player_control()

        self.selected_culture_rect = None
        self.team_setup = {index: {"culture": None, "army": None} for index in range(5)}

        self.rect = self.image.get_rect(center=pos)

    def check_total_cost(self):

        # check and add gold remain
        total_cost = 0
        for army in self.game.custom_team_army[self.team]:
            total_cost += army.cost
        if self.team == 1:
            remain = int(self.game.custom_battle_team1_gold_button.text.replace(",", "").split(": ")[1]) - total_cost
        else:
            remain = int(self.game.custom_battle_team2_gold_button.text.replace(",", "").split(": ")[1]) - total_cost

        if remain < 0:
            self.image.blit(self.cost_warn_text_box, self.cost_warn_text_box_rect)
        else:
            self.image.blit(self.empty_cost_warn_box, self.cost_warn_text_box_rect)

        text_box_image = self.text_box_image.copy()

        text = self.font.render(add_comma_number(remain), True, (30, 30, 30))
        text_box_image.blit(text, text.get_rect(midright=(text_box_image.get_width(), text_box_image.get_height() / 2)))
        self.image.blit(text_box_image, text_box_image.get_rect(midright=(self.image.get_width(),
                                                                          self.cost_text_rects["total"])))

        # check and add supply remain
        total_supply = 0
        for army in self.game.custom_team_army[self.team]:
            total_supply += army.total_supply_usage
        if self.team == 1:
            remain = int(
                self.game.custom_battle_team1_supply_button.text.replace(",", "").split(": ")[1]) - total_supply
        else:
            remain = int(
                self.game.custom_battle_team2_supply_button.text.replace(",", "").split(": ")[1]) - total_supply

        if remain < 0:
            self.image.blit(self.supply_warn_text_box, self.supply_warn_text_box_rect)
        else:
            self.image.blit(self.empty_supply_warn_box, self.supply_warn_text_box_rect)
        text_box_image = self.text_box_image.copy()

        text = self.font.render(add_comma_number(remain), True, (30, 30, 30))
        text_box_image.blit(text, text.get_rect(midleft=(0, text_box_image.get_height() / 2)))
        self.image.blit(text_box_image, text_box_image.get_rect(midleft=(0,  self.cost_text_rects["total"])))

    def change_cost(self, index, cost, supply, check_total=True):
        text_box_image = self.text_box_image.copy()
        text = self.font.render(add_comma_number(cost), True, (30, 30, 30))

        text_box_image.blit(text, text.get_rect(midright=(text_box_image.get_width(), text_box_image.get_height() / 2)))
        self.image.blit(text_box_image,
                        text_box_image.get_rect(midright=(self.image.get_width(), self.cost_text_rects[index])))

        text_box_image = self.text_box_image.copy()
        text = self.font.render(add_comma_number(supply), True, (30, 30, 30))

        text_box_image.blit(text, text.get_rect(midleft=(0, text_box_image.get_height() / 2)))
        self.image.blit(text_box_image,
                        text_box_image.get_rect(midleft=(0, self.cost_text_rects[index])))

        if check_total:
            self.check_total_cost()

    def change_player_control(self):
        self.image.blit(self.circle, self.player_control_rect)
        self.image.blit(self.game.player_image[self.game.custom_team_players[self.team]], self.player_control_rect)

    def change_faction(self, culture, index):
        self.game.custom_team_army[self.team][index].__init__("", "", "", None, [], [], [], [])
        self.team_setup[index]["culture"] = culture
        self.team_setup[index]["army"] = None
        self.image.blit(self.circle, self.culture_coa_rects[index])
        self.remove_from_ui_menu_updater(self.game.custom_team_army_buttons[self.team][index])
        if self.team_setup[index]["culture"]:
            self.image.blit(self.culture_coas[self.team_setup[index]["culture"]]["small"],
                            self.culture_coa_rects[index])
        if self.team_setup[index]["culture"] and self.team_setup[index]["culture"] != "random":
            self.add_to_ui_menu_updater(self.game.custom_team_army_buttons[self.team][index])

        self.game.custom_team_army[self.team][index].__init__("", "", "", None, [], [], [], [])
        self.game.custom_team_army_buttons[self.team][index].change_state("")
        self.change_cost(index, 0, 0)

    def update(self, dt):
        UIMenu.update(self, dt)
        if self.selected_culture_rect is not None:  # selecd faction with popup
            if self.game.custom_culture_selector_popup.selected_faction:
                if self.team_setup[self.selected_culture_rect][
                    "culture"] != self.game.custom_culture_selector_popup.selected_faction:
                    # change faction reset army
                    self.team_setup[self.selected_culture_rect]["army"] = None

                self.change_faction(self.game.custom_culture_selector_popup.selected_faction,
                                    self.selected_culture_rect)
                self.game.custom_culture_selector_popup.selected_faction = None

                self.selected_culture_rect = None

        if self.mouse_over:
            cursor_pos = self.cursor.pos
            inside_mouse_pos = Vector2(
                (cursor_pos[0] - self.rect.topleft[0]),
                (cursor_pos[1] - self.rect.topleft[1]))
            if self.player_control_rect.collidepoint(inside_mouse_pos):
                if self.event_press:
                    self.button_sound_channel.play(choice(self.sound_effect_pool["button"]))
                    self.button_sound_channel.set_volume(self.game.play_effect_volume)
                    if self.game.custom_team_players[self.team] == "player":  # change to computer
                        self.game.custom_team_players[self.team] = "computer"
                    elif self.game.custom_team_players[self.team] == "computer":  # change to player
                        self.game.custom_team_players[self.team] = "player"
                        if self.game.custom_team_players[Opposite_Team[self.team]] == "player":
                            # swap player from another team
                            self.game.custom_team_players[Opposite_Team[self.team]] = "computer"
                            self.game.custom_battle_team_setup[Opposite_Team[self.team]].change_player_control()

                    self.change_player_control()

                self.game.text_popup.popup((cursor_pos[0], cursor_pos[1] - (100 * self.screen_scale_height)),
                                           self.grab_text(("ui", "text_" + self.game.custom_team_players[self.team])))
                self.add_to_ui_menu_updater(self.game.text_popup)

            else:
                for index, rect in enumerate(self.culture_coa_rects):
                    if rect.collidepoint(inside_mouse_pos):
                        if self.event_press:
                            self.button_sound_channel.play(choice(self.sound_effect_pool["button"]))
                            self.button_sound_channel.set_volume(self.game.play_effect_volume)
                            show_pos = (self.rect.topleft[0] + rect.topright[0],
                                        self.rect.topleft[1] + rect.topright[1])
                            self.game.custom_culture_selector_popup.rect.topleft = show_pos
                            self.add_to_ui_menu_updater(self.game.custom_culture_selector_popup)
                            self.selected_culture_rect = index
                            # reset other team setup ui in case player select faction rect while popup for other team
                            self.game.custom_battle_team_setup[Opposite_Team[self.team]].selected_culture_rect = None

                        elif self.event_alt_press:
                            if self.game.custom_culture_selector_popup in self.game.ui_menu_updater:
                                self.remove_from_ui_menu_updater(self.game.custom_culture_selector_popup)
                            self.change_faction(None, index)

                        self.game.text_popup.popup(
                            (cursor_pos[0], cursor_pos[1] - (100 * self.screen_scale_height)),
                            self.grab_text(("culture", str(self.team_setup[index]["culture"]).lower(), "Name")))
                        self.add_to_ui_menu_updater(self.game.text_popup)
                        break


class PresetArmySetupUI(UIMenu):
    empty_army_preset = {"Name": None,
                         "commander": [None],
                         "retinue": [None, None, None],
                         "leader": [None, None, None],
                         "troop": [None, None, None, None, None],
                         "air": [None, None, None, None, None]}

    def __init__(self, pos, player_cursor_interact, layer=10):
        """UI for setting up custom preset army,
        can also be used to show finished preset for selection in custom battle setup."""
        self._layer = layer
        UIMenu.__init__(self, player_cursor_interact)
        self.character_portraits = self.game.sprite_data.character_portraits
        self.character_list = self.game.character_list
        self.image = Surface((int(1500 * self.screen_scale_width), int(1080 * self.screen_scale_height)), SRCALPHA)
        self.image.fill((180, 100, 180))
        self.total_gold_cost = 0
        self.total_supply_usage = 0
        self.total_leadership = 0
        self.portrait_type_rects = {"commander": [],
                                    "retinue": [],
                                    "leader": [],
                                    "troop": [],
                                    "air": []}

        self.circle = Surface((200 * self.screen_scale_width, 200 * self.screen_scale_height), SRCALPHA)
        draw.circle(self.circle, (255, 255, 255),
                    (self.circle.get_width() / 2, self.circle.get_height() / 2),
                    (self.circle.get_width() / 2))

        self.selected_circle = Surface((200 * self.screen_scale_width, 200 * self.screen_scale_height), SRCALPHA)
        draw.circle(self.selected_circle, (100, 200, 100),
                    (self.selected_circle.get_width() / 2, self.selected_circle.get_height() / 2),
                    (self.selected_circle.get_width() / 2), width=int(20 * self.screen_scale_width))

        rect = self.circle.get_rect(center=(150 * self.screen_scale_width, 150 * self.screen_scale_height))
        self.portrait_type_rects["commander"].append(rect)

        for index in (850, 1100, 1350):
            rect = self.circle.get_rect(center=(index * self.screen_scale_width, 150 * self.screen_scale_height))
            self.portrait_type_rects["retinue"].append(rect)

        for index in (150, 400, 650):
            rect = self.circle.get_rect(center=(index * self.screen_scale_width, 400 * self.screen_scale_height))
            self.portrait_type_rects["leader"].append(rect)

        for index in (150, 400, 650, 900, 1150):
            rect = self.circle.get_rect(center=(index * self.screen_scale_width, 650 * self.screen_scale_height))
            self.portrait_type_rects["troop"].append(rect)

        for index in (150, 400, 650, 900, 1150):
            rect = self.circle.get_rect(center=(index * self.screen_scale_width, 900 * self.screen_scale_height))
            self.portrait_type_rects["air"].append(rect)

        self.army_preset = deepcopy(self.empty_army_preset)
        self.selected_faction = Custom_Default_Culture
        self.current_preset = ""
        self.selected_portrait_index = ()
        self.rect = self.image.get_rect(midtop=pos)

    def change_faction(self, selected_faction):
        """Reset army preset when player change faction"""
        self.current_preset = ""
        self.total_gold_cost = 0
        self.total_supply_usage = 0
        self.total_leadership = 0
        self.army_preset = deepcopy(self.empty_army_preset)
        self.selected_faction = selected_faction
        self.selected_portrait_index = ()
        self.game.character_selector.add(None, "")
        self.game.custom_preset_army_title.change_text(self.current_preset, self.total_gold_cost,
                                                       self.total_supply_usage, self.total_leadership)
        self.game.custom_preset_list_box.adapter.__init__()  # reset custom preset list as well
        self.reset()

    def popup(self, army_preset):
        self.army_preset = deepcopy(self.empty_army_preset)
        for index, commander in enumerate(army_preset["commander"]):
            self.selected_portrait_index = ("commander", index)
            self.change_character("commander", index, commander, change_selector=False, reset=False)
        for index, retinue in enumerate(army_preset["retinue"]):
            self.selected_portrait_index = ("retinue", index)
            self.change_character("retinue", index, retinue, change_selector=False, reset=False)
        for index, leader in enumerate(army_preset["leader"]):
            self.selected_portrait_index = ("leader", index)
            self.change_character("leader", index, leader, change_selector=False, reset=False)
        for index, troop in enumerate(army_preset["troop"]):
            self.selected_portrait_index = ("troop", index)
            self.change_character("troop", index, troop, change_selector=False, reset=False)
        for index, air_group in enumerate(army_preset["air"]):
            self.selected_portrait_index = ("air", index)
            self.change_character("air", index, air_group, change_selector=False, reset=False)
        self.selected_portrait_index = ()
        self.reset()

    def change_character(self, character_type, rect_index, character, change_selector=True, reset=True):
        self.army_preset[character_type][rect_index] = character
        if change_selector:
            if character_type in ("commander", "leader", "retinue"):
                self.game.character_selector.add(
                    self.selected_faction, character_type,
                    [value for value in self.army_preset["commander"] + self.army_preset["leader"] +
                     self.army_preset["retinue"] if value])
            else:
                self.game.character_selector.add(self.selected_faction, character_type)

        self.image.blit(self.character_portraits[character]["setup_ui"],
                        self.portrait_type_rects[character_type][rect_index])
        if reset:
            self.reset()

    def change_portrait_selection(self, character_type, new_index):
        self.selected_portrait_index = (character_type, new_index)
        self.reset()
        self.game.character_selector.add(self.selected_faction, None)  # reset character selector first
        if character_type:
            if character_type in ("commander", "leader", "retinue"):
                self.game.character_selector.add(
                    self.selected_faction, character_type,
                    [value for value in self.army_preset["commander"] + self.army_preset["leader"] +
                     self.army_preset["retinue"] if value])
            else:
                self.game.character_selector.add(self.selected_faction, character_type)

    def reset(self):
        self.image.fill((180, 100, 180))

        self.total_gold_cost = 0
        self.total_supply_usage = 0
        self.total_leadership = 0

        for character_type in ("commander", "retinue", "leader", "troop", "air"):
            for index, character in enumerate(self.army_preset[character_type]):
                rect = self.portrait_type_rects[character_type][index]
                self.image.blit(self.circle, self.portrait_type_rects[character_type][index])

                if self.selected_portrait_index and self.selected_portrait_index == (character_type, index):
                    self.image.blit(self.selected_circle, rect)
                if character:
                    self.image.blit(self.character_portraits[character]["setup_ui"], rect)
                    if character_type == "commander":
                        self.total_leadership += self.character_list[character]["Leadership"]
                    elif character_type == "retinue":
                        self.total_leadership += self.character_list[character][
                                                     "Leadership"] * Retinue_Leadership_Add_Modifier
                    self.total_gold_cost += self.character_list[character]["Cost"]
                    if character_type not in ("commander", "air", "retinue"):
                        self.total_supply_usage += self.character_list[character]["Supply"] * self.character_list[character]["Capacity"]

        self.game.custom_preset_army_title.change_text(self.current_preset, self.total_gold_cost,
                                                       self.total_supply_usage, self.total_leadership)

    def update(self, dt):
        UIMenu.update(self, dt)
        if self.mouse_over:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))
            for character_type in ("commander", "retinue", "leader", "troop", "air"):
                for index, rect in enumerate(self.portrait_type_rects[character_type]):
                    if rect.collidepoint(inside_mouse_pos):
                        if self.event_press:
                            self.button_sound_channel.play(choice(self.sound_effect_pool["button"]))
                            self.button_sound_channel.set_volume(self.game.play_effect_volume)
                            self.change_portrait_selection(character_type, index)
                        elif self.event_alt_press:
                            self.button_sound_channel.play(choice(self.sound_effect_pool["button"]))
                            self.button_sound_channel.set_volume(self.game.play_effect_volume)
                            self.army_preset[character_type][index] = None
                            self.change_portrait_selection(character_type, index)

                        character = self.army_preset[character_type][index]
                        if character:
                            character_name_text = self.grab_text(("character", character, "Name"))
                        else:
                            character_name_text = self.grab_text(("ui", "info_text_empty_" + character_type))
                            if character_type == "commander":
                                character_name_text = (character_name_text,
                                                       self.grab_text(("ui", "warn_no_commander")))
                            elif character_type == "retinue":
                                character_name_text = (character_name_text,
                                                       self.grab_text(("ui", "warn_no_retinue")))
                            else:
                                character_name_text = (character_name_text,
                                                       self.grab_text(("ui", "warn_empty_slot")))

                        self.game.text_popup.popup((self.cursor.pos[0],
                                                    self.cursor.pos[1] - (100 * self.screen_scale_height)),
                                                   character_name_text)
                        self.add_to_ui_menu_updater(self.game.text_popup)
                        return


class InputBox(UIMenu):
    def __init__(self, pos, width, text="", layer=41, text_input=True):
        UIMenu.__init__(self)
        self._layer = layer
        self.font = Font(self.ui_font["main_button"], int(60 * self.screen_scale_height))
        self.font_width = self.font.size("a")[0]
        self.typer_image = self.font.render("|", True, (150, 80, 80))
        self.pos = pos
        self.image = Surface((width - 10, int(68 * self.screen_scale_height)))
        self.max_text = int(self.image.get_width() / self.font_width)
        self.image.fill((220, 220, 220))

        self.base_image = self.image.copy()

        self.text = text
        self.text_surface = self.font.render(text, True, (30, 30, 30))
        self.text_rect = self.text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.base_text_surface = self.text_surface.copy()
        self.image.blit(self.text_surface, self.text_rect)
        self.current_pos = 0
        self.select_start_pos = None
        self.select_end_pos = None
        self.text_input = text_input

        self.typer_tick = 0.2
        self.typer_tick_limit = 0.5
        self.typer_rect = self.typer_image.get_rect(midtop=(0, 0))
        self.typer_tick_limit_negative = -self.typer_tick_limit
        self.hold_key = 0
        self.hold_key_unicode = ""

        self.rect = self.image.get_rect(center=self.pos)

    def render_text(self, text, current_to_end_pos=True):
        """Add starting text to input box"""
        self.text = text
        if current_to_end_pos:
            self.current_pos = len(self.text)  # start input at the end
        show_text = self.text

        typer_pos = self.current_pos * self.font_width
        if self.current_pos > self.max_text:
            pos_adjust = len(show_text) - self.max_text
            typer_pos = (self.current_pos - pos_adjust) * self.font_width
            show_text = show_text[len(show_text) - self.max_text:]
        if show_text:
            self.text_surface = self.font.render(show_text, True, (30, 30, 30))
        else:  # prevent text surface being empty surface so it can add typer
            self.text_surface = self.font.render(" ", True, (30, 30, 30))

        self.text_rect = self.text_surface.get_rect(midleft=(0, self.image.get_height() / 2))
        if self.select_end_pos is not None:
            if self.current_pos > self.max_text:
                selected_add = Surface(((self.select_end_pos - self.select_start_pos) * self.font_width,
                                        self.text_surface.get_height()), SRCALPHA)
                selected_add.fill((100, 100, 100, 100))
                selected_add_rect = selected_add.get_rect(
                    midleft=((self.select_start_pos - pos_adjust) * self.font_width,
                             self.text_surface.get_height() / 2))
            else:
                selected_add = Surface(((self.select_end_pos - self.select_start_pos) * self.font_width,
                                        self.text_surface.get_height()), SRCALPHA)
                selected_add.fill((100, 100, 100, 100))
                selected_add_rect = selected_add.get_rect(midleft=(self.select_start_pos * self.font_width,
                                                                   self.text_surface.get_height() / 2))
            self.text_surface.blit(selected_add, selected_add_rect)

        self.base_text_surface = self.text_surface.copy()
        self.image = self.base_image.copy()
        if self.text_input:
            self.typer_rect = self.typer_image.get_rect(midtop=(typer_pos, 0))
            self.text_surface.blit(self.typer_image, self.typer_rect)
        self.image.blit(self.text_surface, self.text_rect)

    def update(self, dt):
        if self.text_input:
            # add blipping typer
            if self.typer_tick > 0.1:
                self.typer_tick += self.game.dt
                if self.typer_tick > self.typer_tick_limit:
                    self.typer_tick = -0.11
                    self.image = self.base_image.copy()
                    self.text_surface = self.base_text_surface.copy()
                    self.text_surface.blit(self.typer_image, self.typer_rect)
                    self.image.blit(self.text_surface, self.text_rect)

            if self.typer_tick < -0.1:
                self.typer_tick -= self.game.dt
                if self.typer_tick < self.typer_tick_limit_negative:
                    self.typer_tick = 0.11
                    self.image = self.base_image.copy()
                    self.text_surface = self.base_text_surface.copy()
                    self.image.blit(self.text_surface, self.text_rect)

    def player_input(self, input_event, key_press):
        """register user keyboard and mouse input"""
        event = input_event
        event_key = None
        event_unicode = ""
        if event:
            event_key = input_event.key
            event_unicode = event.unicode
            self.hold_key = event_key  # save last holding press key
            self.hold_key_unicode = event_unicode

        if event_key == pygame.K_BACKSPACE or self.hold_key == pygame.K_BACKSPACE:
            if self.select_start_pos is None:
                if self.current_pos > 0:
                    if self.current_pos > len(self.text):  # at the last character
                        self.text = self.text[:-1]
                    else:  # delete between text
                        self.text = self.text[:self.current_pos - 1] + self.text[self.current_pos:]
                    self.current_pos -= 1
                    if self.current_pos < 0:
                        self.current_pos = 0
            else:
                self.text = self.text[:self.select_start_pos] + self.text[self.select_end_pos:]
                self.current_pos = self.select_start_pos
                self.select_start_pos = None
                self.select_end_pos = None
        elif event_key == pygame.K_RETURN or event_key == pygame.K_KP_ENTER:  # use external code instead for enter press
            pass
        elif event_key == pygame.K_RIGHT or self.hold_key == pygame.K_RIGHT:
            if self.current_pos < len(self.text):
                if key_press[pygame.K_LSHIFT] or key_press[pygame.K_RSHIFT]:
                    if self.select_start_pos is None:  # start select text
                        self.select_start_pos = self.current_pos
                        self.select_end_pos = self.select_start_pos + 1
                    else:
                        if self.current_pos < self.select_end_pos:
                            self.select_start_pos += 1
                            if self.select_start_pos == self.select_end_pos:
                                self.select_start_pos = None
                                self.select_end_pos = None
                        else:
                            self.select_end_pos += 1
                    if self.current_pos > len(self.text):
                        self.select_end_pos = len(self.text)
                else:
                    self.select_start_pos = None
                    self.select_end_pos = None
                self.current_pos += 1
        elif event_key == pygame.K_LEFT or self.hold_key == pygame.K_LEFT:
            if self.current_pos - 1 >= 0:
                if key_press[pygame.K_LSHIFT] or key_press[pygame.K_RSHIFT]:
                    if self.select_end_pos is None:  # start select text
                        self.select_end_pos = self.current_pos
                        self.select_start_pos = self.select_end_pos - 1
                    else:
                        if self.current_pos > self.select_start_pos:
                            self.select_end_pos -= 1
                            if self.select_start_pos == self.select_end_pos:
                                self.select_start_pos = None
                                self.select_end_pos = None
                        else:
                            self.select_start_pos -= 1
                    if self.current_pos < 0:
                        self.select_start_pos = 0
                else:
                    self.select_start_pos = None
                    self.select_end_pos = None
                self.current_pos -= 1

        elif key_press and (key_press[pygame.K_LCTRL] or key_press[pygame.K_RCTRL]):
            # use keypress for ctrl as is has no effect on its own
            if event_key == pygame.K_c:
                pyperclip.copy(self.text[self.select_start_pos:self.select_end_pos])
            elif event_key == pygame.K_v:
                paste_text = pyperclip.paste()
                if self.select_start_pos is None:
                    self.text = self.text[:self.current_pos] + paste_text + self.text[self.current_pos:]
                    self.current_pos = self.current_pos + len(paste_text)
                else:
                    self.text = self.text[:self.select_start_pos] + paste_text + self.text[self.select_end_pos:]
                    self.current_pos = self.select_start_pos + len(paste_text)
                    self.select_start_pos = None
                    self.select_end_pos = None
            elif event_key == pygame.K_a:  # select all
                self.select_end_pos = len(self.text)
                self.current_pos = self.select_end_pos
                self.select_start_pos = 0

        elif event_unicode != "" or self.hold_key_unicode != "":
            if event_unicode != "":  # input event_unicode first before holding one
                input_unicode = event_unicode
            elif self.hold_key_unicode != "":
                input_unicode = self.hold_key_unicode

            if self.select_start_pos is None:
                self.text = self.text[:self.current_pos] + input_unicode + self.text[self.current_pos:]
                self.current_pos += 1
            else:
                self.text = self.text[:self.select_start_pos] + input_unicode + self.text[self.select_end_pos:]
                self.current_pos = self.select_start_pos + 1
                self.select_start_pos = None
                self.select_end_pos = None

        # Re-render the text
        self.render_text(self.text, current_to_end_pos=False)


class TextBox(UIMenu):
    def __init__(self, image, pos, text):
        self._layer = 13
        UIMenu.__init__(self)

        self.font = Font(self.ui_font["main_button"], int(72 * self.screen_scale_height))
        self.image = image

        self.base_image = self.image.copy()

        text_surface = self.font.render(text, True, (30, 30, 30))
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surface, text_rect)

        self.rect = self.image.get_rect(topright=pos)

    def change_text(self, text):
        self.image = self.base_image.copy()

        text_surface = self.font.render(text, True, (30, 30, 30))
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surface, text_rect)


class MenuImageButton(UIMenu):
    def __init__(self, pos, image, layer=1):
        self._layer = layer
        UIMenu.__init__(self, player_cursor_interact=True)
        self.pos = pos
        self.image = image
        self.rect = self.image.get_rect(center=self.pos)


class MenuButton(UIMenu):
    def __init__(self, images, pos, key_name=(), font_size=56, layer=1):
        self._layer = layer
        UIMenu.__init__(self, play_sound_when_click=True)
        self.pos = pos
        self.button_normal_image = images[0].copy()
        self.button_over_image = images[1].copy()
        self.button_click_image = images[2].copy()

        self.font = Font(self.ui_font["main_button"], int(font_size * self.screen_scale_height))
        self.base_image0 = self.button_normal_image.copy()
        self.base_image1 = self.button_over_image.copy()
        self.base_image2 = self.button_click_image.copy()

        self.text = ""
        if key_name:  # draw text into the button images
            if type(key_name) is not tuple:
                key_name = (key_name,)
            for item in key_name:
                if type(item) is int or item.isdigit():
                    self.text += add_comma_number(int(item))
                else:
                    self.text += self.grab_text(("ui", item))
            text_surface = self.font.render(self.text, True, (30, 30, 30))
            text_rect = text_surface.get_rect(center=(self.button_normal_image.get_width() / 2,
                                                      self.button_normal_image.get_height() / 2))
            self.button_normal_image.blit(text_surface, text_rect)
            self.button_over_image.blit(text_surface, text_rect)
            self.button_click_image.blit(text_surface, text_rect)

        self.image = self.button_normal_image
        self.rect = self.button_normal_image.get_rect(center=self.pos)

    def update(self, dt):
        self.event = False
        self.event_press = False
        self.mouse_over = False
        self.image = self.button_normal_image
        if not self.pause and self.rect.collidepoint(self.cursor.pos):
            self.mouse_over = True
            self.image = self.button_over_image
            if self.cursor.is_select_just_up:
                self.event = True
                self.event_press = True
                self.image = self.button_click_image
                self.cursor.is_select_just_up = False  # reset select button to prevent overlap interaction
            elif self.cursor.is_select_down:
                self.event_hold = True
                self.cursor.is_select_just_down = False  # reset select button to prevent overlap interaction
                self.image = self.button_click_image

    def change_state(self, key_name, no_localisation=False):
        self.button_normal_image = self.base_image0.copy()
        self.button_over_image = self.base_image1.copy()
        self.button_click_image = self.base_image2.copy()
        self.text = ""
        if key_name:
            if type(key_name) is not tuple:
                key_name = (key_name,)
            for item in key_name:
                if type(item) is int or item.isdigit():
                    self.text += add_comma_number(item)
                else:
                    if no_localisation:
                        self.text += item
                    else:
                        self.text += self.grab_text(("ui", item))

            text_surface = self.font.render(self.text, True, (30, 30, 30))
            text_rect = text_surface.get_rect(center=(self.button_normal_image.get_width() / 2,
                                                      self.button_normal_image.get_height() / 2))
            self.button_normal_image.blit(text_surface, text_rect)
            self.button_over_image.blit(text_surface, text_rect)
            self.button_click_image.blit(text_surface, text_rect)
        self.rect = self.button_normal_image.get_rect(center=self.pos)
        self.event = False


class Container:

    def get_rect(self):
        raise NotImplementedError()


class Containable:

    def get_relative_position_inside_container(self):
        raise NotImplementedError()

    def get_relative_size_inside_container(self):
        return None

    def get_size(self):
        raise NotImplementedError()

    def converse_pos_origin(self, pos, container):
        """Convert pos to origin value (-1, 1 scale)"""
        origin = [pos[0], pos[1]]
        for index, this_pos in enumerate(origin):
            container_size = container.get_size()[index]
            this_pos = container_size - this_pos  # some magic to make it appear not too far from pos
            if this_pos > container.get_size()[index] / 2:  # + scale
                origin[index] = round(this_pos / container_size, 2)
            elif this_pos < container.get_size()[index] / 2:  # - scale
                if this_pos == 0:  # 0 value mean at most left/top
                    origin[index] = -1
                else:
                    origin[index] = -1 + round(this_pos / container_size, 2)
            else:  # center
                origin[index] = 0
        return origin

    def change_origin_with_pos(self, pos):
        self.origin = self.converse_pos_origin(pos, self.parent)
        self.rect = self.get_adjusted_rect_to_be_inside_container(self.parent)

    def get_adjusted_rect_to_be_inside_container(self, container):
        rpic = self.get_relative_position_inside_container()
        rsic = self.get_relative_size_inside_container()
        pivot = rpic["pivot"]
        origin = rpic["origin"]

        if rsic is None:
            return Rect(
                *[container.get_rect()[i] - (self.get_size()[i] * (origin[i] + 1)) // 2 + (pivot[i] + 1) *
                  container.get_rect()[i + 2] // 2 for i in
                  range(2)], *self.get_size())
        else:
            size = [container.get_size()[i] * rsic[i] for i in range(2)]
            return Rect(
                *[container.get_rect()[i] - (size[i] * (origin[i] + 1)) // 2 + (pivot[i] + 1) * container.get_rect()[
                    i + 2] // 2 for i in range(2)],
                *size)


class BrownMenuButton(UIMenu, Containable):  # NOTE: the button is not brown anymore, it is white/yellow
    button_frame = None

    def __init__(self, size, pos, key_name, parent):
        """
        Create dynamic button
        @param size: tuple of relative size to parent
        @param pos: relative position inside parent surface
        @param key_name: localisation key name for ui
        @param parent: parent sprite object
        """
        self.parent = parent
        self._layer = parent.layer + 1
        UIMenu.__init__(self, play_sound_when_click=True)
        self.size = size
        self.pos = pos
        self.key_name = key_name
        self.rect = self.get_adjusted_rect_to_be_inside_container(self.parent)
        self.mouse_over = False
        self.event = False
        self.font = Font(self.ui_font["main_button"], int(48 * self.screen_scale_height))
        self.text = self.grab_text(("ui", self.key_name))
        self.images = self.make_buttons(size=tuple(self.rect[2:]), text=self.text, font=self.font)
        self.refresh()

    @lru_cache
    def make_buttons(self, size, text, font):
        normal_button = make_image_by_frame(self.button_frame, size)
        text_surface = font.render(text, True, (0,) * 3)
        text_rect = text_surface.get_rect(center=normal_button.get_rect().center)
        normal_button.blit(text_surface, text_rect)

        hover_button = normal_button.copy()
        draw.rect(hover_button, "#DD0000", hover_button.get_rect(), 2)

        dark_shade = Surface(hover_button.get_size(), SRCALPHA)
        dark_shade.fill((0, 0, 0, 80))
        click_button = normal_button.copy()
        click_button.blit(dark_shade, (0, 0))
        return normal_button, hover_button, click_button

    def get_relative_size_inside_container(self):
        return self.size

    def refresh(self):
        self.image = self.images[0]
        if self.event:
            self.image = self.images[2]
        elif self.mouse_over:
            self.image = self.images[1]

    def get_relative_position_inside_container(self):
        return {
            "origin": (0, 0),
            "pivot": self.pos,
        }

    def update(self, dt):
        UIMenu.update(self, dt)
        self.refresh()

    def get_size(self):
        return self.image.get_size()

    def change_state(self, text):
        pass


class OptionMenuText(UIMenu):
    def __init__(self, pos, text, text_size, button_image=None):
        self._layer = 10
        UIMenu.__init__(self, player_cursor_interact=False)
        self.pos = pos
        self.font = Font(self.ui_font["main_button"], text_size)
        if button_image:  # add image to front of text
            text_surface = text_render_with_bg(text, self.font, Color("black"))
            self.image = Surface((button_image.get_width() + (5 * self.screen_scale_width) +
                                  text_surface.get_width(), button_image.get_height()), SRCALPHA)
            text_rect = text_surface.get_rect(topright=(self.image.get_width(), 0))
            self.image.blit(text_surface, text_rect)
            button_rect = button_image.get_rect(topleft=(0, 0))
            self.image.blit(button_image, button_rect)
        else:
            self.image = text_render_with_bg(text, self.font, Color("black"))
        self.rect = self.image.get_rect(center=(self.pos[0] - (self.image.get_width() / 2), self.pos[1]))


# class RewardInterface(UIMenu):
#     def __init__(self, pos, base_image):
#         self.header_font = Font(self.ui_font["main_button"], int(36 * self.screen_scale_height))
#         self.font = Font(self.ui_font["main_button"], int(22 * self.screen_scale_height))
#         self.small_font = Font(self.ui_font["main_button"], int(18 * self.screen_scale_height))
#         self.reward_list = {}
#         self.shown_reward_list = []
#         self.base_image = base_image
#
#     def add_reward_list(self):
#         self.image = self.base_image.copy()
#         self.shown_reward_list = []
#
#         index = 0
#         row_index = 0
#         for item in self.reward_list:
#             if (index >= self.current_row or self.len_reward_list < 9) and row_index < 9:
#                 if index == 0:  # first item in list
#                     draw.rect(self.image, (150, 150, 150),
#                               (0, (row_index * 100) * self.screen_scale_height, 400 * self.screen_scale_width,
#                                100 * self.screen_scale_height),
#                               width=int(3 * self.screen_scale_width))
#
#                 if index == self.len_reward_list - 1:  # last item in list
#                     draw.rect(self.image, (150, 50, 50),
#                               (0, (row_index * 100) * self.screen_scale_height, 400 * self.screen_scale_width,
#                                100 * self.screen_scale_height),
#                               width=int(3 * self.screen_scale_width))
#
#                 if item in self.game.character_data.character_list:  # follower reward
#                     character_ui = self.game.animation_data.character_portraits[item]
#                     rect = character_ui.get_rect(topleft=(0, row_index * 100 * self.screen_scale_height))
#                     self.image.blit(character_ui, rect)
#                     make_long_text(self.image, self.grab_text(("character", item, "Name")),
#                                    (110 * self.screen_scale_width,
#                                     row_index * 100 * self.screen_scale_height), self.font, color=(30, 30, 30),
#                                    specific_width=self.image.get_width() - (50 * self.screen_scale_width))
#
#                     item_image = self.item_sprite_pool["Normal"][item_id]
#                     rect = item_image.get_rect(topleft=(0, row_index * 100 * self.screen_scale_height))
#                     self.image.blit(item_image, rect)
#
#                 self.shown_reward_list.append((reward_type, item))
#
#                 row_index += 1
#
#             index += 1


class KeybindIcon(UIMenu):
    def __init__(self, pos, text_size, key):
        self._layer = 100
        UIMenu.__init__(self)
        self.font = Font(self.ui_font["main_button"], text_size)
        self.pos = pos
        self.change_key(key)
        self.rect = self.image.get_rect(center=self.pos)

    def change_key(self, key):
        if type(key) is str and "click" in key:
            self.draw_keyboard(key)
        else:
            self.draw_keyboard(pygame.key.name(key))
        self.rect = self.image.get_rect(center=self.pos)

    def draw_keyboard(self, text):
        text_surface = self.font.render(text.capitalize(), True, (30, 30, 30))
        size = text_surface.get_size()
        image_size = size[0] * 2
        if size[0] < 40:
            image_size = size[0] * 4
        self.image = Surface((image_size, size[1] * 2), SRCALPHA)
        draw.rect(self.image, (120, 120, 120), (0, 0, image_size, size[1] * 2), border_radius=2)
        draw.rect(self.image, (220, 220, 220),
                  (image_size * 0.1, size[1] * 0.3, image_size * 0.8, size[1] * 1.5),
                  border_radius=2)
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surface, text_rect)

    def draw_joystick(self, key, keybind_name):
        text_surface = self.font.render(keybind_name[key], True, (30, 30, 30))
        size = text_surface.get_size()
        image_size = size[0] * 2
        if size[0] < 40:
            image_size = size[0] * 4
        self.image = Surface((image_size, size[1] * 2), SRCALPHA)
        draw.circle(self.image, (220, 220, 220), (self.image.get_width() / 2, self.image.get_height() / 2),
                    self.image.get_width() / 2)
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surface, text_rect)


class ValueBox(UIMenu):
    def __init__(self, image, pos, value, text_size):
        self._layer = 26
        UIMenu.__init__(self, player_cursor_interact=False)
        self.font = Font(self.ui_font["main_button"], text_size)
        self.pos = pos
        self.image = image.copy()
        self.base_image = self.image.copy()
        self.value = value
        text_surface = self.font.render(str(self.value), True, (30, 30, 30))
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surface, text_rect)
        self.rect = self.image.get_rect(center=self.pos)

    def change_value(self, value):
        self.value = value
        self.image = self.base_image.copy()
        text_surface = self.font.render(str(self.value), True, (30, 30, 30))
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surface, text_rect)


class NameTextBox(UIMenu):
    def __init__(self, box_size, pos, name, text_size=26, layer=15, box_colour=(220, 220, 220),
                 corner_colour=(30, 30, 30), center_text=False):
        self._layer = layer
        UIMenu.__init__(self)
        self.font = Font(self.ui_font["main_button"], int(text_size * self.screen_scale_height))
        self.name = str(name)

        self.image = Surface(box_size)
        self.image.fill(corner_colour)  # black corner

        # White body square
        white_body = Surface((self.image.get_width() - 2, self.image.get_height() - 2))
        white_body.fill(box_colour)
        small_rect = white_body.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(white_body, small_rect)

        self.image_base = self.image.copy()

        # Name text
        text_surface = self.font.render(self.name, True, (30, 30, 30))
        if center_text:
            text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        else:  # text start at the left
            text_rect = text_surface.get_rect(midleft=(int(text_size * self.screen_scale_height),
                                                       self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)

        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)

    def rename(self, new_name):
        self.name = new_name
        self.image = self.image_base.copy()
        text_surface = self.font.render(self.name, True, (30, 30, 30))
        text_rect = text_surface.get_rect(midleft=(int(3 * self.screen_scale_width), self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)


class ListBox(UIMenu):
    def __init__(self, pos, image, layer=14):
        self._layer = layer
        UIMenu.__init__(self, player_cursor_interact=False)
        self.image = image.copy()
        self.name_list_start = (self.image.get_width(), self.image.get_height())
        self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)

        image_height = int(30 * self.screen_scale_height)
        self.max_row_show = int(self.image.get_height() / image_height)  # max number of map on list can be shown


class NameList(UIMenu):
    def __init__(self, box, pos, name, text_size=26, layer=15):
        self._layer = layer
        UIMenu.__init__(self, play_sound_when_click=True)
        self.font = Font(self.ui_font["main_button"], int(self.screen_scale_height * text_size))
        self.name = str(name)

        self.image = Surface(
            (box.image.get_width() - int(20 * self.screen_scale_width),
             int((text_size + 4) * self.screen_scale_height)))  # black corner
        self.image.fill((30, 30, 30))
        self.selected_image = self.image.copy()
        self.selected = False

        # White body square
        small_image = Surface(
            (
                box.image.get_width() - int(16 * self.screen_scale_width),
                int((text_size + 2) * self.screen_scale_height)))
        small_image.fill((220, 220, 220))
        small_rect = small_image.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(small_image, small_rect)
        small_image.fill((255, 255, 128))
        self.selected_image.blit(small_image, small_rect)

        self.image_base = self.image.copy()

        # text
        text_surface = self.font.render(self.name, True, (30, 30, 30))
        text_rect = text_surface.get_rect(midleft=(int(6 * self.screen_scale_width), self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)
        self.selected_image.blit(text_surface, text_rect)

        self.not_selected_image = self.image.copy()

        self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)

    def select(self):
        if self.selected:
            self.selected = False
            self.image = self.not_selected_image.copy()
        else:
            self.selected = True
            self.image = self.selected_image.copy()

    def rename(self, new_name):
        self.name = new_name
        self.image = self.image_base.copy()
        text_surface = self.font.render(self.name, True, (30, 30, 30))
        text_rect = text_surface.get_rect(midleft=(int(6 * self.screen_scale_width), self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)
        self.selected_image.blit(text_surface, text_rect)

        self.not_selected_image = self.image.copy()


class GrandFactionDetail(UIMenu):
    def __init__(self, layer=15):
        self._layer = layer
        UIMenu.__init__(self, player_cursor_interact=False)
        self.header_font = self.game.preset_name_font
        self.font = self.game.large_generic_ui_font
        self.font_size = self.font.size(" ")[1]
        self.image = Surface((900 * self.screen_scale_width, 1200 * self.screen_scale_height))
        self.image.fill((255, 255, 255))
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect(topleft=self.game.custom_preset_faction_selector.rect.bottomleft)

    def change_faction(self, faction):
        self.image = self.original_image.copy()

        faction_name_text = self.header_font.render(self.grab_text(("faction", faction, "Name")),
                                                    True, (30, 30, 30))
        self.image.blit(faction_name_text, faction_name_text.get_rect(center=(self.image.get_width() / 2,
                                                                              self.font_size)))

        make_long_text(self.image, (self.grab_text(("faction", faction, "Description"))),
                       (self.font_size / 2, self.font_size * 3), self.font,
                       color=(30, 30, 30), specific_width=(self.image.get_width() * 0.95))


class CharacterDescriptionShowCase(UIMenu):
    def __init__(self, layer=15):
        self._layer = layer
        UIMenu.__init__(self)
        self.header_font = self.game.battle_timer_font
        self.font = self.game.large_generic_ui_font
        self.name_cap_font = self.game.screen_fade_font
        self.character_portraits = self.game.sprite_data.character_portraits
        self.showing_character = None
        self.image = Surface((2200 * self.screen_scale_width, 550 * self.screen_scale_height))
        self.image.fill((200, 200, 200))
        self.description_box = Surface((1500 * self.screen_scale_width, 450 * self.screen_scale_height))
        self.description_box.fill((200, 200, 200))
        self.original_image = self.image.copy()

        self.rect = self.image.get_rect(topleft=self.game.lorebook_showcase_character_selector.rect.bottomleft)

    def change_character(self, character):
        if character != self.showing_character:
            self.image = self.original_image.copy()
            portrait = self.character_portraits[character]["character_ui"]
            portrait_rect = portrait.get_rect(topleft=(0, 0))
            self.image.blit(portrait, portrait_rect)
            name = self.grab_text(("character", character, "Name"))
            character_name = self.name_cap_font.render(name, True, (30, 30, 30))
            character_name_rect = character_name.get_rect(topleft=portrait_rect.topright)
            self.image.blit(character_name, character_name_rect)
            self.description_box.fill((200, 200, 200))
            make_long_text(self.description_box, (self.grab_text(("character", character, "Lore"))),
                           (0, 0), self.font)
            self.image.blit(self.description_box, self.description_box.get_rect(topleft=character_name_rect.bottomleft))


class CharacterMovesetShowCase(UIMenu):
    def __init__(self, layer=15):
        self._layer = layer
        UIMenu.__init__(self)
        self.character_list = self.game.character_list
        self.effect_list = self.game.character_data.effect_list
        self.header_font = self.game.battle_timer_font
        self.font = self.game.large_generic_ui_font
        self.font_space_size = self.font.size(" ")
        self.showing_character = None
        self.showing_moveset = None
        self.image = Surface((1640 * self.screen_scale_width, 550 * self.screen_scale_height))
        self.image.fill((200, 200, 200))
        self.original_image = self.image.copy()

        self.rect = self.image.get_rect(topright=self.game.lorebook_showcase_animation_list_box.rect.bottomright)

    def change_moveset(self, character, moveset):
        if character != self.showing_character or moveset != self.showing_moveset:
            self.showing_character = character
            self.showing_moveset = moveset
            self.image = self.original_image.copy()
            if moveset:
                this_moveset = deepcopy(self.character_list[character]["Move"][moveset])

                char_stat = []
                range_use = ""
                if this_moveset["AI Range"]:
                    range_use += self.grab_text(("ui", "info_header_activate_range")) + add_comma_number(
                        this_moveset["AI Range"])
                if this_moveset["Range"]:
                    if range_use:
                        range_use += "/"
                    range_use += self.grab_text(("ui", "info_header_range")) + add_comma_number(this_moveset["Range"])
                if range_use:
                    char_stat.append(range_use)
                if this_moveset["Resource Cost"]:
                    char_stat.append(
                        self.grab_text(("ui", "info_header_resource")) + str(this_moveset["Resource Cost"]))
                if this_moveset["Cooldown"]:
                    char_stat.append(self.grab_text(("ui", "info_header_cooldown")) + str(this_moveset["Cooldown"]))
                if this_moveset["Power"]:
                    char_stat.append(self.grab_text(("ui", "info_header_power")) + str(this_moveset["Power"]))
                if this_moveset["Penetrate"]:
                    char_stat.append(self.grab_text(("ui", "info_header_penetrate")) + str(this_moveset["Penetrate"]))
                if this_moveset["Impact X"] or this_moveset["Impact Y"]:
                    char_stat.append(self.grab_text(("ui", "info_header_impact")) +
                                     add_comma_number(abs(this_moveset["Impact X"]) + abs(this_moveset["Impact Y"])))
                if this_moveset["Critical Chance Bonus"]:
                    char_stat.append(self.grab_text(("ui", "info_header_critical_bonus")) +
                                     str(this_moveset["Critical Chance Bonus"]))
                if this_moveset["Element"]:
                    char_stat.append(self.grab_text(("ui", "info_header_element")) +
                                     self.grab_text(("ui", "element_" + str(this_moveset["Element"]))))
                if this_moveset["Status"]:
                    tag_text = ""
                    ally_status_list = this_moveset["Status"]
                    ally_status_list = set(ally_status_list)
                    for prop in ally_status_list:
                        prop_text = self.grab_text(("status", prop, "Name"))
                        if "(" not in prop_text:  # mean prop has no localisation, likely intentional
                            tag_text += prop_text + ", "
                    if tag_text:
                        tag_text = self.grab_text(("ui", "info_header_status")) + tag_text
                        tag_text = tag_text[:-2]  # remove additional comma
                        char_stat.append(tag_text)
                if this_moveset["Enemy Status"] or this_moveset["Effect Enemy Status"]:
                    tag_text = ""
                    enemy_status_list = this_moveset["Enemy Status"] + this_moveset["Effect Enemy Status"]
                    enemy_status_list = set(enemy_status_list)
                    for prop in enemy_status_list:
                        prop_text = self.grab_text(("status", prop, "Name"))
                        if "(" not in prop_text:  # mean prop has no localisation, likely intentional
                            tag_text += prop_text + ", "
                    if tag_text:
                        tag_text = self.grab_text(("ui", "info_header_enemy_status")) + tag_text
                        tag_text = tag_text[:-2]  # remove additional comma
                        char_stat.append(tag_text)
                if this_moveset["Property"]:
                    tag_text = ""
                    moveset_property = this_moveset["Property"]
                    for prop in moveset_property:
                        prop_text = self.grab_text(("ui", "property_" + prop))
                        if prop == "summon":
                            prop_text = prop_text + self.grab_text(
                                ("character", moveset_property[prop], "Name"))
                        elif prop == "x_momentum":
                            prop_text = prop_text + str(moveset_property[prop])
                        if "(" not in prop_text:  # mean prop has no localisation, likely intentional
                            tag_text += prop_text + ", "
                    if tag_text:
                        tag_text = self.grab_text(("ui", "info_header_property")) + tag_text
                        tag_text = tag_text[:-2]  # remove additional comma
                        char_stat.append(tag_text)
                make_long_text(self.image, char_stat, self.font_space_size, self.font)


class GrandFactionShowCase(UIMenu):
    def __init__(self, layer=15):
        self._layer = layer
        UIMenu.__init__(self)
        self.header_font = self.game.battle_timer_font
        self.font = self.game.large_generic_ui_font
        self.character_portraits = self.game.sprite_data.character_portraits
        self.character_list = self.game.character_list
        self.culture_coas = self.game.sprite_data.culture_coas
        self.image = Surface((900 * self.screen_scale_width, 1200 * self.screen_scale_height))
        self.image.fill((255, 255, 255))
        self.original_image = self.image.copy()

        self.showcase = {"ruler": [None], "leader": [], "troop": []}
        self.showcase_rect = {"ruler": [self.character_portraits[Default_Showcase_Character]["character_ui"].get_rect(
            center=(self.image.get_width() / 2, 250 * self.screen_scale_height))],
            "leader": [self.character_portraits[Default_Showcase_Character]["small"]["right"].get_rect(
                center=(x * self.screen_scale_width, 800 * self.screen_scale_height)) for x in (150, 350, 550, 750)],
            "troop": [self.character_portraits[Default_Showcase_Character]["small"]["right"].get_rect(
                center=(x * self.screen_scale_width, 1000 * self.screen_scale_height)) for x in (150, 350, 550, 750)]}

        self.culture = None
        self.culture_rect = self.culture_coas[tuple(self.culture_coas.keys())[0]]["small"].get_rect(center=(
            self.image.get_width() / 2, 600 * self.screen_scale_height))

        self.rect = self.image.get_rect(topright=self.game.custom_preset_faction_selector.rect.bottomright)

    def change_faction(self, faction):
        self.image = self.original_image.copy()
        faction_data = self.game.map_data.faction_list[faction]
        ruler = faction_data["Ruler"]
        ruler_portrait = self.character_portraits[ruler]["character_ui"]
        self.image.blit(ruler_portrait, self.showcase_rect["ruler"][0])
        self.showcase = {"ruler": [ruler], "leader": [], "troop": []}

        self.culture = faction_data["Culture"]
        culture_coa = self.culture_coas[faction_data["Culture"]]["small"]
        self.image.blit(culture_coa, self.culture_rect)

        for index, character in enumerate(faction_data["Showcase Leader"]):
            self.showcase["leader"].append(character)
            character_portrait = self.character_portraits[character]["small"]["right"]
            self.image.blit(character_portrait, self.showcase_rect["leader"][index])

        for index, character in enumerate(faction_data["Showcase Troop"]):
            self.showcase["troop"].append(character)
            character_portrait = self.character_portraits[character]["small"]["right"]
            self.image.blit(character_portrait, self.showcase_rect["troop"][index])

    def update(self, dt):
        UIMenu.update(self, dt)
        if self.rect.collidepoint(self.cursor.pos):
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))
            if self.culture_rect.collidepoint(inside_mouse_pos):
                culture_stat = [self.grab_text(("ui", "info_header_culture")) + self.grab_text(
                    ("culture", self.culture, "Name")),
                                self.grab_text(("culture", self.culture, "Description")),
                                "",
                                self.grab_text(("ui", "info_header_strengths")) + self.grab_text(
                                    ("culture", self.culture, "Strengths")),
                                "",
                                self.grab_text(("ui", "info_header_weaknesses")) + self.grab_text(
                                    ("culture", self.culture, "Weaknesses"))
                                ]
                self.game.text_popup.popup(self.cursor.rect, culture_stat,
                                           width_text_wrapper=int(1400 * self.screen_scale_width))
                self.add_to_ui_menu_updater(self.game.text_popup)
            else:
                for rect_type, rect_list in self.showcase_rect.items():
                    for index, rect in enumerate(rect_list):
                        if rect.collidepoint(inside_mouse_pos):
                            character_id = self.showcase[rect_type][index]
                            char_stat = [self.grab_text(("ui", "info_header_name")) + self.grab_text(
                                ("character", character_id, "Name")),
                                         self.grab_text(("character", character_id, "Description"))]

                            self.game.text_popup.popup(self.cursor.rect, char_stat,
                                                       width_text_wrapper=int(1200 * self.screen_scale_width))
                            self.add_to_ui_menu_updater(self.game.text_popup)
                            return


class GrandMiniMap(UIMenu):
    def __init__(self, pos, size, ui_purpose, layer=15):
        self._layer = layer
        from engine.grand.grand import Grand
        self.grand = Grand.grand
        if ui_purpose == "setup":
            UIMenu.__init__(self, player_cursor_interact=False)
        elif ui_purpose == "grand":
            UIMenu.__init__(self)

        self.map_data = self.game.map_data
        self.ui_purpose = ui_purpose
        self.region_draw_dict = {}
        self.region_control_data = {}
        self.pos = pos
        self.size = (size[0] * self.screen_scale_width, size[1] * self.screen_scale_height)
        self.base_image = None
        self.before_scale_image = None
        self.before_camera_image = None
        self.map_scale_width = 1
        self.map_scale_height = 1
        self.camera_border_image = None
        self.camera_pos = None
        self.image = Surface(self.size)
        self.rect = self.image.get_rect(midtop=pos)

    def change_grand_setup(self, world_image):
        """Recreate minimap image, create faction image with region in colour of control faction"""
        image = scale(world_image, self.size)
        self.base_image = Surface(image.get_size())
        self.base_image.fill((112, 140, 190))  # fill sea colour
        self.region_draw_dict = {}
        region_draw_dict = self.region_draw_dict
        faction_list = self.map_data.faction_list
        for row_pos in range(image.get_width()):
            for col_pos in range(image.get_height()):
                colour = tuple(image.get_at((row_pos, col_pos)))[:3]
                if colour != (0, 0, 0):
                    region_id = self.map_data.region_by_colour_index[colour]
                    if region_id not in region_draw_dict:
                        region_draw_dict[region_id] = {"min_pos": [float("inf"), float("inf")], "max_pos": [0, 0],
                                                       "array": []}
                    if row_pos < region_draw_dict[region_id]["min_pos"][0]:
                        region_draw_dict[region_id]["min_pos"][0] = row_pos
                    if row_pos > region_draw_dict[region_id]["max_pos"][0]:
                        region_draw_dict[region_id]["max_pos"][0] = row_pos
                    if col_pos < region_draw_dict[region_id]["min_pos"][1]:
                        region_draw_dict[region_id]["min_pos"][1] = col_pos
                    if col_pos > region_draw_dict[region_id]["max_pos"][1]:
                        region_draw_dict[region_id]["max_pos"][1] = col_pos
                    region_draw_dict[region_id]["array"].append((row_pos, col_pos))
                    self.base_image.set_at((row_pos, col_pos), faction_list["free"]["Colour"])

        self.before_scale_image = self.base_image.copy()
        self.before_camera_image = smoothscale(self.before_scale_image, self.size)
        self.image = self.before_camera_image.copy()
        self.rect = self.image.get_rect(midtop=self.pos)

        if self.ui_purpose == "grand":
            self.map_scale_width = self.grand.grand_map.full_shown_map_image.get_width() / self.image.get_width()
            self.map_scale_height = self.grand.grand_map.full_shown_map_image.get_height() / self.image.get_height()
            self.camera_border_image = Surface((self.screen_width / self.map_scale_width,
                                                self.screen_height / self.map_scale_height), SRCALPHA)
            draw.rect(self.camera_border_image, (250, 100, 100), self.camera_border_image.get_rect(),
                      width=int(10 * self.screen_scale_width))

    def change_grand_faction(self, region_control_data):
        """Used in grand campaign game minimap, repaint faction colour of control change regions"""
        if self.region_control_data != region_control_data:
            self.before_scale_image = self.base_image.copy()
            for region_id in region_control_data:
                if (region_id not in self.region_control_data or
                        region_control_data[region_id] != self.region_control_data[region_id]):
                    self.draw_faction(region_control_data[region_id], region_id)
            self.region_control_data = region_control_data.copy()
            self.before_camera_image = smoothscale(self.before_scale_image, self.size)
            self.image = self.before_camera_image.copy()

    def change_faction(self, faction, region_control_data):
        """Used in grand campaign setup menu, highlight region that selected faction control in white colour"""
        self.region_control_data = region_control_data
        self.before_scale_image = self.base_image.copy()
        for region_id in self.region_draw_dict:
            if self.map_data.region_list[region_id]["Control"] == faction:
                self.draw_faction(faction, region_id)
        self.before_camera_image = smoothscale(self.before_scale_image, self.size)
        self.image = self.before_camera_image.copy()

    def draw_faction(self, faction_control, region_id, add_border=True):
        region_draw_data = self.region_draw_dict[region_id]
        new_surf = Surface((region_draw_data["max_pos"][0] - region_draw_data["min_pos"][0],
                            region_draw_data["max_pos"][1] - region_draw_data["min_pos"][1]), SRCALPHA)
        # draw colour based on faction control
        for pos in region_draw_data["array"]:
            new_pos = (pos[0] - region_draw_data["min_pos"][0], pos[1] - region_draw_data["min_pos"][1])
            new_surf.set_at(new_pos, (255, 255, 255))
        in_surf = smoothscale(new_surf, (new_surf.get_width() * 0.8, new_surf.get_height() * 0.8))
        in_surf.fill(self.game.map_data.faction_list[faction_control]["Colour"], special_flags=pygame.BLEND_RGBA_MIN)

        new_surf.blit(in_surf, in_surf.get_rect(center=(new_surf.get_width() / 2, new_surf.get_height() / 2)))
        self.before_scale_image.blit(new_surf, new_surf.get_rect(topleft=region_draw_data["min_pos"]))

    def update(self, dt):
        """update map"""
        if self.player_interact:
            UIMenu.update(self, dt)
            if self.event_press:
                inside_mouse_pos = Vector2(
                    (self.cursor.pos[0] - self.rect.topleft[0]),
                    (self.cursor.pos[1] - self.rect.topleft[1]))
                self.grand.camera_pos = Vector2((inside_mouse_pos[0] * self.map_scale_width) - self.half_screen_width,
                                                (inside_mouse_pos[1] * self.map_scale_height) - self.half_screen_height)
                self.grand.fix_camera()

            if self.camera_pos != self.grand.camera_pos:
                self.image = self.before_camera_image.copy()

                # Draw camera border
                self.image.blit(self.camera_border_image,
                                self.camera_border_image.get_rect(topleft=(
                                    self.grand.camera_pos[0] / self.map_scale_width,
                                    self.grand.camera_pos[1] / self.map_scale_height)))
                self.camera_pos = self.grand.camera_pos.copy()


class ListAdapter:
    def __init__(self, _list, replace_on_select=None, replace_on_alt_select=None, replace_on_mouse_over=None):
        from engine.game.game import Game
        self.game = Game.game
        self.list = _list
        self.last_index = -1
        if replace_on_select:
            self.on_select = types.MethodType(replace_on_select, self)
        if replace_on_alt_select:
            self.on_alt_select = types.MethodType(replace_on_alt_select, self)
        if replace_on_mouse_over:
            self.on_mouse_over = types.MethodType(replace_on_mouse_over, self)

    def __len__(self):
        return len(self.list)

    def to_tuple(self):
        l = len(self)
        x = [self[c] for c in range(l)]
        return tuple(x)

    def __getitem__(self, item):
        return self.list[item]

    def on_select(self, item_index, item_text):
        pass

    def on_alt_select(self, item_index, item_text):
        pass

    def on_mouse_over(self, item_index, item_text):
        pass

    def get_highlighted_index(self):
        return self.last_index


class ListAdapterHideExpand(ListAdapter):

    # actual list refer to the origin full list
    # visual list refer to the list after some if any of the elements been hidden

    def __init__(self, _list, _self=None, replace_on_select=None, replace_on_alt_select=None,
                 replace_on_mouse_over=None):
        self.actual_list = actual_list = [c[1] for c in _list]
        self.actual_list_open_index = [False for element in actual_list]
        self.actual_list_level = [element[0] for element in _list]
        if replace_on_select:
            self.on_select = types.MethodType(replace_on_select, self)
        if replace_on_alt_select:
            self.on_alt_select = types.MethodType(replace_on_alt_select, self)
        if replace_on_mouse_over:
            self.on_mouse_over = types.MethodType(replace_on_mouse_over, self)

    def get_actual_index_level(self, index):
        return self.actual_list_level[index]

    def is_actual_index_hidden(self, index):

        level = self.get_actual_index_level(index)
        if level == 0:
            return False

        # scan up in the list till you hit a top level element and check if it is open
        # and if it is, this element should be open
        for i in range(1, len(self.actual_list)):
            u = index - i
            if self.get_actual_index_level(u) == level - 1:
                break

        if level > 1 and self.is_actual_index_hidden(u):
            return True

        return not self.actual_list_open_index[u]

    def __len__(self):
        return len([i for i in range(len(self.actual_list)) if not self.is_actual_index_hidden(i)])

    def __getitem__(self, item):
        r = list()
        for index, element in enumerate(self.actual_list):
            if self.is_actual_index_hidden(index):
                continue
            r.append(element)
        if item >= len(r):
            return None

        actual_index = self.get_visible_index_actual_index()[item]
        if self.actual_list_open_index[actual_index]:
            return r[item].replace(">", "|")
        else:
            return r[item]

    def get_visible_index_actual_index(self):
        r = dict()
        visible_index = -1
        for actual_index in range(len(self.actual_list)):
            if self.is_actual_index_hidden(actual_index):
                continue
            visible_index += 1
            r[visible_index] = actual_index
        return r

    def get_actual_index_visible_index(self):
        return {v: k for k, v in self.get_visible_index_actual_index().items()}

    def get_highlighted_index(self):
        return -1

    def on_select(self, item_index, item_text):
        actual_index = self.get_visible_index_actual_index().get(item_index)
        if actual_index is None:
            return
        self.actual_list_open_index[actual_index] = not self.actual_list_open_index[actual_index]

    def on_alt_select(self, item_index, item_text):
        actual_index = self.get_visible_index_actual_index().get(item_index)
        if actual_index is None:
            return
        self.actual_list_open_index[actual_index] = not self.actual_list_open_index[actual_index]


class GenericListAdapter(ListAdapterHideExpand):
    def __init__(self, level_list):
        from engine.game.game import Game
        self.game = Game.game

        ListAdapterHideExpand.__init__(self, level_list)
        self.last_click = ()

    def on_select(self, item_index, item_text):
        self.last_click = ("click", self.get_visible_index_actual_index()[item_index])

    def on_alt_select(self, item_index, item_text):
        self.last_click = ("alt_click", self.get_visible_index_actual_index()[item_index])


class CustomPresetListAdapter(ListAdapterHideExpand):
    def __init__(self):
        from engine.game.game import Game
        self.game = Game.game
        self.grab_text = self.game.localisation.grab_text
        actual_level_list = [(0, "New Preset",)]
        if self.game.custom_preset_army_setup.selected_faction in self.game.before_save_preset_army_setup:
            actual_level_list += [
                [0, value["Name"]] for index, value in enumerate(list(self.game.before_save_preset_army_setup[
                                                                          self.game.custom_preset_army_setup.selected_faction].values()))]
        ListAdapterHideExpand.__init__(self, actual_level_list)

    # def get_highlighted_index(self):
    #     if not hasattr(self.game, 'map_selected'):
    #         return None
    #     return self.get_actual_index_visible_index().get(
    #         self.map_source_index[self.game.map_selected])

    def on_select(self, item_index, item_text):

        actual_index = self.get_visible_index_actual_index()[item_index]

        if not actual_index:
            self.game.activate_input_popup(("text_input", "new_preset"),
                                           self.grab_text(("ui", "input_new_preset_name")),
                                           self.game.input_popup_uis)
        else:
            self.game.custom_preset_army_setup.current_preset = item_text
            self.game.custom_preset_army_setup.army_preset = self.game.before_save_preset_army_setup[
                self.game.custom_preset_army_setup.selected_faction]["custom_" + item_text]
            self.game.custom_preset_army_setup.change_portrait_selection(None, None)

    def on_alt_select(self, item_index, item_text):
        actual_index = self.get_visible_index_actual_index()[item_index]

        if actual_index:  # initiate remove clicked item
            self.game.activate_input_popup(("confirm_input", ("remove_preset", item_text)),
                                           self.grab_text(("ui", "input_remove_preset")) + item_text,
                                           self.game.confirm_popup_uis)


class CustomPresetTitle(UIMenu):
    def __init__(self, size, pos):
        UIMenu.__init__(self)
        self.font = self.game.medium_generic_ui_font
        self.pos = pos
        self.name = ""
        self.image = pygame.Surface(size)
        self.image.fill((150, 150, 150))
        self.rect = self.image.get_rect(midbottom=self.pos)

    def change_text(self, name, cost, supply, leadership):
        self.name = name
        self.image.fill((150, 150, 150))

        text_surface = self.font.render(str(self.name), True, (30, 30, 30))
        text_rect = text_surface.get_rect(midleft=(0, self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)

        text_surface = self.font.render(self.grab_text(("ui", "info_header_leadership")) +
                                        add_comma_number(int(leadership)) +
                                        "/" + self.grab_text(("ui", "info_header_cost")) + add_comma_number(cost) +
                                        "/" + self.grab_text(("ui", "info_header_supply")) + add_comma_number(supply),
                                        True, (30, 30, 30))
        text_rect = text_surface.get_rect(midright=(self.image.get_width(), self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)


class TickBox(UIMenu):
    def __init__(self, pos, image, tick_image, option):
        """option is in str text for identifying what kind of tick_box it is"""
        self._layer = 14
        UIMenu.__init__(self, play_sound_when_click=True)

        self.option = option

        self.not_tick_image = image
        self.tick_image = tick_image
        self.tick = False

        self.not_tick_image = image
        self.tick_image = tick_image

        self.image = self.not_tick_image

        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)

    def change_tick(self, tick):
        self.tick = tick
        if self.tick:
            self.image = self.tick_image
        else:
            self.image = self.not_tick_image


class TextPopup(UIMenu):
    def __init__(self, font_size=48, layer=30):
        self._layer = layer
        UIMenu.__init__(self, player_cursor_interact=False)
        self.font_size = int(font_size * self.screen_scale_height)
        self.font = Font(self.ui_font["main_button"], self.font_size)
        self.pos = (0, 0)
        self.black_border_size = 6 * self.screen_scale_width
        self.black_border_size_x2 = self.black_border_size * 2
        self.black_border_size_x4 = self.black_border_size * 4
        self.last_shown_id = None
        self.popup_rect = None
        self.text_input = ""
        self.image = Surface((0, 0))

    def popup(self, popup_rect, text_input, width_text_wrapper=None, custom_screen_size=None,
              bg_colour=(220, 220, 220), font_colour=(30, 30, 30)):
        """Pop out text box with input text list in multiple line, one item equal to one paragraph"""
        if self.popup_rect != popup_rect or self.text_input != text_input:
            if self.text_input != text_input:
                self.text_input = text_input
                if type(text_input) == str:
                    self.text_input = [text_input]
                text_surface = []
                if width_text_wrapper:  # has specific popup width size
                    max_height = 0
                    max_width = width_text_wrapper
                    for text in self.text_input:
                        image_height = int((self.font.size(text)[0] + self.font_size) / width_text_wrapper)
                        if not image_height:  # only one line
                            text_image = Surface((width_text_wrapper,
                                                  self.font_size + 3))  # increase size a bit to prevent letter bottom cut
                            text_image.fill(bg_colour)
                            surface = self.font.render(text, True, font_colour)
                            text_image.blit(surface, (self.font_size, 0))
                            text_surface.append(text_image)  # text input font surface
                            max_height += surface.get_height() + 3
                        else:
                            text_image = Surface((width_text_wrapper,
                                                  calculate_long_text_size(text, self.font,
                                                                           self.font_size, width_text_wrapper,
                                                                           start_pos=(
                                                                               self.font_size, self.font_size + 1))[1]))
                            text_image.fill(bg_colour)
                            make_long_text(text_image, text, (self.font_size, self.font_size), self.font,
                                           color=font_colour, specific_width=width_text_wrapper)
                            text_surface.append(text_image)
                            max_height += text_image.get_height() + 3
                else:
                    max_width = 0
                    max_height = 0
                    for text in self.text_input:
                        surface = self.font.render(text, True, font_colour)
                        text_surface.append(surface)  # text input font surface
                        text_rect = surface.get_rect(
                            topleft=(self.font_size, self.font_size))  # text input position at (1,1) on white box image
                        if text_rect.width > max_width:
                            max_width = text_rect.width
                        max_height += self.font_size + int(self.font_size / 5)

                self.image = Surface((max_width + self.black_border_size_x4,
                                      max_height + self.black_border_size_x4))  # white Box
                self.image.fill((0, 0, 0))  # black border
                self.image.fill(bg_colour, (self.black_border_size,
                                            self.black_border_size,
                                            self.image.get_width() - self.black_border_size_x2,
                                            self.image.get_height() - self.black_border_size_x2
                                            ))

                height = self.black_border_size
                for surface in text_surface:
                    text_rect = surface.get_rect(topleft=(self.black_border_size_x2, height))
                    self.image.blit(surface, text_rect)  # blit text
                    height += surface.get_height()

            if hasattr(popup_rect, "bottomright"):  # popup_rect is rect
                self.rect = self.image.get_rect(bottomleft=popup_rect.bottomright)

                screen_size = self.screen_size
                if custom_screen_size:
                    screen_size = custom_screen_size
                exceed_right = False
                if popup_rect.bottomright[0] + self.image.get_width() > screen_size[0]:  # exceed right screen
                    self.rect = self.image.get_rect(topright=popup_rect.bottomleft)
                    exceed_right = True
                elif popup_rect.bottomleft[0] - self.image.get_width() < 0:  # exceed left side screen
                    self.rect = self.image.get_rect(topleft=popup_rect.bottomright)

                if popup_rect.bottomright[1] + self.image.get_height() > screen_size[1]:  # exceed bottom screen
                    self.rect = self.image.get_rect(bottomleft=popup_rect.topright)
                    if exceed_right:
                        self.rect = self.image.get_rect(bottomright=popup_rect.topleft)
                elif popup_rect.bottomright[1] - self.image.get_height() < 0:  # exceed top screen
                    self.rect = self.image.get_rect(topleft=popup_rect.bottomright)
                    if exceed_right:
                        self.rect = self.image.get_rect(topright=popup_rect.bottomleft)
            else:  # popup_rect is pos
                if type(popup_rect) is tuple:
                    if type(popup_rect[0]) is str:
                        exec(f"self.rect = self.image.get_rect({popup_rect[0]}=popup_rect[1])")
                    else:
                        self.rect = self.image.get_rect(topleft=popup_rect)
            self.popup_rect = popup_rect


class BoxUI(UIMenu, Containable, Container):
    def __init__(self, pos, size, parent, layer=-1):
        self._layer = layer
        UIMenu.__init__(self, player_cursor_interact=False)
        self.font = Font(self.ui_font["main_button"], int(100 * self.screen_scale_height))
        self.black_border_size = 6 * self.screen_scale_width
        self.black_border_size_x2 = self.black_border_size * 2
        self.black_border_size_x4 = self.black_border_size * 4
        self.parent = parent
        self.size = size
        self.pos = pos
        self.rect = self.get_adjusted_rect_to_be_inside_container(self.parent)
        self.image = Surface(self.rect[2:])
        self.text_surface = Surface((self.image.get_width() - self.black_border_size_x2, self.image.get_height() * 0.4))
        self.text_surface.fill((200, 180, 150))
        self.text_rect = self.text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 4))
        self.image.fill((0, 0, 0))
        self.image.fill((200, 180, 150), (self.black_border_size,
                                          self.black_border_size,
                                          self.image.get_width() - self.black_border_size_x2,
                                          self.image.get_height() - self.black_border_size_x2
                                          ))

    def change_instruction(self, text):
        self.image.fill((0, 0, 0))
        self.image.fill((200, 180, 150), (self.black_border_size,
                                          self.black_border_size,
                                          self.image.get_width() - self.black_border_size_x2,
                                          self.image.get_height() - self.black_border_size_x2
                                          ))
        self.text_surface.fill((200, 180, 150))
        make_long_text(self.text_surface, text, (0, 0), self.font,
                       with_texture=(None, (Color("black"), (255, 255, 255), 2)), alignment="center")

        self.image.blit(self.text_surface, self.text_rect)

    def get_relative_size_inside_container(self):
        return self.size[0] / self.parent.get_width(), self.size[1] / self.parent.get_height()

    def get_relative_position_inside_container(self):
        return {
            "pivot": (0, 0),
            "origin": self.pos,
        }

    def get_rect(self):
        return self.rect

    def get_size(self):
        return self.image.get_size()


class ListUI(UIMenu, Containable):
    _frame = None
    _scroll_box_frame = None

    def __init__(self, origin, pivot, size, items, parent, item_size, layer=0):
        # rename arguments
        adapter = items

        if not isinstance(adapter, ListAdapter):
            raise TypeError(items)
        if not type(item_size) == int:
            raise TypeError()

        self._layer = layer
        UIMenu.__init__(self)

        # set position and size related attributes
        self.pivot = pivot
        self.origin = origin
        self.size = size
        self.parent = parent
        self.relative_size_inside_container = size

        # set adapter and capacity attributes
        self.adapter = adapter
        self.items = adapter  # keep old name for compatibility
        self.visible_list_capacity = item_size

        self.in_scroll_box = False  # True if mouse over scroll box
        self.hold_scroll_box = None  # during holding the scroll box this is an integer representing the mouse y position when it was grabbed.
        self.hover_index = None  # on what row index is being hover by mouse
        self.scroll_down_index = 0  # number of rows that has been scrolled down
        self.scroll_down_index_at_grab = None  # how many rows were scrolled down on the last grab of the scroll box

        self.rect = self.get_adjusted_rect_to_be_inside_container(self.parent)

        self.last_length_check = len(self.adapter)

        self.image = self.get_refreshed_image()

    def get_frame(self):
        if self._frame is None:
            frame_file = "new_button.png"  # "list_frame.png" # using the button frame to test if it looks good
            self._frame = load_image(self.data_dir, (1, 1), frame_file, ("ui", "mainmenu_ui"))
        return self._frame

    def get_scroll_box_frame(self):
        if self._scroll_box_frame is None:
            self._scroll_box_frame = load_image(self.game.data_dir, (1, 1), "scroll_box_frame.png",
                                                ("ui", "mainmenu_ui"))
        return self._scroll_box_frame

    @staticmethod
    def get_scroll_box_height(scroll_bar_height, items, item_size):
        len_items = len(items)
        if not len_items:
            len_items = 1
        return int(scroll_bar_height * (item_size / len_items))

    @staticmethod
    def get_has_scroll(items, item_size):
        r = len(items) - item_size
        return False if r <= 0 else True

    @staticmethod
    def get_scroll_step_height(scroll_bar_height, scroll_box_height, number_of_items_outside_visible_list):
        divider = number_of_items_outside_visible_list
        if divider is not None:
            return (scroll_bar_height - scroll_box_height) / divider
        return scroll_bar_height - scroll_box_height

    @staticmethod
    def get_scroll_box_size(scroll_bar_height, item_size, len_items):
        if not len_items:
            len_items = 1
        return (14, int(scroll_bar_height * (item_size / len_items)))

    @staticmethod
    def get_scroll_bar_height_by_rect(rect):
        return rect[3] - 12

    @staticmethod
    def get_number_of_items_outside_visible_list(items, item_size):
        r = len(items) - item_size
        if r <= 0:
            return None
        return r

    @staticmethod
    def get_scroll_bar_rect(has_scroll, rect, scroll_bar_height):
        if not has_scroll:
            return None
        return Rect(rect[2] - 18, 6, 14, scroll_bar_height)

    @staticmethod
    def get_scroll_box_rect(has_scroll, rect, scroll_box_index, scroll_step_height, scroll_box_size):
        if not has_scroll:
            return None
        return Rect(rect[2] - 18, scroll_box_index * scroll_step_height + 6, *scroll_box_size)

    @staticmethod
    def get_item_height(scroll_bar_height, item_size):
        return scroll_bar_height // item_size

    def get_relative_size_inside_container(self):
        return self.relative_size_inside_container

    def get_refreshed_image(self):
        self.image = self.inner_get_refreshed_image(
            self.scroll_down_index,
            tuple(self.rect),
            self.adapter.to_tuple(),
            self.hover_index,
            self.adapter.get_highlighted_index(),
            self.in_scroll_box,
            self.hold_scroll_box,
            self.visible_list_capacity,
        )
        return self.image

    @lru_cache(
        maxsize=2 ** 4)  # size has to be big enough to fit all active list ui on screen but not big enough to take too much memory
    def inner_get_refreshed_image(self, scroll_box_index, rect, items, selected_index, highlighted_index, in_scroll_box,
                                  hold_scroll_box, item_size):

        if not type(scroll_box_index) in (int, tuple):
            raise TypeError()
        if not type(items) is tuple:
            raise TypeError(items)
        if not type(selected_index) in (none_type, int):
            raise TypeError(type(selected_index))
        if not type(highlighted_index) in (int, none_type):
            raise TypeError(highlighted_index)
        if not type(in_scroll_box) is bool:
            raise TypeError()
        if not type(hold_scroll_box) in (none_type, int):
            raise TypeError(hold_scroll_box)

        scroll_bar_height = self.get_scroll_bar_height_by_rect(rect)
        scroll_box_size = self.get_scroll_box_size(scroll_bar_height, item_size, len(items))
        scroll_box_height = scroll_box_size[1]
        number_of_items_outside_visible_list = self.get_number_of_items_outside_visible_list(items, item_size)
        scroll_step_height = self.get_scroll_step_height(scroll_bar_height, scroll_box_height,
                                                         number_of_items_outside_visible_list)
        scroll_bar_rect = self.get_scroll_bar_rect(True, rect, scroll_bar_height)
        scroll_box_rect = self.get_scroll_box_rect(True, rect, scroll_box_index, scroll_step_height,
                                                   scroll_box_size)
        item_height = self.get_item_height(scroll_bar_height, item_size)

        rect = pygame.Rect(*rect)
        scroll_bar_rect = pygame.Rect(*scroll_bar_rect) if scroll_bar_rect else None
        scroll_box_rect = pygame.Rect(*scroll_box_rect) if scroll_box_rect else None
        if scroll_box_rect:
            scroll_box = make_image_by_frame(self.get_scroll_box_frame(), scroll_box_rect[2:])

        assert type(scroll_box_index) is int, type(scroll_box_index)
        size = rect[2:]

        image = make_image_by_frame(self.get_frame(), size)
        # draw items
        if len(items) < item_size:  # For listui with item less than provided size
            item_size = len(items)

        for i in range(item_size):
            item_index = i + scroll_box_index
            text_color = (47 if item_index == selected_index else 0,) * 3
            if item_index == selected_index or item_index == highlighted_index:

                background_color = "#cbc2a9"
                if item_index == highlighted_index:
                    background_color = "#776622"
                    text_color = "#eeeeee"
                draw.rect(image, background_color,
                          (6, 6 + i * item_height, size[0] - 13 * True - 12, item_height))

            if item_index < 0:
                continue
            if item_index >= len(items):
                continue
            blit_text = items[item_index]

            # TODO: big optimize is not to render text that is not visible below

            font = self.game.list_font1
            if items[item_index] is not None:  # assuming list ui has only 3 levels
                if ">>" in items[item_index] or "||" in items[item_index]:
                    font = self.game.list_font2
                    blit_text = "  " + blit_text
                elif ">" in items[item_index] or "|" in items[item_index]:
                    font = self.game.list_font3
                    blit_text = " " + blit_text

            image.blit(
                draw_text(blit_text, font, text_color, ellipsis_length=size[0] - 55),
                (20, item_height // 2 + 6 - 9 + i * item_height))

        # draw scroll bar
        if scroll_bar_rect := scroll_bar_rect:
            draw.rect(image, "#d2cab4", scroll_bar_rect)

        # draw scroll box
        if scroll_box_rect := scroll_box_rect:
            image.blit(scroll_box, scroll_box_rect)
            if in_scroll_box or hold_scroll_box is not None:
                draw.rect(image, (130, 30, 30) if hold_scroll_box is not None else (50, 50, 50),
                          scroll_box_rect, 1)

        return image

    def update(self, dt):
        if self.pause:
            return

        mouse_pos = self.cursor.pos
        relative_mouse_pos = [mouse_pos[i] - self.rect[i] for i in range(2)]

        scroll_bar_height = self.get_scroll_bar_height_by_rect(self.rect)
        self.scroll_box_height = self.get_scroll_box_height(scroll_bar_height, self.items, self.visible_list_capacity)

        scroll_bar_height = self.get_scroll_bar_height_by_rect(self.rect)
        scroll_box_size = self.get_scroll_box_size(scroll_bar_height, self.visible_list_capacity, len(self.items))
        number_of_items_outside_visible_list = self.get_number_of_items_outside_visible_list(self.items,
                                                                                             self.visible_list_capacity)

        scroll_step_height = self.get_scroll_step_height(scroll_bar_height, self.scroll_box_height,
                                                         number_of_items_outside_visible_list)

        # detect what cursor is over
        in_list = False
        self.mouse_over = False
        self.in_scroll_box = False
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
            in_list = True
            if scroll_bar_rect := self.get_scroll_bar_rect(True, self.rect, scroll_bar_height):
                if scroll_bar_rect.collidepoint(relative_mouse_pos):
                    if self.get_scroll_box_rect(True, self.rect, self.scroll_down_index, scroll_step_height,
                                                scroll_box_size).collidepoint(relative_mouse_pos):
                        self.in_scroll_box = True
                    in_list = False
            if self.cursor.scroll_up:
                self.scroll_down_index -= 1
                if self.scroll_down_index < 0:
                    self.scroll_down_index = 0
            elif self.cursor.scroll_down:
                noiovl = self.get_number_of_items_outside_visible_list(self.items, self.visible_list_capacity)
                if noiovl:
                    self.scroll_down_index += 1
                    if self.scroll_down_index > noiovl:
                        self.scroll_down_index = noiovl

        # if the number of items changed a recalculation of the scroll bar is needed
        if self.last_length_check != len(self.items):
            self.last_length_check = len(self.items)
            self.scroll_down_index = 0

        # detect what index is being hovered
        self.hover_index = None
        if in_list and not self.hold_scroll_box:
            item_height = self.get_item_height(scroll_bar_height, self.visible_list_capacity)
            relative_index = ((relative_mouse_pos[1] - 6) // item_height)
            if relative_index >= 0 and relative_index < self.visible_list_capacity:
                self.hover_index = relative_index + self.scroll_down_index
                if self.hover_index >= len(self.items):
                    self.hover_index = None

        # handle select and mouse over logic
        if self.hover_index is not None:
            self.cursor.mouse_over_something = True
            self.items.on_mouse_over(self.hover_index, self.items[self.hover_index])
            if self.cursor.is_select_just_up:
                self.items.on_select(self.hover_index, self.items[self.hover_index])
                self.cursor.is_select_just_up = False
            elif self.cursor.is_alt_select_just_up:
                self.items.on_alt_select(self.hover_index, self.items[self.hover_index])
                self.cursor.is_alt_select_just_up = False
        # handle hold and release of the scroll box
        if not self.cursor.is_select_down:
            self.hold_scroll_box = None
        if self.in_scroll_box and self.cursor.is_select_just_down:
            self.hold_scroll_box = relative_mouse_pos[1]
            self.scroll_down_index_at_grab = self.scroll_down_index

        # handle dragging of the scroll box
        if self.hold_scroll_box:
            noiovl = self.get_number_of_items_outside_visible_list(self.items, self.visible_list_capacity)
            if noiovl:
                self.scroll_down_index = self.scroll_down_index_at_grab + int(
                    (relative_mouse_pos[1] - self.hold_scroll_box + scroll_step_height / 2) / scroll_step_height)
                if self.scroll_down_index > noiovl:
                    self.scroll_down_index = noiovl
                elif self.scroll_down_index < 0:
                    self.scroll_down_index = 0

        self.image = self.get_refreshed_image()

    def get_relative_position_inside_container(self):
        return {
            "pivot": self.pivot,
            "origin": self.origin,
        }

    def get_rect(self):
        return self.rect

    def get_size(self):
        return self.image.get_size()
