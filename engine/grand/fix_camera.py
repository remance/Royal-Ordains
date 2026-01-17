def fix_camera(self):
    if self.camera_pos[0] > self.map_x_end:  # camera cannot go further than max x
        self.camera_pos[0] = self.map_x_end
    elif self.camera_pos[0] < 0:  # camera does not move beyond left corner scene
        self.camera_pos[0] = 0

    if self.camera_pos[1] > self.map_y_end:  # camera cannot go further than max x
        self.camera_pos[1] = self.map_y_end
    elif self.camera_pos[1] < 0:  # camera does not move beyond left corner scene
        self.camera_pos[1] = 0
    self.camera_left = (self.camera_pos[0] - self.camera_center_x)
    self.base_camera_left = self.camera_left / self.screen_scale[0]
