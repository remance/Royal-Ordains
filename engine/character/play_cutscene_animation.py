def play_cutscene_animation(self, dt, hold_check):
    """
    Play character animation during cutscene, does not account for animation speed stat
    :param self: Character object
    :param dt: Time
    :param hold_check: Check if holding animation frame or not
    :return: Boolean of animation finish playing or not
    """
    if not hold_check or "repeat after" in self.current_action:  # not holding current frame, not count if has repeat after
        self.frame_timer += dt
        if self.frame_timer >= self.final_animation_play_time:  # start next frame or end animation
            self.frame_timer = 0
            self.stoppable_frame = False

            if self.show_frame != self.max_show_frame:  # continue next frame
                self.show_frame += 1
            else:  # reach end frame
                if not hold_check:
                    self.show_frame = 0
                if "repeat" not in self.current_action:
                    # not loop and not has freeze animation timer to run out first
                    return True

            if self.current_animation_direction[self.show_frame]["sound_effect"]:  # play sound from animation
                sound = self.current_animation_direction[self.show_frame]["sound_effect"]
                self.battle.add_sound_effect_queue(self.sound_effect_pool[sound[0]][0],
                                                   self.pos, sound[1], sound[2])
            self.start_animation_body_part()

            # check if new frame has play speed mod
            self.final_animation_play_time = self.default_animation_play_time
            if "play_time_mod" in self.current_animation_direction[self.show_frame]:
                self.final_animation_play_time *= self.current_animation_direction[self.show_frame]["play_time_mod"]
    return False
