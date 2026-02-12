from random import choice
from pygame.mixer import find_channel
from engine.effect.effect import Effect, DamageEffect, TrapEffect, ShowcaseEffect


def next_animation_frame(self):
    self.frame_timer = 0
    if "reverse" not in self.current_action:
        if self.show_frame != self.max_show_frame:  # continue next frame
            self.show_frame += 1
        else:  # reach end frame
            self.show_frame = 0
            if "repeat" not in self.current_action:  # not loop
                return True
    else:
        if self.show_frame:  # continue next frame
            self.show_frame -= 1
        else:  # reach end frame
            if "repeat" not in self.current_action:  # not loop
                return True
            else:
                self.show_frame = self.max_show_frame

    self.current_animation_frame = self.current_animation[self.show_frame]
    self.current_animation_direction = self.current_animation_frame[self.direction]
    if self.current_animation_frame["sound_effect"]:  # play sound from animation
        sound = self.current_animation_frame["sound_effect"]
        self.battle.add_sound_effect_queue(self.sound_effect_pool[sound[0]][0],
                                           self.pos, sound[1], sound[2])


def showcase_next_animation_frame(self):
    self.frame_timer = 0
    if "reverse" not in self.current_action:
        if self.show_frame != self.max_show_frame:  # continue next frame
            self.show_frame += 1
        else:  # reach end frame
            self.show_frame = 0
            if "repeat" not in self.current_action:  # not loop
                return True
    else:
        if self.show_frame:  # continue next frame
            self.show_frame -= 1
        else:  # reach end frame
            if "repeat" not in self.current_action:  # not loop
                return True
            else:
                self.show_frame = self.max_show_frame

    self.current_animation_frame = self.current_animation[self.show_frame]
    self.current_animation_direction = self.current_animation_frame[self.direction]
    if self.current_animation_frame["sound_effect"]:  # play sound from animation
        sound = self.current_animation_frame["sound_effect"]
        sound_effect_channel = find_channel()
        if sound_effect_channel:
            sound_effect_channel.set_volume(self.battle.play_effect_volume)
            sound_effect_channel.play(choice(self.sound_effect_pool[sound[0]]))


def play_showcase_animation(self, dt, hold_check):
    """
    Play character animation in lorebook showcase
    :param self: Character object
    :param dt: Time
    :param hold_check: Check if holding animation frame or not
    :return: Boolean of animation finish playing or not
    """
    self.frame_timer += dt
    if self.frame_timer >= self.final_animation_frame_play_time:  # start next frame or end animation
        if self.next_animation_frame():
            return True

        self.final_animation_frame_play_time = self.animation_frame_play_time
        if "play_time_mod" in self.current_animation_frame:
            self.final_animation_frame_play_time *= self.current_animation_frame["play_time_mod"]

        for key, part_data in self.current_animation_direction["effects"].items():
            if part_data[8] and part_data[0] in self.effect_list:  # independent effect must exist in effect list
                if "trap" in self.effect_list[part_data[0]]["Property"]:  # trap effect
                    pass
                else:
                    ShowcaseEffect(self, part_data, base_target_pos=self.current_action["target"])

        self.update_sprite = True
    return False


def play_battle_animation(self, dt, hold_check):
    """
    Play character animation in battle
    :param self: Character object
    :param dt: Time
    :param hold_check: Check if holding animation frame or not
    :return: Boolean of animation finish playing or not
    """
    if not hold_check:
        self.frame_timer += dt
        if self.frame_timer >= self.final_animation_frame_play_time:  # start next frame or end animation
            if self.next_animation_frame():
                return True

            self.final_animation_frame_play_time = self.animation_frame_play_time
            if "play_time_mod" in self.current_animation_frame:
                self.final_animation_frame_play_time *= self.current_animation_frame["play_time_mod"]

            self.sprite_deal_damage = False
            for key, part_data in self.current_animation_direction["effects"].items():
                if part_data[8] and part_data[0] in self.effect_list:  # independent effect must exist in effect list
                    if "trap" in self.effect_list[part_data[0]]["Property"]:  # trap effect
                        TrapEffect(self, part_data, self.current_moveset)
                    elif self.effect_list[part_data[0]]["Damage"]:  # damage effect
                        DamageEffect(self, part_data, self.current_moveset,
                                     base_target_pos=self.current_action["target"])
                    else:  # no damage effect
                        if self.current_moveset:
                            Effect(self, part_data, self.current_moveset,
                                   base_target_pos=self.current_action["target"])
                        else:
                            Effect(self, part_data)
            if "sprite_deal_damage" in self.current_animation_frame["property"] and self.current_moveset:
                self.sprite_deal_damage = True

            self.update_sprite = True

    return False


def play_cutscene_animation(self, dt, hold_check):
    """
    Play character animation during cutscene, does not account for animation speed stat
    :param self: Character object
    :param dt: Time
    :param hold_check: Check if holding animation frame or not
    :return: Boolean of animation finish playing or not
    """
    if not hold_check:  # not holding current frame
        self.frame_timer += dt
        if self.frame_timer >= self.final_animation_frame_play_time:  # start next frame or end animation
            if self.next_animation_frame():
                return True

            # check if new frame has play speed mod
            self.final_animation_frame_play_time = self.default_animation_play_time
            if "play_time_mod" in self.current_animation_frame:
                self.final_animation_frame_play_time *= self.current_animation_frame["play_time_mod"]

            self.update_sprite = True
    return False
