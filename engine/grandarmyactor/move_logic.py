from pygame import Vector2

from engine.constants import Phase_To_Game_Time

infinity = float("inf")


def move_logic(self, dt):
    """Actor always reach target pos within half of the phase in game time when not skipping ahead"""
    distance = self.target_pos.distance_to(self.pos)
    if distance > self.skip_move_length or distance < 1:
        self.pos = Vector2(self.target_pos)
    else:
        move = self.target_pos - self.pos
        move_speed = move.length() / (Phase_To_Game_Time / 2)
        move.normalize_ip()
        move *= move_speed * dt
        self.pos += move

    self.rect = self.image.get_rect(center=self.pos)
