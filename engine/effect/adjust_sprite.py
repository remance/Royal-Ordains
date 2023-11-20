from pygame.mask import from_surface
from pygame.transform import rotate


def adjust_sprite(self):
    # if self.scale_size > 1:
    #     self.image = pygame.transform.smoothscale(self.image, (self.image.get_width() * self.scale_size,
    #                                                            self.image.get_height() * self.scale_size))

    if self.angle:
        self.image = rotate(self.base_image, self.angle)

    self.rect = self.image.get_rect(center=self.pos)
    self.mask = from_surface(self.image)
