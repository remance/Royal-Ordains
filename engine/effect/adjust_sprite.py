from pygame.mask import from_surface
from pygame.transform import rotate


def adjust_sprite(self):
    if self.angle:
        self.image = rotate(self.base_image, self.angle)
    else:
        self.image = self.base_image

    self.rect = self.image.get_rect(center=self.pos)
    self.mask = from_surface(self.image)
