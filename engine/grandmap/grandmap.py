from pygame.sprite import Sprite
from pygame.surface import Surface


class GrandMap(Sprite):
    image = None
    grand = None

    def __init__(self):
        from engine.game.game import Game
        self.main_dir = Game.main_dir
        self.data_dir = Game.data_dir
        self.screen_scale = Game.screen_scale
        self.screen_size = Game.screen_size
        self.screen_width = self.screen_size[0]
        self.screen_height = self.screen_size[1]
        self.half_screen = self.screen_width / 2
        self._layer = 0
        Sprite.__init__(self)
        self.region_by_colour_list = self.grand.map_data.region_by_colour_index
        self.true_map_image = None
        self.full_shown_map_image = None
        self.current_show_map_image = None
        self.camera_y_shift = None
        self.camera_pos = None
        self.rect = None
        self.map_shown_to_actual_scale_width = 1
        self.map_shown_to_actual_scale_height = 1
        self.size_width = self.screen_width
        self.size_height = self.screen_height

    def setup(self, true_map, shown_map):
        self.camera_pos = None
        self.true_map_image = true_map
        self.full_shown_map_image = shown_map
        self.map_shown_to_actual_scale_width = self.full_shown_map_image.get_width() / self.true_map_image.get_width()
        self.map_shown_to_actual_scale_height = self.full_shown_map_image.get_height() / self.true_map_image.get_height()
        self.current_show_map_image = Surface.subsurface(self.full_shown_map_image, (0, 0,
                                                                                     self.size_width, self.size_height))
        return (self.full_shown_map_image.get_width() - self.size_width,
                self.full_shown_map_image.get_height() - self.size_height)

    def update(self):
        if self.camera_pos != self.grand.shown_camera_topleft_pos:
            self.camera_pos = self.grand.shown_camera_topleft_pos.copy()
            self.current_show_map_image = Surface.subsurface(self.full_shown_map_image,
                                                             (self.camera_pos[0], self.camera_pos[1],
                                                              self.size_width, self.size_height))
        # if self.camera_y_shift != self.grand.camera_y_shift:
        #     self.camera_y_shift = self.grand.camera_y_shift
        self.rect = self.current_show_map_image.get_rect(midtop=(self.current_show_map_image.get_width() / 2, 0))
        self.image.blit(self.current_show_map_image, self.rect)
        if self.grand.show_route:
            # add route after map update draw to blit route dots on the map under other sprites.
            self.grand.draw_route()