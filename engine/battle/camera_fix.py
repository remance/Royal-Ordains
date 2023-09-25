def camera_fix(self):
    if self.camera_pos[0] > self.stage_end:  # camera cannot go further than max x
        self.camera_pos[0] = self.stage_end
    elif self.camera_pos[0] < self.stage_start:  # camera does not move beyond left corner stage
        self.camera_pos[0] = self.stage_start

    self.camera_begin = self.camera_pos[0] - self.battle_camera_center[0]
    self.camera_end = self.camera_pos[0] + self.battle_camera_center[0]
