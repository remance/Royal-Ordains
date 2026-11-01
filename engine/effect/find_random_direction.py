from math import cos, sin, radians
from random import uniform


def find_random_direction(self):
    """Find random target direction for the sprite to move to"""
    random_angle = radians(uniform(0, 359))
    target_now = (self.base_pos[0] + 1000) * cos(random_angle), \
                 (self.base_pos[1] + 1000) * sin(random_angle)
    return target_now
