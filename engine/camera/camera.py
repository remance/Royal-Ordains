from pygame import Surface


class Camera:
    def __init__(self, screen, camera_size):
        self.image = Surface.subsurface(screen, (0, 0, camera_size[0], camera_size[1]))  # Camera image
        camera_w, camera_h = self.image.get_rect().size  # get size of camera
        self.camera_w_center = camera_w / 2
        self.camera_h_center = camera_h / 2
        self.camera_left_bound = None
        self.camera_top_bound = None
        self.camera_right_bound = None
        self.camera_bottom_bound = None

    def update(self, blit_objects):
        """Update self camera with sprite blit to camera image"""
        image = self.image
        camera_left_bound = self.camera_left_bound
        camera_top_bound = self.camera_top_bound
        camera_right_bound = self.camera_right_bound
        camera_bottom_bound = self.camera_bottom_bound
        for blit_object in blit_objects:  # Blit sprite to camara image
            surface_rect = blit_object.rect
            surface_left_x, surface_top_y = surface_rect.topleft
            surface_right_x, surface_bottom_y = surface_rect.bottomright

            if (surface_right_x > camera_left_bound and surface_left_x < camera_right_bound and
                    surface_bottom_y > camera_top_bound and surface_top_y < camera_bottom_bound):
                # only blit if image in camera at all
                image.blit(blit_object.image, (surface_left_x - camera_left_bound,
                                               surface_top_y - camera_top_bound))

    def out_update(self, out_surfaces):
        image = self.image
        for surface in out_surfaces:  # surface that get blit with pos on screen instead of in battle
            if surface.image:
                image.blit(surface.image, surface.rect)
