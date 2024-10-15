import pygame

col_loop_colour = ((0, 150, 0), (0, 100, 50), (100, 50, 0), (100, 200, 200), (50, 50, 50),
                   (150, 0, 0), (0, 0, 150), (150, 0, 150), (0, 150, 150), (150, 150, 0))
row_loop_colour = ((0, 150, 0), (0, 100, 50), (100, 50, 0), (100, 200, 200), (150, 0, 0),
                   (0, 0, 150), (150, 0, 150), (50, 50, 50), (0, 150, 150), (150, 150, 0))


class Showroom(pygame.sprite.Sprite):
    def __init__(self, size, screen_size):
        """White space for showing off sprite and animation"""
        self._layer = 10
        pygame.sprite.Sprite.__init__(self)
        self.size = (int(size[0]), int(size[1]))
        self.image = pygame.Surface(self.size)
        self.colour = (200, 200, 200)
        self.showroom_base_point = [0, 0]
        self.image.fill(self.colour)
        self.rect = self.image.get_rect(center=(screen_size[0] / 2, screen_size[1] / 2.35))
        self.grid = True

    def update(self, *args):
        self.image.fill(self.colour)
        if self.grid:
            grid_width = self.image.get_width() / 10
            grid_height = self.image.get_height() / 10

            for loop in range(1, 10):
                pygame.draw.line(self.image, col_loop_colour[loop - 1], (grid_width * loop, 0),
                                 (grid_width * loop, self.image.get_height()), width=1)
                pygame.draw.line(self.image, row_loop_colour[loop - 1], (0, grid_height * loop),
                                 (self.image.get_width(), grid_height * loop), width=1)

            pygame.draw.line(self.image, (0, 0, 0), (self.showroom_base_point[0], 0),
                             (self.showroom_base_point[0], self.image.get_height()), width=3)
            pygame.draw.line(self.image, (0, 0, 0), (0, self.showroom_base_point[1]),
                             (self.image.get_width(), self.showroom_base_point[1]), width=3)
