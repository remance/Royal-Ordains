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

        self.faction_owner = faction_owner
        self.image = None
        self.change_owner_state(faction_owner)

        self.rect = self.image.get_rect(center=self.pos)

    def change_owner_state(self, faction_owner):
        self.faction_owner = faction_owner
        self.image = apply_sprite_colour(self.grand.sprite_data.region_sprites[self.region],
                                         self.grand.map_data.faction_list[faction_owner]["Colour"])

    def update(self, true_dt, dt):
        pass
