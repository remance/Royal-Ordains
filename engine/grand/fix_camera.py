def fix_camera(self):
    if self.camera_topleft_pos[0] > self.map_x_end:  # camera cannot go further than max x
        self.camera_topleft_pos[0] = self.map_x_end
    elif self.camera_topleft_pos[0] < 0:  # camera does not move beyond left corner scene
        self.camera_topleft_pos[0] = 0

    if self.camera_topleft_pos[1] > self.map_y_end:  # camera cannot go further than max x
        self.camera_topleft_pos[1] = self.map_y_end
    elif self.camera_topleft_pos[1] < 0:  # camera does not move beyond left corner scene
        self.camera_topleft_pos[1] = 0

    self.shown_camera_topleft_pos = self.camera_topleft_pos.copy()
    self.camera.camera_left_bound = self.shown_camera_topleft_pos[0]
    self.camera.camera_top_bound = self.shown_camera_topleft_pos[1]
    self.camera.camera_right_bound = self.camera.camera_left_bound + self.screen_width
    self.camera.camera_bottom_bound = self.camera.camera_top_bound + self.screen_height
    self.camera.rect.topleft = (self.camera.camera_left_bound, self.camera.camera_top_bound)
