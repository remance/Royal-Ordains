import types
from functools import lru_cache

import pygame
import pyperclip
from pygame import Surface, SRCALPHA, Rect, Color, draw, mouse
from pygame.font import Font
from pygame.sprite import Sprite

from engine.utils.common import keyboard_mouse_press_check, stat_allocation_check, skill_allocation_check
from engine.utils.data_loading import load_image
from engine.utils.text_making import text_render_with_bg, make_long_text


@lru_cache(maxsize=2 ** 8)
def draw_text(text, font, color, ellipsis_length=None):
    # NOTE: this can be very slow. Imagine you have a very long text it has to step down each
    #       character till it find the a character length that works.
    #       if this method's performance becomes a big issue try make a better estimate on the length
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
        It contain all corners and sides and a pixel in the center.
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

    def __init__(self, player_interact=True, has_containers=False):
        """
        Parent class for all menu user interface objects

        :param player_interact: Player can interact (click) with UI in some way
        :param has_containers: Object has group containers to assign
        """
        from engine.game.game import Game
        self.game = Game.game
        self.screen_scale = Game.screen_scale
        self.main_dir = Game.main_dir
        self.data_dir = Game.data_dir
        self.font_dir = Game.font_dir
        self.ui_font = Game.ui_font
        self.font_texture = Game.font_texture
        self.screen_rect = Game.screen_rect
        self.screen_size = Game.screen_size
        self.localisation = Game.localisation
        self.cursor = Game.cursor
        self.updater = Game.ui_updater
        self.player_interact = player_interact
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
        self._layer = 1000000  # as high as possible, always blit last
        UIMenu.__init__(self, player_interact=False, has_containers=True)
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
        UIMenu.__init__(self, player_interact=False)

        self.pos = pos
        self.image = image

        self.base_image = self.image.copy()

        self.font = Font(self.ui_font["main_button"], int(48 * self.screen_scale[1]))

        self.rect = self.image.get_rect(center=self.pos)

    def change_instruction(self, text):
        self.image = self.base_image.copy()
        self.text = text
        text_surface = self.font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 4))
        self.image.blit(text_surface, text_rect)


class InputBox(UIMenu):
    def __init__(self, pos, width, text="", click_input=False):
        UIMenu.__init__(self, player_interact=False)
        self._layer = 31
        self.font = Font(self.ui_font["main_button"], int(30 * self.screen_scale[1]))
        self.pos = pos
        self.image = Surface((width - 10, int(34 * self.screen_scale[1])))
        self.max_text = int((self.image.get_width() / int(30 * self.screen_scale[1])) * 2)
        self.image.fill((255, 255, 255))

        self.base_image = self.image.copy()

        self.text = text
        text_surface = self.font.render(text, True, (0, 0, 0))
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
        text_surface = self.font.render(show_text, True, (0, 0, 0))
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
            elif key_press[pygame.K_LCTRL] or key_press[
                pygame.K_RCTRL]:  # use keypress for ctrl as is has no effect on its own
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
            text_surface = self.font.render(show_text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(midleft=(0, self.image.get_height() / 2))
            self.image.blit(text_surface, text_rect)


class TextBox(UIMenu):
    def __init__(self, image, pos, text):
        self._layer = 13
        UIMenu.__init__(self)

        self.font = Font(self.ui_font["main_button"], int(36 * self.screen_scale[1]))
        self.image = image

        self.base_image = self.image.copy()

        text_surface = self.font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surface, text_rect)

        self.rect = self.image.get_rect(topright=pos)

    def change_text(self, text):
        self.image = self.base_image.copy()

        text_surface = self.font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surface, text_rect)


class MenuImageButton(UIMenu):
    def __init__(self, pos, image, layer=1):
        self._layer = layer
        UIMenu.__init__(self, player_interact=True)
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
            self.text = self.localisation.grab_text(key=("ui", key_name,))
            text_surface = self.font.render(self.text, True, (0, 0, 0))
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
            self.text = self.localisation.grab_text(key=("ui", key_name))
            self.button_normal_image = self.base_image0.copy()
            self.button_over_image = self.base_image1.copy()
            self.button_click_image = self.base_image2.copy()
            text_surface = self.font.render(self.text, True, (0, 0, 0))
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
        self.text = self.localisation.grab_text(key=("ui", self.key_name))
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
    def __init__(self, pos, text, text_size):
        UIMenu.__init__(self, player_interact=False)
        self.pos = pos
        self.font = Font(self.ui_font["main_button"], text_size)
        self.image = text_render_with_bg(text, self.font, Color("black"))
        self.rect = self.image.get_rect(center=(self.pos[0] - (self.image.get_width() / 2), self.pos[1]))


class CharacterSelector(UIMenu):
    def __init__(self, pos, images):
        UIMenu.__init__(self, player_interact=False)
        self.pos = pos
        self.images = images
        self.image = self.images["Empty"]
        self.mode = "empty"
        self.rect = self.image.get_rect(center=self.pos)
        self.current_row = 0
        self.delay = 0

    def change_mode(self, mode):
        if not self.delay:
            self.image = self.images[mode.capitalize()]
            self.mode = mode
            self.delay = 0.1

    def update(self):
        if self.delay:
            self.delay -= self.game.dt
            if self.delay < 0:
                self.delay = 0


class CharacterStatAllocator(UIMenu):
    def __init__(self, pos, player):
        UIMenu.__init__(self)
        self.font = Font(self.ui_font["main_button"], int(24 * self.screen_scale[1]))
        self.small_font = Font(self.ui_font["main_button"], int(18 * self.screen_scale[1]))
        self.current_row = 0
        self.input_delay = 0
        self.pos = pos
        self.player = player

        self.stat_row = ("Strength", "Dexterity", "Agility",
                         "Constitution", "Intelligence", "Wisdom", "Charisma")
        self.common_skill_row = ("Ground Movement", "Air Movement", "Tinkerer", "Arm Mastery", "Wealth",
                                 "Immunity", "Resourceful", "Combat Contest")
        self.skill_row = []
        self.all_skill_row = []
        self.stat = {}

        self.image = Surface((350 * self.screen_scale[0], 900 * self.screen_scale[1]), SRCALPHA)
        text = self.small_font.render("Status (Cost)", True, (0, 0, 0))
        text_rect = text.get_rect(center=(290 * self.screen_scale[0], 80 * self.screen_scale[1]))
        self.image.blit(text, text_rect)

        self.stat_rect = {}
        self.skill_rect = {}
        start_stat_row = 120 * self.screen_scale[1]

        text = self.small_font.render("Status Point Left: ", True, (0, 0, 0))
        self.status_point_left_text_rect = text.get_rect(midleft=(10 * self.screen_scale[0],
                                                                  80 * self.screen_scale[1]))
        self.image.blit(text, self.status_point_left_text_rect)

        text = self.small_font.render("Skill Point Left: ", True, (0, 0, 0))
        self.skill_point_left_text_rect = text.get_rect(midleft=(10 * self.screen_scale[0],
                                                                 380 * self.screen_scale[1]))
        self.image.blit(text, self.skill_point_left_text_rect)

        for index, stat in enumerate(self.stat_row):
            text = self.font.render(stat + ": ", True, (0, 0, 0))
            text_rect = text.get_rect(midleft=(10 * self.screen_scale[0], start_stat_row))
            self.stat_rect[stat] = text_rect  # save stat name rect for stat point later
            self.image.blit(text, text_rect)
            start_stat_row += 36 * self.screen_scale[1]

        text = self.small_font.render("Current Level", True, (0, 0, 0))
        text_rect = text.get_rect(center=(290 * self.screen_scale[0], 380 * self.screen_scale[1]))
        self.image.blit(text, text_rect)

        # start_stat_row = 440 * self.screen_scale[1]
        # for index, stat in enumerate(self.common_skill_row):
        #     text = self.font.render(stat + ": ", True, (0, 0, 0))
        #     text_rect = text.get_rect(midleft=(10 * self.screen_scale[0], start_stat_row))
        #     self.skill_rect[stat] = text_rect  # save stat name rect for stat point later
        #     self.image.blit(text, text_rect)
        #     start_stat_row += 36 * self.screen_scale[1]

        self.base_image = self.image.copy()

        self.rect = self.image.get_rect(center=self.pos)

    def update(self):
        if not self.pause and self.rect.collidepoint(
                self.cursor.pos):  # check for stat detail popup based on mouse over
            mouse_pos = (self.cursor.pos[0] - self.rect.topleft[0],
                         self.cursor.pos[1] - self.rect.topleft[1])
            for key, value in self.stat_rect.items():
                if value.collidepoint(mouse_pos):
                    self.game.add_ui_updater(self.game.text_popup)
                    self.game.text_popup.popup(self.game.cursor.rect,
                                               (self.game.localisation.grab_text(("help", key, "Name")),
                                                self.game.localisation.grab_text(("help", key, "Description"))),
                                               shown_id=key,
                                               width_text_wrapper=1000 * self.game.screen_scale[0])
                    break

            for key, value in self.skill_rect.items():
                if value.collidepoint(mouse_pos):
                    self.game.add_ui_updater(self.game.text_popup)
                    new_key = key + "." + str(int(self.stat[key]))
                    if self.game.localisation.grab_text(("help", new_key, "Buttons")):
                        text = (self.game.localisation.grab_text(("help", new_key, "Name")),
                                self.game.localisation.grab_text(("help", new_key, "Description")),
                                "Buttons: " + self.game.localisation.grab_text(("help", new_key, "Buttons")))
                    else:
                        text = (self.game.localisation.grab_text(("help", new_key, "Name")),
                                self.game.localisation.grab_text(("help", new_key, "Description")))
                    self.game.text_popup.popup(self.game.cursor.rect, text,
                                               shown_id=key,
                                               width_text_wrapper=1000 * self.game.screen_scale[0])
                    break

        if self.input_delay > 0:
            self.input_delay -= self.game.dt
            if self.input_delay < 0:
                self.input_delay = 0

    def add_stat(self, stat_dict):
        self.stat = stat_dict
        self.image = self.base_image.copy()
        self.skill_row = [key for key in stat_dict if "Remain" not in key and key not in self.common_skill_row and
                          key not in self.stat_row and key != "ID"]
        self.all_skill_row = list(self.common_skill_row) + self.skill_row
        self.last_row = len(self.stat_row) + len(self.common_skill_row) + len(self.skill_row) - 1

        self.skill_rect = {}
        start_stat_row = 400 * self.screen_scale[1]
        for index, stat in enumerate(self.all_skill_row):
            text = self.font.render(stat + ": ", True, (0, 0, 0))
            text_rect = text.get_rect(midleft=(10 * self.screen_scale[0], start_stat_row))
            self.skill_rect[stat] = text_rect  # save stat name rect for stat point later
            self.image.blit(text, text_rect)
            start_stat_row += 36 * self.screen_scale[1]

        for index, stat in enumerate(stat_dict):
            if stat in self.stat_rect:
                if index == self.current_row:
                    text = self.font.render(str(int(stat_dict[stat])) + " (" + str(int(stat_dict[stat] / 10) + 1) + ")",
                                            True, (0, 0, 0), (255, 255, 255, 255))
                else:
                    text = self.font.render(str(int(stat_dict[stat])) + " (" + str(int(stat_dict[stat] / 10) + 1) + ")",
                                            True, (0, 0, 0))
                text_rect = text.get_rect(midright=(330 * self.screen_scale[0], self.stat_rect[stat].midleft[1]))
            elif stat in self.skill_rect:
                if index == self.current_row:
                    text = self.font.render(str(int(stat_dict[stat])),
                                            True, (0, 0, 0), (255, 255, 255, 255))
                else:
                    text = self.font.render(str(int(stat_dict[stat])),
                                            True, (0, 0, 0))
                text_rect = text.get_rect(midright=(330 * self.screen_scale[0], self.skill_rect[stat].midleft[1]))
            elif "Remain" in stat:  # point left
                if "Status" in stat:
                    text = self.font.render(str(int(stat_dict[stat])), True, (0, 0, 0))
                    text_rect = text.get_rect(
                        midleft=(180 * self.screen_scale[0], self.status_point_left_text_rect.midleft[1]))
                else:
                    text = self.font.render(str(int(stat_dict[stat])), True, (0, 0, 0))
                    text_rect = text.get_rect(
                        midleft=(180 * self.screen_scale[0], self.skill_point_left_text_rect.midleft[1]))
            self.image.blit(text, text_rect)

    def change_stat(self, stat, how):
        self.stat[stat], self.stat["Status Remain"] = stat_allocation_check(self.stat[stat], self.stat["Status Remain"],
                                                                            how)
        self.add_stat(self.stat)

    def change_skill(self, skill, how):
        self.stat[skill], self.stat["Skill Remain"] = skill_allocation_check(self.stat[skill],
                                                                             self.stat["Skill Remain"], how)
        self.add_stat(self.stat)

    def player_input(self, key):
        if not self.input_delay:
            if key == "Up":
                self.current_row -= 1
                if self.current_row < 0:
                    self.current_row = self.last_row
                self.add_stat(self.stat)
                self.input_delay = 0.15
            elif key == "Down":
                self.current_row += 1
                if self.current_row > self.last_row:
                    self.current_row = 0
                self.add_stat(self.stat)
                self.input_delay = 0.15
            elif key == "Left":  # switch to previous in playable_character list
                if self.current_row <= 6:  # change stat
                    self.change_stat(self.stat_row[self.current_row], "down")
                else:  # change skill
                    self.change_skill(self.all_skill_row[self.current_row - 7], "down")
                self.input_delay = 0.15
            elif key == "Right":  # switch to next in playable_character list
                if self.current_row <= 6:  # change stat
                    self.change_stat(self.stat_row[self.current_row], "up")
                else:  # change skill
                    self.change_skill(self.all_skill_row[self.current_row - 7], "up")
                self.input_delay = 0.15


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
        text_surface = self.font.render(text, True, (0, 0, 0))
        size = text_surface.get_size()
        image_size = size[0] * 2
        if size[0] < 40:
            image_size = size[0] * 4
        self.image = Surface((image_size, size[1] * 2), SRCALPHA)
        draw.rect(self.image, (50, 50, 50), (0, 0, image_size, size[1] * 2), border_radius=2)
        draw.rect(self.image, (255, 255, 255),
                  (image_size * 0.1, size[1] * 0.3, image_size * 0.8, size[1] * 1.5),
                  border_radius=2)
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surface, text_rect)

    def draw_joystick(self, key, keybind_name):

        text_surface = self.font.render(keybind_name[key], True, (0, 0, 0))
        size = text_surface.get_size()
        image_size = size[0] * 2
        if size[0] < 40:
            image_size = size[0] * 4
        self.image = Surface((image_size, size[1] * 2), SRCALPHA)
        draw.circle(self.image, (255, 255, 255), (self.image.get_width() / 2, self.image.get_height() / 2),
                    self.image.get_width() / 2)
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surface, text_rect)


class ValueBox(UIMenu):
    def __init__(self, image, pos, value, text_size):
        self._layer = 26
        UIMenu.__init__(self, player_interact=False)
        self.font = Font(self.ui_font["main_button"], text_size)
        self.pos = pos
        self.image = image.copy()
        self.base_image = self.image.copy()
        self.value = value
        text_surface = self.font.render(str(self.value), True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surface, text_rect)
        self.rect = self.image.get_rect(center=self.pos)

    def change_value(self, value):
        self.value = value
        self.image = self.base_image.copy()
        text_surface = self.font.render(str(self.value), True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surface, text_rect)


class MapTitle(UIMenu):
    def __init__(self, pos):
        UIMenu.__init__(self)

        self.font = Font(self.ui_font["name_font"], int(44 * self.screen_scale[1]))
        self.pos = pos
        self.name = ""
        text_surface = self.font.render(str(self.name), True, (0, 0, 0))
        self.image = pygame.Surface((int(text_surface.get_width() + (5 * self.screen_scale[0])),
                                     int(text_surface.get_height() + (5 * self.screen_scale[1]))))

    def change_name(self, name):
        self.name = name
        text_surface = self.font.render(str(self.name), True, (0, 0, 0))
        self.image = pygame.Surface((int(text_surface.get_width() + (5 * self.screen_scale[0])),
                                     int(text_surface.get_height() + (5 * self.screen_scale[1]))))
        self.image.fill((0, 0, 0))

        white_body = pygame.Surface((text_surface.get_width(), text_surface.get_height()))
        white_body.fill((239, 228, 176))
        white_rect = white_body.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(white_body, white_rect)

        text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)
        self.rect = self.image.get_rect(midtop=self.pos)


class NameTextBox(UIMenu):
    def __init__(self, box_size, pos, name, text_size=26, layer=15, box_colour=(255, 255, 255), center_text=False):
        self._layer = layer
        UIMenu.__init__(self)
        self.font = Font(self.ui_font["main_button"], int(text_size * self.screen_scale[1]))
        self.name = str(name)

        self.image = Surface(box_size)
        self.image.fill((0, 0, 0))  # black corner

        # White body square
        white_body = Surface((self.image.get_width() - 2, self.image.get_height() - 2))
        white_body.fill(box_colour)
        small_rect = white_body.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(white_body, small_rect)

        self.image_base = self.image.copy()

        # Name text
        text_surface = self.font.render(self.name, True, (0, 0, 0))
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
        text_surface = self.font.render(self.name, True, (0, 0, 0))
        text_rect = text_surface.get_rect(midleft=(int(3 * self.screen_scale[0]), self.image.get_height() / 2))
        self.image.blit(text_surface, text_rect)


class ListBox(UIMenu):
    def __init__(self, pos, image, layer=14):
        self._layer = layer
        UIMenu.__init__(self, player_interact=False)
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
        self.image.fill((0, 0, 0))
        self.selected_image = self.image.copy()
        self.selected = False

        # White body square
        small_image = Surface(
            (box.image.get_width() - int(16 * self.screen_scale[0]), int((text_size + 2) * self.screen_scale[1])))
        small_image.fill((255, 255, 255))
        small_rect = small_image.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(small_image, small_rect)
        small_image.fill((255, 255, 128))
        self.selected_image.blit(small_image, small_rect)

        self.image_base = self.image.copy()

        # Name text
        text_surface = self.font.render(self.name, True, (0, 0, 0))
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
        text_surface = self.font.render(self.name, True, (0, 0, 0))
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


class BackgroundBox(UIMenu):
    def __init__(self, pos, image, layer=10):
        self._layer = layer
        UIMenu.__init__(self, player_interact=False)
        self.image = image.copy()

        self.font = Font(self.ui_font["main_button"], int(20 * self.screen_scale[1]))

        text_surface = self.font.render("Start Battle At Night", True, (0, 0, 0))
        text_rect = text_surface.get_rect(midleft=(self.image.get_width() / 3.5, self.image.get_height() / 5))
        self.image.blit(text_surface, text_rect)

        self.rect = self.image.get_rect(topright=pos)


class TextPopup(UIMenu):
    def __init__(self):
        self._layer = 30
        UIMenu.__init__(self, player_interact=False)
        self.font_size = int(24 * self.screen_scale[1])
        self.font = Font(self.ui_font["main_button"], self.font_size)
        self.pos = (0, 0)
        self.last_shown_id = None
        self.text_input = ""

    def popup(self, popup_rect, text_input, shown_id=None, width_text_wrapper=0, custom_screen_size=None):
        """Pop out text box with input text list in multiple line, one item equal to one paragraph"""
        self.last_shown_id = shown_id

        if text_input is not None and (self.text_input != text_input or self.last_shown_id != shown_id):
            self.text_input = text_input
            if type(text_input) == str:
                self.text_input = [text_input]
            text_surface = []
            if width_text_wrapper:
                max_height = 0
                max_width = width_text_wrapper
                for text in self.text_input:
                    image_height = int((len(text) * self.font_size) / (width_text_wrapper * 1.2))
                    if not image_height:  # only one line
                        text_image = Surface((width_text_wrapper, self.font_size))
                        text_image.fill((255, 255, 255))
                        surface = self.font.render(text, True, (0, 0, 0))
                        text_image.blit(surface, (self.font_size, 0))
                        text_surface.append(text_image)  # text input font surface
                        max_height += self.font_size * 2
                    else:
                        # Find new image height, using code from make_long_text
                        x, y = (self.font_size, self.font_size)
                        words = [word.split(" ") for word in
                                 str(text).splitlines()]  # 2D array where each row is a list of words
                        space = self.font.size(" ")[0]  # the width of a space
                        for line in words:
                            for word in line:
                                word_surface = self.font.render(word, True, (0, 0, 0))
                                word_width, word_height = word_surface.get_size()
                                if x + word_width >= max_width:
                                    x = self.font_size  # reset x
                                    y += word_height  # start on new row.
                                x += word_width + space
                            x = self.font_size  # reset x
                            y += word_height  # start on new row
                        image_height = y
                        text_image = Surface((width_text_wrapper, image_height))
                        text_image.fill((255, 255, 255))
                        make_long_text(text_image, text, (self.font_size, self.font_size), self.font)
                        text_surface.append(text_image)
                        max_height += text_image.get_height()
            else:
                max_width = 0
                max_height = 0
                for text in self.text_input:
                    surface = self.font.render(text, True, (0, 0, 0))
                    text_surface.append(surface)  # text input font surface
                    text_rect = surface.get_rect(
                        topleft=(self.font_size, self.font_size))  # text input position at (1,1) on white box image
                    if text_rect.width > max_width:
                        max_width = text_rect.width
                    max_height += self.font_size + int(self.font_size / 5)

            self.image = Surface((max_width + 6, max_height + 6))  # black border
            image = Surface((max_width + 2, max_height + 2))  # white Box
            image.fill((255, 255, 255))
            rect = self.image.get_rect(topleft=(2, 2))  # white box image position at (2,2) on black border image
            self.image.blit(image, rect)

            height = 1
            for surface in text_surface:
                text_rect = surface.get_rect(topleft=(4, height))
                image.blit(surface, text_rect)
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
            self.rect = self.image.get_rect(midbottom=popup_rect)


class BoxUI(UIMenu, Containable, Container):

    def __init__(self, size, parent):
        UIMenu.__init__(self, player_interact=False)
        self.parent = parent
        self.size = size
        self._layer = -1  # NOTE: not sure if this is good since underscore indicate it is a private variable but it works for now
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
        return int(scroll_bar_height * (item_size / len(items)))

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
        maxsize=2 ** 4)  # size has to be big enough to fit all active list ui on screen but not big enough to take to much memory
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

        font1 = Font(ui_font["main_button"], 20)
        font2 = Font(ui_font["main_button"], 14)
        font3 = Font(ui_font["main_button"], 18)

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
                draw.rect(image, (100, 0, 0) if hold_scroll_box is not None else (50,) * 3,
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
            if self.rect.collidepoint(mouse_pos):
                in_list = True
            if scroll_bar_rect := self.get_scroll_bar_rect(has_scroll, self.rect, scroll_bar_height):
                if scroll_bar_rect.collidepoint(relative_mouse_pos):
                    if self.get_scroll_box_rect(has_scroll, self.rect, self.scroll_down_index, scroll_step_height,
                                                scroll_box_size).collidepoint(relative_mouse_pos):
                        self.in_scroll_box = True
                    in_list = False

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
