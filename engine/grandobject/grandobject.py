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
        self.cursor = self.grand.cursor
        self.sprite_id = "default"
        if sprite_id in self.building_portraits:
            self.sprite_id = sprite_id

        self.building_state = active_state
        self.image = self.building_portraits[self.sprite_id]["building_ui"]
        self.change_state(self.building_state)
        self.max_description_box_width = int(1000 * self.grand.screen_scale_width)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, true_dt, dt):
        grand = self.grand
        text_popup = grand.text_popup
        if self.rect.collidepoint(grand.cursor_pos) and not grand.cursor.event and not grand.player_interact.rect:
            text_popup.popup(self.cursor.rect, (grand.grab_text(("building", self.sprite_id, "Name")), "",
                                                grand.grab_text(("building", self.sprite_id, "Description"))),
                                  width_text_wrapper=self.max_description_box_width)
            grand.add_to_outer_ui_menu_updater(text_popup)

    def change_state(self, new_state):
        if self.building_state != new_state:
            self.building_state = new_state
        self.image = self.building_portraits[self.sprite_id]["building_ui"]
        if not self.building_state:
            self.image = self.image.copy()
            if not new_state[1]:  # damaged building
                self.image.blit(self.building_portraits["unique_damaged"]["building_ui"], (0, 0))
            if new_state[2]:  # constructing building
                self.image.blit(self.building_portraits["unique_progress"]["building_ui"], (0, 0))


class SettlementObject(GrandObject):
    slot_rects = []

    def __init__(self, region, base_pos, building_state):
        """Object for settlement on grand map, the sprite also has building slots around the settlement icon"""
        self.grand_ui_images = self.grand.grand_ui_images
        self.building_list = self.grand.building_list
        self.base_image = Surface((300 * self.grand.screen_scale_width, 300 * self.grand.screen_scale_height),
                                  SRCALPHA)
        self.base_image_center = (self.base_image.get_width() / 2, self.base_image.get_height() / 2)
        self.building_states = {}
        self.building_state = building_state
        self.region = region
        if not self.slot_rects:
            icon = self.grand.building_portraits[building_state[0]]["building_ui"]
            icon_rect = icon.get_rect(center=self.base_image_center)
            slot = self.grand_ui_images["slot_damaged"]
            self.slot_rects += [slot.get_rect(center=icon_rect.topleft), slot.get_rect(center=icon_rect.midtop),
                                slot.get_rect(center=icon_rect.topright),
                                slot.get_rect(center=icon_rect.midleft), slot.get_rect(center=icon_rect.midright),
                                slot.get_rect(center=icon_rect.bottomleft), slot.get_rect(center=icon_rect.midbottom),
                                slot.get_rect(center=icon_rect.bottomright), ]

        GrandObject.__init__(self, building_state[0], base_pos, building_state)

        for building_index, building in enumerate(self.grand.current_campaign_state["region"][region]["building"]):
            self.building_states[building_index] = ()
            self.change_building_state(building_index, building)
        self.change_state(building_state)

    def update(self, true_dt, dt):
        pass

    def change_state(self, new_state):
        self.building_state = new_state
        self.image = self.base_image.copy()
        self.sprite_id = new_state[0]
        if self.sprite_id in self.building_portraits:
            icon = self.building_portraits[self.sprite_id]["building_ui"]
        else:
            icon = self.building_portraits["default"]["building_ui"]
        icon_rect = icon.get_rect(center=self.base_image_center)
        self.image.blit(icon, icon_rect)

        if not new_state[1]:  # damaged building
            self.image.blit(self.building_portraits["damaged"]["building_ui"], icon_rect)
        if new_state[2]:  # constructing building
            self.image.blit(self.building_portraits["progress"]["building_ui"], icon_rect)

    def change_building_state(self, building_index, new_state, also_change_state=False):
        if building_index:
            non_settlement_index = building_index - 1
            if self.building_states[non_settlement_index] != new_state:
                slot_rect = self.slot_rects[non_settlement_index]
                self.base_image.blit(self.grand_ui_images["slot_" + self.building_list[new_state[0]]["Type"]],
                                     slot_rect)
                if not new_state[1]:
                    self.base_image.blit(self.grand_ui_images["slot_damaged"], slot_rect)
                if new_state[2]:
                    self.base_image.blit(self.grand_ui_images["slot_progress"], slot_rect)
                if not new_state[3]:
                    self.base_image.blit(self.grand_ui_images["slot_unavailable"], slot_rect)
                self.building_states[non_settlement_index] = new_state.copy()

            if also_change_state:
                self.change_state(self.building_state)

            if building_index in self.grand.region_list[self.region]["Object"]:
                #  this building is wonder on map, also update it too
                self.grand.wonder_object_list[(self.region, building_index)].change_state(new_state)
        elif also_change_state:
            self.change_state(new_state)
