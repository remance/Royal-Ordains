from pygame import Vector2
from pygame.sprite import Sprite

from engine.utils.common import clean_object
from engine.utils.sprite_altering import apply_sprite_colour


class GrandRegion(Sprite):
    clean_object = clean_object

    containers = None
    grand = None

    def __init__(self, region, base_pos, faction_owner):
        self._layer = 1
        Sprite.__init__(self, self.containers)
        self.region = region

        self.base_pos = base_pos
        self.pos = Vector2((base_pos[0] * self.grand.map_shown_to_base_scale_width,
                            base_pos[1] * self.grand.map_shown_to_base_scale_height))

        self.change_owner_animation_progress = []

        self.faction_owner = faction_owner
        self.faction_colour = self.grand.map_data.faction_list[faction_owner]["Colour"]
        self.image = None
        self.change_timer = 0
        self.change_owner_state(faction_owner)

        self.white_colour_for_animation = []

        image = self.grand.sprite_data.region_sprites[self.region]

        for x in range(image.get_width()):
            new_row = []
            self.white_colour_for_animation.append(new_row)
            for y in range(image.get_height()):
                original_pixel = image.get_at((x, y))
                mean = int(sum(original_pixel[0:3]) / 3)
                if mean > 10:  # skip blackish colour
                    colour = image.get_at((x, y))
                    intensity = (sum(colour[0:3]) / 3) / 255
                    if (sum(abs(item - mean) for item in original_pixel) / 3) / mean < 0.02:
                        new_row.append(((x, y), colour, intensity, 1 - intensity))

        self.rect = self.image.get_rect(center=self.pos)

    def change_owner_state(self, faction_owner, play_animation=False):
        self.faction_owner = faction_owner
        self.faction_colour = self.grand.map_data.faction_list[faction_owner]["Colour"]
        # self.image = self.grand.sprite_data.region_sprites[self.region]
        if play_animation:
            self.change_owner_animation_progress = self.white_colour_for_animation.copy()
        else:
            self.image = apply_sprite_colour(self.grand.sprite_data.region_sprites[self.region],
                                             self.grand.map_data.faction_list[faction_owner]["Colour"],
                                             white_only=True)

    def change_owner_state_animation(self):
        columns = self.change_owner_animation_progress[:2]
        image = self.image
        colour = self.faction_colour
        for column in columns:
            for row in column:
                original_pixel = row[1]
                intensity = row[2]
                revert_intensity = row[3]
                new_colour = tuple(
                    [int(item * revert_intensity + (colour[index] * intensity)) if index < 3 else item for index, item in
                     enumerate(original_pixel)])
                image.set_at(row[0], new_colour)
        self.change_owner_animation_progress = self.change_owner_animation_progress[2:]

    def update(self, true_dt, dt):
        if self.change_owner_animation_progress:
            self.change_timer += true_dt
            if self.change_timer > 0.01:
                self.change_owner_state_animation()
                self.change_timer = 0
