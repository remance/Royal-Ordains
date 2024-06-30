def play_animation(self, dt, hold_check):
    """
    Play character animation
    :param self: Character object
    :param dt: Time
    :param hold_check: Check if holding animation frame or not
    :return: Boolean of animation finish playing or not
    """
    done = False
    if not hold_check:  # not holding current frame
        self.frame_timer += dt
        if self.frame_timer >= self.final_animation_play_time:  # start next frame or end animation
            self.frame_timer = 0
            self.stoppable_frame = False
            if self.show_frame != self.max_show_frame:  # continue next frame
                self.show_frame += 1
            else:  # reach end frame
                self.show_frame = 0
                if "repeat" not in self.current_action:
                    # not loop and not has freeze animation timer to run out first
                    done = True
            if self.current_animation_direction[self.show_frame]["sound_effect"]:  # play sound from animation
                sound = self.current_animation_direction[self.show_frame]["sound_effect"]
                self.battle.add_sound_effect_queue(self.sound_effect_pool[sound[0]][0],
                                                   self.pos, sound[1], sound[2])
            if not done:  # check if new frame has play speed mod
                self.start_animation_body_part()
                self.final_animation_play_time = self.animation_play_time
                if (self.hit_enemy or self.can_combo_with_no_hit or "no hit combo" in self.current_action) and \
                        "stoppable" in self.current_animation_direction[self.show_frame]["property"]:
                    """only comboable after hit enemy, with exception for char with combo_with_no_hit"""
                    self.hit_enemy = False
                    self.stoppable_frame = True
                    # delay frame speed when hit, so it is easier to connect next move
                    if not self.can_combo_with_no_hit or self.hit_enemy:  # only slow down for frame that hit enemy
                        self.final_animation_play_time *= 2
                        if self.final_animation_play_time < 0.2:
                            self.final_animation_play_time = 0.2
                elif "play_time_mod" in self.current_animation_direction[self.show_frame]:
                    self.final_animation_play_time *= self.current_animation_direction[self.show_frame]["play_time_mod"]
    elif self.just_change_mode:
        if hold_check:  # only do this when hold to change sprite mode
            self.start_animation_body_part()
        self.just_change_mode = False
    return done
