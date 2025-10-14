def fix_camera(self):
    if self.camera_pos[0] > self.stage_end:  # camera cannot go further than max x
        self.camera_pos[0] = self.stage_end
    elif self.camera_pos[0] < self.stage_start:  # camera does not move beyond left corner scene
        self.camera_pos[0] = self.stage_start
    self.camera_left = (self.camera_pos[0] - self.camera_center_x)
    self.base_camera_left = self.camera_left / self.screen_scale[0]
