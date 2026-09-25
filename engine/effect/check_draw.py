def check_draw(self):
    camera = self.camera
    surface_rect = self.rect
    surface_left_x, surface_top_y = surface_rect.topleft
    surface_right_x, surface_bottom_y = surface_rect.bottomright

    if (surface_right_x > camera.camera_left_bound and surface_left_x < camera.camera_right_bound and
            surface_bottom_y > camera.camera_top_bound and surface_top_y < camera.camera_bottom_bound):
        if self not in self.battle_camera_drawer:
            self.battle_camera_drawer.add(self)
    elif self in self.battle_camera_drawer:
        self.battle_camera_drawer.remove(self)
