import cProfile
import datetime
from math import cos, sin, radians

import pygame.transform
from pygame import Vector2, Surface, SRCALPHA, Color, Rect, draw, mouse
from pygame.font import Font
from pygame.sprite import Sprite
from pygame.transform import smoothscale

from engine.uimenu.uimenu import UIMenu
from engine.utils.text_making import number_to_minus_or_plus, text_render_with_bg, minimise_number_text

team_colour = {1: Color("black"), 2: Color("red"), 3: Color("blue"), 4: Color("darkgoldenrod1"),
               "health": Color("seagreen4"), "resource": Color("slateblue1"), "revive": Color("purple")}


class UIBattle(UIMenu):
    def __init__(self, player_interact=True, has_containers=False):
        """
        Parent class for all battle menu user interface
        """
        from engine.battle.battle import Battle
        UIMenu.__init__(self, player_interact=player_interact, has_containers=has_containers)
        self.updater = Battle.ui_updater  # change updater to use battle ui updater instead of main menu one
        self.battle = Battle.battle
        self.screen = Battle.screen
        self.battle_camera_size = Battle.battle_camera_size
        self.battle_camera_min = Battle.battle_camera_min
        self.battle_camera_max = Battle.battle_camera_max


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


class BattleCursor(UIBattle):
    def __init__(self, images, player_input):
        """Game battle cursor"""
        self._layer = 100  # as high as possible, always blit last
        UIBattle.__init__(self)
        self.pos_change = False

        self.images = images
        self.image = images["normal"]
        self.pos = Vector2(self.screen_size[0] / 2, self.screen_size[1] / 29)
        self.old_mouse_pos = (0, 0)
        self.rect = self.image.get_rect(topleft=self.pos)
        self.player_input = player_input
        self.shown = True

    def change_input(self, player_input):
        self.player_input = player_input

    def change_image(self, image_name):
        """Change cursor image to whatever input name"""
        self.image = self.images[image_name]
        self.rect = self.image.get_rect(topleft=self.pos)

    def update(self):
        """Update cursor position based on joystick or mouse input"""
        new_pos = mouse.get_pos()
        self.pos_change = False
        if self.old_mouse_pos != new_pos:
            self.old_mouse_pos = new_pos
            self.pos = Vector2(self.old_mouse_pos)  # get pos from mouse first
            self.pos_change = True

        if self.player_input == "joystick":  # joystick control
            for joystick in self.battle.joysticks.values():
                for i in range(joystick.get_numaxes()):
                    if joystick.get_axis(i) > 0.1 or joystick.get_axis(i) < -0.1:
                        axis_name = number_to_minus_or_plus(joystick.get_axis(i))
                        if i == 2:
                            if axis_name == "+":
                                self.pos[0] += 5
                            else:
                                self.pos[0] -= 5
                        if i == 3:
                            if axis_name == "+":
                                self.pos[1] += 5
                            else:
                                self.pos[1] -= 5
                        self.pos_change = True

        if self.pos[0] > self.battle_camera_max[0]:
            self.pos[0] = self.battle_camera_max[0]
        elif self.pos[0] < 0:
            self.pos[0] = 0
        if self.pos[1] > self.battle_camera_max[1]:
            self.pos[1] = self.battle_camera_max[1]
        if self.pos[1] < 0:
            self.pos[1] = 0

        if self.shown:
            self.rect.topleft = self.pos


class PlayerPortrait(UIBattle):
    def __init__(self, image, health_bar_image, resource_bar_image, guard_bar_image, pos):
        self._layer = 9
        UIBattle.__init__(self, player_interact=False)
        self.image = image.copy()
        self.rect = self.image.get_rect(center=pos)

        self.font = Font(self.ui_font["main_button"], int(20 * self.screen_scale[1]))

        self.health_bar_image = health_bar_image
        self.base_health_bar_image = health_bar_image.copy()
        self.health_bar_rect = self.health_bar_image.get_rect(topleft=(290 * self.screen_scale[0],
                                                                       87 * self.screen_scale[1]))
        self.health_text_rect = self.health_bar_image.get_rect(center=(self.health_bar_image.get_width() / 2,
                                                                       self.health_bar_image.get_height() / 2))

        self.resource_bar_image = resource_bar_image
        self.base_resource_bar_image = resource_bar_image.copy()
        self.resource_bar_rect = self.resource_bar_image.get_rect(topleft=(290 * self.screen_scale[0],
                                                                           123 * self.screen_scale[1]))
        self.resource_text_rect = self.resource_bar_image.get_rect(center=(self.health_bar_image.get_width() / 2,
                                                                           self.health_bar_image.get_height() / 2))

        self.guard_bar_image = guard_bar_image
        self.base_guard_bar_image = guard_bar_image.copy()
        self.guard_bar_rect = self.guard_bar_image.get_rect(topleft=(290 * self.screen_scale[0],
                                                                     161 * self.screen_scale[1]))
        self.guard_text_rect = self.guard_bar_image.get_rect(center=(self.health_bar_image.get_width() / 2,
                                                                     self.health_bar_image.get_height() / 2))

        self.bar_size = self.base_health_bar_image.get_size()
        self.last_health_value = None
        self.last_resource_value = None
        self.last_guard_value = None

    def value_input(self, who):
        if self.last_health_value != who.health:
            self.last_health_value = who.health
            self.health_bar_image = self.base_health_bar_image.copy()
            percent = 1 - (who.health / who.max_health)
            bar = Surface((self.bar_size[0] * percent, self.bar_size[1]))
            bar.fill((0, 0, 0))
            self.health_bar_image.blit(bar, (self.bar_size[0] - bar.get_width(), 0))
            value_text = self.font.render(str(int(self.last_health_value)) + " / " + str(who.max_health), True,
                                          (255, 255, 255))
            self.health_bar_image.blit(value_text, self.health_text_rect)
            self.image.blit(self.health_bar_image, self.health_bar_rect)

        if self.last_resource_value != who.resource:
            self.last_resource_value = who.resource
            self.resource_bar_image = self.base_resource_bar_image.copy()
            percent = 1 - (who.resource / who.max_resource)
            bar = Surface((self.bar_size[0] * percent, self.bar_size[1]))
            bar.fill((0, 0, 0))
            self.resource_bar_image.blit(bar, (self.bar_size[0] - bar.get_width(), 0))
            value_text = self.font.render(str(int(self.last_resource_value)) + " / " + str(who.max_resource), True,
                                          (255, 255, 255))
            self.resource_bar_image.blit(value_text, self.resource_text_rect)
            self.image.blit(self.resource_bar_image, self.resource_bar_rect)

        if self.last_guard_value != who.guard_meter:
            self.last_guard_value = who.guard_meter
            self.guard_bar_image = self.base_guard_bar_image.copy()
            percent = 1 - (who.guard_meter / who.max_guard)
            bar = Surface((self.bar_size[0] * percent, self.bar_size[1]))
            bar.fill((0, 0, 0))
            self.guard_bar_image.blit(bar, (self.bar_size[0] - bar.get_width(), 0))
            value_text = self.font.render(str(int(self.last_guard_value)) + " / " + str(who.max_guard), True,
                                          (255, 255, 255))
            self.guard_bar_image.blit(value_text, self.guard_text_rect)
            self.image.blit(self.guard_bar_image, self.guard_bar_rect)


class FPSCount(UIBattle):
    def __init__(self, parent):
        self._layer = 12
        UIBattle.__init__(self, player_interact=False)
        self.image = Surface((80 * self.screen_scale[0], 40 * self.screen_scale[1]), SRCALPHA)
        self.base_image = self.image.copy()
        self.font = Font(self.ui_font["main_button"], int(30 * self.screen_scale[1]))
        self.clock = parent.clock
        fps_text = self.font.render("60", True, (255, 60, 60))
        self.text_rect = fps_text.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.rect = self.image.get_rect(topleft=self.screen_rect.topleft)

    def update(self):
        """Update current fps"""
        self.image = self.base_image.copy()
        fps = str(int(self.clock.get_fps()))
        fps_text = self.font.render(fps, True, (255, 60, 60))
        self.image.blit(fps_text, self.text_rect)


class YesNo(UIBattle):
    def __init__(self, images):
        UIBattle.__init__(self)
        self._layer = 5
        self.yes_image = images["yes"]
        self.no_image = images["no"]

        self.yes_zoom_animation_timer = 0
        self.no_zoom_animation_timer = 0

        self.image = Surface((self.yes_image.get_width() * 2.5, self.yes_image.get_height() * 1.5), SRCALPHA)
        self.base_image = self.image.copy()

        self.pos = Vector2(self.screen_size[0] / 2, 400 * self.screen_scale[1])
        yes_image_rect = self.yes_image.get_rect(midleft=(0, self.image.get_height() / 2))
        no_image_rect = self.no_image.get_rect(midright=(self.image.get_width(), self.image.get_height() / 2))
        self.image.blit(self.yes_image, yes_image_rect)
        self.image.blit(self.no_image, no_image_rect)
        self.base_image2 = self.image.copy()
        self.selected = None

        self.rect = self.image.get_rect(center=self.pos)

    def update(self):
        yes_image_rect = self.yes_image.get_rect(midleft=(0, self.image.get_height() / 2))
        no_image_rect = self.no_image.get_rect(midright=(self.image.get_width(),
                                                         self.image.get_height() / 2))
        cursor_pos = (self.battle.main_player_battle_cursor.pos[0] - self.rect.topleft[0],
                      self.battle.main_player_battle_cursor.pos[1] - self.rect.topleft[1])
        if yes_image_rect.collidepoint(cursor_pos):
            self.image = self.base_image.copy()
            self.no_zoom_animation_timer = 0
            if not self.yes_zoom_animation_timer:
                self.yes_zoom_animation_timer = 0.01
                yes_zoom_animation_timer = 1.01
            else:
                self.yes_zoom_animation_timer += self.battle.dt / 5
                yes_zoom_animation_timer = 1 + self.yes_zoom_animation_timer
                if self.yes_zoom_animation_timer > 0.2:
                    yes_zoom_animation_timer = 1.2 - (self.yes_zoom_animation_timer - 0.2)
                    if self.yes_zoom_animation_timer > 0.4:
                        self.yes_zoom_animation_timer = 0

            yes_image = smoothscale(self.yes_image, (self.yes_image.get_width() * yes_zoom_animation_timer,
                                                     self.yes_image.get_height() * yes_zoom_animation_timer))
            yes_image_rect = yes_image.get_rect(midleft=(0, self.image.get_height() / 2))
            self.image.blit(yes_image, yes_image_rect)
            self.image.blit(self.no_image, no_image_rect)

        elif no_image_rect.collidepoint(cursor_pos):
            self.image = self.base_image.copy()
            self.yes_zoom_animation_timer = 0
            if not self.no_zoom_animation_timer:
                self.no_zoom_animation_timer = 0.01
                no_zoom_animation_timer = 1.01
            else:
                self.no_zoom_animation_timer += self.battle.dt / 5
                no_zoom_animation_timer = 1 + self.no_zoom_animation_timer
                if self.no_zoom_animation_timer > 0.2:
                    no_zoom_animation_timer = 1.2 - (self.no_zoom_animation_timer - 0.2)
                    if self.no_zoom_animation_timer > 0.4:
                        self.no_zoom_animation_timer = 0

            no_image = smoothscale(self.no_image, (self.no_image.get_width() * no_zoom_animation_timer,
                                                   self.no_image.get_height() * no_zoom_animation_timer))
            no_image_rect = no_image.get_rect(midright=(self.image.get_width(), self.image.get_height() / 2))
            self.image.blit(no_image, no_image_rect)
            self.image.blit(self.yes_image, yes_image_rect)

        elif self.no_zoom_animation_timer or self.yes_zoom_animation_timer:
            self.no_zoom_animation_timer = 0
            self.yes_zoom_animation_timer = 0
            self.image = self.base_image2.copy()

        if self.battle.player_key_press[self.battle.main_player]["Weak"]:
            if yes_image_rect.collidepoint(cursor_pos):
                self.selected = "yes"
            elif no_image_rect.collidepoint(cursor_pos):
                self.selected = "no"
                pass


class CharacterIndicator(UIBattle):
    def __init__(self, character):
        self._layer = 9999999999999999998
        UIBattle.__init__(self, has_containers=True)
        self.font = Font(self.ui_font["main_button"], 42)
        self.character = character
        self.height_adjust = self.character.sprite_size * 3.5
        if character.player_control:
            text = character.game_id

            self.image = text_render_with_bg(text,
                                             Font(self.ui_font["manuscript_font"], int(42 * self.screen_scale[1])),
                                             gf_colour=team_colour[self.character.team], o_colour=Color("white"))
        else:
            text = "C" + str(character.team)

            self.image = text_render_with_bg(text,
                                             Font(self.ui_font["manuscript_font"], int(32 * self.screen_scale[1])),
                                             gf_colour=team_colour[self.character.team], o_colour=Color("white"))

        self.base_pos = None
        self.pos = self.character.pos
        self.rect = self.image.get_rect(midbottom=self.pos)

    def update(self, dt):
        if self.base_pos != self.character.base_pos:
            self.base_pos = self.character.base_pos.copy()
            self.pos = (self.character.pos[0], (self.character.pos[1] - self.height_adjust))
            self.rect.midbottom = self.pos


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
        if mouse_pos and self.rect.collidepoint(mouse_pos):
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


class UnitSelector(UIBattle):
    def __init__(self, pos, image, icon_scale=1):
        self._layer = 10
        UIBattle.__init__(self, player_interact=False)
        self.image = image
        self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)
        self.icon_scale = icon_scale
        self.current_row = 0
        self.max_row_show = 2
        self.row_size = 0
        self.scroll = None  # got add after create scroll object

    def setup_unit_icon(self, troop_icon_group, subunit_list):
        """Setup character selection list in selector ui"""
        if troop_icon_group:  # remove all old icon first before making new list
            for icon in troop_icon_group:
                icon.kill()
                del icon

        if subunit_list:
            for this_subunit in subunit_list:
                max_column_show = int(
                    self.image.get_width() / ((this_subunit.portrait.get_width() * self.icon_scale * 1.5)))
                break
            current_index = int(self.current_row * max_column_show)  # the first index of current row
            self.row_size = len(subunit_list) / max_column_show

            if not self.row_size.is_integer():
                self.row_size = int(self.row_size) + 1

            if self.current_row > self.row_size - 1:
                self.current_row = self.row_size - 1
                current_index = int(self.current_row * max_column_show)

            for index, this_subunit in enumerate(
                    subunit_list):  # add character icon for drawing according to appropriated current row
                if this_subunit.is_leader:
                    if index == 0:
                        start_column = self.rect.topleft[0] + (this_subunit.portrait.get_width() / 1.5)
                        column = start_column
                        row = self.rect.topleft[1] + (this_subunit.portrait.get_height() / 2)
                    if index >= current_index:
                        new_icon = UnitIcon((column, row), this_subunit,
                                            (int(this_subunit.portrait.get_width() * self.icon_scale),
                                             int(this_subunit.portrait.get_height() * self.icon_scale)))
                        troop_icon_group.add(new_icon)
                        column += new_icon.image.get_width() * 1.2
                        if column > self.rect.topright[0] - ((new_icon.image.get_width() * self.icon_scale) * 3):
                            row += new_icon.image.get_height() * 1.5
                            column = start_column
                        if row > self.rect.bottomright[1] - ((new_icon.image.get_height() / 2) * self.icon_scale):
                            break  # do not draw for row that exceed the box
        self.scroll.change_image(new_row=self.current_row, row_size=self.row_size)


class UnitIcon(UIBattle, Sprite):
    colour = None

    def __init__(self, pos, unit, size):
        self._layer = 11
        UIBattle.__init__(self, has_containers=True)
        self.who = unit  # link character object so when click can correctly select or go to position
        self.pos = pos  # pos on character selector ui
        self.place_pos = pos  # pos when drag by mouse
        self.name = ""  # not used for character icon, for checking with CampIcon
        self.selected = False
        self.right_selected = False

        self.leader_image = smoothscale(unit.portrait, size)  # scale leader image to fit the icon
        self.not_selected_image = Surface((self.leader_image.get_width() + (self.leader_image.get_width() / 7),
                                           self.leader_image.get_height() + (
                                                   self.leader_image.get_height() / 7)))  # create image black corner block
        self.selected_image = self.not_selected_image.copy()
        self.selected_image.fill((0, 0, 0))  # fill black corner
        self.right_selected_image = self.not_selected_image.copy()
        self.right_selected_image.fill((150, 150, 150))  # fill grey corner
        self.not_selected_image.fill((255, 255, 255))  # fill white corner

        for image in (
                self.not_selected_image, self.selected_image,
                self.right_selected_image):  # add team colour and leader image
            center_image = Surface((self.leader_image.get_width() + (self.leader_image.get_width() / 14),
                                    self.leader_image.get_height() + (
                                            self.leader_image.get_height() / 14)))  # create image block
            center_image.fill(self.colour[self.who.team])  # fill colour according to team
            image_rect = center_image.get_rect(center=((image.get_width() / 2),
                                                       (image.get_height() / 2)))
            image.blit(center_image, image_rect)  # blit colour block into border image
            self.leader_image_rect = self.leader_image.get_rect(center=(image.get_width() / 2,
                                                                        image.get_height() / 2))
            image.blit(self.leader_image, self.leader_image_rect)  # blit leader image

        self.image = self.not_selected_image
        self.rect = self.image.get_rect(center=self.pos)

    def change_pos(self, pos):
        """change position of icon to new one"""
        self.rect = self.image.get_rect(center=pos)

    def change_image(self, new_image=None, change_side=False):
        """For changing side"""
        if change_side:
            self.image.fill((144, 167, 255))
            if self.who.team == 2:
                self.image.fill((255, 114, 114))
            self.image.blit(self.leader_image, self.leader_image_rect)
        if new_image:
            self.leader_image = new_image
            self.image.blit(self.leader_image, self.leader_image_rect)

    def selection(self, how="left"):
        if how == "left":
            if self.selected:
                self.selected = False
                self.image = self.not_selected_image
            else:
                self.selected = True
                self.right_selected = False
                self.image = self.selected_image
        else:
            if self.right_selected:
                self.right_selected = False
                self.image = self.not_selected_image
            else:
                self.right_selected = True
                self.selected = False
                self.image = self.right_selected_image


class ScoreBoard(UIBattle):
    def __init__(self, body_part):
        UIBattle.__init__(self, player_interact=False)
        self.body_part = body_part
        self.font = Font(self.ui_font["main_button"], int(20 * self.screen_scale[1]))

    def update(self):
        """Add score and gold to scoreboard image"""
        score_text = self.font.render(minimise_number_text(self.battle.mission_score) + "/" +
                                      str(self.battle.reserve_resurrect_mission_score), True, (0, 0, 0))
        gold_text = self.font.render(minimise_number_text(self.battle.mission_gold), True, (0, 0, 0))

        if self.body_part.owner.sprite_direction == "l_side":
            score_rect = score_text.get_rect(center=(self.body_part.base_image.get_width() / 3,
                                                     self.body_part.base_image.get_height() / 2.5))
            gold_rect = gold_text.get_rect(center=(self.body_part.base_image.get_width() / 3,
                                                   self.body_part.base_image.get_height() / 1.3))
        else:
            score_rect = score_text.get_rect(center=(self.body_part.base_image.get_width() / 1.5,
                                                     self.body_part.base_image.get_height() / 2.5))
            gold_rect = gold_text.get_rect(center=(self.body_part.base_image.get_width() / 1.5,
                                                   self.body_part.base_image.get_height() / 1.3))
        self.body_part.base_image = self.body_part.base_image.copy()
        self.body_part.base_image.blit(score_text, score_rect)
        self.body_part.base_image.blit(gold_text, gold_rect)


class CityMap(UIBattle):
    def __init__(self, images):
        UIBattle.__init__(self)
        self._layer = 1
        self.selected_animation_timer = []
        self.images = images
        self.image = self.images["map"]
        self.base_image = self.image.copy()

        self.base_image2 = self.image.copy()
        self.selected = None

        self.rect = self.image.get_rect(topleft=(0, 0))

        self.stage_select_rect = {"herbalist": self.images["herbalist"].get_rect(center=(252 * self.screen_scale[0], 691 * self.screen_scale[1])),
                                  "barrack": self.images["barrack"].get_rect(center=(428 * self.screen_scale[0], 394 * self.screen_scale[1])),
                                  "blacksmith": self.images["blacksmith"].get_rect(center=(438 * self.screen_scale[0], 579 * self.screen_scale[1])),
                                  "cathedral": self.images["cathedral"].get_rect(center=(711 * self.screen_scale[0], 645 * self.screen_scale[1])),
                                  "plaza": self.images["plaza"].get_rect(center=(884 * self.screen_scale[0], 704 * self.screen_scale[1])),
                                  "tavern": self.images["tavern"].get_rect(center=(970 * self.screen_scale[0], 801 * self.screen_scale[1])),
                                  "garden": self.images["garden"].get_rect(center=(1022 * self.screen_scale[0], 497 * self.screen_scale[1])),
                                  "artificer": self.images["artificer"].get_rect(center=(1339 * self.screen_scale[0], 382 * self.screen_scale[1])),
                                  "market": self.images["market"].get_rect(center=(1377 * self.screen_scale[0], 629 * self.screen_scale[1])),
                                  "scriptorium": self.images["scriptorium"].get_rect(center=(1617 * self.screen_scale[0], 436 * self.screen_scale[1])),
                                  "throne": self.images["throne"].get_rect(center=(1015 * self.screen_scale[0], 109 * self.screen_scale[1])),
                                  "library": self.images["library"].get_rect(center=(730 * self.screen_scale[0], 202 * self.screen_scale[1])),
                                  "hall": self.images["hall"].get_rect(center=(1021 * self.screen_scale[0], 199 * self.screen_scale[1])),
                                  "council": self.images["council"].get_rect(center=(1298 * self.screen_scale[0], 198 * self.screen_scale[1]))
                                  }

        for image, rect in self.stage_select_rect.items():
            self.base_image.blit(self.images[image], rect)
        self.image = self.base_image.copy()
        self.selected_map = None

    def update(self):
        cursor_pos = (self.battle.cursor.pos[0] - self.rect.topleft[0],
                      self.battle.cursor.pos[1] - self.rect.topleft[1])
        found_select = False
        self.selected_map = None
        for image, rect in self.stage_select_rect.items():
            if rect.collidepoint(cursor_pos):
                found_select = True
                self.image = self.base_image.copy()
                if self.selected_animation_timer:  # already has previous hovering
                    if self.selected_animation_timer[0] != image:  # different hovering
                        self.selected_animation_timer = [image, 0]
                else:
                    self.selected_animation_timer = [image, 0]
                self.selected_animation_timer[1] += self.battle.dt / 5
                zoom_animation_timer = 1 + self.selected_animation_timer[1]
                if self.selected_animation_timer[1] > 0.2:
                    zoom_animation_timer = 1.2 - (self.selected_animation_timer[1] - 0.2)
                    if self.selected_animation_timer[1] > 0.4:
                        self.selected_animation_timer[1] = 0

                new_image = smoothscale(self.images[image],
                                        (self.images[image].get_width() * zoom_animation_timer,
                                         self.images[image].get_height() * zoom_animation_timer))
                self.image.blit(new_image, new_image.get_rect(center=rect.center))

                if self.battle.player_key_press[self.battle.main_player]["Weak"]:
                    self.selected_map = image
                break

        if not found_select:
            self.selected_animation_timer = []
            self.image = self.base_image


class CharacterInteractPrompt(UIBattle):
    def __init__(self, image):
        """Weak button prompt that indicate player can talk to target"""
        self._layer = 9999999999999999999998
        UIBattle.__init__(self, player_interact=False)
        self.character = None
        self.target = None
        font = Font(self.ui_font["manuscript_font"], int(40 * self.screen_scale[1]))
        text_surface = text_render_with_bg("Talk", font)
        self.image = Surface((150 * self.screen_scale[0], 50 * self.screen_scale[1]), SRCALPHA)
        text_rect = text_surface.get_rect(midright=self.image.get_rect().midright)
        self.image.blit(text_surface, text_rect)
        self.image.blit(image, image.get_rect(midleft=self.image.get_rect().midleft))

        self.rect = self.image.get_rect(center=(0, 0))

    def add_to_screen(self, character, target):
        self.character = character
        self.target = target
        self.rect = self.image.get_rect(midbottom=(self.target[0] * self.screen_scale[0],
                                                   self.target[1] * self.screen_scale[1]))
        if self not in self.battle.battle_camera:
            self.battle.battle_camera.add(self)
            self.battle.effect_updater.add(self)

    def update(self, *args):
        if self.target and not 100 < abs(self.character.base_pos[0] - self.target[0]) < 250:
            # check if player move too far from current target prompt
            self.clear()

    def clear(self):
        self.character = None
        self.target = None
        if self in self.battle.battle_camera:
            self.battle.battle_camera.remove(self)
            self.battle.effect_updater.remove(self)


class CharacterSpeechBox(UIBattle):
    images = {}
    font_name = "manuscript_font"

    def __init__(self, character, text, specific_timer=None, player_input_indicator=False, cutscene_event=None):
        """Speech box that appear from character head"""
        self._layer = 9999999999999999998
        UIBattle.__init__(self, player_interact=False, has_containers=True)
        self.body = self.images["speech_body"]
        self.left_corner = self.images["speech_start"]
        self.right_corner = self.images["speech_end"]
        self.font_size = int(34 * self.screen_scale[1])

        self.left_corner_rect = self.left_corner.get_rect(topleft=(0, 0))  # The starting point

        self.character = character
        self.player_input_indicator = player_input_indicator
        self.cutscene_event = cutscene_event
        self.head_part = self.character.body_parts["p1_head"]  # assuming character always has p1 head
        self.base_pos = self.character.base_pos.copy()
        self.finish_unfolding = False
        self.current_length = self.left_corner.get_width()  # current unfolded length start at 20
        self.text_surface = Font(self.ui_font[self.font_name], self.font_size).render(text, True, (0, 0, 0))
        self.base_image = Surface((self.text_surface.get_width() + int(self.left_corner.get_width() * 1.5),
                                   self.left_corner.get_height()), SRCALPHA)
        self.base_image.blit(self.left_corner, self.left_corner_rect)  # start animation with the left corner
        self.max_length = self.base_image.get_width()  # max length of the body, not counting the end corner
        self.rect = self.base_image.get_rect(midleft=self.head_part.rect.center)
        if specific_timer:
            self.timer = specific_timer
        else:
            self.timer = 3
            if len(text) > 20:
                self.timer += int(len(text) / 20)

    def update(self, dt):
        """Play unfold animation and blit drama text at the end"""
        if self.current_length < self.max_length:  # keep unfolding if not yet reach max length
            body_rect = self.body.get_rect(topleft=(self.current_length, 0))  # body of the drama popup
            self.base_image.blit(self.body, body_rect)
            self.image = self.base_image.copy()
            self.current_length += self.body.get_width()
        elif not self.finish_unfolding:
            # right corner end
            right_corner_rect = self.right_corner.get_rect(topright=(self.base_image.get_width(), 0))
            self.base_image.blit(self.right_corner, right_corner_rect)
            if self.player_input_indicator:  # add player weak button indicate for closing speech in cutscene
                rect = self.images["button_weak"].get_rect(topright=(self.base_image.get_width(),
                                                                     self.right_corner.get_height() * 0.8))
                self.base_image.blit(self.images["button_weak"], rect)
            self.image = self.base_image.copy()
            self.finish_unfolding = True

        else:  # finish animation, count down timer
            self.timer -= dt
            if self.timer <= 0:
                self.kill()
                return

        if self.character.alive is False:  # kill speech if character die
            self.kill()
            return

        if self.character.sprite_direction == "l_side":  # left direction facing
            if self.head_part.rect.midleft[0] - (
                    self.battle.shown_camera_pos[0] - self.battle.camera.camera_w_center) < self.base_image.get_width():
                # text will exceed screen, go other way
                self.image = self.base_image.copy()
                self.rect.bottomleft = self.head_part.rect.midright
            else:
                self.image = pygame.transform.flip(self.base_image, 1, 0)
                self.rect.bottomright = self.head_part.rect.midleft

        else:  # right direction facing
            if (self.battle.shown_camera_pos[0] + self.battle.camera.camera_w_center) - \
                    self.head_part.rect.midright[0] < self.base_image.get_width():
                # text will exceed screen, go other way
                self.image = pygame.transform.flip(self.base_image, 1, 0)
                self.rect.bottomright = self.head_part.rect.midleft
            else:
                self.image = self.base_image.copy()
                self.rect.bottomleft = self.head_part.rect.midright

        if self.rect.midtop[1] < 0:  # exceed top scene
            self.rect.midtop = Vector2(self.rect.midtop[0], 0)

        if self.current_length >= self.max_length:
            # blit text when finish unfold
            text_rect = self.text_surface.get_rect(center=(int(self.image.get_width() / 2),
                                                           int(self.body.get_height() / 2)))
            self.image.blit(self.text_surface, text_rect)


class DamageNumber(UIBattle):
    def __init__(self, value, pos, critical, team, move=True):
        self._layer = 9999999999999999999
        UIBattle.__init__(self, has_containers=True)
        self.move = move

        if critical:
            self.image = text_render_with_bg(str(value),
                                             Font(self.ui_font["manuscript_font2"], int(76 * self.screen_scale[1])),
                                             gf_colour=team_colour[team])
        else:
            self.image = text_render_with_bg(str(value),
                                             Font(self.ui_font["manuscript_font"], int(46 * self.screen_scale[1])),
                                             gf_colour=team_colour[team])
        self.rect = self.image.get_rect(midbottom=pos)
        self.timer = 0.5

    def update(self, dt):
        self.timer -= dt
        if self.move:
            self.rect.center = (self.rect.center[0], self.rect.center[1] - (dt * 200))
        if self.timer <= 0:
            self.kill()


class WheelUI(UIBattle):
    item_sprite_pool = None
    choice_list_key = {"Down": 1, "Left": 2, "Up": 3, "Right": 4}
    choice_key = tuple(choice_list_key.keys())

    def __init__(self, images, pos, text_size=20):
        """Wheel choice ui to select item"""
        self._layer = 11
        UIBattle.__init__(self)
        self.font = Font(self.ui_font["main_button"], text_size)
        self.pos = pos
        self.choice_list = ()
        self.selected = "Up"

        self.wheel_button_image = images["wheel"]
        self.wheel_selected_button_image = images["wheel_selected"]
        self.wheel_text_image = images["wheel_text"]

        self.base_image2 = Surface((self.wheel_button_image.get_width() * 5,
                                    self.wheel_button_image.get_height() * 4), SRCALPHA)  # empty image
        self.rect = self.base_image2.get_rect(midtop=self.pos)

        image_center = (self.base_image2.get_width() / 2, self.base_image2.get_height() / 2)
        self.wheel_image_with_stuff = []
        self.wheel_selected_image_with_stuff = []
        self.wheel_rect = []
        angle_space = 360 / 4
        angle = 0
        for wheel_button in range(4):
            base_target = Vector2(image_center[0] - (image_center[0] / 2 *
                                                     sin(radians(angle))),
                                  image_center[1] + (image_center[1] / 1.6 *
                                                     cos(radians(angle))))
            angle += angle_space

            self.wheel_image_with_stuff.append(self.wheel_button_image.copy())
            self.wheel_selected_image_with_stuff.append(self.wheel_selected_button_image.copy())
            self.wheel_rect.append(self.wheel_button_image.get_rect(center=base_target))
            self.base_image2.blit(self.wheel_image_with_stuff[wheel_button], self.wheel_rect[wheel_button])
        self.image = self.base_image2.copy()

    def selection(self, key_input):
        self.selected = key_input
        for index, rect in enumerate(self.wheel_rect):
            if self.selected == self.choice_key[index]:
                self.image.blit(self.wheel_selected_image_with_stuff[index], rect)
            else:
                self.image.blit(self.wheel_image_with_stuff[index], rect)
            text_image = self.wheel_text_image.copy()
            text_surface = self.font.render(self.choice_list[index], True, (0, 0, 0))
            text_image.blit(text_surface, text_surface.get_rect(center=(text_image.get_width() / 2,
                                                                        text_image.get_height() / 2)))

            self.image.blit(text_image, text_image.get_rect(center=self.wheel_rect[index].midbottom))

    def change_text_icon(self, blit_list):
        """Add icon or text to the wheel choice"""
        self.image = self.base_image2.copy()
        self.choice_list = blit_list
        for index, item in enumerate(blit_list):
            if item:  # Wheel choice with icon or text inside
                surface = self.item_sprite_pool[self.battle.chapter_sprite_ver]["Normal"][item][1][0]
                rect = surface.get_rect(center=(self.wheel_image_with_stuff[index].get_width() / 2,
                                                self.wheel_image_with_stuff[index].get_height() / 2))
                self.wheel_image_with_stuff[index].blit(surface, rect)
                self.wheel_selected_image_with_stuff[index].blit(surface, rect)
                if self.selected == self.choice_key[index]:
                    self.image.blit(self.wheel_selected_image_with_stuff[index], self.wheel_rect[index])
                else:
                    self.image.blit(self.wheel_image_with_stuff[index], self.wheel_rect[index])
                text_image = self.wheel_text_image.copy()
                text_surface = self.font.render(item, True, (0, 0, 0))
                text_image.blit(text_surface, text_surface.get_rect(center=(text_image.get_width() / 2,
                                                                            text_image.get_height() / 2)))

                self.image.blit(text_image, text_image.get_rect(center=self.wheel_rect[index].midbottom))


class EscBox(UIBattle):
    def __init__(self, image):
        self._layer = 1
        UIBattle.__init__(self, player_interact=False)
        self.pos = (self.screen_size[0] / 2, self.screen_size[1] / 2)
        self.mode = "menu"  # Current menu mode
        self.image = image
        self.rect = self.image.get_rect(center=self.pos)

    def change_mode(self, mode):
        """Change between 0 menu, 1 option, 2 lorebook mode"""
        self.mode = mode


class EscButton(UIBattle):
    def __init__(self, images, pos, text="", text_size=16):
        self._layer = 25
        UIBattle.__init__(self)
        self.pos = pos
        self.images = [image.copy() for image in list(images.values())]
        self.text = text
        self.font = Font(self.ui_font["main_button"], text_size)

        if text != "":  # blit menu text into button image
            text_surface = self.font.render(self.text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=self.images[0].get_rect().center)
            self.images[0].blit(text_surface, text_rect)  # button idle image
            self.images[1].blit(text_surface, text_rect)  # button mouse over image
            self.images[2].blit(text_surface, text_rect)  # button click image

        self.image = self.images[0]
        self.rect = self.image.get_rect(center=self.pos)


class Profiler(cProfile.Profile, UIBattle):

    def __init__(self):
        UIBattle.__init__(self, player_interact=False)
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
