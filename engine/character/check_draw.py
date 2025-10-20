def check_draw(self):
    if not self.invisible:
        blit_check = (self.char_id, int(self.base_pos[0] / 10), int(self.base_pos[1] / 10),
                      self.direction, self.animation_name)
        if blit_check not in self.blit_culling_check:
            self.blit_culling_check.add(blit_check)
            if not self.in_drawer:
                self.battle_camera_drawer.add(self)
                self.in_drawer = True
        else:  # other character with exact same location and animation exist no need to blit it
            if self.in_drawer:
                self.battle_camera_drawer.remove(self)
                self.in_drawer = False
    elif self.in_drawer:
        self.battle_camera_drawer.remove(self)
        self.in_drawer = False
