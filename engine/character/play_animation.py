import engine.character.character
from engine.effect.effect import Effect, DamageEffect, TrapEffect


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
        if self.frame_timer >= self.final_animation_play_time:  # start next frame or end animation
            if self.next_animation_frame():
                return True

            self.final_animation_play_time = self.animation_play_time
            if "play_time_mod" in self.current_animation_frame:
                self.final_animation_play_time *= self.current_animation_frame["play_time_mod"]

            self.sprite_deal_damage = False
            for key, part_data in self.current_animation_direction["effects"].items():
                if part_data[8] and not self.battle.cutscene_playing:  # independent effect
                    if "summon" in self.current_moveset["Property"]:
                        # summon battle character, using effect with damage does not create Effect
                        start_pos = (self.base_pos[0] + (part_data[2]),
                                     self.base_ground_pos)
                        (engine.character.character.
                         BattleCharacter(self.battle.last_char_game_id, self.character_data.character_list[
                                             self.current_moveset["Property"]["summon"]] |
                                         {"ID": self.current_moveset["Property"]["summon"], "Direction": self.direction,
                                          "Team": self.team, "POS": start_pos, "Start Health": 1,
                                          "Start Resource": 1}, leader=self))
                        self.battle.last_char_game_id += 1

                    elif "trap" in self.effect_list[part_data[0]]["Property"]:
                        TrapEffect(self, part_data, self.current_moveset)
                    else:
                        if self.effect_list[part_data[0]]["Damage"]:  # damage effect
                            DamageEffect(self, part_data, self.current_moveset,
                                         base_target_pos=self.current_action["target"])
                        else:  # no damage effect
                            Effect(self, part_data, self.current_moveset,
                                   base_target_pos=self.current_action["target"])
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
        if self.frame_timer >= self.final_animation_play_time:  # start next frame or end animation
            if self.next_animation_frame():
                return True

            # check if new frame has play speed mod
            self.final_animation_play_time = self.default_animation_play_time
            if "play_time_mod" in self.current_animation_frame:
                self.final_animation_play_time *= self.current_animation_frame["play_time_mod"]

            self.update_sprite = True
    return False
