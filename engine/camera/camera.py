from pygame import Surface


class Camera:
    def __init__(self, screen, camera_size):
        self.image = Surface.subsurface(screen, (0, 0, camera_size[0], camera_size[1]))  # Camera image
        camera_w, camera_h = self.image.get_rect().size  # get size of camera
        self.camera_w_center = camera_w / 2
        self.camera_h_center = camera_h / 2
        self.camera_x_shift = None
        self.camera_y_shift = None

    def update(self, surfaces):
        """Update self camera with sprite blit to camera image"""
        for surface in surfaces:  # Blit sprite to camara image
            surface_x, surface_y = surface.rect.topleft
            self.image.blit(surface.image, (surface_x - self.camera_x_shift, surface_y - self.camera_y_shift))

    def out_update(self, out_surfaces):
        for surface in out_surfaces:  # surface that get blit with pos on screen instead of in battle
            if surface.image:
                self.image.blit(surface.image, surface.rect)
