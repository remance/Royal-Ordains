import copy
import datetime
import types
from functools import lru_cache

import pygame
import pyperclip
from pygame import Surface, SRCALPHA, Rect, Color, draw, mouse
from pygame.font import Font
from pygame.transform import smoothscale
from pygame.sprite import Sprite

from engine.game.generate_custom_equipment import rarity_mod_number
from engine.utils.common import keyboard_mouse_press_check, stat_allocation_check, skill_allocation_check
from engine.utils.data_loading import load_image
from engine.utils.text_making import text_render_with_bg, make_long_text, minimise_number_text


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
    assert frame.get_size()[0] % 2 == 1

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

    def __init__(self, player_cursor_interact=True, has_containers=False):
        """
        Parent class for all menu user interface objects

        :param player_cursor_interact: Player can interact (click) with UI in some way
        :param has_containers: Object has group containers to assign
        """
        from engine.game.game import Game
        self.game = Game.game
        self.screen_scale = Game.screen_scale
        self.data_dir = Game.data_dir
        self.ui_font = Game.ui_font
        self.font_texture = Game.font_texture
        self.screen_rect = Game.screen_rect
        self.screen_size = Game.screen_size
        self.localisation = Game.localisation
        self.grab_text = self.localisation.grab_text
        self.cursor = Game.cursor
        self.updater = Game.ui_updater
        self.player_interact = player_cursor_interact
        if has_containers:
            Sprite.__init__(self, self.containers)
        else:
            Sprite.__init__(self)
        self.event = False
        self.event_press = False
        self.event_hold = False
        self.mouse_over = False
        self.pause = False

    def update(self):
        self.event = False
        self.event_press = False
        self.event_hold = False  # some UI differentiates between press release or holding, if not just use event
        self.mouse_over = False
        if not self.pause and self.rect.collidepoint(self.cursor.pos):
            self.mouse_over = True
            self.cursor.mouse_over_something = True
            if self.player_interact:
                if self.cursor.is_select_just_up or self.cursor.is_select_down:
                    self.event = True
                    if self.cursor.is_select_just_up:
                        self.event_press = True
                        self.cursor.is_select_just_up = False  # reset select button to prevent overlap interaction
                    elif self.cursor.is_select_down:
                        self.event_hold = True
                        self.cursor.is_select_just_down = False  # reset select button to prevent overlap interaction


class MenuCursor(UIMenu):
    def __init__(self, images):
        """Game menu cursor"""
        self._layer = 999999999999  # as high as possible, always blit last
        UIMenu.__init__(self, player_cursor_interact=False, has_containers=True)
        self.images = images
        self.image = images["normal"]
        self.pos = (0, 0)
        self.rect = self.image.get_rect(topleft=self.pos)
        self.is_select_just_down = False
        self.is_select_down = False
        self.is_select_just_up = False
        self.is_alt_select_just_down = False
        self.is_alt_select_down = False
        self.is_alt_select_just_up = False
        self.mouse_over_something = False  # for checking if mouse over already checked on UI starting from top layer
        self.scroll_up = False
        self.scroll_down = False

    def update(self):
        """Update cursor position based on mouse position and mouse button click"""
        self.pos = mouse.get_pos()
        self.rect.topleft = self.pos
        self.mouse_over_something = False
        old_mouse_click = self.is_select_down
        if self.game and 1 in self.game.player_joystick:  # check for joystick button press as well
            for name, button in self.game.player_key_bind_name[1].items():
                if button == "Weak":  # weak attack button = confirm
                    self.is_select_just_down, self.is_select_down, self.is_select_just_up = keyboard_mouse_press_check(
                        mouse, 0, self.is_select_just_down, self.is_select_down, self.is_select_just_up,
                        joystick_check=(self.game.joysticks[self.game.player_joystick[1]], name))
                    break
        else:
            self.is_select_just_down, self.is_select_down, self.is_select_just_up = keyboard_mouse_press_check(
                mouse, 0, self.is_select_just_down, self.is_select_down, self.is_select_just_up)
            if old_mouse_click != self.is_select_down:
                if self.is_select_down:
                    self.image = self.images["click"]
                else:
                    self.image = self.images["normal"]
        # Alternative select press button, like mouse right
        self.is_alt_select_just_down, self.is_alt_select_down, self.is_alt_select_just_up = keyboard_mouse_press_check(
            mouse, 2, self.is_alt_select_just_down, self.is_alt_select_down, self.is_alt_select_just_up)

    def change_image(self, image_name):
        """Change cursor image to whatever input name"""
        self.image = self.images[image_name]
        self.rect = self.image.get_rect(topleft=self.pos)


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
        UIMenu.__init__(self, has_containers=True)
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
        self._layer = 30
        UIMenu.__init__(self, player_cursor_interact=False)

        self.pos = pos
        self.image = image

        self.base_image = self.image.copy()

        self.font = Font(self.ui_font["main_button"], int(48 * self.screen_scale[1]))

        self.rect = self.image.get_rect(center=self.pos)

    def change_instruction(self, text):
        self.image = self.base_image.copy()
        self.text = text
        text_surface = self.font.render(text, True, (30, 30, 30))
        text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 4))
        self.image.blit(text_surface, text_rect)


class InputBox(UIMenu):
    def __init__(self, pos, width, text="", click_input=False):
        UIMenu.__init__(self, player_cursor_interact=False)
        self._layer = 31
        self.font = Font(self.ui_font["main_button"], int(30 * self.screen_scale[1]))
        self.pos = pos
        self.image = Surface((width - 10, int(34 * self.screen_scale[1])))
        self.max_text = int((self.image.get_width() / int(30 * self.screen_scale[1])) * 2)
        self.image.fill((220, 220, 220))

        self.base_image = self.image.copy()

        self.text = text
        text_surface = self.font.render(text, True, (30, 30, 30))
        text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)
        self.current_pos = 0

        self.hold_key = 0
        self.hold_key_unicode = ""

        self.active = True
        self.click_input = False
        if click_input:  # active only when click
            self.active = False
            self.click_input = click_input

        self.rect = self.image.get_rect(center=self.pos)

    def text_start(self, text):
        """Add starting text to input box"""
        self.image = self.base_image.copy()
        self.text = text
        self.current_pos = len(self.text)  # start input at the end
        show_text = self.text[:self.current_pos] + "|" + self.text[self.current_pos:]
        text_surface = self.font.render(show_text, True, (30, 30, 30))
        text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)

    def player_input(self, input_event, key_press):
        """register user keyboard and mouse input"""
        if self.active:  # text input
            self.image = self.base_image.copy()
            event = input_event
            event_key = None
            event_unicode = ""
            if event:
                event_key = input_event.key
                event_unicode = event.unicode
                self.hold_key = event_key  # save last holding press key
                self.hold_key_unicode = event_unicode

            if event_key == pygame.K_BACKSPACE or self.hold_key == pygame.K_BACKSPACE:
                if self.current_pos > 0:
                    if self.current_pos > len(self.text):
                        self.text = self.text[:-1]
                    else:
                        self.text = self.text[:self.current_pos - 1] + self.text[self.current_pos:]
                    self.current_pos -= 1
                    if self.current_pos < 0:
                        self.current_pos = 0
            elif event_key == pygame.K_RETURN or event_key == pygame.K_KP_ENTER:  # use external code instead for enter press
                pass
            elif event_key == pygame.K_RIGHT or self.hold_key == pygame.K_RIGHT:
                self.current_pos += 1
                if self.current_pos > len(self.text):
                    self.current_pos = len(self.text)
            elif event_key == pygame.K_LEFT or self.hold_key == pygame.K_LEFT:
                self.current_pos -= 1
                if self.current_pos < 0:
                    self.current_pos = 0
            elif key_press[pygame.K_LCTRL] or key_press[pygame.K_RCTRL]:
                # use keypress for ctrl as is has no effect on its own
                if event_key == pygame.K_c:
                    pyperclip.copy(self.text)
                elif event_key == pygame.K_v:
                    paste_text = pyperclip.paste()
                    self.text = self.text[:self.current_pos] + paste_text + self.text[self.current_pos:]
                    self.current_pos = self.current_pos + len(paste_text)
            elif event_unicode != "" or self.hold_key_unicode != "":
                if event_unicode != "":  # input event_unicode first before holding one
                    input_unicode = event_unicode
                elif self.hold_key_unicode != "":
                    input_unicode = self.hold_key_unicode
                self.text = self.text[:self.current_pos] + input_unicode + self.text[self.current_pos:]
                self.current_pos += 1
            # Re-render the text
            show_text = self.text[:self.current_pos] + "|" + self.text[self.current_pos:]
            if self.current_pos > self.max_text:
                if self.current_pos + self.max_text > len(show_text):
                    show_text = show_text[len(show_text) - self.max_text:]
                else:
                    show_text = show_text[self.current_pos:]
            text_surface = self.font.render(show_text, True, (30, 30, 30))
            text_rect = text_surface.get_rect(midleft=(0, self.image.get_height() / 2))
            self.image.blit(text_surface, text_rect)


class TextBox(UIMenu):
    def __init__(self, image, pos, text):
        self._layer = 13
        UIMenu.__init__(self)

        self.font = Font(self.ui_font["main_button"], int(36 * self.screen_scale[1]))
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
    def __init__(self, images, pos, key_name="", font_size=28, layer=1):
        self._layer = layer
        UIMenu.__init__(self)
        self.pos = pos
        self.button_normal_image = images[0].copy()
        self.button_over_image = images[1].copy()
        self.button_click_image = images[2].copy()

        self.font = Font(self.ui_font["main_button"], int(font_size * self.screen_scale[1]))
        self.base_image0 = self.button_normal_image.copy()
        self.base_image1 = self.button_over_image.copy()
        self.base_image2 = self.button_click_image.copy()

        self.text = ""
        if key_name != "":  # draw text into the button images
            self.text = self.grab_text(("ui", key_name))
            text_surface = self.font.render(self.text, True, (30, 30, 30))
            text_rect = text_surface.get_rect(center=self.button_normal_image.get_rect().center)
            self.button_normal_image.blit(text_surface, text_rect)
            self.button_over_image.blit(text_surface, text_rect)
            self.button_click_image.blit(text_surface, text_rect)

        self.image = self.button_normal_image
        self.rect = self.button_normal_image.get_rect(center=self.pos)

    def update(self):
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

    def change_state(self, key_name):
        if key_name != "":
            self.text = self.grab_text(("ui", key_name))
            self.button_normal_image = self.base_image0.copy()
            self.button_over_image = self.base_image1.copy()
            self.button_click_image = self.base_image2.copy()
            text_surface = self.font.render(self.text, True, (30, 30, 30))
            text_rect = text_surface.get_rect(center=self.button_normal_image.get_rect().center)
            self.button_normal_image.blit(text_surface, text_rect)
            self.button_over_image.blit(text_surface, text_rect)
            self.button_click_image.blit(text_surface, text_rect)
        self.rect = self.button_normal_image.get_rect(center=self.pos)
        self.event = False


class URLIconLink(UIMenu):
    def __init__(self, image, pos, url, layer=1):
        self._layer = layer
        UIMenu.__init__(self)
        self.pos = pos
        self.image = image
        self.url = url
        self.rect = self.image.get_rect(topright=self.pos)


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

    @classmethod
    @lru_cache
    def make_buttons(cls, size, text, font):
        from engine.game.game import Game
        game = Game.game

        frame = load_image(game.data_dir, (1, 1), "new_button.png", ("ui", "mainmenu_ui"))

        normal_button = make_image_by_frame(frame, size)
        text_surface = font.render(text, True, (0,) * 3)
        text_rect = text_surface.get_rect(center=normal_button.get_rect().center)
        normal_button.blit(text_surface, text_rect)

        hover_button = normal_button.copy()
        draw.rect(hover_button, "#DD0000", hover_button.get_rect(), 1)

        return (normal_button, hover_button)

    def get_relative_size_inside_container(self):
        return (.5, .1)

    def __init__(self, pos, key_name="", width=200, parent=None):
        UIMenu.__init__(self)
        self.pos = pos
        self.parent = parent
        self.key_name = key_name
        self.rect = self.get_adjusted_rect_to_be_inside_container(self.parent)
        self.mouse_over = False
        self.event = False
        self.font = Font(self.ui_font["main_button"], 17)
        self.text = self.grab_text(("ui", self.key_name))
        self.refresh()

    def refresh(self):
        images = self.make_buttons(size=tuple(self.rect[2:]), text=self.text, font=self.font)

        self.image = images[0]
        if self.mouse_over:
            self.image = images[1]

    def get_relative_position_inside_container(self):
        return {
            "origin": (0, 0),
            "pivot": self.pos,
        }

    def update(self):

        mouse_pos = self.cursor.pos
        sju = self.cursor.is_select_just_up
        self.event = False

        self.mouse_over = False
        if not self.pause and self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
            if sju:
                self.event = True
                self.cursor.is_select_just_up = False  # reset select button to prevent overlap interaction

        self.rect = self.get_adjusted_rect_to_be_inside_container(self.parent)
        self.refresh()

    def get_size(self):
        return self.image.get_size()

    def change_state(self, text):
        pass


class OptionMenuText(UIMenu):
    def __init__(self, pos, text, text_size, button_image=None):
        UIMenu.__init__(self, player_cursor_interact=False)
        self.pos = pos
        self.font = Font(self.ui_font["main_button"], text_size)
        if button_image:  # add image to front of text
            text_surface = text_render_with_bg(text, self.font, Color("black"))
            self.image = Surface((button_image.get_width() + (5 * self.screen_scale[0]) +
                                  text_surface.get_width(), button_image.get_height()), SRCALPHA)
            text_rect = text_surface.get_rect(topright=(self.image.get_width(), 0))
            self.image.blit(text_surface, text_rect)
            button_rect = button_image.get_rect(topleft=(0, 0))
            self.image.blit(button_image, button_rect)
        else:
            self.image = text_render_with_bg(text, self.font, Color("black"))
        self.rect = self.image.get_rect(center=(self.pos[0] - (self.image.get_width() / 2), self.pos[1]))


class CharacterProfileBox(UIMenu):
    image = None

    def __init__(self, pos):
        UIMenu.__init__(self, player_cursor_interact=False)
        self.font = Font(self.ui_font["main_button"], int(26 * self.screen_scale[1]))
        self.small_font = Font(self.ui_font["main_button"], int(22 * self.screen_scale[1]))
        self.selected_box = Surface(self.image.get_size(), SRCALPHA)
        self.selected_box.fill((200, 200, 200))
        self.taken_box = Surface(self.image.get_size(), SRCALPHA)
        self.taken_box.fill((100, 100, 100))
        self.pos = pos
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(topleft=self.pos)

    def change_profile(self, slot_number, data, selected):
        if selected is True:
            self.image = self.selected_box.copy()
            self.image.blit(self.base_image, self.base_image.get_rect(topleft=(0, 0)))
        elif selected == 1:
            self.image = self.taken_box.copy()
            self.image.blit(self.base_image, self.base_image.get_rect(topleft=(0, 0)))
        else:
            self.image = self.base_image.copy()

        # add slot number
        text = self.font.render("(" + slot_number + ")", True, (30, 30, 30))
        text_rect = text.get_rect(bottomright=(self.image.get_width(), self.image.get_height()))
        self.image.blit(text, text_rect)

        if data:
            char_id = data["character"]["ID"] + str(data["character"]["Sprite Ver"])
            # add portrait
            portrait = self.game.character_data.character_portraits[char_id]
            portrait_rect = portrait.get_rect(topleft=(0, 0))
            self.image.blit(portrait, portrait_rect)

            # add name
            text = self.font.render(self.grab_text(("character", char_id, "Name")), True,
                                    (30, 30, 30))
            text_rect = text.get_rect(topleft=(120 * self.screen_scale[0], 5 * self.screen_scale[1]))
            self.image.blit(text, text_rect)

            # add play stat
            text = self.small_font.render(self.grab_text(("ui", "Chapter")) +
                                          ": " + data["chapter"] + "." + data["mission"], True,
                                          (30, 30, 30))
            text_rect = text.get_rect(topleft=(120 * self.screen_scale[0], 40 * self.screen_scale[1]))
            self.image.blit(text, text_rect)

            playtime = datetime.timedelta(seconds=data["playtime"])
            playtime = str(playtime).split(".")[0]
            text = self.small_font.render(self.grab_text(("ui", "Time")) +
                                          ": " + playtime, True, (30, 30, 30))
            text_rect = text.get_rect(topleft=(120 * self.screen_scale[0], 70 * self.screen_scale[1]))
            self.image.blit(text, text_rect)

            text = self.small_font.render(self.grab_text(("ui", "Save")) +
                                          ": " + data["last save"], True, (30, 30, 30))
            text_rect = text.get_rect(topleft=(15 * self.screen_scale[0], 100 * self.screen_scale[1]))
            self.image.blit(text, text_rect)

            # add char stat
            text = self.small_font.render(self.grab_text(("ui", "Stat")) +
                                          ": " + str(int(data["character"]["Strength"])) + "/" +
                                          str(int(data["character"]["Dexterity"])) + "/" +
                                          str(int(data["character"]["Agility"])) + "/" +
                                          str(int(data["character"]["Constitution"])) + "/" +
                                          str(int(data["character"]["Intelligence"])) + "/" +
                                          str(int(data["character"]["Wisdom"])) + "/" +
                                          str(int(data["character"]["Charisma"])), True, (30, 30, 30))
            text_rect = text.get_rect(topleft=(15 * self.screen_scale[0], 125 * self.screen_scale[1]))
            self.image.blit(text, text_rect)

            text = self.small_font.render(self.grab_text(("ui", "Total Kills(Boss)")) + ": " +
                                          minimise_number_text(str(int(data["total kills"]))) + "(" +
                                          minimise_number_text(str(int(data["boss kills"]))) + ")", True, (30, 30, 30))
            text_rect = text.get_rect(topleft=(15 * self.screen_scale[0], 150 * self.screen_scale[1]))
            self.image.blit(text, text_rect)

            text = self.small_font.render(self.grab_text(("ui", "Golds/Scores")) +
                                          ": " + minimise_number_text(str(int(data["total golds"]))) + "/" +
                                          minimise_number_text(str(int(data["total scores"]))), True, (30, 30, 30))
            text_rect = text.get_rect(topleft=(15 * self.screen_scale[0], 175 * self.screen_scale[1]))
            self.image.blit(text, text_rect)

            # for key, value in data.items():
            #     text = self.small_font.render(key, True, (30, 30, 30))
            #     text_rect = text.get_rect(center=(120 * self.screen_scale[0], row))
            #     self.image.blit(text, text_rect)
            #     row += 20 * self.screen_scale[1]
        else:  # empty profile data
            text = self.font.render(self.grab_text(("ui", "Empty")), True, (30, 30, 30))
            text_rect = text.get_rect(center=(200 * self.screen_scale[0], 80 * self.screen_scale[1]))
            self.image.blit(text, text_rect)


class CharacterSelector(UIMenu):
    def __init__(self, pos, images):
        UIMenu.__init__(self, player_cursor_interact=False)
        self.pos = pos
        self.images = images
        self.image = self.images["Empty"]
        self.mode = "empty"
        self.rect = self.image.get_rect(center=self.pos)
        self.current_row = 0
        self.delay = 0

    def change_mode(self, mode, delay=True):
        if not self.delay:
            if mode not in ("stat", "Profile_confirm"):
                self.image = self.images[mode.capitalize()]
            else:
                self.image = self.images["Profile"]
            self.mode = mode
            if delay:
                self.delay = 0.1

    def update(self):
        if self.delay:
            self.delay -= self.game.dt
            if self.delay < 0:
                self.delay = 0


class CharacterInterface(UIMenu):
    item_sprite_pool = None
    storage_first_row = tuple([5 * item for item in range(12)])
    storage_last_row = tuple([item + 4 for item in storage_first_row])
    item_sort_list = ("Name Ascending", "Name Descending", "Type Ascending", "Type Descending",
                      "Value Ascending", "Value Descending", "Quantity Ascending", "Quantity Descending",
                      "Rarity Ascending", "Rarity Descending")
    enchant_sort_list = ("Name Ascending", "Name Descending", "Equipped Ascending", "Type Ascending", "Type Descending",
                         "Rarity Ascending", "Rarity Descending")
    follower_sort_list = ("Name Ascending", "Name Descending", "Type Ascending", "Type Descending", "Cost Ascending",
                          "Cost Descending", "Single Ascending", "Single Descending")
    follower_clear_list = ("Clear Follower", "Cancel Clear")
    purchase_confirm_list = ("Confirm Purchase", "Cancel Purchase")
    purchase_clear_confirm_list = ("Confirm Clear", "Cancel Clear")
    enchant_confirm_list = ("Confirm Re-enchant", "Cancel Re-enchant")
    storage_sell_list = ("Sell All", "Sell Half", "Sell One", "Cancel")
    stat_row = ("Strength", "Dexterity", "Agility", "Constitution", "Intelligence", "Wisdom", "Charisma")
    common_skill_row = ("Ground Movement", "Air Movement", "Tinkerer", "Arm Mastery", "Wealth",
                        "Immunity", "Resourceful", "Combat Contest")

    stat_base_image = None
    equipment_list_base_image = None
    equipment_base_image = None
    follower_preset_base_image = None
    follower_base_image = None
    storage_base_image = None
    shop_base_image = None
    reward_base_image = None
    enchant_base_image = None
    equipment_slot_rect = None
    equipment_list_slot_rect = None
    storage_box_rects = None
    stat_rect = None
    status_point_left_text_rect = None
    skill_point_left_text_rect = None
    follower_preset_box_rects = None
    small_box_images = None

    def __init__(self, pos, player, text_popup):
        UIMenu.__init__(self)
        self.header_font = Font(self.ui_font["main_button"], int(36 * self.screen_scale[1]))
        self.font = Font(self.ui_font["main_button"], int(22 * self.screen_scale[1]))
        self.small_font = Font(self.ui_font["main_button"], int(18 * self.screen_scale[1]))
        self.current_row = 0
        self.current_page = 0
        self.max_page = 0
        self.input_delay = 0
        self.pos = pos
        self.player = player
        self.mode = "stat"
        self.text_popup = text_popup
        self.sub_menu_current_row = 0
        self.sub_menu_button_list = ()
        self.current_equipment_list = []
        self.show_equip_list = []
        self.selected_equipment_slot = None
        self.total_equip_stat = {}
        self.total_select_equip_stat = {}
        self.purchase_list = {}
        self.shop_list = []
        self.reward_list = {}
        self.shown_reward_list = []
        self.all_custom_item = []

        self.skill_rect = {}

        self.skill_row = []
        self.all_skill_row = []
        self.stat = {}
        self.profile = {}
        self.current_follower_preset_num = 1
        self.current_follower_preset = {}
        self.current_follower_preset_cost = 0
        self.max_follower_allowance = 0
        self.old_equipment = None
        self.old_storage_list = None
        self.gear_mod_list = self.game.character_data.gear_mod_list

        self.base_image = None

        self.image = self.stat_base_image

        self.page_text = NameTextBox((self.image.get_width() / 1.5, 42 * self.screen_scale[1]),
                                     (self.image.get_width() / 2, self.image.get_height() - 75 * self.screen_scale[1]),
                                     "1/1", text_size=36 * self.screen_scale[1], center_text=True)

        self.player_input = self.player_input_stat
        self.rect = self.image.get_rect(topleft=self.pos)

    def update(self):
        if self.input_delay > 0:
            if self.game.battle.city_mode:
                self.input_delay -= self.game.battle.true_dt
            else:
                self.input_delay -= self.game.dt
            if self.input_delay < 0:
                self.input_delay = 0

    def add_profile(self, profile):
        self.profile = profile
        start_stat = {key: value for key, value in profile["character"].items() if key in
                      ("Strength", "Dexterity", "Agility", "Constitution", "Intelligence",
                       "Wisdom", "Charisma")} | profile["character"]["skill allocation"] | \
                     {key: value for key, value in profile["character"].items() if key in
                      ("Status Remain", "Skill Remain", "ID")}
        self.add_stat(start_stat)

    def add_stat(self, stat_dict):
        self.stat = stat_dict
        self.image = self.stat_base_image.copy()
        if self.stat:
            self.all_skill_row = [item for item in self.common_skill_row]
            for key, value in self.game.character_data.character_list[stat_dict["ID"]]["Skill UI"].items():
                if ".1" in key and "C" in key:  # starting skill
                    self.all_skill_row.append(value["Name"])
            self.last_row = len(self.stat_row) + len(self.all_skill_row) - 1

            self.skill_rect = {}
            start_stat_row = 350 * self.screen_scale[1]
            for stat in self.all_skill_row:
                text = self.font.render(stat + ": ", True, (30, 30, 30))
                text_rect = text.get_rect(midleft=(10 * self.screen_scale[0], start_stat_row))
                self.skill_rect[stat] = text_rect  # save stat name rect for stat point later
                self.image.blit(text, text_rect)
                start_stat_row += 36 * self.screen_scale[1]

            row = 0
            for stat in stat_dict:
                if stat in self.stat_rect:
                    if row == self.current_row:
                        text = self.font.render(
                            str(int(stat_dict[stat])) + " (" + str(int(stat_dict[stat] / 10) + 1) + ")",
                            True, (30, 30, 30), (220, 220, 220, 255))
                    else:
                        text = self.font.render(
                            str(int(stat_dict[stat])) + " (" + str(int(stat_dict[stat] / 10) + 1) + ")",
                            True, (30, 30, 30))
                    text_rect = text.get_rect(midright=(380 * self.screen_scale[0], self.stat_rect[stat].midleft[1]))
                    self.image.blit(text, text_rect)
                    row += 1
                elif stat in self.skill_rect:
                    if row == self.current_row:
                        text = self.font.render(str(int(stat_dict[stat])),
                                                True, (30, 30, 30), (220, 220, 220, 255))
                    else:
                        text = self.font.render(str(int(stat_dict[stat])),
                                                True, (30, 30, 30))
                    text_rect = text.get_rect(midright=(380 * self.screen_scale[0], self.skill_rect[stat].midleft[1]))
                    self.image.blit(text, text_rect)
                    row += 1
                elif "Remain" in stat:  # point left
                    if "Status" in stat:
                        text = self.font.render(str(int(stat_dict[stat])), True, (30, 30, 30))
                        text_rect = text.get_rect(
                            midleft=(180 * self.screen_scale[0], self.status_point_left_text_rect.midleft[1]))
                    else:
                        text = self.font.render(str(int(stat_dict[stat])), True, (30, 30, 30))
                        text_rect = text.get_rect(
                            midleft=(180 * self.screen_scale[0], self.skill_point_left_text_rect.midleft[1]))
                    self.image.blit(text, text_rect)
                    row += 1

            if self.profile:
                self.max_follower_allowance = (int(self.profile["chapter"]) * 20) + stat_dict["Charisma"]
                for key, value in self.stat.items():
                    if key in self.all_skill_row:
                        self.profile["character"]["skill allocation"][key] = value
                    else:
                        self.profile["character"][key] = value

    def check_total_equipment_stat(self, equip_dict):
        total_equip_stat = {}
        for slot, item in equip_dict.items():
            if "item" not in slot and item:
                if type(item) not in (tuple, dict):  # unique equip
                    stat = self.game.character_data.gear_list[item]
                else:  # custom equipment
                    stat = dict(item)
                for mod, value in dict(stat["Modifier"]).items():
                    if mod not in total_equip_stat:
                        total_equip_stat[mod] = value
                    else:
                        if isinstance(value, (int, float)):  # add value
                            total_equip_stat[mod] += value
        return total_equip_stat

    def change_equipment(self):
        if not self.base_image or self.profile["equipment"] != self.old_equipment:
            self.image = self.equipment_base_image.copy()
            self.total_equip_stat = self.check_total_equipment_stat(self.profile["equipment"])
            self.old_equipment = copy.deepcopy(self.profile["equipment"])
            for equip_type, rect in self.equipment_slot_rect.items():
                if "item" in equip_type:  # consumable item type
                    item = self.profile["equipment"]["item"][equip_type.split(" ")[1]]
                    if item:
                        item_image = smoothscale(self.item_sprite_pool[self.game.battle.chapter][
                                                     "Normal"][item][1][0], (60 * self.screen_scale[0],
                                                                             60 * self.screen_scale[1]))
                        image_rect = item_image.get_rect(center=rect.center)
                        self.image.blit(item_image, image_rect)
                        text_surface = text_render_with_bg(minimise_number_text(str(self.profile["storage"][item])),
                                                           self.font, Color("black"))
                        text_rect = text_surface.get_rect(bottomright=rect.bottomright)
                        self.image.blit(text_surface, text_rect)  # add item number
                else:
                    item = self.profile["equipment"][equip_type]
                    if item:
                        item_id = item
                        if item not in self.game.character_data.gear_list:
                            stat = dict(item)  # custom equipment
                            item_id = "Custom " + stat["Rarity"] + "_" + stat["Type"]
                        item_image = smoothscale(self.item_sprite_pool[self.game.battle.chapter][
                                                     "Normal"][item_id][1][0], (60 * self.screen_scale[0],
                                                                                60 * self.screen_scale[1]))
                        image_rect = item_image.get_rect(center=rect.center)
                        self.image.blit(item_image, image_rect)

            self.base_image = self.image.copy()
        else:
            self.image = self.base_image.copy()

        equip_type = tuple(self.equipment_slot_rect.keys())[self.current_row]
        if "item" in equip_type:
            item = self.profile["equipment"]["item"][equip_type.split(" ")[1]]
        else:
            item = self.profile["equipment"][equip_type]
        if item and item != "Unequip":
            if item in self.game.character_data.equip_item_list:  # item type
                stat = self.game.character_data.equip_item_list[item]
                name = self.grab_text(("item", item, "Name"))

                text_surface = self.font.render(
                    self.grab_text(("ui", "Base Capacity")) + ": " + str(stat["Capacity"]),
                    True, (30, 30, 30))
                text_rect = text_surface.get_rect(
                    topleft=(10 * self.screen_scale[0], 660 * self.screen_scale[1]))
                self.image.blit(text_surface, text_rect)

                make_long_text(self.image, self.grab_text(("item", item, "Description")),
                               (10 * self.screen_scale[0], 680 * self.screen_scale[1]),
                               self.font)
            else:  # gear type
                if item in self.game.character_data.gear_list:
                    stat = self.get_equipment_description(dict(item))[1:]
                    name = self.grab_text(("gear", item, "Name"))
                else:
                    stat = self.get_custom_equipment_description(dict(item))[1:]
                    name = self.get_custom_equipment_name(dict(item))

                index2 = 0
                for value in stat:
                    text_surface = self.small_font.render(value, True, (30, 30, 30))
                    text_rect = text_surface.get_rect(topleft=(10 * self.screen_scale[0],
                                                               (700 + (25 * index2)) * self.screen_scale[1]))
                    self.image.blit(text_surface, text_rect)
                    index2 += 1

            make_long_text(self.image, name,  # add item name
                           (10 * self.screen_scale[0], 630 * self.screen_scale[1]), self.header_font)
        else:
            text_surface = self.header_font.render(self.grab_text(("ui", "Empty")), True, (30, 30, 30))
            text_rect = text_surface.get_rect(topleft=(10 * self.screen_scale[0], 650 * self.screen_scale[1]))
            self.image.blit(text_surface, text_rect)

        pygame.draw.rect(self.image, (200, 200, 0),
                         (self.equipment_slot_rect[tuple(self.equipment_slot_rect.keys())[self.current_row]].topleft[0],
                          self.equipment_slot_rect[tuple(self.equipment_slot_rect.keys())[self.current_row]].topleft[1],
                          self.equipment_slot_rect[tuple(self.equipment_slot_rect.keys())[self.current_row]].width,
                          self.equipment_slot_rect[tuple(self.equipment_slot_rect.keys())[self.current_row]].height),
                         width=int(5 * self.screen_scale[0]))

    def change_equipment_list(self):
        self.image = self.equipment_list_base_image.copy()
        text_pos = (5 * self.screen_scale[0], 300 * self.screen_scale[0])
        if "item" in self.selected_equipment_slot:
            profile_equipment = self.profile["equipment"]["item"][self.selected_equipment_slot.split(" ")[1]]
        else:
            profile_equipment = self.profile["equipment"][self.selected_equipment_slot]
        self.show_equip_list = ["Unequip"] + [item for item in self.current_equipment_list if
                                              item not in list(self.profile["equipment"].values()) + list(
                                                  self.profile["equipment"]["item"].values())]
        if self.current_row > len(
                self.show_equip_list) - 1:  # in case equip item and show_equip_list remove it from list
            self.current_row -= 1

        compare_equip = copy.deepcopy(self.profile["equipment"])
        item = self.show_equip_list[self.current_row]
        if item != "Unequip":
            if item in self.game.character_data.equip_item_list:  # item type
                pass
            else:  # gear type
                if item in self.game.character_data.gear_list:
                    stat = self.game.character_data.gear_list[item]
                else:
                    stat = dict(item)  # custom equipment
                compare_equip[self.selected_equipment_slot] = stat
        else:
            compare_equip[self.selected_equipment_slot] = None

        self.total_select_equip_stat = self.check_total_equipment_stat(compare_equip)

        for index, item in enumerate((profile_equipment, self.show_equip_list[self.current_row])):
            # show stat of equipped and currently select item
            if item and item != "Unequip":
                item_id = item
                if item in self.game.character_data.equip_item_list:  # item type
                    stat = self.game.character_data.equip_item_list[item]
                    name = self.grab_text(("item", item, "Name"))

                    text_surface = self.small_font.render(
                        self.grab_text(("ui", "Base Capacity")) + ": " + str(stat["Capacity"]),
                        True, (30, 30, 30))
                    text_rect = text_surface.get_rect(
                        topleft=(text_pos[index] * self.screen_scale[0], 230 * self.screen_scale[1]))
                    self.image.blit(text_surface, text_rect)

                    make_long_text(self.image, self.grab_text(("item", item, "Description")),
                                   (text_pos[index] * self.screen_scale[0], 250 * self.screen_scale[1]),
                                   self.small_font,
                                   specific_width=((self.image.get_width() / 2) +
                                                   (text_pos[index] - 20) * self.screen_scale[0]))

                else:  # gear type
                    if item in self.game.character_data.gear_list:
                        stat = self.get_equipment_description(dict(item))[1:]
                        name = self.grab_text(("gear", item, "Name"))
                    else:
                        stat = self.get_custom_equipment_description(dict(item))[1:]  # custom equipment
                        item_id = "Custom " + dict(item)["Rarity"] + "_" + dict(item)["Type"]
                        name = self.get_custom_equipment_name(dict(item))

                    index2 = 0
                    for value in stat:
                        text_surface = self.small_font.render(value, True, (30, 30, 30))
                        text_rect = text_surface.get_rect(topleft=(text_pos[index] * self.screen_scale[0],
                                                                   (200 + (25 * index2)) * self.screen_scale[1]))
                        self.image.blit(text_surface, text_rect)
                        index2 += 1

                item_image = smoothscale(self.item_sprite_pool[self.game.battle.chapter][
                                             "Normal"][item_id][1][0], (60 * self.screen_scale[0],
                                                                        60 * self.screen_scale[1]))
                item_rect = item_image.get_rect(center=self.equipment_list_slot_rect[("equip", "new")[index]].center)
                self.image.blit(item_image, item_rect)

                if item in self.game.character_data.equip_item_list:  # item type, add number in storage
                    number = self.profile["storage"][item]
                    text_surface = text_render_with_bg(minimise_number_text(str(number)), self.small_font,
                                                       Color("black"))
                    text_rect = text_surface.get_rect(bottomright=item_rect.bottomright)
                    self.image.blit(text_surface, text_rect)

                if item in self.profile["storage_new"]:  # viewed, remove not view state in profile
                    self.profile["storage_new"].remove(item)

                make_long_text(self.image, name,  # add item name
                               (text_pos[index] * self.screen_scale[0], 130 * self.screen_scale[1]), self.font,
                               specific_width=((self.image.get_width() / 2) +
                                               (text_pos[index] - 20) * self.screen_scale[0]))

            else:  # empty equipment
                text_surface = self.header_font.render(self.grab_text(("ui", "Empty")), True, (30, 30, 30))
                if not index:
                    text_rect = text_surface.get_rect(midtop=(self.equipment_list_slot_rect["equip"].center[0],
                                                              250 * self.screen_scale[1]))
                else:
                    text_rect = text_surface.get_rect(midtop=(self.equipment_list_slot_rect["new"].center[0],
                                                              250 * self.screen_scale[1]))
                self.image.blit(text_surface, text_rect)

        row_index = 0
        for index, item in enumerate(self.show_equip_list):  # add list of possible item to equip
            if (index >= self.current_row or len(self.show_equip_list) < 11) and row_index < 11:
                button_image = Surface((self.image.get_width(), (50 * self.screen_scale[1])))
                button_image.fill((220, 220, 220))
                if self.current_row == index:
                    pygame.draw.rect(button_image, (150, 150, 20),
                                     (0, 0, self.image.get_width(), (50 * self.screen_scale[1])),
                                     width=int(5 * self.screen_scale[0]))
                else:
                    pygame.draw.rect(button_image, (30, 30, 30),
                                     (0, 0, self.image.get_width(), (50 * self.screen_scale[1])),
                                     width=int(5 * self.screen_scale[0]))
                if item == "Unequip":
                    text_surface = self.small_font.render(self.grab_text(("ui", item)),
                                                          True, (30, 30, 30))
                elif item in self.game.character_data.equip_item_list:
                    text_surface = self.small_font.render(self.grab_text(("item", item, "Name")),
                                                          True, (30, 30, 30))
                elif item in self.game.character_data.gear_list:
                    text_surface = self.small_font.render(self.grab_text(("gear", item, "Name")),
                                                          True, (30, 30, 30))
                else:
                    stat = dict(item)
                    text_surface = self.small_font.render(
                        self.get_custom_equipment_name(stat),
                        True, (30, 30, 30))

                text_rect = text_surface.get_rect(
                    midleft=(5 * self.screen_scale[0], int(button_image.get_height() / 2)))
                button_image.blit(text_surface, text_rect)
                button_rect = button_image.get_rect(topleft=(0, (400 * self.screen_scale[1]) +
                                                             ((40 * self.screen_scale[1]) * row_index)))
                self.image.blit(button_image, button_rect)

                if item in self.profile["storage_new"]:  # not yet viewed
                    text_surface = text_render_with_bg("!", self.font,
                                                       Color("black"))
                    text_rect = text_surface.get_rect(topleft=button_rect.topright)
                    self.image.blit(text_surface, text_rect)

                row_index += 1

    def change_storage_list(self):
        page_current_row = self.current_row - (60 * int(self.current_row / 60))

        if tuple(self.profile["storage"].keys())[page_current_row] in self.profile["storage_new"]:
            # viewed, remove not view state in profile
            self.old_storage_list = None   # reset storage
            self.profile["storage_new"].remove(tuple(self.profile["storage"].keys())[page_current_row])

        if not self.base_image or self.profile["storage"] != self.old_storage_list or \
                tuple(self.profile["storage"].keys()) != tuple(self.old_storage_list.keys()):
            # also check if order change
            self.image = self.storage_base_image.copy()
            self.old_storage_list = copy.deepcopy(self.profile["storage"])
            self.old_equipment = {}  # reset equipment as well

            slot_index = 0
            page_slot_index = 0
            if self.current_page:
                slot_index += 60 * self.current_page
            all_equip_item = list(self.profile["equipment"].values()) + list(self.profile["equipment"]["item"].values())
            for index, item in enumerate(self.profile["storage"]):
                if index == slot_index:  # only add item of current page
                    number = self.profile["storage"][item]
                    rect = self.storage_box_rects[page_slot_index]

                    item_id = item
                    if item in self.game.character_data.equip_item_list:  # item type
                        self.image.blit(self.small_box_images["item"], rect)
                    else:  # equipment type
                        if item in self.game.character_data.gear_list:
                            self.image.blit(self.small_box_images[self.game.character_data.gear_list[item]["Type"]],
                                            rect)
                        else:  # custom equipment
                            stat = dict(item)
                            item_id = "Custom " + stat["Rarity"] + "_" + stat["Type"]
                            self.image.blit(self.small_box_images[stat["Type"]], rect)
                    item_image = smoothscale(self.item_sprite_pool[self.game.battle.chapter][
                                                 "Normal"][item_id][1][0], (50 * self.screen_scale[0],
                                                                            50 * self.screen_scale[1]))
                    image_rect = item_image.get_rect(center=rect.center)
                    self.image.blit(item_image, image_rect)

                    text_surface = text_render_with_bg(minimise_number_text(str(number)), self.small_font,
                                                       Color("black"))
                    text_rect = text_surface.get_rect(bottomright=rect.bottomright)
                    self.image.blit(text_surface, text_rect)

                    if item in all_equip_item:  # add equipped indication
                        text_surface = text_render_with_bg("E", self.small_font,
                                                           Color("black"))
                        text_rect = text_surface.get_rect(topleft=rect.topleft)
                        self.image.blit(text_surface, text_rect)

                    if item in self.profile["storage_new"]:  # not yet viewed
                        text_surface = text_render_with_bg("!", self.font,
                                                           Color("black"))
                        text_rect = text_surface.get_rect(topleft=rect.topright)
                        self.image.blit(text_surface, text_rect)

                    page_slot_index += 1
                    slot_index += 1
                if page_slot_index == 60:
                    break
            self.base_image = self.image.copy()
        else:
            self.image = self.base_image.copy()

        pygame.draw.rect(self.image, (200, 100, 100), (self.storage_box_rects[page_current_row].topleft[0],
                                                       self.storage_box_rects[page_current_row].topleft[1],
                                                       50 * self.screen_scale[0],
                                                       50 * self.screen_scale[1]), width=int(5 * self.screen_scale[0]))

        text_surface = self.font.render(self.grab_text(("ui", "Gold")) +
                                        ": " + minimise_number_text(str(self.profile["total golds"])),
                                        True, (30, 30, 30))
        text_rect = text_surface.get_rect(topleft=(20 * self.screen_scale[0], 830 * self.screen_scale[1]))
        self.image.blit(text_surface, text_rect)

        self.page_text.rename(str(self.current_page + 1) + "/" + str(self.max_page + 1))
        self.image.blit(self.page_text.image, self.page_text.rect)

    def calculate_follower_stuff(self, follower_dict):
        total_cost = 0
        total_melee = 0
        total_range = 0
        for follower, num in follower_dict.items():
            total_cost += self.game.character_data.character_list[follower]["Follower Cost"] * num
            if self.game.character_data.character_list[follower]["Type"] == "Melee":
                total_melee += num
            else:
                total_range += num
        return total_cost, total_melee, total_range

    def add_follower_preset_list(self):
        self.image = self.follower_preset_base_image.copy()
        for preset, rect in self.follower_preset_box_rects.items():
            real_preset = (preset + 1) + (4 * self.current_page) - 1
            preset_num = real_preset + 1
            if self.current_row == preset:  # current preset row
                draw.rect(self.image, (220, 220, 220),
                          (0, rect.topleft[1], 400 * self.screen_scale[0], 200 * self.screen_scale[1]),
                          width=int(3 * self.screen_scale[0]))
            if real_preset == self.profile["selected follower preset"]:  # currently selected preset for battle
                draw.rect(self.image, (150, 30, 30),
                          ((5 * self.screen_scale[0]), rect.topleft[1] + (5 * self.screen_scale[0]),
                           395 * self.screen_scale[0], 195 * self.screen_scale[1]),
                          width=int(5 * self.screen_scale[0]))
            if self.profile["follower preset"][real_preset]:
                self.image.blit(
                    self.game.character_data.character_portraits[
                        tuple(self.profile["follower preset"][real_preset].keys())[0]],
                    rect)
                total_cost, total_melee, total_range = self.calculate_follower_stuff(
                    self.profile["follower preset"][real_preset])
                text_surface = self.font.render(
                    self.grab_text(("ui", "Cost/Fund")) +
                    ": " + str(total_cost) + "/" + str(self.max_follower_allowance), True, (30, 30, 30))
                text_rect = text_surface.get_rect(topleft=(110 * self.screen_scale[0],
                                                           rect.topright[1] + (20 * self.screen_scale[1])))
                self.image.blit(text_surface, text_rect)

                text_surface = self.font.render(self.grab_text(("ui", "Melee/Range")) +
                                                ": " + str(total_melee) + "/" + str(total_range),
                                                True, (30, 30, 30))
                text_rect = text_surface.get_rect(topleft=(110 * self.screen_scale[0],
                                                           rect.topright[1] + (70 * self.screen_scale[1])))
                self.image.blit(text_surface, text_rect)

                if total_cost > self.max_follower_allowance:
                    text_surface = self.font.render(self.grab_text(("ui", "cost_exceed_warn")),
                                                    True, (30, 30, 30))
                    text_rect = text_surface.get_rect(topleft=(10 * self.screen_scale[0],
                                                               rect.topright[1] + (120 * self.screen_scale[1])))
                    self.image.blit(text_surface, text_rect)

                    text_surface = self.small_font.render(self.grab_text(("ui", "follower_exceed_warn")),
                                                          True, (30, 30, 30))
                    text_rect = text_surface.get_rect(topleft=(10 * self.screen_scale[0],
                                                               rect.topright[1] + (150 * self.screen_scale[1])))
                    self.image.blit(text_surface, text_rect)
            else:
                text_surface = self.font.render(self.grab_text(("ui", "Empty")), True, (30, 30, 30))
                text_rect = text_surface.get_rect(topleft=(110 * self.screen_scale[0],
                                                           rect.topright[1] + (20 * self.screen_scale[1])))
                self.image.blit(text_surface, text_rect)

            # Add preset number
            text_surface = self.font.render("(" + str(preset_num) + ")", True, (30, 30, 30))
            text_rect = text_surface.get_rect(bottomright=(rect.bottomright[0],
                                                           rect.bottomright[1] - (5 * self.screen_scale[1])))
            self.image.blit(text_surface, text_rect)

        self.page_text.rename(str(self.current_page + 1) + "/3")
        self.image.blit(self.page_text.image, self.page_text.rect)

    def add_follower_list(self):
        self.image = self.follower_base_image.copy()

        text_surface = self.font.render(self.grab_text(("ui", "Preset")) + " " +
                                        str(self.current_follower_preset_num), True, (30, 30, 30))
        text_rect = text_surface.get_rect(topleft=(20 * self.screen_scale[0], 20 * self.screen_scale[1]))
        self.image.blit(text_surface, text_rect)

        total_cost, total_melee, total_range = self.calculate_follower_stuff(
            self.profile["follower preset"][self.current_follower_preset_num])
        remain_fund = self.max_follower_allowance - total_cost
        text_surface = self.small_font.render(
            self.grab_text(("ui", "Total Cost")) + ": " + str(total_cost) + "/" +
            self.grab_text(("ui", "Remaining Fund")) + ": " + str(remain_fund),
            True, (30, 30, 30))
        text_rect = text_surface.get_rect(topleft=(20 * self.screen_scale[0], 50 * self.screen_scale[1]))
        self.image.blit(text_surface, text_rect)

        text_surface = self.small_font.render(self.grab_text(("ui", "Total Melee/Range")) + ": " +
                                              str(total_melee) + "/" + str(total_range),
                                              True, (30, 30, 30))
        text_rect = text_surface.get_rect(topleft=(20 * self.screen_scale[0], 70 * self.screen_scale[1]))
        self.image.blit(text_surface, text_rect)

        row_index = 0
        for index, follower in enumerate(self.profile["follower list"]):
            if (index >= self.current_row or len(self.profile["follower list"]) < 9) and row_index < 8:
                if self.current_row == index:  # current preset row
                    draw.rect(self.image, (220, 220, 220),
                              (0, ((row_index + 1) * 100) * self.screen_scale[1], 400 * self.screen_scale[0],
                               100 * self.screen_scale[1]),
                              width=int(3 * self.screen_scale[0]))

                portrait = self.game.character_data.character_portraits[follower]
                rect = portrait.get_rect(topleft=(0, (row_index + 1) * 100 * self.screen_scale[1]))
                self.image.blit(portrait, rect)

                text_surface = self.small_font.render(self.grab_text(("character", follower, "Name")),
                                                      True, (30, 30, 30))
                text_rect = text_surface.get_rect(topleft=(110 * self.screen_scale[0],
                                                           (row_index + 1) * 100 * self.screen_scale[1]))
                self.image.blit(text_surface, text_rect)
                follower_num = 0
                if follower in self.current_follower_preset:
                    follower_num = self.current_follower_preset[follower]
                text_surface = self.font.render("x" + str(follower_num),
                                                True, (30, 30, 30))
                text_rect = text_surface.get_rect(topleft=(110 * self.screen_scale[0],
                                                           (((row_index + 1) * 100) + 20) * self.screen_scale[1]))
                self.image.blit(text_surface, text_rect)

                text_surface = self.small_font.render(
                    str(self.game.character_data.character_list[follower]["Follower Cost"]) + " Cost",
                    True, (30, 30, 30))
                text_rect = text_surface.get_rect(topright=(400 * self.screen_scale[0],
                                                            (((row_index + 1) * 100) + 20) * self.screen_scale[1]))
                self.image.blit(text_surface, text_rect)

                text = str(self.game.character_data.character_list[follower]["Type"])
                if self.game.character_data.character_list[follower]["Boss"]:
                    text += " " + self.grab_text(("ui", "only_one"))
                text_surface = self.small_font.render(text, True, (30, 30, 30))
                text_rect = text_surface.get_rect(topleft=(110 * self.screen_scale[0],
                                                           (((row_index + 1) * 100) + 50) * self.screen_scale[1]))

                self.image.blit(text_surface, text_rect)
                row_index += 1

    def calculate_shop_cost(self):
        total_cost = 0
        for item_id, num in self.purchase_list.items():
            total_cost += self.game.character_data.shop_list[item_id]["Value"] * num
        return total_cost

    def add_shop_list(self):
        self.image = self.shop_base_image.copy()

        total_cost = self.calculate_shop_cost()
        remain_fund = self.profile["total golds"] - total_cost
        text_surface = self.font.render(
            self.grab_text(("ui", "Total Cost")) + ": " + str(total_cost),
            True, (30, 30, 30))
        text_rect = text_surface.get_rect(topleft=(20 * self.screen_scale[0], 20 * self.screen_scale[1]))
        self.image.blit(text_surface, text_rect)
        text_surface = self.font.render(
            self.grab_text(("ui", "Remaining Gold")) + ": " + str(remain_fund),
            True, (30, 30, 30))
        text_rect = text_surface.get_rect(topleft=(20 * self.screen_scale[0], 50 * self.screen_scale[1]))
        self.image.blit(text_surface, text_rect)

        row_index = 0
        for index, item in enumerate(self.shop_list):
            if (index >= self.current_row or len(self.shop_list) < 9) and row_index < 9:
                if self.current_row == index:  # current preset row
                    draw.rect(self.image, (220, 220, 220),
                              (0, ((index + 1) * 100) * self.screen_scale[1], 400 * self.screen_scale[0],
                               100 * self.screen_scale[1]),
                              width=int(3 * self.screen_scale[0]))

                item_image = self.item_sprite_pool[self.game.battle.chapter]["Normal"][item][1][0]
                rect = item_image.get_rect(topleft=(0, (index + 1) * 100 * self.screen_scale[1]))
                self.image.blit(item_image, rect)

                if item in self.game.character_data.equip_item_list:
                    make_long_text(self.image, self.grab_text(("item", item, "Name")),  # add item name
                                   (110 * self.screen_scale[0],
                                    (index + 1) * 100 * self.screen_scale[1]), self.font, color=(30, 30, 30),
                                   specific_width=self.image.get_width() - (50 * self.screen_scale[0]))
                elif item in self.game.character_data.gear_list:
                    make_long_text(self.image, self.grab_text(("gear", item, "Name")),  # add item name
                                   (110 * self.screen_scale[0],
                                    (index + 1) * 100 * self.screen_scale[1]), self.font, color=(30, 30, 30),
                                   specific_width=self.image.get_width() - (50 * self.screen_scale[0]))
                else:
                    stat = dict(item)
                    make_long_text(self.image,
                                   self.get_custom_equipment_name(stat),  # add item name
                                   (110 * self.screen_scale[0],
                                    (index + 1) * 100 * self.screen_scale[1]), self.font, color=(30, 30, 30),
                                   specific_width=self.image.get_width() - (100 * self.screen_scale[0]))

                purchase_num = 0
                if item in self.purchase_list:
                    purchase_num = self.purchase_list[item]
                text_surface = self.font.render("x" + str(purchase_num),
                                                True, (30, 30, 30))
                text_rect = text_surface.get_rect(topleft=(110 * self.screen_scale[0],
                                                           (((index + 1) * 100) + 50) * self.screen_scale[1]))
                self.image.blit(text_surface, text_rect)

                text_surface = self.font.render(
                    str(self.game.character_data.shop_list[item]["Value"]) + " " + self.grab_text(("ui", "Gold Cost")),
                    True, (30, 30, 30))
                text_rect = text_surface.get_rect(topright=(400 * self.screen_scale[0],
                                                            (((index + 1) * 100) + 50) * self.screen_scale[1]))
                self.image.blit(text_surface, text_rect)
                row_index += 1

    def add_reward_list(self):
        self.image = self.reward_base_image.copy()
        self.shown_reward_list = []
        self.len_reward_list = len(self.reward_list["one"]) + len(self.reward_list["choice"]) + len(
            self.reward_list["multi"])

        index = 0
        row_index = 0
        for reward_type in ("one", "choice", "multi"):
            for item in self.reward_list[reward_type]:
                if (index >= self.current_row or self.len_reward_list < 9) and row_index < 9:
                    gold_value = 0

                    if index == 0:  # first item in list
                        draw.rect(self.image, (150, 150, 150),
                                  (0, (row_index * 100) * self.screen_scale[1], 400 * self.screen_scale[0],
                                   100 * self.screen_scale[1]),
                                  width=int(3 * self.screen_scale[0]))

                    if index == self.len_reward_list - 1:  # last item in list
                        draw.rect(self.image, (150, 50, 50),
                                  (0, (row_index * 100) * self.screen_scale[1], 400 * self.screen_scale[0],
                                   100 * self.screen_scale[1]),
                                  width=int(3 * self.screen_scale[0]))

                    if item in self.game.character_data.character_list:  # follower reward
                        portrait = self.game.character_data.character_portraits[item]
                        rect = portrait.get_rect(topleft=(0, row_index * 100 * self.screen_scale[1]))
                        self.image.blit(portrait, rect)
                        make_long_text(self.image, self.grab_text(("character", item, "Name")),
                                       (110 * self.screen_scale[0],
                                        row_index * 100 * self.screen_scale[1]), self.font, color=(30, 30, 30),
                                       specific_width=self.image.get_width() - (50 * self.screen_scale[0]))
                    else:  # item reward
                        item_id = item
                        if item in self.game.character_data.equip_item_list:
                            gold_value = self.game.character_data.equip_item_list[item]["Value"]
                            make_long_text(self.image, self.grab_text(("item", item, "Name")),
                                           (110 * self.screen_scale[0],
                                            row_index * 100 * self.screen_scale[1]), self.font, color=(30, 30, 30),
                                           specific_width=self.image.get_width() - (50 * self.screen_scale[0]))
                        elif item in self.game.character_data.gear_list:
                            gold_value = self.game.character_data.gear_list[item]["Value"]
                            make_long_text(self.image, self.grab_text(("gear", item, "Name")),
                                           (110 * self.screen_scale[0],
                                            row_index * 100 * self.screen_scale[1]), self.font, color=(30, 30, 30),
                                           specific_width=self.image.get_width() - (50 * self.screen_scale[0]))
                        elif item == "gold":
                            gold_value = 1
                            item_id = "Gold"
                            make_long_text(self.image, self.grab_text(("ui", "Gold")),
                                           (110 * self.screen_scale[0],
                                            row_index * 100 * self.screen_scale[1]), self.font, color=(30, 30, 30),
                                           specific_width=self.image.get_width() - (50 * self.screen_scale[0]))
                        elif item == "stat":
                            item_id = "Stat"
                            make_long_text(self.image, self.grab_text(("ui", "Status Points")),
                                           (110 * self.screen_scale[0],
                                            row_index * 100 * self.screen_scale[1]), self.font, color=(30, 30, 30),
                                           specific_width=self.image.get_width() - (50 * self.screen_scale[0]))
                        elif item == "skill":
                            item_id = "Skill"
                            make_long_text(self.image, self.grab_text(("ui", "Skill Points")),
                                           (110 * self.screen_scale[0],
                                            row_index * 100 * self.screen_scale[1]), self.font, color=(30, 30, 30),
                                           specific_width=self.image.get_width() - (50 * self.screen_scale[0]))
                        else:  # custom equipment
                            stat = dict(item)
                            item_id = "Custom " + stat["Rarity"] + "_" + stat["Type"]
                            gold_value = stat["Value"]
                            make_long_text(self.image,
                                           self.get_custom_equipment_name(stat),  # add item name
                                           (110 * self.screen_scale[0],
                                            row_index * 100 * self.screen_scale[1]), self.font, color=(30, 30, 30),
                                           specific_width=self.image.get_width() - (50 * self.screen_scale[0]))
                        item_image = self.item_sprite_pool[self.game.battle.chapter]["Normal"][item_id][1][0]
                        rect = item_image.get_rect(topleft=(0, row_index * 100 * self.screen_scale[1]))
                        self.image.blit(item_image, rect)

                    text_surface = self.font.render("x" + str(self.reward_list[reward_type][item]), True, (30, 30, 30))
                    text_rect = text_surface.get_rect(topleft=(110 * self.screen_scale[0],
                                                               ((row_index * 100) + 50) * self.screen_scale[1]))
                    self.image.blit(text_surface, text_rect)

                    text_surface = self.font.render(
                        str(gold_value * self.reward_list[reward_type][
                            item]) + " Gold Value",
                        True, (30, 30, 30))
                    text_rect = text_surface.get_rect(topright=(400 * self.screen_scale[0],
                                                                ((row_index * 100) + 50) * self.screen_scale[1]))
                    self.image.blit(text_surface, text_rect)

                    if reward_type == "one":
                        text_surface = self.font.render(self.grab_text(("ui", "one_time_reward")),
                                                        True, (150, 30, 30))
                    elif reward_type == "choice":
                        text_surface = self.font.render(self.grab_text(("ui", "choice_reward")),
                                                        True, (30, 150, 30))
                    else:
                        text_surface = self.font.render(self.grab_text(("ui", "multi_time_reward")),
                                                        True, (30, 30, 150))
                    text_rect = text_surface.get_rect(topright=(400 * self.screen_scale[0],
                                                                ((row_index * 100) + 70) * self.screen_scale[1]))
                    self.image.blit(text_surface, text_rect)

                    self.shown_reward_list.append((reward_type, item))

                    row_index += 1

                index += 1

    def add_enchant_list(self):
        self.image = self.enchant_base_image.copy()
        all_equip_item = list(self.profile["equipment"].values()) + list(
            self.profile["equipment"]["item"].values())
        row_index = 0
        for index, item in enumerate(self.all_custom_item):
            if (index >= self.current_row or len(self.all_custom_item) < 5) and row_index < 5:
                stat = dict(item)
                item_id = "Custom " + stat["Rarity"] + "_" + stat["Type"]
                item_image = self.item_sprite_pool[self.game.battle.chapter]["Normal"][item_id][1][0]
                if index == self.current_row:
                    # image and info to the top
                    rect = item_image.get_rect(center=(200 * self.screen_scale[0], 90 * self.screen_scale[1]))
                    self.image.blit(item_image, rect)

                    index2 = 0
                    for value in self.get_custom_equipment_description(dict(item)):
                        text_surface = self.small_font.render(value, True, (30, 30, 30))
                        text_rect = text_surface.get_rect(topleft=(20 * self.screen_scale[0],
                                                                   (150 + (25 * index2)) * self.screen_scale[1]))
                        self.image.blit(text_surface, text_rect)
                        index2 += 1

                    remain_fund = self.profile["total golds"] - stat["Rework Cost"]

                    text_surface = self.font.render(
                        self.grab_text(("ui", "Total Cost")) + ": " + str(stat["Rework Cost"]),
                        True, (30, 30, 30))
                    text_rect = text_surface.get_rect(topleft=(20 * self.screen_scale[0], 360 * self.screen_scale[1]))
                    self.image.blit(text_surface, text_rect)
                    text_surface = self.font.render(
                        self.grab_text(("ui", "Remaining Gold")) + ": " + str(remain_fund),
                        True, (30, 30, 30))
                    text_rect = text_surface.get_rect(topleft=(20 * self.screen_scale[0], 380 * self.screen_scale[1]))
                    self.image.blit(text_surface, text_rect)

                    if item in self.profile["storage_new"]:  # viewed, remove not view state in profile
                        self.profile["storage_new"].remove(item)

                    draw.rect(self.image, (220, 220, 220),
                              (0, ((row_index + 4) * 100) * self.screen_scale[1], 400 * self.screen_scale[0],
                               100 * self.screen_scale[1]),
                              width=int(3 * self.screen_scale[0]))

                make_long_text(self.image,
                               self.get_custom_equipment_name(stat),  # add item name
                               (110 * self.screen_scale[0],
                                (row_index + 4) * 100 * self.screen_scale[1]), self.font, color=(30, 30, 30),
                               specific_width=self.image.get_width() - (50 * self.screen_scale[0]))
                rect = item_image.get_rect(topleft=(0, (row_index + 4) * 100 * self.screen_scale[1]))
                self.image.blit(item_image, rect)

                text_surface = self.font.render(str(stat["Rework Cost"]) + " " + self.grab_text(("ui", "Gold Cost")),
                                                True, (30, 30, 30))
                text_rect = text_surface.get_rect(topright=(400 * self.screen_scale[0],
                                                            ((row_index + 4) * 100 + 50) * self.screen_scale[1]))
                self.image.blit(text_surface, text_rect)

                if item in all_equip_item:  # add equipped indication
                    text_surface = text_render_with_bg("E", self.font,
                                                       Color("black"))
                    text_rect = text_surface.get_rect(topleft=rect.topleft)
                    self.image.blit(text_surface, text_rect)
                if item in self.profile["storage_new"]:  # not yet viewed
                    text_surface = text_render_with_bg("!", self.font,
                                                       Color("black"))
                    text_rect = text_surface.get_rect(topleft=rect.topright)
                    self.image.blit(text_surface, text_rect)
                row_index += 1

    def start_new_mode(self):
        self.game.battle.remove_ui_updater(self.text_popup)
        self.game.remove_ui_updater(self.text_popup)
        if self.mode == "stat":
            self.player_input = self.player_input_stat
            self.add_stat(self.stat)
        elif self.mode == "equipment":
            self.player_input = self.player_input_equipment
            self.change_equipment()
        elif self.mode == "equipment_list":
            self.player_input = self.player_input_equipment_list
            self.change_equipment_list()
        elif "follower" in self.mode:
            self.player_input = self.player_input_follower
            if self.mode == "follower":
                self.add_follower_preset_list()
            else:
                self.add_follower_list()
        elif "storage" in self.mode:
            self.max_page = int(len(self.profile["storage"]) / 61)
            self.player_input = self.player_input_storage
            self.change_storage_list()
        elif "shop" in self.mode:
            self.player_input = self.player_input_shop
            self.add_shop_list()
        elif "reward" in self.mode:
            self.player_input = self.player_input_reward
            self.add_reward_list()
        elif "enchant" in self.mode:
            self.player_input = self.player_input_enchant
            self.add_enchant_list()

    def change_mode(self, mode):
        self.mode = mode
        self.base_image = None
        self.current_row = 0
        self.sub_menu_current_row = 0
        self.current_page = 0
        self.start_new_mode()

    def add_remove_text_popup(self):
        if self.game.battle.city_mode:
            if self.text_popup not in self.game.battle.ui_updater:
                self.game.battle.add_ui_updater(self.text_popup)
            else:
                self.game.battle.remove_ui_updater(self.text_popup)
        else:
            if self.text_popup not in self.game.ui_updater:
                self.game.add_ui_updater(self.text_popup)
            else:
                self.game.remove_ui_updater(self.text_popup)

    def change_stat(self, stat, how):
        self.stat[stat], self.stat["Status Remain"] = stat_allocation_check(self.stat[stat], self.stat["Status Remain"],
                                                                            how)
        self.add_stat(self.stat)

    def change_skill(self, skill, how):
        chapter = 1
        if "Chapter" in self.profile:
            chapter = int(self.profile["Chapter"])
        self.stat[skill], self.stat["Skill Remain"] = skill_allocation_check(self.stat[skill],
                                                                             self.stat["Skill Remain"], how, chapter)
        self.add_stat(self.stat)

    def open_sub_menu(self, button_list):
        self.sub_menu_current_row = 0
        self.sub_menu_button_list = button_list
        self.player_input = self.player_input_sub_menu
        self.add_sub_menu()

    def add_sub_menu(self):
        sub_menu_image = Surface((self.image.get_width(), (40 * self.screen_scale[1]) * len(self.sub_menu_button_list)))
        for index, button in enumerate(self.sub_menu_button_list):
            button_image = Surface((self.image.get_width(), (40 * self.screen_scale[1])))
            button_image.fill((150, 150, 150))
            if index == self.sub_menu_current_row:
                pygame.draw.rect(button_image, (150, 150, 20),
                                 (0, 0, self.image.get_width(), (40 * self.screen_scale[1])),
                                 width=int(5 * self.screen_scale[0]))
            else:
                pygame.draw.rect(button_image, (30, 30, 30),
                                 (0, 0, self.image.get_width(), (40 * self.screen_scale[1])),
                                 width=int(5 * self.screen_scale[0]))
            text_surface = self.font.render(self.grab_text(("ui", button)), True, (30, 30, 30))
            text_rect = text_surface.get_rect(midleft=(10 * self.screen_scale[0], int(button_image.get_height() / 2)))
            button_image.blit(text_surface, text_rect)
            button_rect = button_image.get_rect(topleft=(0, (40 * self.screen_scale[1]) * index))
            sub_menu_image.blit(button_image, button_rect)
        sub_menu_rect = sub_menu_image.get_rect(bottomleft=(0, self.image.get_height()))
        self.image.blit(sub_menu_image, sub_menu_rect)

    def player_input_sub_menu(self, key):
        """Player input for when sub menu is active"""
        if not self.input_delay:
            if key in ("Up", "Down"):
                self.input_delay = 0.2
                if key == "Up":
                    self.sub_menu_current_row -= 1
                    if self.sub_menu_current_row < 0:
                        self.sub_menu_current_row = len(self.sub_menu_button_list) - 1
                    self.add_sub_menu()
                elif key == "Down":
                    self.sub_menu_current_row += 1
                    if self.sub_menu_current_row > len(self.sub_menu_button_list) - 1:
                        self.sub_menu_current_row = 0
                    self.add_sub_menu()
            else:
                self.input_delay = 0.3
                if key == "Weak":  # confirm and sort based on selected option
                    if self.sub_menu_button_list == self.item_sort_list:
                        sort_how = self.item_sort_list[self.sub_menu_current_row].split(" ")
                        if self.mode == "equipment_list":
                            if sort_how[0] == "Name":
                                sort_list = {key: self.grab_text(("gear", key, "Name")) if
                                key in self.game.character_data.gear_list else self.grab_text(
                                    ("item", key,
                                     "Name")) if key in self.game.character_data.equip_item_list else
                                self.get_custom_equipment_name(dict(key)) for key in self.current_equipment_list}
                            elif sort_how[0] == "Type":
                                sort_list = {key: self.game.character_data.gear_list[key][
                                    "Type"] if key in self.game.character_data.gear_list else
                                self.game.character_data.equip_item_list[key][
                                    "Type"] if key in self.game.character_data.equip_item_list else dict(key)["Type"] for key
                                             in self.current_equipment_list}
                            elif sort_how[0] == "Quantity":
                                sort_list = {key: self.profile["storage"][key] for key in self.current_equipment_list}
                            elif sort_how[0] == "Value":
                                sort_list = {key: self.game.character_data.gear_list[key][
                                    "Value"] if key in self.game.character_data.gear_list else
                                self.game.character_data.equip_item_list[key][
                                    "Value"] if key in self.game.character_data.equip_item_list else dict(key)["Value"] for
                                             key
                                             in self.current_equipment_list}
                            elif sort_how[0] == "Rarity":
                                sort_list = {key: self.game.character_data.gear_list[key][
                                    "Rarity"] if key in self.game.character_data.gear_list else
                                "Common" if key in self.game.character_data.equip_item_list else dict(key)["Rarity"] for key
                                             in self.current_equipment_list}

                            if sort_how[1] == "Ascending":
                                sort_list = dict(sorted(sort_list.items(), key=lambda item: item[1]))
                            else:
                                sort_list = dict(sorted(sort_list.items(), key=lambda item: item[1], reverse=True))
                            self.current_equipment_list = list(sort_list.keys())
                            self.change_equipment_list()
                        elif "storage" in self.mode:
                            if sort_how[0] == "Name":
                                sort_list = {key: self.grab_text(
                                    ("gear", key, "Name")) if key in self.game.character_data.gear_list else
                                self.grab_text(("item", key, "Name")) if key in self.game.character_data.equip_item_list
                                else self.get_custom_equipment_name(dict(key)) for key in self.profile["storage"]}
                            elif sort_how[0] == "Type":
                                sort_list = {key: self.game.character_data.gear_list[key][
                                    "Type"] if key in self.game.character_data.gear_list else
                                self.game.character_data.equip_item_list[key][
                                    "Type"] if key in self.game.character_data.equip_item_list else dict(key)["Type"] for key
                                             in self.profile["storage"]}
                            elif sort_how[0] == "Quantity":
                                sort_list = {key: value for key, value in self.profile["storage"].items()}
                            elif sort_how[0] == "Value":
                                sort_list = {key: self.game.character_data.gear_list[key][
                                    "Value"] if key in self.game.character_data.gear_list else
                                self.game.character_data.equip_item_list[key][
                                    "Value"] if key in self.game.character_data.equip_item_list else dict(key)["Value"] for
                                             key
                                             in self.profile["storage"]}
                            elif sort_how[0] == "Rarity":
                                sort_list = {key: self.game.character_data.gear_list[key][
                                    "Rarity"] if key in self.game.character_data.gear_list else
                                "Common" if key in self.game.character_data.equip_item_list else dict(key)["Rarity"] for key
                                             in self.profile["storage"]}
                            if sort_how[1] == "Ascending":
                                sort_list = dict(sorted(sort_list.items(), key=lambda item: item[1]))
                            else:
                                sort_list = dict(sorted(sort_list.items(), key=lambda item: item[1], reverse=True))
                            self.profile["storage"] = {key: self.profile["storage"][key] for key in sort_list}
                    elif self.sub_menu_button_list == self.enchant_sort_list:
                        sort_how = self.enchant_sort_list[self.sub_menu_current_row].split(" ")
                        all_equip_item = list(self.profile["equipment"].values()) + list(
                            self.profile["equipment"]["item"].values())
                        sort_list = [item for item in self.profile["storage"] if type(item) is tuple]
                        if sort_how[0] == "Name":
                            sort_list = {key: self.get_custom_equipment_name(dict(key)) for key in sort_list}
                        elif sort_how[0] == "Type":
                            sort_list = {key: dict(key)["Type"] for key in sort_list}
                        elif sort_how[0] == "Equipped":
                            sort_list = {key: 1 if key in all_equip_item else 2 for key in sort_list}
                        elif sort_how[0] == "Rarity":
                            sort_list = {key: dict(key)["Value"] for key in sort_list}
                        if sort_how[1] == "Ascending":
                            sort_list = dict(sorted(sort_list.items(), key=lambda item: item[1]))
                        else:
                            sort_list = dict(sorted(sort_list.items(), key=lambda item: item[1], reverse=True))
                        self.all_custom_item = [item for item in sort_list]
                        self.add_enchant_list()
                    elif self.sub_menu_button_list == self.follower_sort_list:
                        sort_how = self.follower_sort_list[self.sub_menu_current_row].split(" ")
                        if self.mode == "follower_list":
                            if sort_how[0] == "Name":
                                sort_list = {key: self.grab_text(("character", key, "Name")) for key in
                                             self.profile["follower list"]}
                            elif sort_how[0] == "Type":
                                sort_list = {key: self.game.character_data.character_list[key]["Type"] for key in
                                             self.profile["follower list"]}
                            elif sort_how[0] == "Cost":
                                sort_list = {key: self.game.character_data.character_list[key]["Follower Cost"] for key
                                             in self.profile["follower list"]}
                            elif sort_how[0] == "Single":
                                sort_list = {key: self.game.character_data.character_list[key]["Boss"] for key in
                                             self.profile["follower list"]}

                            if sort_how[1] == "Ascending":
                                sort_list = dict(sorted(sort_list.items(), key=lambda item: item[1]))
                            else:
                                sort_list = dict(sorted(sort_list.items(), key=lambda item: item[1], reverse=True))
                            self.profile["follower list"] = [key for key in sort_list]
                    elif self.sub_menu_button_list == self.follower_clear_list:
                        if self.follower_clear_list[self.sub_menu_current_row] == "Clear Follower":
                            for key in tuple(self.current_follower_preset.keys()):
                                self.current_follower_preset.pop(key)
                            self.add_follower_list()
                    elif self.sub_menu_button_list == self.purchase_confirm_list:
                        if self.purchase_confirm_list[self.sub_menu_current_row] == "Confirm Purchase":
                            total_cost = self.calculate_shop_cost()
                            if total_cost <= self.profile["total golds"]:
                                for key, value in self.purchase_list.items():
                                    if key in self.profile["storage"]:
                                        self.profile["storage"][key] += value
                                    else:
                                        self.profile["storage"][key] = value
                                self.profile["total golds"] -= total_cost
                    elif self.sub_menu_button_list == self.enchant_confirm_list:
                        if "Confirm" in self.purchase_confirm_list[self.sub_menu_current_row]:
                            new_gear = self.game.generate_custom_equipment(dict(self.all_custom_item[self.current_row])["Type"],
                                                                           dict(self.all_custom_item[self.current_row])["Rarity"])
                            new_gear = tuple(new_gear.items())
                            for item in self.profile["storage"].copy():
                                if item == self.all_custom_item[self.current_row]:
                                    for key, item2 in self.profile["equipment"].items():
                                        if item2 == item:  # replace equipped gear with new one
                                            self.profile["equipment"][key] = new_gear
                                    self.all_custom_item[self.all_custom_item.index(item)] = new_gear
                                    self.profile["storage"][new_gear] = self.profile["storage"].pop(item)  # replace in storage
                                    break
                            self.add_enchant_list()
                            self.game.save_data.add_profilesave_profile["character"][self.game.profile_index[self.player]]["last save"] = \
                                datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")  # save after enchant
                            self.game.write_all_player_save()

                            self.input_delay = 1
                    elif self.sub_menu_button_list == self.purchase_clear_confirm_list:
                        if self.purchase_clear_confirm_list[self.sub_menu_current_row] == "Confirm Clear":
                            self.purchase_list = {}
                    elif self.sub_menu_button_list == self.storage_sell_list:
                        if "Sell" in self.storage_sell_list[self.sub_menu_current_row]:
                            item = tuple(self.profile["storage"].keys())[self.current_row]
                            if "All" in self.storage_sell_list[self.sub_menu_current_row]:
                                sell_number = self.profile["storage"][item]
                                self.profile["storage"][item] = 0
                            elif "Half" in self.storage_sell_list[self.sub_menu_current_row]:
                                sell_number = int(self.profile["storage"][item] / 2)
                                self.profile["storage"][item] -= sell_number
                            else:  # sell one item
                                sell_number = 1
                                self.profile["storage"][item] -= 1
                            if item in self.game.character_data.equip_item_list:  # item type
                                self.profile["total golds"] += self.game.character_data.equip_item_list[item][
                                                                   "Value"] * sell_number
                            else:  # equipment type
                                if item in self.game.character_data.gear_list:
                                    self.profile["total golds"] += self.game.character_data.gear_list[item][
                                                                       "Value"] * sell_number
                                else:  # custom equipment
                                    self.profile["total golds"] += dict(item)["Value"] * sell_number
                            if not self.profile["storage"][item]:  # item no longer exist in storage
                                if item not in self.game.character_data.equip_item_list:
                                    # check if item is equipped, if so unequip it
                                    if item in self.profile["equipment"].values():
                                        for key, value in self.profile["equipment"].items():
                                            if value == item:
                                                self.profile["equipment"][key] = None
                                    self.profile["storage"].pop(item)  # remove sold equip from storage
                    self.start_new_mode()

                elif key == "Strong":  # cancel, change back to previous interface
                    self.start_new_mode()
                elif key == "Guard":
                    self.add_remove_text_popup()
                    self.text_popup.popup(self.rect.topleft,
                                          (self.grab_text(("ui", "keybind_weak_attack")) + " " +
                                           self.grab_text(("ui", "Button")) + " (" +
                                           self.game.player_key_bind_button_name[self.player]["Weak"] +
                                           "): " + self.grab_text(("ui", "confirm_button")),
                                           self.grab_text(("ui", "keybind_strong_attack")) + " " +
                                           self.grab_text(("ui", "Button")) + " (" +
                                           self.game.player_key_bind_button_name[self.player]["Strong"] +
                                           "): " + self.grab_text(("ui", "cancel_button"))),
                                          shown_id=key, width_text_wrapper=400 * self.game.screen_scale[0])

    def player_input_stat(self, key):
        if not self.input_delay:
            if key in ("Up", "Down", "Left", "Right"):
                self.input_delay = 0.2
                if key == "Up":
                    self.current_row -= 1
                    if self.current_row < 0:
                        self.current_row = self.last_row
                    self.add_stat(self.stat)
                elif key == "Down":
                    self.current_row += 1
                    if self.current_row > self.last_row:
                        self.current_row = 0
                    self.add_stat(self.stat)
                elif key == "Left":
                    if self.current_row <= 6:  # change stat
                        self.change_stat(self.stat_row[self.current_row], "down")
                    else:  # change skill
                        self.change_skill(self.all_skill_row[self.current_row - 7], "down")
                elif key == "Right":
                    if self.current_row <= 6:  # change stat
                        self.change_stat(self.stat_row[self.current_row], "up")
                    else:  # change skill
                        self.change_skill(self.all_skill_row[self.current_row - 7], "up")
            else:
                self.input_delay = 0.3
                if key == "Special":  # popup text description
                    self.add_remove_text_popup()
                    if self.current_row <= 6:
                        stat = self.stat_row[self.current_row]
                        self.text_popup.popup(self.rect.topleft,
                                              (self.grab_text(("help", stat, "Name")),
                                               self.grab_text(("help", stat, "Description"))),
                                              shown_id=stat, width_text_wrapper=400 * self.game.screen_scale[0])
                    else:
                        warning = ""
                        chapter = 1
                        if "Chapter" in self.profile:
                            chapter = int(self.profile["Chapter"])
                        if self.stat[self.all_skill_row[self.current_row - 7]] == chapter + 1 and \
                                self.stat[self.all_skill_row[self.current_row - 7]] != 5:
                            warning = self.grab_text(("ui", "warn_skill_next_chapter"))
                        elif self.stat[self.all_skill_row[self.current_row - 7]] == 5:
                            warning = self.grab_text(("ui", "warn_skill_max_level"))
                        skill_level = int(self.stat[self.all_skill_row[self.current_row - 7]])
                        new_key = self.all_skill_row[self.current_row - 7] + "." + str(skill_level)
                        if skill_level and self.current_row - 7 > 7:  # char skill with buttons to perform
                            skill_index = self.current_row - 14
                            if skill_index <= 6:
                                skill_id = "C" + str(skill_index) + "." + str(skill_level)
                            buttons = self.game.character_data.character_list[self.profile["character"]["ID"]]["Skill UI"][skill_id]["Buttons"]
                            buttons = "(" + self.game.character_data.character_list[self.profile["character"]["ID"]]["Skill UI"][skill_id]["Position"] + ") " + " + ".join(buttons)
                            text = (self.grab_text(("help", new_key, "Name")),
                                    self.grab_text(("help", new_key, "Description")),
                                    self.grab_text(("ui", "Buttons")) + ":" + buttons,
                                    warning)
                        else:
                            text = (self.grab_text(("help", new_key, "Name")),
                                    self.grab_text(("help", new_key, "Description")),
                                    warning)
                        self.text_popup.popup(self.rect.topleft, text,
                                              shown_id=key, width_text_wrapper=400 * self.game.screen_scale[0])
                elif key == "Guard":
                    self.add_remove_text_popup()
                    self.text_popup.popup(self.rect.topleft,
                                          (self.grab_text(("ui", "keybind_inventory_menu")) + " " +
                                           self.grab_text(("ui", "Button")) + " (" +
                                           self.game.player_key_bind_button_name[self.player]["Inventory Menu"] +
                                           "): " + self.grab_text(("ui", "stat_to_equip")),
                                           self.grab_text(("ui", "keybind_order_menu")) + " " +
                                           self.grab_text(("ui", "Button")) + " (" +
                                           self.game.player_key_bind_button_name[self.player]["Order Menu"] +
                                           "): " + self.grab_text(("ui", "stat_to_storage")),
                                           self.grab_text(("ui", "keybind_special")) + " " +
                                           self.grab_text(("ui", "Button")) + " (" +
                                           self.game.player_key_bind_button_name[self.player]["Special"] +
                                           "): " + self.grab_text(("ui", "Toggle description"))),
                                          shown_id=key, width_text_wrapper=400 * self.game.screen_scale[0])
                if self.game.battle.city_mode:
                    if key == "Inventory Menu":  # go to next page (equipment)
                        self.change_mode("equipment")
                    elif key == "Order Menu":  # go to previous page (storage)
                        self.change_mode("storage")

    def player_input_equipment(self, key):
        if not self.input_delay:
            if key in ("Up", "Down", "Left", "Right"):
                self.input_delay = 0.2
                if key == "Up":
                    self.current_row -= 1
                    if self.current_row < 0:
                        self.current_row = len(self.equipment_slot_rect) - 1
                    self.change_equipment()
                elif key == "Down":
                    self.current_row += 1
                    if self.current_row > len(self.equipment_slot_rect) - 1:
                        self.current_row = 0
                    self.change_equipment()
                elif key == "Left":
                    self.current_row -= 7
                    if self.current_row < 0:
                        self.current_row = len(self.equipment_slot_rect) + self.current_row
                    self.change_equipment()
                elif key == "Right":
                    self.current_row += 7
                    if self.current_row > len(self.equipment_slot_rect) - 1:
                        self.current_row = self.current_row - len(self.equipment_slot_rect)
                    self.change_equipment()

            else:
                self.input_delay = 0.3
                if key == "Inventory Menu":  # go to next page (follower)
                    self.change_mode("follower")
                elif key == "Order Menu":  # go to previous page (stat)
                    self.change_mode("stat")
                elif key == "Weak":  # equip the selected gear
                    equip_type = tuple(self.equipment_slot_rect.keys())[self.current_row]
                    if "accessory" in equip_type:  # change accessory (number e.g., accessory 1) to accessory
                        equip_type = equip_type.split(" ")[0]
                    self.selected_equipment_slot = tuple(self.equipment_slot_rect.keys())[self.current_row]
                    self.current_equipment_list = []
                    for key in self.profile["storage"]:
                        if "item" in equip_type and key in self.game.character_data.equip_item_list:
                            self.current_equipment_list.append(key)
                        else:
                            if key in self.game.character_data.gear_list:
                                if self.game.character_data.gear_list[key]["Type"] == equip_type:
                                    self.current_equipment_list.append(key)
                            elif type(key) is tuple:
                                stat = dict(key)
                                if stat["Type"] == equip_type:
                                    self.current_equipment_list.append(key)

                    self.change_mode("equipment_list")
                elif key == "Special":  # show total equipment stat
                    self.add_remove_text_popup()
                    shown_stat = {}
                    for mod in self.total_equip_stat:  # find mod that will no longer exist if equip select gear
                        stat = str(self.total_equip_stat[mod])
                        if isinstance(self.total_equip_stat[mod], (int, float)):
                            if self.total_equip_stat[mod] < 1:
                                stat = str(float(stat) * 100) + "%"
                            if "-" not in stat:
                                stat = "+" + stat.replace("-", "")
                            shown_stat[mod] = stat
                    self.text_popup.popup(self.rect.topleft, ["Total Equipment Modifiers"] +
                                          [self.grab_text(("gear_mod", key, "Name")) + ": " + str(value)
                                           for key, value in shown_stat.items()],
                                          shown_id=key, width_text_wrapper=400 * self.game.screen_scale[0])
                elif key == "Guard":
                    self.add_remove_text_popup()

                    self.text_popup.popup(self.rect.topleft,
                                          (self.grab_text(("ui", "keybind_inventory_menu")) + " " +
                                           self.grab_text(("ui", "Button")) + " (" +
                                           self.game.player_key_bind_button_name[self.player]["Inventory Menu"] +
                                           "): " + self.grab_text(("ui", "to_follower_preset")),
                                           self.grab_text(("ui", "keybind_order_menu")) + " " +
                                           self.grab_text(("ui", "Button")) + " (" +
                                           self.game.player_key_bind_button_name[self.player]["Order Menu"] +
                                           "): " + self.grab_text(("ui", "to_stat")),
                                           self.grab_text(("ui", "keybind_special")) + " " +
                                           self.grab_text(("ui", "Button")) + " (" +
                                           self.game.player_key_bind_button_name[self.player]["Special"] +
                                           "): " + self.grab_text(("ui", "Toggle total modifier")),
                                           self.grab_text(("ui", "keybind_weak_attack")) + " " +
                                           self.grab_text(("ui", "Button")) + " (" +
                                           self.game.player_key_bind_button_name[self.player]["Weak"] +
                                           "): " + self.grab_text(("ui", "slot_select_equip"))),
                                          shown_id=key, width_text_wrapper=400 * self.game.screen_scale[0])

    def player_input_equipment_list(self, key):
        if not self.input_delay:
            if key in ("Up", "Down", "Left", "Right"):
                self.input_delay = 0.2
                if key == "Up":
                    self.current_row -= 1
                    if self.current_row < 0:
                        self.current_row = len(self.show_equip_list) - 1
                    self.change_equipment_list()
                elif key == "Down":
                    self.current_row += 1
                    if self.current_row > len(self.show_equip_list) - 1:
                        self.current_row = 0
                    self.change_equipment_list()

            else:
                self.input_delay = 0.3
                if key == "Special":
                    self.add_remove_text_popup()
                    compare_stat = {}
                    for mod in self.total_select_equip_stat:
                        compare_stat[mod] = ""
                        if mod in self.total_equip_stat:
                            stat = str(self.total_equip_stat[mod])
                            if self.total_equip_stat[mod] < 1:
                                stat = str(float(stat) * 100) + "%"
                            if "-" not in stat:
                                stat = "+" + stat
                            difference = str(self.total_select_equip_stat[mod] - self.total_equip_stat[mod])
                            if self.total_select_equip_stat[mod] < 1:
                                difference = str(float(difference) * 100) + "%"
                            if "-" not in difference:
                                difference = "+" + difference
                            compare_stat[mod] = stat + "(" + difference + ")"
                        else:
                            stat = str(self.total_select_equip_stat[mod])
                            if self.total_select_equip_stat[mod] < 1:
                                stat = str(float(stat) * 100) + "%"
                            if "-" not in stat:
                                stat = "+" + stat
                            compare_stat[mod] = "0 (" + stat + ")"
                    for mod in self.total_equip_stat:  # find mod that will no longer exist if equip select gear
                        if mod not in self.total_select_equip_stat:
                            stat = str(self.total_equip_stat[mod])
                            if not isinstance(self.total_equip_stat[mod], (bool,)) and \
                                    isinstance(self.total_equip_stat[mod], (int, float)):
                                if self.total_equip_stat[mod] < 1:
                                    stat = str(float(stat) * 100) + "%"
                                if "-" in stat:
                                    stat = "+" + stat.replace("-", "")
                                else:
                                    stat = "-" + stat
                                compare_stat[mod] = "0 " + "(" + stat + ")"
                            else:
                                compare_stat[mod] = "Removed"

                    self.text_popup.popup(self.rect.topleft, ["Total Equipment Modifiers"] +
                                          [self.grab_text(("gear_mod", key, "Name")) + ": " + str(value)
                                           for key, value in compare_stat.items()],
                                          shown_id=key, width_text_wrapper=400 * self.game.screen_scale[0])
                elif key == "Weak":
                    item = self.show_equip_list[self.current_row]
                    if self.show_equip_list[self.current_row] == "Unequip":
                        item = None
                    if "item" in self.selected_equipment_slot:
                        self.profile["equipment"]["item"][self.selected_equipment_slot.split(" ")[1]] = item
                    else:
                        self.profile["equipment"][self.selected_equipment_slot] = item
                    self.total_equip_stat = self.check_total_equipment_stat(self.profile["equipment"])
                    self.change_equipment_list()
                elif key == "Order Menu":
                    self.change_mode("equipment")
                elif key == "Strong":  # open sort list
                    self.open_sub_menu(self.item_sort_list)
                elif key == "Guard":
                    self.add_remove_text_popup()
                    self.text_popup.popup(self.rect.topleft,
                                          (self.grab_text(("ui", "keybind_order_menu")) + " " +
                                           self.grab_text(("ui", "Button")) + " (" +
                                           self.game.player_key_bind_button_name[self.player]["Order Menu"] +
                                           "): " + self.grab_text(("ui", "equiplist_to_equip")),
                                           self.grab_text(("ui", "keybind_special")) + " " +
                                           self.grab_text(("ui", "Button")) + " (" +
                                           self.game.player_key_bind_button_name[self.player]["Special"] +
                                           "): " + self.grab_text(("ui", "Toggle total modifier")),
                                           self.grab_text(("ui", "keybind_weak_attack")) + " " +
                                           self.grab_text(("ui", "Button")) + " (" +
                                           self.game.player_key_bind_button_name[self.player]["Weak"] +
                                           "): " + self.grab_text(("ui", "equip_item")),
                                           self.grab_text(("ui", "keybind_strong_attack")) + " " +
                                           self.grab_text(("ui", "Button")) + " (" +
                                           self.game.player_key_bind_button_name[self.player]["Strong"] +
                                           "): " + self.grab_text(("ui", "sort_item"))),
                                          shown_id=key, width_text_wrapper=400 * self.game.screen_scale[0])

    def player_input_follower(self, key):
        if not self.input_delay:
            if self.mode == "follower":  # follower preset list
                if key in ("Up", "Down", "Left", "Right"):
                    self.input_delay = 0.25
                    if key == "Up":
                        self.current_row -= 1
                        if self.current_row < 0:
                            self.current_row = 3
                        self.add_follower_preset_list()
                    elif key == "Down":
                        self.current_row += 1
                        if self.current_row > 3:
                            self.current_row = 0
                        self.add_follower_preset_list()
                    elif key == "Left":
                        self.current_page -= 1
                        if self.current_page < 0:
                            self.current_page = 2
                        self.current_row = 0
                        self.add_follower_preset_list()
                    elif key == "Right":
                        self.current_page += 1
                        if self.current_page > 2:
                            self.current_page = 0
                        self.current_row = 0
                        self.add_follower_preset_list()
                else:
                    self.input_delay = 0.3
                    if key == "Special":  # popup follower description
                        self.add_remove_text_popup()
                        follower_list = ["Empty"]
                        if self.profile["follower preset"][self.current_row * (self.current_page + 1)]:
                            follower_list = []
                            for key, value in self.profile["follower preset"][
                                self.current_row * (self.current_page + 1)].items():
                                follower_list.append(
                                    self.grab_text(("character", key, "Name")) + " x" + str(value))
                        self.text_popup.popup(self.rect.topleft,
                                              follower_list,
                                              shown_id=follower_list,
                                              width_text_wrapper=400 * self.game.screen_scale[0])
                    elif key == "Strong":  # edit selected preset
                        self.current_follower_preset_num = self.current_row * (self.current_page + 1)
                        self.current_follower_preset = self.profile["follower preset"][self.current_follower_preset_num]
                        self.change_mode("follower_list")
                    elif key == "Weak":  # use this preset
                        self.profile["selected follower preset"] = self.current_row * (self.current_page + 1)
                        self.add_follower_preset_list()
                    elif key == "Inventory Menu":  # go to next page (storage)
                        self.change_mode("storage")
                    elif key == "Order Menu":  # go to previous page (equipment)
                        self.change_mode("equipment")
                    elif key == "Guard":
                        self.add_remove_text_popup()
                        self.text_popup.popup(self.rect.topleft,
                                              (self.grab_text(("ui", "keybind_inventory_menu")) + " " +
                                               self.grab_text(("ui", "Button")) + " (" +
                                               self.game.player_key_bind_button_name[self.player]["Inventory Menu"] +
                                               "): " + self.grab_text(("ui", "to_storage")),
                                               self.grab_text(("ui", "keybind_order_menu")) + " " +
                                               self.grab_text(("ui", "Button")) + " (" +
                                               self.game.player_key_bind_button_name[self.player]["Order Menu"] +
                                               "): " + self.grab_text(("ui", "to_equipment")),
                                               self.grab_text(("ui", "keybind_special")) + " " +
                                               self.grab_text(("ui", "Button")) + " (" +
                                               self.game.player_key_bind_button_name[self.player]["Special"] +
                                               "): " + self.grab_text(("ui", "Toggle description")),
                                               self.grab_text(("ui", "keybind_strong_attack")) + " " +
                                               self.grab_text(("ui", "Button")) + " (" +
                                               self.game.player_key_bind_button_name[self.player]["Strong"] +
                                               "): " + self.grab_text(("ui", "edit_preset")),
                                               self.grab_text(("ui", "keybind_weak_attack")) + " " +
                                               self.grab_text(("ui", "Button")) + " (" +
                                               self.game.player_key_bind_button_name[self.player]["Weak"] +
                                               "): " + self.grab_text(("ui", "use_preset"))),
                                              shown_id=key, width_text_wrapper=400 * self.game.screen_scale[0])

            else:  # follower list
                if key in ("Up", "Down", "Left", "Right"):
                    self.input_delay = 0.25
                    if key == "Up":
                        self.current_row -= 1
                        if self.current_row < 0:
                            self.current_row = len(self.profile["follower list"]) - 1
                        self.add_follower_list()
                    elif key == "Down":
                        self.current_row += 1
                        if self.current_row > len(self.profile["follower list"]) - 1:
                            self.current_row = 0
                        self.add_follower_list()
                    elif key == "Left":
                        if self.profile["follower list"][self.current_row] in self.current_follower_preset:
                            self.current_follower_preset[self.profile["follower list"][self.current_row]] -= 1
                            if not self.current_follower_preset[self.profile["follower list"][self.current_row]]:
                                self.current_follower_preset.pop(self.profile["follower list"][self.current_row])
                            self.add_follower_list()
                    elif key == "Right":
                        total_cost, total_melee, total_range = self.calculate_follower_stuff(
                            self.profile["follower preset"][self.current_follower_preset_num])
                        remain_fund = (self.max_follower_allowance - total_cost) - \
                                      self.game.character_data.character_list[
                                          self.profile["follower list"][self.current_row]][
                                          "Follower Cost"]
                        if remain_fund >= 0:  # can add follower since has enough fund
                            if self.profile["follower list"][self.current_row] in self.current_follower_preset:
                                if not self.game.character_data.character_list[
                                    self.profile["follower list"][self.current_row]][
                                    "Boss"]:
                                    # Boss follower can only be single follower
                                    self.current_follower_preset[self.profile["follower list"][self.current_row]] += 1
                            else:
                                self.current_follower_preset[self.profile["follower list"][self.current_row]] = 1
                        self.add_follower_list()
                else:
                    self.input_delay = 0.3
                    if key == "Special":  # popup follower description
                        self.add_remove_text_popup()
                        follower_stat = self.game.character_data.character_list[
                            self.profile["follower list"][self.current_row]]
                        stat = str(follower_stat["Strength"]) + "/" + str(follower_stat["Dexterity"]) + "/" + \
                               str(follower_stat["Agility"]) + "/" + str(follower_stat["Constitution"]) + "/" + \
                               str(follower_stat["Intelligence"]) + "/" + str(follower_stat["Wisdom"]) + "/" + \
                               str(follower_stat["Charisma"])
                        self.text_popup.popup(self.rect.topleft,
                                              (self.grab_text(
                                                  ("character", self.profile["follower list"][self.current_row],
                                                   "Name")),
                                               self.grab_text(
                                                   ("character", self.profile["follower list"][self.current_row],
                                                    "Description")),
                                               self.grab_text(("ui", "Base Stat")) + ": " + stat,
                                               self.grab_text(("ui", "Base Health")) + ": " +
                                               minimise_number_text(str(follower_stat["Base Health"])),
                                               self.grab_text(("ui", "Type")) + ": " + follower_stat[
                                                   "Type"]),
                                              shown_id=stat, width_text_wrapper=400 * self.game.screen_scale[0])
                    elif key == "Weak":
                        self.open_sub_menu(self.follower_clear_list)
                    elif key == "Strong":
                        self.open_sub_menu(self.follower_sort_list)
                    elif key == "Order Menu":  # go to previous page (equipment)
                        self.change_mode("follower")
                    elif key == "Guard":
                        self.add_remove_text_popup()
                        self.text_popup.popup(self.rect.topleft,
                                              (self.grab_text(("ui", "keybind_order_menu")) + " " +
                                               self.grab_text(("ui", "Button")) + " (" +
                                               self.game.player_key_bind_button_name[self.player]["Order Menu"] +
                                               "): " + self.grab_text(("ui", "list_to_follower_preset")),
                                               self.grab_text(("ui", "keybind_special")) + " " +
                                               self.grab_text(("ui", "Button")) + " (" +
                                               self.game.player_key_bind_button_name[self.player]["Special"] +
                                               "): " + self.grab_text(("ui", "Toggle description")),
                                               self.grab_text(("ui", "keybind_strong_attack")) + " " +
                                               self.grab_text(("ui", "Button")) + " (" +
                                               self.game.player_key_bind_button_name[self.player]["Strong"] +
                                               "): " + self.grab_text(("ui", "sort_follower")),
                                               self.grab_text(("ui", "keybind_weak_attack")) + " " +
                                               self.grab_text(("ui", "Button")) + " (" +
                                               self.game.player_key_bind_button_name[self.player]["Strong"] +
                                               "): " + self.grab_text(("ui", "clear_follower"))),
                                              shown_id=key, width_text_wrapper=400 * self.game.screen_scale[0])

    def player_input_storage(self, key):
        if not self.input_delay:
            if key in ("Up", "Down", "Left", "Right"):
                self.input_delay = 0.2
                if key == "Up":
                    if self.current_row - (60 * int(self.current_row / 60)) < 5:
                        self.current_row += 55
                    else:
                        self.current_row -= 5
                    self.change_storage_list()
                elif key == "Down":
                    if self.current_row - (60 * int(self.current_row / 60)) > 54:
                        self.current_row -= 55
                    else:
                        self.current_row += 5
                    self.change_storage_list()
                elif key == "Left":
                    page_row = self.current_row - (60 * int(self.current_row / 60))
                    if page_row in self.storage_first_row:
                        if self.max_page:  # has more than one page
                            self.base_image = None
                            if self.current_page == 0:  # go to last page
                                self.current_page = self.max_page
                                self.current_row += (64 * self.max_page)
                            else:
                                self.current_page -= 1
                                self.current_row -= 56
                        else:
                            self.current_row += 4
                    else:
                        self.current_row -= 1
                    self.change_storage_list()
                elif key == "Right":
                    page_row = self.current_row - (60 * int(self.current_row / 60))
                    if page_row in self.storage_last_row:
                        if self.max_page:  # has more than one page
                            self.base_image = None
                            if self.current_page == self.max_page:  # back to first
                                self.current_row -= ((60 * self.current_page) + 4)
                                self.current_page = 0
                            else:
                                self.current_page += 1
                                self.current_row += 56
                        else:  # go to opposite
                            self.current_row -= 4
                    else:
                        self.current_row += 1
                    self.change_storage_list()
            else:
                self.input_delay = 0.3
                if key == "Special":  # popup item description
                    self.add_remove_text_popup()
                    stat = ("Empty",)
                    try:
                        item = tuple(self.profile["storage"].keys())[self.current_row]
                        if item in self.game.character_data.equip_item_list:  # item type
                            stat = (self.grab_text(("item", item, "Name")),
                                    self.grab_text(("item", item, "Description")))
                        else:  # equipment type
                            if item in self.game.character_data.gear_list:
                                stat = self.get_equipment_description(item)

                            else:  # custom equipment
                                stat = self.get_custom_equipment_description(dict(item))
                    except IndexError:  # Empty slot
                        pass

                    self.text_popup.popup(self.rect.topleft, stat,
                                          shown_id=stat, width_text_wrapper=400 * self.game.screen_scale[0])
                elif key == "Strong":
                    self.open_sub_menu(self.item_sort_list)
                elif key == "Weak":
                    try:
                        var = tuple(self.profile["storage"].keys())[self.current_row]
                        self.open_sub_menu(self.storage_sell_list)
                    except KeyError:  # empty slot, not open sell menu
                        pass
                elif key == "Inventory Menu":  # go to next page (stat) or shop
                    if self.shop_list:
                        self.change_mode("shop")
                    else:
                        self.change_mode("stat")
                elif key == "Order Menu":  # go to previous page (follower) or shop
                    if self.shop_list:
                        self.change_mode("shop")
                    else:
                        self.change_mode("follower")
                elif key == "Guard":
                    self.add_remove_text_popup()
                    self.text_popup.popup(self.rect.topleft,
                                          (self.grab_text(("ui", "keybind_inventory_menu")) + " " +
                                           self.grab_text(("ui", "Button")) + " (" +
                                           self.game.player_key_bind_button_name[self.player]["Inventory Menu"] +
                                           "): " + self.grab_text(("ui", "storage_to_stat")),
                                           self.grab_text(("ui", "keybind_order_menu")) + " " +
                                           self.grab_text(("ui", "Button")) + " (" +
                                           self.game.player_key_bind_button_name[self.player]["Order Menu"] +
                                           "): " + self.grab_text(("ui", "storage_to_follower_preset")),
                                           self.grab_text(("ui", "keybind_special")) + " " +
                                           self.grab_text(("ui", "Button")) + " (" +
                                           self.game.player_key_bind_button_name[self.player]["Special"] +
                                           "): " + self.grab_text(("ui", "Toggle description")),
                                           self.grab_text(("ui", "keybind_strong_attack")) + " " +
                                           self.grab_text(("ui", "Button")) + " (" +
                                           self.game.player_key_bind_button_name[self.player]["Strong"] +
                                           "): " + self.grab_text(("ui", "sort_item")),
                                           self.grab_text(("ui", "keybind_weak_attack")) + " " +
                                           self.grab_text(("ui", "Button")) + " (" +
                                           self.game.player_key_bind_button_name[self.player]["Weak"] +
                                           "): " + self.grab_text(("ui", "sell_item"))),
                                          shown_id=key, width_text_wrapper=400 * self.game.screen_scale[0])

    def player_input_shop(self, key):
        if not self.input_delay:
            if key in ("Up", "Down", "Left", "Right"):
                self.input_delay = 0.25
                if key == "Up":
                    self.current_row -= 1
                    if self.current_row < 0:
                        self.current_row = len(self.shop_list) - 1
                    self.add_shop_list()
                elif key == "Down":
                    self.current_row += 1
                    if self.current_row > len(self.shop_list) - 1:
                        self.current_row = 0
                    self.add_shop_list()
                elif key == "Left":
                    if self.shop_list[self.current_row] in self.purchase_list:
                        self.purchase_list[self.shop_list[self.current_row]] -= 1
                        if not self.purchase_list[self.shop_list[self.current_row]]:
                            self.purchase_list.pop(self.shop_list[self.current_row])
                        self.add_shop_list()
                elif key == "Right":
                    total_cost = self.calculate_shop_cost()
                    remain_fund = (self.profile["total golds"] - total_cost) - \
                                  self.game.character_data.shop_list[self.shop_list[self.current_row]]["Value"]
                    if remain_fund >= 0:  # can add to purchase since enough gold left to purchase
                        if self.shop_list[self.current_row] in self.purchase_list:
                            self.purchase_list[self.shop_list[self.current_row]] += 1
                        else:
                            self.purchase_list[self.shop_list[self.current_row]] = 1
                    self.add_shop_list()
            else:
                self.input_delay = 0.3
                if key == "Special":  # popup item description
                    self.add_remove_text_popup()
                    stat = ("Empty",)
                    try:
                        item = self.shop_list[self.current_row]
                        if item in self.game.character_data.equip_item_list:  # item type
                            stat = (self.grab_text(("item", item, "Name")),
                                    self.grab_text(("item", item, "Description")))
                        else:  # equipment type
                            if item in self.game.character_data.gear_list:
                                stat = self.get_equipment_description(item)
                            else:  # custom equipment
                                stat = self.get_custom_equipment_description(dict(item))
                    except IndexError:  # Empty slot
                        pass

                    self.text_popup.popup(self.rect.topleft, stat,
                                          shown_id=stat, width_text_wrapper=400 * self.game.screen_scale[0])
                elif key == "Weak":  # open up purchase confirm
                    self.open_sub_menu(self.purchase_confirm_list)
                elif key == "Strong":  # open up purchase clear confirm
                    self.open_sub_menu(self.purchase_clear_confirm_list)
                elif key == "Order Menu" or key == "Inventory Menu":  # go to storage page
                    self.change_mode("storage")
                elif key == "Guard":
                    self.add_remove_text_popup()
                    self.text_popup.popup(self.rect.topleft,
                                          (self.grab_text(("ui", "keybind_order_menu")) + " " +
                                           self.grab_text(("ui", "Button")) + " (" +
                                           self.game.player_key_bind_button_name[self.player][
                                               "Order Menu"] + "): " + self.grab_text(
                                              ("ui", "to_storage")),
                                           self.grab_text(("ui", "keybind_inventory_menu")) + " " +
                                           self.grab_text(("ui", "Button")) + " (" +
                                           self.game.player_key_bind_button_name[self.player][
                                               "Inventory Menu"] + "): " + self.grab_text(
                                               ("ui", "to_storage")),
                                           self.grab_text(("ui", "keybind_special")) + " " +
                                           self.grab_text(("ui", "Button")) + " (" +
                                           self.game.player_key_bind_button_name[self.player]["Special"] +
                                           "): " + self.grab_text(("ui", "Toggle description")),
                                           self.grab_text(("ui", "keybind_weak_attack")) + " " +
                                           self.grab_text(("ui", "Button")) + " (" +
                                           self.game.player_key_bind_button_name[self.player]["Weak"] +
                                           "): " + self.grab_text(("ui", "purchase_item")),
                                           self.grab_text(("ui", "keybind_strong_attack")) + " " +
                                           self.grab_text(("ui", "Button")) + " (" +
                                           self.game.player_key_bind_button_name[self.player]["Strong"] +
                                           "): " + self.grab_text(("ui", "clear_purchase_item")),
                                           self.grab_text(("ui", "keybind_esc")) +
                                           ": " + self.grab_text(("ui", "close_shop"))
                                           ),
                                          shown_id=key, width_text_wrapper=400 * self.game.screen_scale[0])

    def player_input_reward(self, key):
        if not self.input_delay:
            if key in ("Up", "Down", "Left", "Right"):
                self.input_delay = 0.25
                if key == "Up":
                    self.current_row -= 1
                    if self.current_row < 0:
                        self.current_row = self.len_reward_list - 9
                    self.add_reward_list()
                elif key == "Down":
                    self.current_row += 1
                    if self.current_row > self.len_reward_list - 9:
                        self.current_row = 0
                    self.add_reward_list()
            else:
                self.input_delay = 0.3
                if key == "Guard":
                    self.add_remove_text_popup()
                    self.text_popup.popup(self.rect.topleft,
                                          (self.grab_text(("ui", "keybind_esc")) +
                                           ": " + self.grab_text(("ui", "close_reward"))
                                           ),
                                          shown_id=key, width_text_wrapper=400 * self.game.screen_scale[0])

    def player_input_enchant(self, key):
        if not self.input_delay:
            if key in ("Up", "Down", "Left", "Right"):
                self.input_delay = 0.25
                if key == "Up":
                    self.current_row -= 1
                    if self.current_row < 0:
                        self.current_row = len(self.all_custom_item) - 1
                    self.add_enchant_list()
                elif key == "Down":
                    self.current_row += 1
                    if self.current_row > len(self.all_custom_item) - 1:
                        self.current_row = 0
                    self.add_enchant_list()
            else:
                self.input_delay = 0.3
                if key == "Special":  # popup possible mod list
                    self.add_remove_text_popup()
                    stat = ("Empty",)
                    selected_equip = dict(self.all_custom_item[self.current_row])
                    mod_list = [self.grab_text(("gear_mod", key, "Name")) + ":" +
                                " - ".join([str(mod * 100) + "%" if mod < 1 else str(mod)
                                            for mod in value[selected_equip["Rarity"]]]) for
                                key, value in self.gear_mod_list[selected_equip["Type"].split(" ")[0]].items()]

                    self.text_popup.popup(self.rect.topleft, mod_list,
                                          shown_id=stat, width_text_wrapper=400 * self.game.screen_scale[0])
                elif key == "Weak":
                    remain_fund = self.profile["total golds"] - dict(self.all_custom_item[self.current_row])["Rework Cost"]
                    if remain_fund >= 0:
                        self.open_sub_menu(self.enchant_confirm_list)
                elif key == "Strong":
                    self.open_sub_menu(self.enchant_sort_list)
                elif key == "Guard":
                    self.add_remove_text_popup()
                    self.text_popup.popup(self.rect.topleft,
                                          (self.grab_text(("ui", "keybind_weak_attack")) + " " +
                                           self.grab_text(("ui", "Button")) + " (" +
                                           self.game.player_key_bind_button_name[self.player]["Weak"] +
                                           "): " + self.grab_text(("ui", "enchant_item")),
                                           self.grab_text(("ui", "keybind_strong_attack")) + " " +
                                           self.grab_text(("ui", "Button")) + " (" +
                                           self.game.player_key_bind_button_name[self.player]["Strong"] +
                                           "): " + self.grab_text(("ui", "sort_item")),
                                           self.grab_text(("ui", "keybind_special")) + " " +
                                           self.grab_text(("ui", "Button")) + " (" +
                                           self.game.player_key_bind_button_name[self.player]["Special"] +
                                           "): " + self.grab_text(("ui", "Toggle mod list")),
                                           self.grab_text(("ui", "keybind_esc")) +
                                           ": " + self.grab_text(("ui", "close_enchant"))
                                           ),
                                          shown_id=key, width_text_wrapper=400 * self.game.screen_scale[0])

    def get_equipment_description(self, item):
        stat = [self.grab_text(("gear", item, "Name")),
                self.grab_text(("gear", item, "Description")),
                "Rarity: " + self.grab_text(
                    ("ui", self.game.character_data.gear_list[item]["Rarity"])),
                self.grab_text(("ui", "Weight")) + ": " + str(self.game.character_data.gear_list[item]["Weight"])]
        for key, value in self.game.character_data.gear_list[item]["Modifier"].items():
            stat_str = str(value)
            if -1 < value < 1:  # convert percentage
                stat_str = str(value * 100) + "%"
            if "-" not in stat_str:
                stat_str = "+" + stat_str

            stat.append(self.grab_text(("gear_mod", key, "Name")) +
                        ": " + stat_str)
        return stat

    def get_custom_equipment_description(self, item):
        stat = [self.get_custom_equipment_name(item),
                self.grab_text(("ui", "Rarity")) +": " + self.grab_text(("ui", item["Rarity"])),
                self.grab_text(("ui", "Weight")) +": " + str(item["Weight"])]
        for key, value in dict(item["Modifier"]).items():
            stat_str = str(value)
            if value < 1:  # convert percentage
                stat_str = str(value * 100) + "%"
            if "-" not in stat_str:
                stat_str = "+" + stat_str
            stat.append(self.grab_text(("gear_mod", key, "Name")) +
                        ": " + stat_str)
        return stat

    def get_custom_equipment_name(self, item):
        return self.grab_text(("gear_rarity", item["Rarity"], "Name")).split(",")[item["Name"][0]] + " " + \
               self.grab_text(("gear_preset", self.profile["character"]["ID"], item["Type"])) + " " + \
               self.grab_text(("gear_mod", item["Name"][1], "Suffix")).split(",")[rarity_mod_number[item["Rarity"]] - 1]


class ControllerIcon(UIMenu):
    def __init__(self, pos, images, control_type):
        UIMenu.__init__(self)
        self.pos = pos
        self.font = Font(self.ui_font["main_button"], int(46 * self.screen_scale[1]))
        self.images = images
        self.image = self.images[control_type].copy()
        self.rect = self.image.get_rect(center=self.pos)
        self.player = 1
        self.control_type = control_type

    def change_control(self, control_type, player):
        self.player = player
        self.control_type = control_type
        if "joystick" in control_type:
            self.image = self.images[control_type[:-1]].copy()
            number_after = "J" + control_type[-1]
        else:
            self.image = self.images[control_type]
            number_after = ""
        text_surface = text_render_with_bg("P" + str(self.player) + number_after, self.font, gf_colour=(150, 100, 0),
                                           o_colour=(255, 255, 0))
        text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)


class KeybindIcon(UIMenu):
    controller_icon = {}

    def __init__(self, pos, text_size, control_type, key):
        UIMenu.__init__(self)
        self.font = Font(self.ui_font["main_button"], text_size)
        self.pos = pos
        self.change_key(control_type, key, keybind_name=None)
        self.rect = self.image.get_rect(center=self.pos)

    def change_key(self, control_type, key, keybind_name):
        if control_type == "keyboard":
            if type(key) is str and "click" in key:
                self.draw_keyboard(key)
            else:
                self.draw_keyboard(pygame.key.name(key))
        else:
            self.draw_joystick(key, keybind_name)
        self.rect = self.image.get_rect(center=self.pos)

    def draw_keyboard(self, text):
        text_surface = self.font.render(text, True, (30, 30, 30))
        size = text_surface.get_size()
        image_size = size[0] * 2
        if size[0] < 40:
            image_size = size[0] * 4
        self.image = Surface((image_size, size[1] * 2), SRCALPHA)
        draw.rect(self.image, (50, 50, 50), (0, 0, image_size, size[1] * 2), border_radius=2)
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


class MapTitle(UIMenu):
    def __init__(self, pos):
        UIMenu.__init__(self)

        self.font = Font(self.ui_font["name_font"], int(44 * self.screen_scale[1]))
        self.pos = pos
        self.name = ""
        text_surface = self.font.render(str(self.name), True, (30, 30, 30))
        self.image = pygame.Surface((int(text_surface.get_width() + (5 * self.screen_scale[0])),
                                     int(text_surface.get_height() + (5 * self.screen_scale[1]))))

    def change_name(self, name):
        self.name = name
        text_surface = self.font.render(str(self.name), True, (30, 30, 30))
        self.image = pygame.Surface((int(text_surface.get_width() + (5 * self.screen_scale[0])),
                                     int(text_surface.get_height() + (5 * self.screen_scale[1]))))
        self.image.fill((30, 30, 30))

        white_body = pygame.Surface((text_surface.get_width(), text_surface.get_height()))
        white_body.fill((239, 228, 176))
        white_rect = white_body.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(white_body, white_rect)

        text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)
        self.rect = self.image.get_rect(midtop=self.pos)


class NameTextBox(UIMenu):
    def __init__(self, box_size, pos, name, text_size=26, layer=15, box_colour=(220, 220, 220),
                 corner_colour=(30, 30, 30), center_text=False):
        self._layer = layer
        UIMenu.__init__(self)
        self.font = Font(self.ui_font["main_button"], int(text_size * self.screen_scale[1]))
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
            text_rect = text_surface.get_rect(midleft=(int(text_size * self.screen_scale[1]),
                                                       self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)

        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)

    def rename(self, new_name):
        self.name = new_name
        self.image = self.image_base.copy()
        text_surface = self.font.render(self.name, True, (30, 30, 30))
        text_rect = text_surface.get_rect(midleft=(int(3 * self.screen_scale[0]), self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)


class ListBox(UIMenu):
    def __init__(self, pos, image, layer=14):
        self._layer = layer
        UIMenu.__init__(self, player_cursor_interact=False)
        self.image = image.copy()
        self.name_list_start = (self.image.get_width(), self.image.get_height())
        self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)

        image_height = int(26 * self.screen_scale[1])
        self.max_row_show = int(
            self.image.get_height() / (
                    image_height + (6 * self.screen_scale[1])))  # max number of map on list can be shown


class NameList(UIMenu):
    def __init__(self, box, pos, name, text_size=26, layer=15):
        self._layer = layer
        UIMenu.__init__(self)
        self.font = Font(self.ui_font["main_button"], int(self.screen_scale[1] * text_size))
        self.name = str(name)

        self.image = Surface(
            (box.image.get_width() - int(18 * self.screen_scale[0]),
             int((text_size + 4) * self.screen_scale[1])))  # black corner
        self.image.fill((30, 30, 30))
        self.selected_image = self.image.copy()
        self.selected = False

        # White body square
        small_image = Surface(
            (box.image.get_width() - int(16 * self.screen_scale[0]), int((text_size + 2) * self.screen_scale[1])))
        small_image.fill((220, 220, 220))
        small_rect = small_image.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(small_image, small_rect)
        small_image.fill((255, 255, 128))
        self.selected_image.blit(small_image, small_rect)

        self.image_base = self.image.copy()

        # Name text
        text_surface = self.font.render(self.name, True, (30, 30, 30))
        text_rect = text_surface.get_rect(midleft=(int(3 * self.screen_scale[0]), self.image.get_height() / 2))
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
        text_rect = text_surface.get_rect(midleft=(int(3 * self.screen_scale[0]), self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)
        self.selected_image.blit(text_surface, text_rect)

        self.not_selected_image = self.image.copy()


class ListAdapter:
    def __init__(self, _list, replace_on_select=None, replace_on_mouse_over=None):
        from engine.game.game import Game
        self.game = Game.game
        self.list = _list
        self.last_index = -1
        if replace_on_select:
            self.on_select = types.MethodType(replace_on_select, self)
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

    def on_mouse_over(self, item_index, item_text):
        pass

    def get_highlighted_index(self):
        return self.last_index


class ListAdapterHideExpand(ListAdapter):

    # actual list refer to the origin full list
    # visual list refer to the list after some if any of the elements been hidden

    def __init__(self, _list, _self=None, replace_on_select=None, replace_on_mouse_over=None):
        self.actual_list = actual_list = [c[1] for c in _list]
        self.actual_list_open_index = [False for element in actual_list]
        self.actual_list_level = [element[0] for element in _list]

        if replace_on_select:
            self.on_select = types.MethodType(replace_on_select, self)
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


class TickBox(UIMenu):
    def __init__(self, pos, image, tick_image, option):
        """option is in str text for identifying what kind of tick_box it is"""
        self._layer = 14
        UIMenu.__init__(self)

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
    def __init__(self):
        self._layer = 30
        UIMenu.__init__(self, player_cursor_interact=False)
        self.font_size = int(24 * self.screen_scale[1])
        self.font = Font(self.ui_font["main_button"], self.font_size)
        self.pos = (0, 0)
        self.last_shown_id = None
        self.text_input = ""

    def popup(self, popup_rect, text_input, shown_id=None, width_text_wrapper=None, custom_screen_size=None):
        """Pop out text box with input text list in multiple line, one item equal to one paragraph"""
        self.last_shown_id = shown_id

        if text_input is not None and (self.text_input != text_input or self.last_shown_id != shown_id):
            self.text_input = text_input
            if type(text_input) == str:
                self.text_input = [text_input]
            text_surface = []
            if width_text_wrapper:  # has specific popup width size
                max_height = 0
                max_width = width_text_wrapper
                for text in self.text_input:
                    image_height = int((self.font.render(text, True, (0, 0, 0)).get_width()) / width_text_wrapper)
                    if not image_height:  # only one line
                        text_image = Surface((width_text_wrapper, self.font_size))
                        text_image.fill((220, 220, 220))
                        surface = self.font.render(text, True, (30, 30, 30))
                        text_image.blit(surface, (self.font_size, 0))
                        text_surface.append(text_image)  # text input font surface
                        max_height += surface.get_height()
                    else:
                        # Find new image height, using code from make_long_text
                        x, y = (self.font_size, self.font_size)
                        words = [word.split(" ") for word in
                                 str(text).splitlines()]  # 2D array where each row is a list of words
                        space = self.font.size(" ")[0]  # the width of a space
                        for line in words:
                            for word in line:
                                word_surface = self.font.render(word, True, (30, 30, 30))
                                word_width, word_height = word_surface.get_size()
                                if x + word_width >= max_width:
                                    x = self.font_size  # reset x
                                    y += word_height  # start on new row.
                                x += word_width + space
                            x = self.font_size  # reset x
                            y += word_height  # start on new row
                        text_image = Surface((width_text_wrapper, y))
                        text_image.fill((220, 220, 220))
                        make_long_text(text_image, text, (self.font_size, self.font_size), self.font,
                                       specific_width=width_text_wrapper)
                        text_surface.append(text_image)
                        max_height += text_image.get_height()
            else:
                max_width = 0
                max_height = 0
                for text in self.text_input:
                    surface = self.font.render(text, True, (30, 30, 30))
                    text_surface.append(surface)  # text input font surface
                    text_rect = surface.get_rect(
                        topleft=(self.font_size, self.font_size))  # text input position at (1,1) on white box image
                    if text_rect.width > max_width:
                        max_width = text_rect.width
                    max_height += self.font_size + int(self.font_size / 5)

            self.image = Surface((max_width, max_height))  # white Box
            self.image.fill((220, 220, 220))

            height = 0
            for surface in text_surface:
                text_rect = surface.get_rect(topleft=(0, height))
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
            self.rect = self.image.get_rect(topleft=popup_rect)


class BoxUI(UIMenu, Containable, Container):

    def __init__(self, size, parent):
        UIMenu.__init__(self, player_cursor_interact=False)
        self.parent = parent
        self.size = size
        self._layer = -1
        self.pos = (0, 0)
        self.rect = self.get_adjusted_rect_to_be_inside_container(self.parent)
        self.image = Surface(self.rect[2:], SRCALPHA)
        # self.image.fill("#302d2ce0")

    def update(self):
        self.rect = self.get_adjusted_rect_to_be_inside_container(self.parent)
        self.image = Surface(self.rect[2:], SRCALPHA)
        # self.image.fill("#bbbbaabb")

    def get_relative_size_inside_container(self):
        return (0.3, 0.5)

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

    @classmethod
    def get_frame(cls):
        from engine.game.game import Game
        game = Game.game
        if cls._frame is None:
            frame_file = "new_button.png"  # "list_frame.png" # using the button frame to test if it looks good
            cls._frame = load_image(game.data_dir, (1, 1), frame_file, ("ui", "mainmenu_ui"))
        return cls._frame

    @classmethod
    def get_scroll_box_frame(cls):
        from engine.game.game import Game
        game = Game.game
        if cls._scroll_box_frame is None:
            cls._scroll_box_frame = load_image(game.data_dir, (1, 1), "scroll_box_frame.png", ("ui", "mainmenu_ui"))
        return cls._scroll_box_frame

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
        return None

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

        self.image = ListUI.inner_get_refreshed_image(
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

    @classmethod
    @lru_cache(
        maxsize=2 ** 4)  # size has to be big enough to fit all active list ui on screen but not big enough to take too much memory
    def inner_get_refreshed_image(cls, scroll_box_index, rect, items, selected_index, highlighted_index, in_scroll_box,
                                  hold_scroll_box, item_size):
        from engine.game.game import Game

        ui_font = Game.ui_font

        if not type(scroll_box_index) == int:
            raise TypeError()
        if not type(rect) == tuple:
            raise TypeError()
        if not type(items) == tuple:
            raise TypeError(items)
        if not type(selected_index) in (type(None), int):
            raise TypeError(type(selected_index))
        if not type(highlighted_index) in (int, type(None)):
            raise TypeError(highlighted_index)
        if not type(in_scroll_box) == bool:
            raise TypeError()
        if not type(hold_scroll_box) in (type(None), int):
            raise TypeError(hold_scroll_box)

        has_scroll = cls.get_has_scroll(items, item_size)

        scroll_bar_height = cls.get_scroll_bar_height_by_rect(rect)
        scroll_box_size = cls.get_scroll_box_size(scroll_bar_height, item_size, len(items))
        scroll_box_height = scroll_box_size[1]
        number_of_items_outside_visible_list = cls.get_number_of_items_outside_visible_list(items, item_size)
        scroll_step_height = cls.get_scroll_step_height(scroll_bar_height, scroll_box_height,
                                                        number_of_items_outside_visible_list)
        scroll_bar_rect = cls.get_scroll_bar_rect(has_scroll, rect, scroll_bar_height)
        scroll_box_rect = cls.get_scroll_box_rect(has_scroll, rect, scroll_box_index, scroll_step_height,
                                                  scroll_box_size)
        item_height = cls.get_item_height(scroll_bar_height, item_size)

        rect = pygame.Rect(*rect)
        scroll_bar_rect = pygame.Rect(*scroll_bar_rect) if scroll_bar_rect else None
        scroll_box_rect = pygame.Rect(*scroll_box_rect) if scroll_box_rect else None
        if scroll_box_rect:
            scroll_box = make_image_by_frame(cls.get_scroll_box_frame(), scroll_box_rect[2:])

        font1 = Font(ui_font["text_paragraph"], int(20 * Game.screen_scale[1]))
        font2 = Font(ui_font["text_paragraph"], int(16 * Game.screen_scale[1]))
        font3 = Font(ui_font["text_paragraph"], int(12 * Game.screen_scale[1]))

        assert type(scroll_box_index) == int, type(scroll_box_index)
        size = rect[2:]

        image = make_image_by_frame(cls.get_frame(), size)
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
                          (6, 6 + i * item_height, size[0] - 13 * has_scroll - 12, item_height))

            if item_index < 0:
                continue
            if item_index >= len(items):
                continue
            blit_text = items[item_index]

            # TODO: big optimize is not to render text that is not visible below

            font = font1
            if items[item_index] is not None:  # assuming list ui has only 3 levels
                if ">>" in items[item_index] or "||" in items[item_index]:
                    font = font2
                    blit_text = "  " + blit_text
                elif ">" in items[item_index] or "|" in items[item_index]:
                    font = font3
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

    def update(self):
        if self.pause:
            return

        cls = ListUI
        mouse_pos = self.cursor.pos
        relative_mouse_pos = [mouse_pos[i] - self.rect[i] for i in range(2)]

        scroll_bar_height = self.get_scroll_bar_height_by_rect(self.rect)
        self.scroll_box_height = self.get_scroll_box_height(scroll_bar_height, self.items, self.visible_list_capacity)

        scroll_bar_height = self.get_scroll_bar_height_by_rect(self.rect)
        has_scroll = self.get_has_scroll(self.items, self.visible_list_capacity)
        scroll_box_size = self.get_scroll_box_size(scroll_bar_height, self.visible_list_capacity, len(self.items))
        number_of_items_outside_visible_list = cls.get_number_of_items_outside_visible_list(self.items,
                                                                                            self.visible_list_capacity)

        scroll_step_height = cls.get_scroll_step_height(scroll_bar_height, self.scroll_box_height,
                                                        number_of_items_outside_visible_list)

        # detect what cursor is over
        in_list = False
        self.mouse_over = False
        self.in_scroll_box = False
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
            in_list = True
            if scroll_bar_rect := self.get_scroll_bar_rect(has_scroll, self.rect, scroll_bar_height):
                if scroll_bar_rect.collidepoint(relative_mouse_pos):
                    if self.get_scroll_box_rect(has_scroll, self.rect, self.scroll_down_index, scroll_step_height,
                                                scroll_box_size).collidepoint(relative_mouse_pos):
                        self.in_scroll_box = True
                    in_list = False
            if self.cursor.scroll_up:
                self.scroll_down_index -= 1
                if self.scroll_down_index < 0:
                    self.scroll_down_index = 0
            elif self.cursor.scroll_down:
                self.scroll_down_index += 1
                noiovl = self.get_number_of_items_outside_visible_list(self.items, self.visible_list_capacity)
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
            if self.cursor.is_select_just_up or self.cursor.is_alt_select_just_up:
                self.items.on_select(self.hover_index, self.items[self.hover_index])
                self.cursor.is_select_just_up = False
                self.cursor.is_alt_select_just_up = False

        # handle hold and release of the scroll box
        if not self.cursor.is_select_down:
            self.hold_scroll_box = None
        if self.in_scroll_box and self.cursor.is_select_just_down:
            self.hold_scroll_box = relative_mouse_pos[1]
            self.scroll_down_index_at_grab = self.scroll_down_index

        # handle dragging of the scroll box
        if self.hold_scroll_box:
            self.scroll_down_index = self.scroll_down_index_at_grab + int(
                (relative_mouse_pos[1] - self.hold_scroll_box + scroll_step_height / 2) / scroll_step_height)
            noiovl = self.get_number_of_items_outside_visible_list(self.items, self.visible_list_capacity)
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
