def check_draw(self, dt):
    if not self.invisible:
        camera = self.camera
        surface_rect = self.rect
        surface_left_x, surface_top_y = surface_rect.topleft
        surface_right_x, surface_bottom_y = surface_rect.bottomright
        if (surface_right_x > camera.camera_left_bound and surface_left_x < camera.camera_right_bound and
                surface_bottom_y > camera.camera_top_bound and surface_top_y < camera.camera_bottom_bound):
            blit_check = (self.char_id, int(self.pos[0]), int(self.pos[1]), self.direction, self.animation_name)
            if blit_check not in self.blit_culling_check:
                if self.not_show_delay:
                    self.not_show_delay -= dt
                    if self.not_show_delay < 0:
                        self.not_show_delay = 0
                else:
                    self.blit_culling_check.add(blit_check)
                    if not self.in_drawer:
                        self.battle_camera_drawer.add(self)
                        self.in_drawer = True
            else:  # other character with very close location and same animation exist no need to blit it
                if self.in_drawer:
                    if not self.not_show_delay:
                        self.not_show_delay = 1
                    self.battle_camera_drawer.remove(self)
                    self.in_drawer = False
        elif self.in_drawer:
            self.not_show_delay = 0
            self.battle_camera_drawer.remove(self)
            self.in_drawer = False
    elif self.in_drawer:
        self.battle_camera_drawer.remove(self)
        self.in_drawer = False
