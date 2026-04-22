from pygame import Vector2

from engine.constants import Phase_To_Game_Time

infinity = float("inf")


def move_logic(self, dt):
    """Actor always reach target pos within half of the phase in game time when not skipping ahead"""
    if self.target_pos != self.pos:  # has movement
        if self.target_pos.distance_to(self.pos) > 500:
            self.pos = Vector2((self.target_pos[0] * self.screen_scale_width,
                                self.target_pos[1] * self.screen_scale_height))
        else:
            if self.animation_name != "Walk":  # pick walk animation
                self.pick_animation("Walk")
            move = self.target_pos - self.base_pos
            move_speed = move.length() / (Phase_To_Game_Time / 2)
            if move.length():
                move.normalize_ip()
                move *= move_speed * dt
                self.pos += move

                self.update_sprite = True
    else:
        if self.animation_name != "Idle":  # pick walk animation
            self.pick_animation("Idle")
