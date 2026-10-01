from pygame import Vector2, Surface, SRCALPHA
from pygame.sprite import Sprite

from engine.utils.common import clean_object

# TODO add ongoing building/repair effect


class GrandObject(Sprite):
    clean_object = clean_object

    containers = None
    grand = None

    def __init__(self, sprite_id, base_pos, active_state):
        self.building_portraits = self.grand.building_portraits
        if type(base_pos) is str:
            self.base_pos = Vector2([float(item) for item in base_pos.split(",")])
        else:
            self.base_pos = Vector2([float(item) for item in base_pos])

        self.pos = Vector2((self.base_pos[0] * self.grand.map_shown_to_base_scale_width,
                            self.base_pos[1] * self.grand.map_shown_to_base_scale_height))

        self._layer = 10 + self.pos[1]
        Sprite.__init__(self, self.containers)
        self.sprite_id = "default"
        if sprite_id in self.building_portraits:
            self.sprite_id = sprite_id

        self.active_state = active_state
        self.image = self.building_portraits[self.sprite_id]["building_ui"]
        self.change_state(self.active_state)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, true_dt, dt):
        pass

    def change_state(self, new_state):
        self.active_state = new_state
        self.image = self.building_portraits[self.sprite_id]["building_ui"]
        if not self.active_state:
            self.image = self.image.copy()
            self.image.blit(self.building_portraits["unique_damaged"]["building_ui"], (0, 0))


class SettlementObject(GrandObject):
    slot_rects = []

    def __init__(self, region, sprite_id, base_pos, active_state):
        """Object for settlement on grand map, the sprite also has building slots around the settlement icon"""
        self.grand_ui_images = self.grand.grand_ui_images
        self.building_list = self.grand.building_list
        self.base_image = Surface((300 * self.grand.screen_scale_width, 300 * self.grand.screen_scale_height),
                                  SRCALPHA)
        self.base_image_center = (self.base_image.get_width() / 2, self.base_image.get_height() / 2)
        self.region = region
        if not self.slot_rects:
            icon = self.grand.building_portraits[sprite_id]["building_ui"]
            icon_rect = icon.get_rect(center=self.base_image_center)
            slot = self.grand_ui_images["slot_damaged"]
            self.slot_rects += [slot.get_rect(center=icon_rect.topleft), slot.get_rect(center=icon_rect.midtop), slot.get_rect(center=icon_rect.topright),
                                slot.get_rect(center=icon_rect.midleft), slot.get_rect(center=icon_rect.midright),
                                slot.get_rect(center=icon_rect.bottomleft), slot.get_rect(center=icon_rect.midbottom), slot.get_rect(center=icon_rect.bottomright),]
        for building_index, building in enumerate(self.grand.current_campaign_state["region"]["building"][region][1:]):
            self.change_building_state(building_index, self.building_list[building[0]]["Type"], building[1], building[2])
        GrandObject.__init__(self, sprite_id, base_pos, active_state)

    def change_state(self, new_state):
        self.active_state = new_state
        self.image = self.base_image.copy()
        icon = self.building_portraits[self.sprite_id]["building_ui"]
        icon_rect = icon.get_rect(center=self.base_image_center)
        self.image.blit(icon, icon_rect)
        if not new_state[0]:  # damaged building
            self.image.blit(self.building_portraits["damaged"]["building_ui"], icon_rect)
        if new_state[1]:  # constructing building
            self.image.blit(self.building_portraits["progress"]["building_ui"], icon_rect)

    def change_building_state(self, building_index, building_type, ready_state, constructing_state):
        slot_rect = self.slot_rects[building_index]
        self.base_image.blit(self.grand_ui_images["slot_" + building_type], slot_rect)
        if not ready_state:
            self.image.blit(self.grand_ui_images["slot_damaged"], slot_rect)
        if constructing_state:
            self.image.blit(self.grand_ui_images["slot_progress"], slot_rect)
