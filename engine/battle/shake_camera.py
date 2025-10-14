from math import log
from random import uniform


def shake_camera(self):
    log_shake = log(self.screen_shake_value)
    self.shown_camera_pos = [self.shown_camera_pos[0] + uniform(-1, 1) * log_shake,
                             self.shown_camera_pos[1] + uniform(-1, 1) * log_shake]
