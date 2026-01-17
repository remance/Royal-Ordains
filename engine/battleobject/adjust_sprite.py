from pygame.transform import rotate, flip, smoothscale


def adjust_sprite(self):
    self.image = self.base_image
    if self.sprite_flip:
        self.image = flip(self.image, True, False)
    if self.angle:
        self.image = rotate(self.image, self.angle)
    if self.height_scale != 1 or self.width_scale != 1:
        self.image = smoothscale(self.image, (int(self.image.get_width() * self.width_scale),
                                              int(self.image.get_height() * self.height_scale)))

    self.rect = self.image.get_rect(center=self.pos)
