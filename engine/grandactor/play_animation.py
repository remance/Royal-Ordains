from engine.character.play_animation import change_animation_frame


def play_animation(self, dt):
    """
    Play character actor animation in grand campaign
    :param self: GrandActor object
    :param dt: Time
    :param hold_check: Check if holding animation frame or not
    :return: Boolean of animation finish playing or not
    """
    self.frame_timer += dt
    if self.frame_timer >= self.final_animation_frame_play_time:  # start next frame or end animation
        self.update_sprite = True
        if change_animation_frame(self):
            return True
        self.final_animation_frame_play_time = self.animation_frame_play_time
        if "play_time_mod" in self.current_animation_frame:
            self.final_animation_frame_play_time *= self.current_animation_frame["play_time_mod"]

    return False
