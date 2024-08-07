from pygame.mask import from_surface
from pygame.transform import rotate


def adjust_sprite(self):
    self.image = self.base_image
    if self.angle:
        self.image = rotate(self.base_image, self.angle)

    self.rect = self.image.get_rect(center=self.pos)
    self.mask = from_surface(self.image)
