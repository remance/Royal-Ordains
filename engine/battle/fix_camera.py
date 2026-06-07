from pygame import Vector2


def fix_camera(self):
    if self.camera_pos[0] > self.stage_end:  # camera cannot go further than max x
        self.camera_pos[0] = self.stage_end
    elif self.camera_pos[0] < self.stage_start:  # camera does not move beyond left corner scene
        self.camera_pos[0] = self.stage_start
    self.camera_left_bound = (self.camera_pos[0] - self.camera_center_x)
    self.base_camera_left_bound = self.camera_left_bound / self.screen_scale_width
    self.base_camera_pos = Vector2(self.camera_pos[0] / self.screen_scale_width,
                                   self.camera_pos[1] / self.screen_scale_height)
