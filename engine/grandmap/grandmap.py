from pygame import SRCALPHA
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
        self.region_by_colour_list = self.grand.map_data.region_by_colour_list
        self.images = {}
        self.true_map_image = None
        self.full_shown_map_image = None
        self.current_show_map_image = None
        self.shown_camera_pos = None
        self.camera_y_shift = None
        self.camera_pos = None
        self.rect = None
        self.map_shown_to_actual_scale_width = 1
        self.map_shown_to_actual_scale_height = 1
        self.size_width = self.screen_width
        self.size_height = self.screen_height

    def setup(self, image):
        self.true_map_image = image
        self.full_shown_map_image = Surface((self.screen_width * len(self.images),
                                             self.screen_height * len(self.images[0])), SRCALPHA)
        self.map_shown_to_actual_scale_width = self.full_shown_map_image.get_width() / self.true_map_image.get_width()
        self.map_shown_to_actual_scale_height = self.full_shown_map_image.get_height() / self.true_map_image.get_height()
        for row_index, row in enumerate(self.images):
            for col_index, image in enumerate(self.images[row_index]):
                self.full_shown_map_image.blit(image,
                                               image.get_rect(topleft=(row_index * image.get_width(),
                                                                       col_index * image.get_height())))
        self.current_show_map_image = Surface.subsurface(self.full_shown_map_image, (0, 0,
                                                                                     self.size_width, self.size_height))
        return (self.full_shown_map_image.get_width() - self.size_width,
                self.full_shown_map_image.get_height() - self.size_height)

    def update(self):
        if self.camera_pos != self.grand.camera_pos:
            self.camera_pos = self.grand.camera_pos.copy()
            self.current_show_map_image = Surface.subsurface(self.full_shown_map_image,
                                                             (self.camera_pos[0], self.camera_pos[1],
                                                              self.size_width, self.size_height))
        # if self.camera_y_shift != self.grand.camera_y_shift:
        #     self.camera_y_shift = self.grand.camera_y_shift
        self.rect = self.current_show_map_image.get_rect(midtop=(self.current_show_map_image.get_width() / 2, 0))
        self.image.blit(self.current_show_map_image, self.rect)

        if self.rect.collidepoint(self.grand.cursor.pos):
            if self.grand.cursor.is_select_just_up:
                region_colour = tuple(self.true_map_image.get_at((int(self.grand.base_cursor_pos[0]),
                                                                  int(self.grand.base_cursor_pos[1]))))[:3]
                if region_colour in self.grand.regions:
                    region = self.grand.regions[region_colour]
                    for object in region.build_objects.values():
                        if object.rect.collidepoint(self.grand.cursor_pos):
                            self.grand.text_popup.popup(self.grand.cursor.rect.bottomright,
                                                        (self.grand.localisation.grab_text(
                                                            ("building", object.sprite_id, "Name"))),
                                                        width_text_wrapper=800 * self.screen_scale[0]
                                                        )
                            self.grand.outer_ui_updater.add(self.grand.text_popup)
                            return

                    controller = self.grand.current_campaign_state["region_control"][region_colour]
                    self.grand.text_popup.popup(self.grand.cursor.rect.bottomright,
                                                (self.grand.localisation.grab_text(("ui", "Region:")) +
                                                 self.grand.localisation.grab_text(("region",
                                                                                    self.region_by_colour_list[
                                                                                        region_colour]["ID"], "Name")),
                                                 self.grand.localisation.grab_text(("ui", "Control:")) +
                                                 self.grand.localisation.grab_text(("faction", controller, "Name")),
                                                 self.grand.localisation.grab_text(("ui", "Income:")),
                                                 self.grand.localisation.grab_text(("ui", "Supply:")),
                                                 self.grand.localisation.grab_text(("ui", "Happiness:"))),
                                                width_text_wrapper=800 * self.screen_scale[0]
                                                )
                    self.grand.outer_ui_updater.add(self.grand.text_popup)
            # elif self.grand.cursor.is_alt_select_just_up:
            #     region_colour = tuple(self.true_map_image.get_at((int(self.grand.base_cursor_pos[0]),
            #                                                       int(self.grand.base_cursor_pos[1]))))[:3]
            #     if region_colour in self.grand.regions:
            #         self.grand.outer_ui_updater.add(self.grand.region_manage_menu)
