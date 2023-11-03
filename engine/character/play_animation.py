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
            if self.show_frame != self.max_show_frame:
                self.show_frame += 1
            else:
                if "repeat" in self.current_action:
                    self.show_frame = 0
                elif not self.freeze_timer:  # not has freeze animation timer to run out first
                    done = True
            self.start_animation_body_part()
            if self.current_animation_direction[self.show_frame]["sound_effect"]:
                sound = self.current_animation_direction[self.show_frame]["sound_effect"]
                self.battle.add_sound_effect_queue(self.sound_effect_pool[sound[0]][0],
                                                   self.pos, sound[1], sound[1])

            if not done:  # check if new frame has play speed mod
                self.final_animation_play_time = self.animation_play_time
                if self.hit_enemy and "stoppable" in self.current_animation_direction[self.show_frame]["property"]:
                    self.hit_enemy = False
                    self.stoppable_frame = True
                    # if attack_connect:  # delay frame speed when hit, so it is easier to connect next move
                    self.final_animation_play_time = 0.3
                elif "play_time_mod" in self.current_animation_direction[self.show_frame]:
                    self.final_animation_play_time *= self.current_animation_direction[self.show_frame]["play_time_mod"]

            # self.image = current_animation["sprite"]
            #
            # self.offset_pos = self.pos - current_animation["offset"]
            # self.rect = self.image.get_rect(midbottom=self.offset_pos)

    # if self.current_effect:  # play effect animation
    #     self.effectbox.image = self.status_animation_pool[self.current_effect]["frame"][self.effect_frame]
    #     self.effectbox.rect = self.effectbox.image.get_rect(midbottom=self.offset_pos)
    #     self.effect_timer += dt
    #     if self.effect_timer >= 0.1:
    #         self.effect_timer = 0
    #         if self.effect_frame < self.max_effect_frame:
    #             self.effect_frame += 1
    #         else:
    #             self.effect_frame = 0
    #             self.max_effect_frame = 0
    #             self.current_effect = None
    #             self.battle.battle_camera.remove(self.effectbox)

    return done
