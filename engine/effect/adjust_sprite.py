from pygame.mask import from_surface
from pygame.transform import rotate, flip, smoothscale


def adjust_sprite(self):
    self.image = self.base_image
    if self.angle:
        self.image = rotate(self.base_image, self.angle)
    if self.flip:
        self.image = flip(self.image, True, False)
    if self.scale:
        self.image = smoothscale(self.image, (int(self.image.get_width() * self.scale),
                                              int(self.image.get_height() * self.scale)))


    self.rect = self.image.get_rect(center=self.pos)
    self.mask = from_surface(self.image)
