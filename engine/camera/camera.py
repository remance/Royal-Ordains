from pygame import Surface


class Camera:
    def __init__(self, screen, camera_size):
        self.image = Surface.subsurface(screen, (0, 0, camera_size[0], camera_size[1]))  # Camera image
        camera_w, camera_h = self.image.get_rect().size  # get size of camera
        self.camera_w_center = camera_w / 2
        self.camera_h_center = camera_h / 2
        self.camera_topleft_x_shift = None
        self.camera_topleft_y_shift = None
        self.camera_right_x_shift = None

    def update(self, surfaces):
        """Update self camera with sprite blit to camera image"""
        image = self.image
        camera_topleft_x_shift = self.camera_topleft_x_shift
        camera_topleft_y_shift = self.camera_topleft_y_shift
        camera_right_x_shift = self.camera_right_x_shift
        for surface in surfaces:  # Blit sprite to camara image
            surface_x, surface_y = surface.rect.topleft
            surface_w, surface_h = surface.rect.size
            if (surface_x + surface_w - camera_topleft_x_shift > 0 and (surface.rect.topright[0] - surface_w) <= camera_right_x_shift and
                    surface_y + surface_h - camera_topleft_y_shift > 0):
                # only blit if image in camera at all
                image.blit(surface.image, (surface_x - camera_topleft_x_shift, surface_y - camera_topleft_y_shift))

    def out_update(self, out_surfaces):
        image = self.image
        for surface in out_surfaces:  # surface that get blit with pos on screen instead of in battle
            if surface.image:
                image.blit(surface.image, surface.rect)
