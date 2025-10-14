import types
from functools import lru_cache

import pygame
import pyperclip
from pygame import Surface, SRCALPHA, Rect, Color, draw, mouse
from pygame.font import Font
from pygame.sprite import Sprite

from engine.utils.common import keyboard_mouse_press_check
from engine.utils.data_loading import load_image
from engine.utils.text_making import text_render_with_bg, make_long_text

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
        self.event_alt_press = False
        self.event_alt_hold = False
        self.mouse_over = False
        self.pause = False

    def update(self):
        self.event = False
        self.event_press = False
        self.event_hold = False  # some UI differentiates between press release or holding, if not just use event
        self.event_alt_press = False
        self.event_alt_hold = False
        self.mouse_over = False
        if self.player_interact and not self.pause:
            if self.rect.collidepoint(self.cursor.pos):
                self.mouse_over = True
                self.cursor.mouse_over = True
                if self.cursor.is_select_just_up:
                    self.event_press = True
                    self.cursor.is_select_just_up = False  # reset select button to prevent overlap interaction
                elif self.cursor.is_select_down:
                    self.event_hold = True
                    self.cursor.is_select_just_down = False  # reset select button to prevent overlap interaction

                elif self.cursor.is_alt_select_just_up:
                    self.event_alt_press = True
                    self.cursor.is_alt_select_just_up = False  # reset select button to prevent overlap interaction
                elif self.cursor.is_alt_select_down:
                    self.event_alt_hold = True
                    self.cursor.is_alt_select_just_down = False  # reset select button to prevent overlap interaction


class MenuCursor(UIMenu):
    def __init__(self, images):
        """Game menu cursor"""
        self._layer = 999999999999  # as high as possible, always blit last
        UIMenu.__init__(self, player_cursor_interact=False)
        self.images = images
        self.image = images["normal"]
        self.current_image = "normal"
        self.pos = (0, 0)
        self.is_select_just_down = False
        self.is_select_down = False
        self.is_select_just_up = False
        self.is_alt_select_just_down = False
        self.is_alt_select_down = False
        self.is_alt_select_just_up = False
        self.scroll_up = False
        self.scroll_down = False
        self.rect = self.image.get_rect(topleft=self.pos)
        self.shown = True

    def update(self):
        """Update cursor position based on mouse position and mouse button click"""
        self.pos = mouse.get_pos()
        self.rect.topleft = self.pos
        self.mouse_over = False
        self.is_select_just_down, self.is_select_down, self.is_select_just_up = keyboard_mouse_press_check(
            mouse, 0, self.is_select_just_down, self.is_select_down, self.is_select_just_up)

        # Alternative select press button, like mouse right
        self.is_alt_select_just_down, self.is_alt_select_down, self.is_alt_select_just_up = keyboard_mouse_press_check(
            mouse, 2, self.is_alt_select_just_down, self.is_alt_select_down, self.is_alt_select_just_up)

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
        self.font = Font(self.ui_font["main_button"], int(96 * self.screen_scale[1]))
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
        self.font = Font(self.ui_font["main_button"], int(60 * self.screen_scale[1]))
        self.pos = pos
        self.image = Surface((width - 10, int(68 * self.screen_scale[1])))
        self.max_text = int((self.image.get_width() / int(60 * self.screen_scale[1])) * 2)
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

        self.font = Font(self.ui_font["main_button"], int(72 * self.screen_scale[1]))
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
    def __init__(self, images, pos, key_name="", font_size=56, layer=1):
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
            text_rect = text_surface.get_rect(center=(self.button_normal_image.get_width() / 2,
                                                      self.button_normal_image.get_height() / 2))
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

    def __init__(self, pos, key_name="", parent=None):
        self._layer = 100
        UIMenu.__init__(self)
        self.pos = pos
        self.parent = parent
        self.key_name = key_name
        self.rect = self.get_adjusted_rect_to_be_inside_container(self.parent)
        self.mouse_over = False
        self.event = False
        self.font = Font(self.ui_font["main_button"], int(48 * self.screen_scale[1]))
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
        return normal_button, hover_button

    def get_relative_size_inside_container(self):
        return (.5, .1)

    def refresh(self):
        self.image = self.images[0]
        if self.mouse_over:
            self.image = self.images[1]

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
        self._layer = 10
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


class CharacterSelector(UIMenu):
    def __init__(self, pos, images):
        UIMenu.__init__(self, player_cursor_interact=False)
        self.pos = pos
        self.images = images
        self.mode = "empty"
        self.image = self.images[self.mode]
        self.rect = self.image.get_rect(topleft=self.pos)

    def change_mode(self, mode, delay=True):
        if mode != "ready":
            self.image = self.images["empty"]
        else:
            self.image = self.images["ready"]
        self.mode = mode


# class RewardInterface(UIMenu):
#     def __init__(self, pos, base_image):
#         self.header_font = Font(self.ui_font["main_button"], int(36 * self.screen_scale[1]))
#         self.font = Font(self.ui_font["main_button"], int(22 * self.screen_scale[1]))
#         self.small_font = Font(self.ui_font["main_button"], int(18 * self.screen_scale[1]))
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
#                               (0, (row_index * 100) * self.screen_scale[1], 400 * self.screen_scale[0],
#                                100 * self.screen_scale[1]),
#                               width=int(3 * self.screen_scale[0]))
#
#                 if index == self.len_reward_list - 1:  # last item in list
#                     draw.rect(self.image, (150, 50, 50),
#                               (0, (row_index * 100) * self.screen_scale[1], 400 * self.screen_scale[0],
#                                100 * self.screen_scale[1]),
#                               width=int(3 * self.screen_scale[0]))
#
#                 if item in self.game.character_data.character_list:  # follower reward
#                     portrait = self.game.animation_data.character_portraits[item]
#                     rect = portrait.get_rect(topleft=(0, row_index * 100 * self.screen_scale[1]))
#                     self.image.blit(portrait, rect)
#                     make_long_text(self.image, self.grab_text(("character", item, "Name")),
#                                    (110 * self.screen_scale[0],
#                                     row_index * 100 * self.screen_scale[1]), self.font, color=(30, 30, 30),
#                                    specific_width=self.image.get_width() - (50 * self.screen_scale[0]))
#
#                     item_image = self.item_sprite_pool["Normal"][item_id]
#                     rect = item_image.get_rect(topleft=(0, row_index * 100 * self.screen_scale[1]))
#                     self.image.blit(item_image, rect)
#
#                 self.shown_reward_list.append((reward_type, item))
#
#                 row_index += 1
#
#             index += 1


class CharacterInterface(UIMenu):
    base_image = None

    def __init__(self, pos, player, text_popup):
        UIMenu.__init__(self)
        self.header_font = Font(self.ui_font["main_button"], int(36 * self.screen_scale[1]))
        self.font = Font(self.ui_font["main_button"], int(22 * self.screen_scale[1]))
        self.small_font = Font(self.ui_font["main_button"], int(18 * self.screen_scale[1]))
        self.current_select = 0
        self.input_delay = 0
        self.pos = pos
        self.player = player
        self.mode = "empty"
        self.text_popup = text_popup

        self.portrait_list_rects = {}

        guard_button = pygame.key.name(self.game.player_key_bind_list["Guard"])

        text_surface = text_render_with_bg(self.localisation.grab_text(("ui", "press")) + " " + guard_button + " " +
                                           self.localisation.grab_text(("ui", "help")),
                                           self.font, Color("black"))

        button_image = self.game.battle_ui_images["button_guard"]
        helper_image = Surface((button_image.get_width() + (5 * self.screen_scale[0]) +
                                text_surface.get_width(), button_image.get_height()), SRCALPHA)
        text_rect = text_surface.get_rect(topright=(helper_image.get_width(), 0))
        helper_image.blit(text_surface, text_rect)
        button_rect = button_image.get_rect(topleft=(0, 0))
        helper_image.blit(button_image, button_rect)
        helper_image_rect = helper_image.get_rect(topleft=(0, 680 * self.screen_scale[1]))
        self.base_image = Surface((800 * self.screen_scale[0], 750 * self.screen_scale[1]), SRCALPHA)
        self.base_image.blit(helper_image, helper_image_rect)

        text_surface = text_render_with_bg(self.localisation.grab_text(("ui", "Player")) + str(self.player) + ": ",
                                           self.header_font, Color("black"))
        text_rect = text_surface.get_rect(topleft=(0, 0))
        self.base_image.blit(text_surface, text_rect)
        self.image = self.base_image.copy()

        self.rect = self.image.get_rect(topleft=self.pos)
        self.change_mode("empty")

    def remake(self):
        if self.game.config["USER"]["control player " + str(self.player)] == "joystick":
            name_list = self.game.joystick_bind_name[self.game.joystick_name[self.game.player_joystick[self.player]]]
            guard_button = self.game.player_key_bind_list[self.player]["joystick"]["Guard"]
            guard_button = name_list[guard_button]
        else:
            guard_button = pygame.key.name(self.game.player_key_bind_list[self.player]["keyboard"]["Guard"])

        text_surface = text_render_with_bg(self.localisation.grab_text(("ui", "press")) + " " + guard_button + " " +
                                           self.localisation.grab_text(("ui", "help")),
                                           self.font, Color("black"))

        button_image = self.game.battle_ui_images["button_guard"]
        helper_image = Surface((button_image.get_width() + (5 * self.screen_scale[0]) +
                                text_surface.get_width(), button_image.get_height()), SRCALPHA)
        text_rect = text_surface.get_rect(topright=(helper_image.get_width(), 0))
        helper_image.blit(text_surface, text_rect)
        button_rect = button_image.get_rect(topleft=(0, 0))
        helper_image.blit(button_image, button_rect)
        helper_image_rect = helper_image.get_rect(topleft=(0, 680 * self.screen_scale[1]))
        self.base_image = Surface((800 * self.screen_scale[0], 750 * self.screen_scale[1]), SRCALPHA)
        self.base_image.blit(helper_image, helper_image_rect)

        text_surface = text_render_with_bg(self.localisation.grab_text(("ui", "Player")) + str(self.player) + ": ",
                                           self.header_font, Color("black"))
        text_rect = text_surface.get_rect(topleft=(0, 0))
        self.base_image.blit(text_surface, text_rect)
        self.image = self.base_image.copy()
        self.change_mode("empty")

    def update(self):
        if self.input_delay > 0:
            self.input_delay -= self.game.true_dt
            if self.input_delay < 0:
                self.input_delay = 0

    def change_portrait_list(self):
        self.input_delay = 0.15
        self.image = self.base_image.copy()
        current_list = {"character": self.character_list, "followers": self.followers_list}[self.mode]
        if self.current_select == -1:
            self.current_select = len(current_list) - 1
        elif self.current_select < 0:
            self.current_select += (int(len(current_list) / 4) * 4) + 4
        elif self.current_select == len(current_list):
            self.current_select = 0
        elif self.current_select > len(current_list):
            self.current_select -= (int(len(current_list) / 4) * 4) + 4
        if self.mode == "character":
            self.make_character_list()
            if self.character_list[self.current_select] in self.game.save_data.save_profile["new"]["character"]:
                self.game.save_data.save_profile["new"]["character"].remove(self.character_list[self.current_select])
        else:
            self.make_followers_list()
            if self.followers_list[self.current_select] in self.game.save_data.save_profile["new"]["followers"]:
                self.game.save_data.save_profile["new"]["followers"].remove(self.followers_list[self.current_select])

    def change_mode(self, mode):
        self.input_delay = 0.3
        self.mode = mode
        self.current_select = 0
        self.game.remove_ui_updater(self.text_popup)
        self.image = self.base_image.copy()
        if self.mode == "character":
            self.make_character_list()
        elif self.mode == "empty":
            weak_button = pygame.key.name(self.game.player_key_bind_list["Confirm"])

            text_surface = text_render_with_bg(self.localisation.grab_text(("ui", "press")) + " " + weak_button + " " +
                                               self.localisation.grab_text(("ui", "to_join")),
                                               self.header_font, Color("black"))
            text_rect = text_surface.get_rect(topleft=(150 * self.screen_scale[0], 0))
            self.image.blit(text_surface, text_rect)
        elif self.mode == "followers":
            self.make_followers_list()

    def make_character_list(self):
        self.character_list = [item for item in self.game.save_data.save_profile["favourite"]["character"]]
        self.character_list += [item for item in self.game.start_playable_character if item not in self.character_list]
        self.character_list += [item for item in self.game.save_data.save_profile["unlock"]["character"] if
                                item not in self.character_list]
        self.portrait_list_rects = {}
        start = 0
        max_number = 12
        if len(self.character_list) < max_number:
            max_number = len(self.character_list)
        elif self.current_select > 11:
            start = int(self.current_select / 4) * 4
            max_number = start + 12
            if len(self.character_list) < max_number:
                max_number = len(self.character_list)
        true_count = 0
        count = 0
        start_x = 20 * self.screen_scale[0]
        start_y = 100 * self.screen_scale[1]
        x = start_x
        y = start_y
        for number in range(start, max_number):
            self.portrait_list_rects[true_count] = self.game.sprite_data.character_portraits[
                self.character_list[number]].get_rect(topleft=(x, y))
            if number == self.current_select:
                draw.circle(self.image, (140, 140, 220), self.portrait_list_rects[true_count].center,
                            90 * self.screen_scale[0])
            elif self.character_list[number] in self.game.save_data.save_profile["favourite"][self.player]["character"]:
                draw.circle(self.image, (220, 140, 140), self.portrait_list_rects[true_count].center,
                            90 * self.screen_scale[0])
            self.image.blit(self.game.sprite_data.character_portraits[self.character_list[number]],
                            self.portrait_list_rects[number])
            count += 1
            true_count += 1
            x += 180 * self.screen_scale[0]
            if count == 4:
                x = start_x
                y += 180 * self.screen_scale[1]
                count = 0

        text_surface = text_render_with_bg(self.localisation.grab_text(("character",
                                                                        self.character_list[self.current_select],
                                                                        "Name")),
                                           self.header_font, Color("black"))
        text_rect = text_surface.get_rect(topleft=(150 * self.screen_scale[0], 0))
        self.image.blit(text_surface, text_rect)

    def make_followers_list(self):
        self.followers_list = [item for item in self.game.save_data.save_profile["favourite"][self.player]["followers"]]
        self.followers_list += [item for item in self.game.start_followers if item not in self.followers_list]
        self.followers_list += [item for item in self.game.save_data.save_profile["unlock"]["followers"] if
                                item not in self.followers_list]
        self.portrait_list_rects = {}
        start = 0
        max_number = 12
        if len(self.followers_list) < max_number:
            max_number = len(self.followers_list)
        elif self.current_select > 11:
            start = int(self.current_select / 4) * 4
            max_number = start + 12
            if len(self.followers_list) < max_number:
                max_number = len(self.followers_list)
        true_count = 0
        count = 0
        start_x = 20 * self.screen_scale[0]
        start_y = 100 * self.screen_scale[1]
        x = start_x
        y = start_y
        for number in range(start, max_number):
            if self.followers_list[number] == "None":
                portrait = self.game.sprite_data.character_portraits[self.followers_list[number]]
            else:
                # Use first follower character in data as portrait
                portrait = \
                    tuple(self.game.character_data.followers_list[self.followers_list[number]]["Followers"].keys())[0]
                portrait = self.game.sprite_data.character_portraits[portrait]
            self.portrait_list_rects[true_count] = portrait.get_rect(topleft=(x, y))
            if number == self.current_select:
                draw.circle(self.image, (140, 140, 220), self.portrait_list_rects[true_count].center,
                            90 * self.screen_scale[0])
            elif self.followers_list[number] in self.game.save_data.save_profile["favourite"][self.player]["followers"]:
                draw.circle(self.image, (220, 140, 140), self.portrait_list_rects[true_count].center,
                            90 * self.screen_scale[0])
            self.image.blit(portrait, self.portrait_list_rects[number])
            count += 1
            true_count += 1
            x += 180 * self.screen_scale[0]
            if count == 4:
                x = start_x
                y += 180 * self.screen_scale[1]
                count = 0

        text_surface = text_render_with_bg(self.localisation.grab_text(("character",
                                                                        self.game.player_char_select[self.player][
                                                                            "character"],
                                                                        "Name")) + " + " +
                                           self.localisation.grab_text(("followers",
                                                                        self.followers_list[self.current_select],
                                                                        "Name")),
                                           self.header_font, Color("black"))
        text_rect = text_surface.get_rect(topleft=(150 * self.screen_scale[0], 0))
        self.image.blit(text_surface, text_rect)

    def add_remove_text_popup(self):
        if self.text_popup not in self.game.ui_updater:
            self.game.add_ui_updater(self.text_popup)
        else:
            self.game.remove_ui_updater(self.text_popup)


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
            (box.image.get_width() - int(20 * self.screen_scale[0]),
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

        # text
        text_surface = self.font.render(self.name, True, (30, 30, 30))
        text_rect = text_surface.get_rect(midleft=(int(6 * self.screen_scale[0]), self.image.get_height() / 2))
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
        text_rect = text_surface.get_rect(midleft=(int(6 * self.screen_scale[0]), self.image.get_height() / 2))
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


class CampaignListAdapter(ListAdapterHideExpand):

    def __init__(self):
        from engine.game.game import Game
        self.game = Game.game
        self.map_source_index = dict()
        localisation = Game.localisation
        map_data = self.game.preset_map_data
        actual_level_list = []

        self.map_name_index = {}
        self.map_source_name_index = {}

        for mission_name in map_data:
            if "event" not in mission_name:
                map_name = localisation.grab_text(key=("mission", mission_name, "Name"))
                actual_level_list.append((0, map_name))
                self.map_name_index[map_name] = mission_name
                # for map_file_name in map_data[mission_name]:  # add map
                #     map_name = localisation.grab_text(key=("preset_map", mission_name, "info", map_file_name, "Name"))
                #     actual_level_list.append((1, "> " + map_name))
                #     self.map_name_index[map_name] = map_file_name
                #     for source_file_name in map_data[mission_name][map_file_name]["source"]:  # add source
                #         source_name = localisation.grab_text(key=(
                #             "preset_map", mission_name, map_file_name, "source", int(source_file_name), "Source"))
                #         self.map_source_name_index[source_name] = source_file_name
                #         current_index = len(actual_level_list)
                #         self.map_source_index[(map_file_name, source_file_name)] = current_index
                #         actual_level_list.append((2, ">> " + source_name))

        ListAdapterHideExpand.__init__(self, actual_level_list)

    def get_highlighted_index(self):
        if not hasattr(self.game, 'map_selected'):
            return None
        return self.get_actual_index_visible_index().get(
            self.map_source_index[self.game.map_selected])

    def on_select(self, item_index, item_text):

        actual_index = self.get_visible_index_actual_index()[item_index]

        # if click on a source then load it
        self.game.map_selected = item_text

    def on_mouse_over(self, item_index, item_text):
        """
        Method for campaign map list where player hovering over item will display historical information of campaign, map,
        or map source
        :param self: Listui object
        :param item_index: Index of selected item in list
        :param item_text: Text of selected item
        """
        item_name = item_text.replace(">", "")
        item_name = item_name.replace("|", "")
        item_id = (item_text, item_index)
        if item_id != self.game.text_popup.last_shown_id:
            if item_name[0] == " ":  # remove space from subsection name
                item_name = item_name[1:]
            if ">>" in item_text or "||" in item_text:  # source item
                actual_index = self.get_visible_index_actual_index()[item_index]

                _map, source = {v: k for k, v in self.map_source_index.items()}[actual_index]
                popup_text = [value for key, value in
                              self.game.localisation.grab_text(("preset_map",
                                                                self.game.battle_campaign[_map],
                                                                _map, "source",
                                                                source)).items()]
            elif ">" in item_text or "|" in item_text:  # map item
                popup_text = [value for key, value in
                              self.game.localisation.grab_text(("preset_map",
                                                                self.game.battle_campaign[
                                                                    self.map_name_index[item_name]],
                                                                "info", self.map_name_index[item_name])).items()]

            else:  # campaign item
                popup_text = [value for key, value in
                              self.game.localisation.grab_text(("preset_map", "info",
                                                                self.campaign_name_index[item_name])).items()]

            self.game.text_popup.popup(self.game.cursor.rect, popup_text, shown_id=item_id,
                                       width_text_wrapper=1000 * self.game.screen_scale[0])
        else:  # already showing this leader no need to create text again
            self.game.text_popup.popup(self.game.cursor.rect, None, shown_id=item_id,
                                       width_text_wrapper=1000 * self.game.screen_scale[0])
        self.game.add_ui_updater(self.game.text_popup)


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
    def __init__(self, font_size=48):
        self._layer = 30
        UIMenu.__init__(self, player_cursor_interact=False)
        self.font_size = int(font_size * self.screen_scale[1])
        self.font = Font(self.ui_font["main_button"], self.font_size)
        self.pos = (0, 0)
        self.last_shown_id = None
        self.text_input = ""

    def popup(self, popup_rect, text_input, shown_id=None, width_text_wrapper=None, custom_screen_size=None,
              bg_colour=(220, 220, 220), font_colour=(30, 30, 30)):
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
                    image_height = int(((self.font.render(text, True, (0, 0, 0)).get_width()) +
                                        self.font_size) / width_text_wrapper)
                    if not image_height:  # only one line
                        text_image = Surface((width_text_wrapper, self.font_size))
                        text_image.fill(bg_colour)
                        surface = self.font.render(text, True, font_colour)
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
                                word_surface = self.font.render(word, True, font_colour)
                                word_width, word_height = word_surface.get_size()
                                if x + word_width >= max_width:
                                    x = self.font_size  # reset x
                                    y += word_height  # start on new row.
                                x += word_width + space
                            x = self.font_size  # reset x
                            y += word_height  # start on new row
                        text_image = Surface((width_text_wrapper, y))
                        text_image.fill(bg_colour)
                        make_long_text(text_image, text, (self.font_size, self.font_size), self.font,
                                       color=font_colour, specific_width=width_text_wrapper)
                        text_surface.append(text_image)
                        max_height += text_image.get_height()
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

            self.image = Surface((max_width, max_height))  # white Box
            self.image.fill(bg_colour)

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
            if type(popup_rect) is tuple:
                if type(popup_rect[0]) is str:
                    exec(f"self.rect = self.image.get_rect({popup_rect[0]}=popup_rect[1])")
                else:
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

    def update(self):
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

#
# from math import cos, sin
# from pygame import Vector2, display, sprite, Surface
# from pygame.mask import from_surface
# from pygame.sprite import spritecollide, collide_mask
# import pygame
#
# pygame.init()
#
# screen_width, screen_height = 1920, 1080
# screen = display.set_mode((screen_width, screen_height))
# display.set_caption("Fantasy Universe")
#
# font = pygame.font.SysFont("Arial", 16)
# speed_font = pygame.font.SysFont("Arial", 32)
#
#
# def circle_orbit(center, radius, angle, *args):
#     """
#     Finding the x,y coordinates on circle, based on given angle
#     """
#     # center of circle, angle in degree and radius of circle
#     x = center[0] + (radius[0] * cos(angle))
#     y = center[1] + (radius[0] * sin(angle))
#     return x, y
#
#
# def custom_orbit(center, _, angle, movement_surface, collide_surface):
#     collide_surface.image = collide_surface.check_image.copy()
#
#     pygame.draw.line(collide_surface.image, (0, 0, 0), collide_surface.image_center,
#                      (collide_surface.image_center[0] + (10000 * cos(angle)),
#                       collide_surface.image_center[1] + (10000 * sin(angle))))
#     collide_surface.mask = from_surface(collide_surface.image)
#     collide_pos = collide_mask(collide_surface, movement_surface)
#     return (center[0] + (collide_pos[0] - collide_surface.image_center[0]),
#             center[1] + (collide_pos[1] - collide_surface.image_center[1]))
#
#
# def create_movement_image(shape, size):
#     base_image = Surface((size[0], size[1]), pygame.SRCALPHA)
#     collide_check_image = Surface((size[0], size[1]), pygame.SRCALPHA)
#     if shape == "square":
#         pygame.draw.rect(base_image, color=(255, 255, 255), rect=(0, 0, size[0], size[1]), width=2)
#     elif shape == "ellipse":
#         pygame.draw.ellipse(base_image, color=(255, 255, 255), rect=(0, 0, size[0], size[1]), width=2)
#
#     return base_image, collide_check_image
#
#
# class CollideSurface(sprite.Sprite):
#     def __init__(self, image):
#         sprite.Sprite.__init__(self)
#         self.image = image
#         self.check_image = image
#         self.image_center = (self.image.get_width() / 2, self.image.get_height() / 2)
#         self.rect = image.get_rect(center=(0, 0))
#         self.mask = from_surface(image)
#
#     def update(self, pos):
#         self.rect.center = Vector2(pos[0], pos[1])
#         self.mask = from_surface(self.image)
#
#
# class Planet(pygame.sprite.Sprite):
#     def __init__(self, start_angle, sprite_radius, color, name, orbit=None, epicycle=None, specific_pos=()):
#         self.sprite_radius = sprite_radius
#         self.color = color
#         self.name = name
#
#         self.last_path = ()
#         self.pos = ()
#
#         self.current_orbit_angle = start_angle
#         self.parent = None
#         self.parent_radius = 0
#         self.orbit_speed = 0
#         self.orbit_shape = "circle"
#         self.orbit_movement_check = None
#         self.orbit_collide_check = None
#         if orbit:
#             self.orbit_speed = orbit["speed"]
#             self.orbit_shape = orbit["shape"]
#             self.parent_radius = orbit["radius"]
#             self.parent = orbit["parent"]
#             orbit_movement_check_image, orbit_collide_check_image = create_movement_image(orbit["shape"],
#                                                                                           orbit["radius"])
#             self.orbit_movement_check = CollideSurface(orbit_movement_check_image)
#             self.orbit_collide_check = CollideSurface(orbit_collide_check_image)
#         elif not specific_pos:  # assume to be center of universe
#             self.pos = (screen_width / 2, screen_height / 2)
#         else:
#             self.pos = specific_pos
#         self.orbit_pos = self.pos
#         self.orbit_process = circle_orbit
#         if self.orbit_shape != "circle":
#             self.orbit_process = custom_orbit
#
#         self.current_epicycle_angle = 0
#         self.epicycle_speed = 0
#         self.epicycle_radius = 0
#         self.epicycle_shape = "circle"
#         self.epicycle_movement_check = None
#         self.epicycle_collide_check = None
#         if epicycle:
#             self.epicycle_speed = epicycle["speed"]
#             self.epicycle_radius = epicycle["radius"]
#             self.epicycle_shape = epicycle["shape"]
#             epicycle_movement_check_image, epicycle_collide_check_image = create_movement_image(epicycle["shape"],
#                                                                                                 epicycle["radius"])
#             self.epicycle_movement_check = CollideSurface(epicycle_movement_check_image)
#             self.epicycle_collide_check = CollideSurface(epicycle_collide_check_image)
#         self.epicycle_process = circle_orbit
#         if self.epicycle_shape != "circle":
#             self.epicycle_process = custom_orbit
#         self.update_position(0, 0)
#
#     def draw(self, win, background, show_base_shape):
#         # Draw the orbit path
#         if show_base_shape:
#             if self.orbit_movement_check:
#                 background.blit(self.orbit_movement_check.image, self.orbit_collide_check.rect)
#         else:
#             if self.last_path:
#                 pygame.draw.line(background, self.color, self.pos, self.last_path, 2)
#                 self.last_path = ()
#
#         # Draw the planet
#         pygame.draw.circle(win, self.color, self.pos, self.sprite_radius)
#
#         # Draw distance to the sun for planets other than the sun
#         # if not self.sun:
#         #     distance_text = font.render(f"{round(self.distance_to_sun / 1000, 1)} km", True, WHITE)
#         #     win.blit(distance_text, (int(x - distance_text.get_width() / 2), int(y - distance_text.get_height() / 2)))
#
#         # Draw name and additional info if planet is selected
#         info_text = font.render(self.name, True, (255, 255, 255))
#         win.blit(info_text, (int(self.pos[0] - info_text.get_width() / 2), int(self.pos[1] - self.sprite_radius - 20)))
#
#     def update_position(self, dt, speed):
#         self.last_path = self.pos
#         if self.orbit_speed:
#             self.current_orbit_angle += self.orbit_speed * dt * speed
#             # if self.current_orbit_angle >= 360:
#             #     self.current_orbit_angle -= 360
#             # elif self.current_orbit_angle < 0:
#             #     self.current_orbit_angle += 360
#             self.orbit_movement_check.update(self.parent.pos)
#             self.orbit_collide_check.update(self.parent.pos)
#             self.orbit_pos = self.orbit_process(self.parent.pos, self.parent_radius, self.current_orbit_angle,
#                                                 self.orbit_movement_check, self.orbit_collide_check)
#             self.pos = self.orbit_pos
#         if self.epicycle_speed:
#             self.current_epicycle_angle += self.epicycle_speed * dt * speed
#             self.epicycle_movement_check.update(self.orbit_pos)
#             self.epicycle_collide_check.update(self.orbit_pos)
#             self.pos = self.epicycle_process(self.orbit_pos, self.epicycle_radius, self.current_epicycle_angle,
#                                              self.epicycle_movement_check, self.epicycle_collide_check)
#
#
# def main():
#     run = True
#     clock = pygame.time.Clock()
#
#     background_base = Surface((screen_width, screen_height))
#     background = background_base.copy()
#
#     sun_helio = Planet(20, 20, (255, 0, 0), "Sol")
#     earth_helio = Planet(0,  8, (255, 0, 0), "Terra",
#                           orbit={"parent": sun_helio, "speed": 0.7, "shape": "circle", "radius": (200, 200)})
#     planets_helio = [Planet(180, 8, (30, 30, 150), "Lunar",
#                           orbit={"parent": earth_helio, "speed": 1, "shape": "circle", "radius": (50, 50)}),
#                    Planet(270,  8, (255, 255, 255), "Planar 1",
#                           orbit={"parent": sun_helio, "speed": 0.8, "shape": "circle", "radius": (500, 500)}),
#                    sun_helio, earth_helio]
#
#     # Create the sun with a smaller radius
#     terra_geo = Planet(20, 15, (50, 50, 200), "Terra")
#
#     # Add planets
#     planets_geo = [Planet(200, 10, (30, 30, 150), "Lunar",
#                           orbit={"parent": terra_geo, "speed": 1, "shape": "circle", "radius": (80, 80)}),
#                    Planet(150,  8, (255, 255, 255), "Planar 1",
#                           orbit={"parent": terra_geo, "speed": 0.8, "shape": "circle", "radius": (200, 200)},
#                           epicycle={"speed": 0.5, "shape": "circle", "radius": (150, 150)}),
#                    Planet(200,  12, (255, 0, 0), "Sol",
#                           orbit={"parent": terra_geo, "speed": 0.7, "shape": "circle", "radius": (300, 300)}),
#                    terra_geo]
#
#     sun_nonsense = Planet(20, 20, (255, 0, 0), "Sol",
#                           epicycle={"speed": 0.5, "shape": "square", "radius": (30, 100)})
#     earth_nonsense = Planet(200,  8, (255, 0, 0), "Our World",
#                           orbit={"parent": sun_nonsense, "speed": 0.7, "shape": "circle", "radius": (300, 300)})
#     planets_nonsense = [Planet(200, 8, (30, 30, 150), "Lunar",
#                           orbit={"parent": earth_nonsense, "speed": 1, "shape": "circle", "radius": (200, 200)}),
#                         Planet(150,  8, (255, 255, 255), "Planar 1",
#                                orbit={"parent": sun_nonsense, "speed": 3, "shape": "ellipse", "radius": (300, 200)}),
#                         sun_nonsense, earth_nonsense]
#
#     models = {
#         "Faux Heliocentric": planets_helio,
#         "Faux Geocentric": planets_geo,
#         "Nonsense": planets_nonsense
#     }
#     speed = 1
#     keypress_delay = 0
#     day = 0
#     current_model = 0
#     show_base_shape = False
#     planets = models[tuple(models.keys())[current_model]]
#     speed_text = speed_font.render("Speed: " + str(speed), True, (255, 255, 255))
#     speed_text_rect = speed_text.get_rect(topleft=(0, screen_height - 100))
#     model_text = speed_font.render("Model: " + tuple(models.keys())[current_model], True, (255, 255, 255))
#     model_text_rect = model_text.get_rect(topright=(screen_width, screen_height - 100))
#
#     while run:
#         clock.tick(1000)
#         screen.fill((0, 0, 0))
#         dt = clock.get_time() / 1000
#         if dt > 0.1:  # one frame update should not be longer than 0.1 second for calculation
#             dt = 0.1  # make it so stutter and lag does not cause overtime issue
#
#         # Handle events
#         shift_press = False
#         key_press = pygame.key.get_pressed()
#         if key_press is not None and not keypress_delay:
#             if key_press[pygame.K_LSHIFT] or key_press[pygame.K_RSHIFT]:
#                 shift_press = True
#             if key_press[pygame.K_KP_PLUS]:
#                 if shift_press:
#                     speed += 1
#                 else:
#                     speed += 0.1
#                 speed_text = speed_font.render("Speed: " + str(round(speed, 1)), True, (255, 255, 255))
#                 keypress_delay = 0.1
#             elif key_press[pygame.K_KP_MINUS]:
#                 if shift_press:
#                     speed -= 1
#                 else:
#                     speed -= 0.1
#                 speed_text = speed_font.render("Speed: " + str(round(speed, 1)), True, (255, 255, 255))
#                 keypress_delay = 0.1
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 run = False
#             elif event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_ESCAPE:
#                     run = False
#                 elif event.key == pygame.K_TAB:
#                     if show_base_shape:
#                         show_base_shape = False
#                     else:
#                         show_base_shape = True
#                     background = background_base.copy()
#                 elif event.key == pygame.K_p:  # Pause/Play
#                     speed = 0
#                     speed_text = speed_font.render("Speed: " + str(round(speed, 1)), True, (255, 255, 255))
#                 elif event.key == pygame.K_LEFTBRACKET:
#                     current_model -= 1
#                     if current_model < 0:
#                         current_model = len(models) - 1
#                     planets = models[tuple(models.keys())[current_model]]
#                     background = background_base.copy()
#                     model_text = speed_font.render("Model: " + tuple(models.keys())[current_model], True,
#                                                    (255, 255, 255))
#                 elif event.key == pygame.K_RIGHTBRACKET:
#                     current_model += 1
#                     if current_model == len(models):
#                         current_model = 0
#                     planets = models[tuple(models.keys())[current_model]]
#                     background = background_base.copy()
#                     model_text = speed_font.render("Model: " + tuple(models.keys())[current_model], True,
#                                                    (255, 255, 255))
#
#         if keypress_delay:
#             keypress_delay -= dt
#             if keypress_delay < 0:
#                 keypress_delay = 0
#
#         # Update and draw planets
#         screen.blit(background, (0, 0))
#         for planet in planets:
#             planet.update_position(dt, speed)
#             planet.draw(screen, background, show_base_shape)
#         screen.blit(speed_text, speed_text_rect)
#         screen.blit(model_text, model_text_rect)
#         display.update()
#
#     pygame.quit()
