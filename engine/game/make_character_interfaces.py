from pygame import Surface, SRCALPHA, Color, draw
from pygame.font import Font
from pygame.transform import smoothscale

from engine.uimenu.uimenu import CharacterSelector, CharacterInterface
from engine.utils.text_making import text_render_with_bg


def make_character_interfaces(self):
    header_font = Font(self.ui_font["main_button"], int(36 * self.screen_scale[1]))
    font = Font(self.ui_font["main_button"], int(22 * self.screen_scale[1]))
    small_font = Font(self.ui_font["main_button"], int(18 * self.screen_scale[1]))
    stat_base_image = Surface((400 * self.screen_scale[0], 950 * self.screen_scale[1]), SRCALPHA)
    text = small_font.render(self.localisation.grab_text(("ui", "Status (Cost)")), True, (30, 30, 30))
    text_rect = text.get_rect(center=(330 * self.screen_scale[0], 30 * self.screen_scale[1]))
    stat_base_image.blit(text, text_rect)

    stat_rect = {}
    start_stat_row = 50 * self.screen_scale[1]

    text = small_font.render(self.localisation.grab_text(("ui", "Status Points Left")) + ": ", True,
                             (30, 30, 30))
    status_point_left_text_rect = text.get_rect(midleft=(10 * self.screen_scale[0],
                                                         30 * self.screen_scale[1]))
    stat_base_image.blit(text, status_point_left_text_rect)

    text = small_font.render(self.localisation.grab_text(("ui", "Skill Points Left")) +
                             ": ", True, (30, 30, 30))
    skill_point_left_text_rect = text.get_rect(midleft=(10 * self.screen_scale[0],
                                                        320 * self.screen_scale[1]))
    stat_base_image.blit(text, skill_point_left_text_rect)

    for index, stat in enumerate(CharacterInterface.stat_row):
        text = font.render(self.localisation.grab_text(("ui", stat)) + ": ", True, (30, 30, 30))
        text_rect = text.get_rect(midleft=(10 * self.screen_scale[0], start_stat_row))
        stat_rect[stat] = text_rect  # save stat name rect for stat point later
        stat_base_image.blit(text, text_rect)
        start_stat_row += 36 * self.screen_scale[1]

    text = small_font.render(self.localisation.grab_text(("ui", "Current Level")), True, (30, 30, 30))
    text_rect = text.get_rect(center=(320 * self.screen_scale[0], 320 * self.screen_scale[1]))
    stat_base_image.blit(text, text_rect)

    text_surface = text_render_with_bg(self.localisation.grab_text(("ui", "Help")), font, Color("black"))
    button_image = self.battle_ui_images["button_guard"]
    helper_image = Surface((button_image.get_width() + (5 * self.screen_scale[0]) +
                            text_surface.get_width(), button_image.get_height()), SRCALPHA)
    text_rect = text_surface.get_rect(topright=(helper_image.get_width(), 0))
    helper_image.blit(text_surface, text_rect)
    button_rect = button_image.get_rect(topleft=(0, 0))
    helper_image.blit(button_image, button_rect)
    helper_image_rect = helper_image.get_rect(topleft=(0, 900 * self.screen_scale[1]))
    stat_base_image.blit(helper_image, helper_image_rect)

    # Equipment interface
    equipment_base_image = Surface((400 * self.screen_scale[0], 950 * self.screen_scale[1]), SRCALPHA)
    slot_image = self.char_selector_images["Box_accessory"]
    equipment_slot_rect = {"weapon 1": slot_image.get_rect(topleft=(100 * self.screen_scale[0],
                                                                    10 * self.screen_scale[1])),
                           "weapon 2": slot_image.get_rect(topleft=(100 * self.screen_scale[0],
                                                                    100 * self.screen_scale[1])),
                           "accessory 1": slot_image.get_rect(topleft=(100 * self.screen_scale[0],
                                                                       190 * self.screen_scale[1])),
                           "accessory 2": slot_image.get_rect(topleft=(100 * self.screen_scale[0],
                                                                       280 * self.screen_scale[1])),
                           "accessory 3": slot_image.get_rect(topleft=(100 * self.screen_scale[0],
                                                                       370 * self.screen_scale[1])),
                           "item Up": slot_image.get_rect(topleft=(100 * self.screen_scale[0],
                                                                   460 * self.screen_scale[1])),
                           "item Right": slot_image.get_rect(topleft=(100 * self.screen_scale[0],
                                                                      550 * self.screen_scale[1])),
                           "head": slot_image.get_rect(topleft=(230 * self.screen_scale[0],
                                                                10 * self.screen_scale[1])),
                           "chest": slot_image.get_rect(topleft=(230 * self.screen_scale[0],
                                                                100 * self.screen_scale[1])),
                           "arm": slot_image.get_rect(topleft=(230 * self.screen_scale[0],
                                                               190 * self.screen_scale[1])),
                           "leg": slot_image.get_rect(topleft=(230 * self.screen_scale[0],
                                                               280 * self.screen_scale[1])),
                           "accessory 4": slot_image.get_rect(topleft=(230 * self.screen_scale[0],
                                                                       370 * self.screen_scale[1])),
                           "item Down": slot_image.get_rect(topleft=(230 * self.screen_scale[0],
                                                                     460 * self.screen_scale[1])),
                           "item Left": slot_image.get_rect(topleft=(230 * self.screen_scale[0],
                                                                     550 * self.screen_scale[1]))}
    for key, value in equipment_slot_rect.items():
        if "weapon" in key:
            equipment_base_image.blit(self.char_selector_images["Box_weapon" + key[-1]], value)
        elif "accessory" in key:
            equipment_base_image.blit(self.char_selector_images["Box_accessory"], value)
        elif "item" in key:
            equipment_base_image.blit(self.char_selector_images["Box_item"], value)
        else:
            equipment_base_image.blit(self.char_selector_images["Box_" + key], value)

    equipment_base_image.blit(helper_image, helper_image_rect)

    # Equipment list interface
    equipment_list_base_image = Surface((400 * self.screen_scale[0], 950 * self.screen_scale[1]), SRCALPHA)
    draw.line(equipment_list_base_image, (30, 30, 30), (int(equipment_list_base_image.get_width() / 2), 0),
              (int(equipment_list_base_image.get_width() / 2), int(400 * self.screen_scale[1])),
              width=int(4 * self.screen_scale[0]))
    draw.line(equipment_list_base_image, (30, 30, 30), (0, int(400 * self.screen_scale[1])),
              (equipment_list_base_image.get_width(), int(400 * self.screen_scale[1])),
              width=int(4 * self.screen_scale[0]))

    text_surface = header_font.render(self.localisation.grab_text(("ui", "Equipped")), True, (30, 30, 30))
    text_rect = text_surface.get_rect(topleft=(30 * self.screen_scale[0], 10 * self.screen_scale[1]))
    equipment_list_base_image.blit(text_surface, text_rect)

    text_surface = header_font.render(self.localisation.grab_text(("ui", "Selected")), True, (30, 30, 30))
    text_rect = text_surface.get_rect(topleft=(230 * self.screen_scale[0], 10 * self.screen_scale[1]))
    equipment_list_base_image.blit(text_surface, text_rect)

    slot_image = self.char_selector_images["Box_empty"]
    equipment_list_slot_rect = {"equip": slot_image.get_rect(topleft=(70 * self.screen_scale[0],
                                                                      60 * self.screen_scale[1])),
                                "new": slot_image.get_rect(topleft=(270 * self.screen_scale[0],
                                                                    60 * self.screen_scale[1]))}
    for key, value in equipment_list_slot_rect.items():
        equipment_list_base_image.blit(self.char_selector_images["Box_empty"], value)
    equipment_list_base_image.blit(helper_image, helper_image_rect)

    # Follower preset interface
    follower_preset_base_image = Surface((400 * self.screen_scale[0], 950 * self.screen_scale[1]), SRCALPHA)
    follower_preset_box_image = self.char_selector_images["Charsheet"]
    follower_preset_box_rects = {
        key: follower_preset_box_image.get_rect(topleft=(0, (key * (210 * self.screen_scale[1])))) for key in
        range(4)}
    for box, rect in follower_preset_box_rects.items():
        follower_preset_base_image.blit(follower_preset_box_image, rect)
    follower_preset_base_image.blit(helper_image, helper_image_rect)

    # Follower list interface
    big_list_base_image = Surface((400 * self.screen_scale[0], 950 * self.screen_scale[1]), SRCALPHA)
    for index in range(9):
        draw.line(big_list_base_image, (30, 30, 30), (0, ((index + 1) * 100) * self.screen_scale[1]),
                  (400, (index + 1) * 100 * self.screen_scale[1]), 2)
    big_list_base_image.blit(helper_image, helper_image_rect)

    # Storage interface
    storage_base_image = Surface((400 * self.screen_scale[0], 950 * self.screen_scale[1]), SRCALPHA)
    self.small_box_images = {"weapon 1": smoothscale(self.char_selector_images["Box_weapon1"],
                                                     (50 * self.screen_scale[0],
                                                      50 * self.screen_scale[1])),
                             "weapon 2": smoothscale(self.char_selector_images["Box_weapon2"],
                                                     (50 * self.screen_scale[0],
                                                      50 * self.screen_scale[1])),
                             "head": smoothscale(self.char_selector_images["Box_head"],
                                                 (50 * self.screen_scale[0],
                                                  50 * self.screen_scale[1])),
                             "chest": smoothscale(self.char_selector_images["Box_chest"],
                                                 (50 * self.screen_scale[0],
                                                  50 * self.screen_scale[1])),
                             "arm": smoothscale(self.char_selector_images["Box_arm"],
                                                (50 * self.screen_scale[0],
                                                 50 * self.screen_scale[1])),
                             "leg": smoothscale(self.char_selector_images["Box_leg"],
                                                (50 * self.screen_scale[0],
                                                 50 * self.screen_scale[1])),
                             "accessory": smoothscale(self.char_selector_images["Box_accessory"],
                                                      (50 * self.screen_scale[0],
                                                       50 * self.screen_scale[1])),
                             "item": smoothscale(self.char_selector_images["Box_item"],
                                                 (50 * self.screen_scale[0],
                                                  50 * self.screen_scale[1])),
                             "empty": smoothscale(self.char_selector_images["Box_empty"],
                                                  (50 * self.screen_scale[0],
                                                   50 * self.screen_scale[1]))}
    storage_box_rects = {}
    slot_index = 0
    for col in range(12):
        for row in range(5):
            storage_box_rects[slot_index] = self.small_box_images["empty"].get_rect(
                topleft=((35 * self.screen_scale[0]) + (row * 70 * self.screen_scale[0]),
                         (14 * self.screen_scale[1]) + (col * 70 * self.screen_scale[1])))
            storage_base_image.blit(self.small_box_images["empty"], storage_box_rects[slot_index])
            slot_index += 1

    storage_base_image.blit(helper_image, helper_image_rect)

    # Enchant interface
    enchant_base_image = Surface((400 * self.screen_scale[0], 950 * self.screen_scale[1]), SRCALPHA)
    draw.line(enchant_base_image, (30, 30, 30), (0, int(400 * self.screen_scale[1])),
              (enchant_base_image.get_width(), int(400 * self.screen_scale[1])),
              width=int(4 * self.screen_scale[0]))

    text_surface = header_font.render(self.localisation.grab_text(("ui", "Selected")), True, (30, 30, 30))
    text_rect = text_surface.get_rect(center=(200 * self.screen_scale[0], 20 * self.screen_scale[1]))
    enchant_base_image.blit(text_surface, text_rect)

    enchant_base_image.blit(helper_image, helper_image_rect)

    CharacterInterface.stat_base_image = stat_base_image
    CharacterInterface.equipment_list_base_image = equipment_list_base_image
    CharacterInterface.equipment_base_image = equipment_base_image
    CharacterInterface.follower_preset_base_image = follower_preset_base_image
    CharacterInterface.follower_base_image = big_list_base_image
    CharacterInterface.storage_base_image = storage_base_image
    CharacterInterface.shop_base_image = big_list_base_image
    CharacterInterface.reward_base_image = big_list_base_image
    CharacterInterface.enchant_base_image = enchant_base_image
    CharacterInterface.equipment_slot_rect = equipment_slot_rect
    CharacterInterface.equipment_list_slot_rect = equipment_list_slot_rect
    CharacterInterface.storage_box_rects = storage_box_rects
    CharacterInterface.stat_rect = stat_rect
    CharacterInterface.status_point_left_text_rect = status_point_left_text_rect
    CharacterInterface.skill_point_left_text_rect = skill_point_left_text_rect
    CharacterInterface.follower_preset_box_rects = follower_preset_box_rects
    CharacterInterface.small_box_images = self.small_box_images

    selectors = {1: CharacterSelector((self.screen_width / 8, self.screen_height / 2.4), self.char_selector_images),
                 2: CharacterSelector((self.screen_width / 2.7, self.screen_height / 2.4), self.char_selector_images),
                 3: CharacterSelector((self.screen_width / 1.6, self.screen_height / 2.4), self.char_selector_images),
                 4: CharacterSelector((self.screen_width / 1.15, self.screen_height / 2.4), self.char_selector_images)}
    char_interfaces = {index: CharacterInterface(selectors[index].rect.topleft, index,
                                                 self.char_interface_text_popup[index]) for index in range(1, 5)}

    return selectors, char_interfaces
