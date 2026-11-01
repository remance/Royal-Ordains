from math import log
from random import uniform


def shake_camera(self):
    log_shake = log(self.screen_shake_value)
    self.shown_camera_center_pos = [self.shown_camera_center_pos[0] + uniform(-1, 1) * log_shake,
                                    self.shown_camera_center_pos[1] + uniform(-1, 1) * log_shake]
    if self.shown_camera_center_pos[0] > self.stage_end:  # camera cannot go further than max x
        self.shown_camera_center_pos[0] = self.stage_end
    elif self.shown_camera_center_pos[0] < self.stage_start:  # camera does not move beyond left corner scene
        self.shown_camera_center_pos[0] = self.stage_start
