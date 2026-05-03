from datetime import datetime
from random import choice

from pygame import Surface, SRCALPHA

from engine.uibattle.uibattle import UIBattle
from engine.utils.text_making import text_render_with_bg


class TextDrama(UIBattle):
    images = []

    def __init__(self, battle):
        self._layer = 17
        UIBattle.__init__(self, player_cursor_interact=False)
        self.body = {False: self.images["body"], True: self.images["body_bad"]}
        self.left_corner = {False: self.images["start"], True: self.images["start_bad"]}
        self.right_corner = {False: self.images["end"], True: self.images["end_bad"]}
        self.showing_body = None
        self.showing_left_corner = None
        self.showing_right_corner = None
        self.battle = battle
        # drama appear at around center top pos of battle camera
        self.pos = (self.battle.camera_center_x, self.battle.camera_height / 4.8)
        self.font = self.game.drama_font
        self.queue = []  # text list to popup
        self.blit_text = False
        self.current_length = 0
        self.max_length = 0
        self.timer = 0
        self.text_input = ""

    def process_queue(self):
        """Initiate the first text in list and remove it"""
        # add to battle log
        battle_log = self.battle.save_data.save_profile["battle log"]
        battle_log.append(
            ("(" + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + ") At " + self.battle.mission + ", " +
             self.localisation.grab_text(("ui", "log_header_battle")), self.queue[0][1]))
        if len(battle_log) > 500:
            self.battle.save_data.save_profile["battle log"] = battle_log[1:]

        self.slow_drama(self.queue[0])  # Process the first item in list
        self.queue = self.queue[1:]  # Delete already processed item

    def slow_drama(self, input_item):
        """Create text and image to play animation,
        input item should be in array like item with (0=text, 1=sound effect to play)"""
        self.blit_text = False
        self.showing_body = self.body[input_item[0]]
        self.showing_left_corner = self.left_corner[input_item[0]]
        self.showing_right_corner = self.right_corner[input_item[0]]
        self.current_length = self.showing_left_corner.get_width()  # current unfolded length start at 20
        self.text_input = input_item[1]
        if input_item[2] in self.battle.sound_effect_pool:  # play sound effect
            self.battle.add_sound_effect_queue(choice(self.battle.sound_effect_pool[input_item[2]]),
                                               self.battle.camera_pos, 2000, 0)
        self.text_surface = text_render_with_bg(self.text_input, self.font, gf_colour=(225, 225, 225),
                                                o_colour=(20, 20, 20))
        self.image = Surface((self.text_surface.get_width() + int(self.showing_left_corner.get_width() * 4),
                              self.showing_left_corner.get_height()), SRCALPHA)
        self.image.blit(self.showing_left_corner, (0, 0))  # start animation with the left corner
        self.rect = self.image.get_rect(center=self.pos)
        self.max_length = self.image.get_width() - self.showing_left_corner.get_width()  # max length of the body, not counting the end corner
        self.timer = 3 + (len(self.text_input) / 20)  # timer to last is 3 seconds + 1 seconds per 20 characters

    def play_animation(self):
        """Play unfold animation and blit drama text at the end"""
        if self.current_length < self.max_length:  # keep unfolding if not yet reach max length
            body_rect = self.showing_body.get_rect(midleft=(self.current_length,
                                                            int(self.image.get_height() / 2)))  # body of the drama popup
            self.image.blit(self.showing_body, body_rect)
            self.current_length += self.showing_body.get_width()
        elif self.current_length >= self.max_length and not self.blit_text:  # blit text when finish unfold and only once
            text_rect = self.text_surface.get_rect(center=(int(self.image.get_width() / 2),
                                                           int(self.image.get_height() / 2)))
            self.image.blit(self.text_surface, text_rect)
            right_corner_rect = self.showing_right_corner.get_rect(
                topright=(self.image.get_width(), 0))  # right corner end
            self.image.blit(self.showing_right_corner, right_corner_rect)
            self.blit_text = True
