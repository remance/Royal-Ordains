from datetime import datetime
from random import choice

from pygame import Surface, SRCALPHA
from pygame.font import Font
from pygame.transform import smoothscale, flip

from engine.constants import *
from engine.uimenu.uimenu import UIMenu
from engine.utils.text_making import text_render_with_bg, make_long_text, calculate_long_text_size


class UIBattle(UIMenu):
    def __init__(self, player_cursor_interact=False, has_containers=False):
        """
        Parent class for all battle menu user interface that exist inside of battle camera, 
        typically player cannot directly interact with them
        """
        from engine.battle.battle import Battle
        UIMenu.__init__(self, player_cursor_interact=player_cursor_interact, has_containers=has_containers)
        self.battle = Battle.battle
        self.camera = self.battle.camera
        self.battle_camera_ui_drawer = self.battle.battle_camera_ui_drawer
        self.battle_effect_updater = self.battle.battle_effect_updater

    def check_draw(self):
        battle_camera_ui_drawer = self.battle_camera_ui_drawer
        if self.rect.colliderect(self.camera.rect):
            if self not in battle_camera_ui_drawer:
                battle_camera_ui_drawer.add(self)
        elif self in battle_camera_ui_drawer:
            battle_camera_ui_drawer.remove(self)


class CharacterCommandIndicator(UIBattle):
    def __init__(self, pos_y, move_image, attack_image):
        self._layer = 9999999999999999998
        UIBattle.__init__(self, has_containers=True)
        self.move_image = move_image.copy()
        self.attack_image = attack_image.copy()
        self.command_dict = {"move": self.move_image, "attack": self.attack_image}
        self.image = self.move_image
        self.pos_y = pos_y * self.screen_scale_height
        self.rect = self.image.get_rect(center=(0, 0))
        self.check_order = None
        self.leader = None

    def setup(self, leader=None):
        if leader:
            self.leader = leader
            self.move_image.blit(self.leader.icon["right"], self.leader.icon["right"].get_rect(topleft=(0, 0)))
            self.attack_image.blit(self.leader.icon["right"], self.leader.icon["right"].get_rect(topleft=(0, 0)))
            self.battle_effect_updater.add(self)
        else:
            self.battle_effect_updater.remove(self)

    def update(self, dt):
        if self.leader.alive:
            order_check = self.leader.true_commander_order
            if order_check and "stay" not in order_check:  # only show move and attack command
                if self not in self.battle_camera_ui_drawer:
                    self.battle_camera_ui_drawer.add(self)
                if self.check_order != order_check:
                    self.check_order = order_check
                    self.image = self.command_dict[order_check[0]]
                    self.rect.center = (order_check[1] * self.screen_scale_width, self.pos_y)
            else:
                if self in self.battle_camera_ui_drawer:
                    self.battle_camera_ui_drawer.remove(self)

        else:
            if self in self.battle_camera_ui_drawer:
                self.battle_camera_ui_drawer.remove(self)

    def check_draw(self):
        """For when the game speed is paused to 0"""
        self.update(0)


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
        self.image = Surface((150 * self.screen_scale_width, 55 * self.screen_scale_height), SRCALPHA)
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
                              (10 * self.screen_scale_width), 55 * self.screen_scale_height), SRCALPHA)
        text_rect = text_surface.get_rect(midright=self.image.get_rect().midright)
        self.image.blit(text_surface, text_rect)
        self.image.blit(self.button_image, self.button_image.get_rect(midleft=self.image.get_rect().midleft))

        self.rect = self.image.get_rect(midbottom=(self.target_pos[0] * self.screen_scale_width,
                                                   self.target_pos[1] * self.screen_scale_height))
        if self not in self.battle_camera_ui_drawer:
            self.battle_camera_ui_drawer.add(self)
            self.battle_effect_updater.add(self)

    def update(self, dt):
        self.check_draw()
        if self.target_pos and not 100 < abs(self.character.base_pos[0] - self.target_pos[0]) < 250:
            # check if player move too far from current target prompt
            self.clear()

    def clear(self):
        self.character = None
        self.target = None
        self.target_pos = None
        if self in self.battle_camera_ui_drawer:
            self.battle_camera_ui_drawer.remove(self)
            self.battle_effect_updater.remove(self)


class CharacterSpeechBox(UIBattle):
    images = {}
    simple_font = False

    def __init__(self, character, text, specific_timer=None, player_input_indicator=False, cutscene_event=None,
                 voice=False, font_size=60, max_text_width=800):
        """Speech box that appear from character head"""
        self._layer = 9999999999999999998
        UIBattle.__init__(self, player_cursor_interact=False, has_containers=True)
        font = "simple"
        if not self.simple_font and self.game.language in ("en", "es", "it", "fr", "de",):
            # culture font only available for latin alphabet sadly
            font = "culture_" + character.culture

        self.font_size = int(font_size * self.screen_scale_height)
        self.font = Font(self.ui_font[font], self.font_size)
        max_text_width *= self.screen_scale_width

        self.text_surface = Surface(calculate_long_text_size(text, self.font, self.font_size, max_text_width), SRCALPHA)
        self.text_surface.fill((224, 224, 224))
        make_long_text(self.text_surface, text, (0, 0), self.font)

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

        self.right_image = self.base_image
        self.left_image = flip(self.base_image, 1, 0)

        text_rect = self.text_surface.get_rect(topleft=start_mid_rect.topright)
        self.right_image.blit(self.text_surface, text_rect)

        text_rect = self.text_surface.get_rect(topright=(self.base_image.get_width() - start_mid_rect.topright[0],
                                                         start_mid_rect.topright[1]))
        self.left_image.blit(self.text_surface, text_rect)

        if player_input_indicator:  # add player weak button indicate for closing speech in cutscene
            self.left_image.blit(self.images["button_weak"],
                                 self.images["button_weak"].get_rect(topleft=(0, text_rect.height * 1.2)))

            self.right_image.blit(self.images["button_weak"],
                                  self.images["button_weak"].get_rect(topright=(self.base_image.get_width(),
                                                                                text_rect.height * 1.2)))

        self.character = character
        self.character.speech = self
        self.player_input_indicator = player_input_indicator
        self.cutscene_event = cutscene_event
        self.base_pos = self.character.base_pos.copy()
        self.finish_unfolding = False
        self.direction_left = False
        self.current_length = start_top.get_width()

        self.max_length = self.base_image.get_width()

        self.image = self.base_image.subsurface((0, 0, self.current_length, self.base_image.get_height()))
        self.rect = self.image.get_rect(midleft=self.character.rect.center)

        if voice:
            self.battle.add_sound_effect_queue(choice(self.battle.sound_effect_pool[voice[0]]),
                                               self.character.base_pos, voice[1],
                                               voice[2], volume="voice")
        elif voice is False:  # None will play no sound
            self.battle.add_sound_effect_queue(choice(self.battle.sound_effect_pool["parchment_write"]),
                                               self.character.base_pos, 1000,
                                               0, volume="voice")

        if specific_timer:
            self.timer = specific_timer
        else:
            self.timer = 3
            if len(text) > 20:
                self.timer += int(len(text) / 20)

        self.battle.save_data.save_profile["battle log"].append(
            ("(" + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + ") At " + self.battle.stage + ", " +
             self.character.name + ": ", text))
        if len(self.battle.save_data.save_profile["battle log"]) > 500:
            self.battle.save_data.save_profile["battle log"] = self.battle.save_data.save_profile["battle log"][
                                                               1:]

    def update(self, dt):
        """Play unfold animation and blit text at the end"""
        if self.character.alive:  # update head position
            self.direction_left = False
            # always use p1 head to place speak
            head_rect = (
                (self.character.pos[0] + (
                        self.character.current_animation_direction["head"][0] * self.screen_scale_width)),
                (self.character.pos[1] + (
                        self.character.current_animation_direction["head"][1] * self.screen_scale_height)))
            if self.character.direction == "left":  # left direction facing
                if head_rect[0] - (
                        self.battle.shown_camera_center_pos[0] - self.battle.camera.camera_w_center) < self.max_length:
                    self.base_image = self.right_image
                    self.rect = self.image.get_rect(bottomleft=head_rect)
                else:
                    # text will exceed screen, go other way
                    self.direction_left = True
                    self.base_image = self.left_image
                    self.rect = self.image.get_rect(bottomright=head_rect)

            else:  # right direction facing
                if (self.battle.shown_camera_center_pos[0] + self.battle.camera.camera_w_center) - \
                        head_rect[0] < self.max_length:
                    # text will exceed screen, go other way
                    self.direction_left = True
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
            if self.direction_left:
                self.image = self.base_image.subsurface((self.max_length - self.current_length, 0,
                                                         self.current_length, self.image.get_height()))
            else:
                self.image = self.base_image.subsurface((0, 0, self.current_length, self.image.get_height()))

        else:  # finish animation, count down timer
            self.image = self.base_image
            self.timer -= dt
            if self.timer <= 0:
                self.character.speech = None
                self.kill()
                return

        self.check_draw()


class StrategyIcon(UIBattle):
    strategy_icons = {}

    def __init__(self, icon, base_pos_x):
        self._layer = 9999999999999999996
        UIBattle.__init__(self, has_containers=True)
        self.timer = 5
        self.image = self.strategy_icons[icon]

        self.rect = self.image.get_rect(center=(base_pos_x * self.screen_scale_width,
                                                800 * self.screen_scale_height))

    def update(self, dt):
        self.check_draw()
        self.timer -= dt
        if self.timer <= 0:
            self.kill()


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
        self.check_draw()
        self.timer -= dt
        if self.move:
            self.rect.center = (self.rect.center[0], self.rect.center[1] - (dt * 200))
        if self.timer <= 0:
            self.kill()

