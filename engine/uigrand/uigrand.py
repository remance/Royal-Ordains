from math import ceil

from pygame import Vector2, Surface, SRCALPHA, Rect, draw, Color
from pygame.transform import smoothscale

from engine.constants import Culture_Policy_Integration
from engine.uimenu.uimenu import UIMenu
from engine.utils.text_making import number_to_minus_or_plus, add_comma_number, text_render_with_bg


class UIGrand(UIMenu):
    def __init__(self, player_cursor_interact=True, has_containers=False):
        """
        Parent class for all battle menu user interface
        """
        from engine.grand.grand import Grand
        UIMenu.__init__(self, player_cursor_interact=player_cursor_interact, has_containers=has_containers)
        self.grand = Grand.grand
        self.cursor = Grand.cursor  # use battle cursor for battle ui
        self.text_popup = self.grand.text_popup
        self.outer_ui_updater = self.grand.outer_ui_updater
        self.max_description_box_width = int(1000 * self.screen_scale_width)


class YesNo(UIGrand):
    def __init__(self, images):
        UIGrand.__init__(self)
        self._layer = 5
        self.yes_image = images["yes"]
        self.no_image = images["no"]

        self.yes_zoom_animation_timer = 0
        self.no_zoom_animation_timer = 0

        self.image = Surface((self.yes_image.get_width() * 2.5, self.yes_image.get_height() * 1.5), SRCALPHA)
        self.base_image = self.image.copy()

        self.pos = Vector2(self.screen_size[0] / 2, 400 * self.screen_scale_height)
        yes_image_rect = self.yes_image.get_rect(midleft=(0, self.image.get_height() / 2))
        no_image_rect = self.no_image.get_rect(midright=(self.image.get_width(), self.image.get_height() / 2))
        self.image.blit(self.yes_image, yes_image_rect)
        self.image.blit(self.no_image, no_image_rect)
        self.base_image2 = self.image.copy()
        self.selected = None

        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt):
        yes_image_rect = self.yes_image.get_rect(midleft=(0, self.image.get_height() / 2))
        no_image_rect = self.no_image.get_rect(midright=(self.image.get_width(),
                                                         self.image.get_height() / 2))
        cursor_pos = (self.cursor.pos[0] - self.rect.topleft[0],
                      self.cursor.pos[1] - self.rect.topleft[1])
        if yes_image_rect.collidepoint(cursor_pos):
            if self.event_press:
                self.selected = "yes"
                return
            else:
                self.image = self.base_image.copy()
                self.no_zoom_animation_timer = 0
                if not self.yes_zoom_animation_timer:
                    self.yes_zoom_animation_timer = 0.01
                    yes_zoom_animation_timer = 1.01
                else:
                    self.yes_zoom_animation_timer += self.grand.true_dt / 5
                    yes_zoom_animation_timer = 1 + self.yes_zoom_animation_timer
                    if self.yes_zoom_animation_timer > 0.2:
                        yes_zoom_animation_timer = 1.2 - (self.yes_zoom_animation_timer - 0.2)
                        if self.yes_zoom_animation_timer > 0.4:
                            self.yes_zoom_animation_timer = 0

                yes_image = smoothscale(self.yes_image, (self.yes_image.get_width() * yes_zoom_animation_timer,
                                                         self.yes_image.get_height() * yes_zoom_animation_timer))
                yes_image_rect = yes_image.get_rect(midleft=(0, self.image.get_height() / 2))
                self.image.blit(yes_image, yes_image_rect)
                self.image.blit(self.no_image, no_image_rect)

        elif no_image_rect.collidepoint(cursor_pos):
            if self.event_press:
                self.selected = "no"
                return
            else:
                self.image = self.base_image.copy()
                self.yes_zoom_animation_timer = 0
                if not self.no_zoom_animation_timer:
                    self.no_zoom_animation_timer = 0.01
                    no_zoom_animation_timer = 1.01
                else:
                    self.no_zoom_animation_timer += self.grand.true_dt / 5
                    no_zoom_animation_timer = 1 + self.no_zoom_animation_timer
                    if self.no_zoom_animation_timer > 0.2:
                        no_zoom_animation_timer = 1.2 - (self.no_zoom_animation_timer - 0.2)
                        if self.no_zoom_animation_timer > 0.4:
                            self.no_zoom_animation_timer = 0

                no_image = smoothscale(self.no_image, (self.no_image.get_width() * no_zoom_animation_timer,
                                                       self.no_image.get_height() * no_zoom_animation_timer))
                no_image_rect = no_image.get_rect(midright=(self.image.get_width(), self.image.get_height() / 2))
                self.image.blit(no_image, no_image_rect)
                self.image.blit(self.yes_image, yes_image_rect)

        elif self.no_zoom_animation_timer or self.yes_zoom_animation_timer:
            self.no_zoom_animation_timer = 0
            self.yes_zoom_animation_timer = 0
            self.image = self.base_image2


class PlayerFactionResourceBar(UIGrand):
    def __init__(self):
        self._layer = 5
        UIGrand.__init__(self)
        self.image = Surface((1400 * self.screen_scale_width, 100 * self.screen_scale_height), SRCALPHA)
        self.image.fill((255, 255, 255))
        self.base_image = self.image.copy()
        self.font = self.game.large_generic_ui_font
        self.text_rect = {"gold": (500 * self.screen_scale_width, 20 * self.screen_scale_height),
                          "supply": (1000 * self.screen_scale_width, 20 * self.screen_scale_height),
                          "happiness": (1300 * self.screen_scale_width, 20 * self.screen_scale_height)}
        self.blit_text_rect = {}
        self.player_faction_resource = {}
        self.rect = self.image.get_rect(topleft=(0, 0))

    def update(self, dt):
        resource = self.grand.current_campaign_state["faction"][self.grand.player_faction]
        resource = ((resource["gold"], resource["gold_income"]), (resource["supply"], resource["supply_income"]),
                    resource["happiness"])
        if self.player_faction_resource != resource:
            self.blit_text_rect = {}
            self.image = self.base_image.copy()
            self.player_faction_resource = resource

            for index, text in enumerate(self.text_rect):
                value = str(resource[index])
                if text != "happiness":
                    value = (add_comma_number(resource[index][0]) + " (" +
                             number_to_minus_or_plus(resource[index][1]) + add_comma_number(resource[index][1]) + ")")
                value = self.font.render(value, True, (0, 0, 0))
                blit_text_rect = value.get_rect(topright=self.text_rect[text])
                self.image.blit(value, blit_text_rect)
                self.blit_text_rect[text] = blit_text_rect

        UIMenu.update(self, dt)

        if self.mouse_over:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))
            for key, rect in self.blit_text_rect.items():
                if rect.collidepoint(inside_mouse_pos):
                    text = (self.grab_text(("ui", "info_text_" + key)),)
                    self.text_popup.popup(self.cursor.rect.bottomright, text)
                    self.outer_ui_updater.add(self.text_popup)


class PlayerFactionCultureList(UIGrand):
    def __init__(self):
        self._layer = 5
        UIGrand.__init__(self)
        self.font = self.game.medium_generic_ui_font
        self.character_portraits = self.grand.character_portraits
        self.culture_coas = self.grand.sprite_data.culture_coas
        self.image = Surface((0, 0))
        self.image_width = self.image.get_width()
        self.image.fill((255, 255, 255))
        self.base_image = self.image.copy()
        self.culture_coa_rects = {}
        self.culture_value = {}
        self.rect = self.image.get_rect(topleft=self.grand.player_faction_resource_bar_ui.rect.bottomleft)

    def culture_change(self):
        culture_value = {}
        faction_culture_state = self.grand.current_campaign_state["faction"][self.grand.player_faction]["culture"]

        for index, culture in enumerate(faction_culture_state):
            culture_state = faction_culture_state[culture]
            culture_value[culture] = {"integration": str(culture_state["integration"] * 100) + "%",
                                      "influence": str(culture_state["influence"] * 100) + "%"}

        if self.culture_value != culture_value:
            if len(faction_culture_state) > 8:
                self.image = Surface(((2000 + 100) * self.screen_scale_width, 400 * self.screen_scale_height))
                self.image_width = self.image.get_width()
                self.image.fill((255, 255, 255))
            else:
                self.image = Surface((((250 * len(faction_culture_state)) + 100) * self.screen_scale_width,
                                      200 * self.screen_scale_height))
                self.image_width = self.image.get_width()
                self.image.fill((255, 255, 255))

            self.culture_coa_rects = {}
            self.culture_value = {}

            for index, culture in enumerate(faction_culture_state):
                culture_state = faction_culture_state[culture]
                self.culture_value[culture] = {"integration": str(int(culture_state["integration"] * 100)) + "%",
                                               "influence": str(int(culture_state["influence"] * 100)) + "%"}
                culture_image = self.culture_coas[culture]["tiny"]
                culture_rect = culture_image.get_rect(topleft=(250 * self.screen_scale_width * index,
                                                               25 * self.screen_scale_height))
                self.image.blit(culture_image, culture_rect)
                text_surface = text_render_with_bg(self.culture_value[culture]["integration"], self.font,
                                                   Color("black"))
                self.image.blit(text_surface, text_surface.get_rect(midtop=culture_rect.topright))
                text_surface = text_render_with_bg(self.culture_value[culture]["influence"], self.font,
                                                   Color("black"))
                self.image.blit(text_surface, text_surface.get_rect(midbottom=culture_rect.bottomright))
                self.culture_coa_rects[culture] = culture_rect
            self.rect = self.image.get_rect(topleft=self.grand.player_faction_resource_bar_ui.rect.bottomleft)

    def update(self, dt):
        UIMenu.update(self, dt)

        if self.mouse_over:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))
            for culture, rect in self.culture_coa_rects.items():
                if rect.collidepoint(inside_mouse_pos):
                    culture_state = self.grand.current_campaign_state["faction"][self.grand.player_faction]["culture"][
                        culture]
                    text = (self.grab_text(("culture", culture, "Name")),
                            self.grab_text(("ui", "info_header_policy")) + self.grab_text(
                                ("ui", "culture_" + culture_state["policy"])),
                            self.grab_text(("ui", "info_header_integration")) + self.culture_value[culture][
                                "integration"],
                            self.grab_text(("ui", "info_header_influence")) + self.culture_value[culture]["influence"])
                    self.text_popup.popup(self.cursor.rect.bottomright, text,
                                          width_text_wrapper=self.max_description_box_width)
                    self.outer_ui_updater.add(self.text_popup)
                    break


class PlayerArmyListSortOption(UIGrand):
    def __init__(self):
        self._layer = 5
        UIGrand.__init__(self)
        self.image = Surface((796 * self.screen_scale_width, 100 * self.screen_scale_height))
        self.image.fill((10, 100, 50))
        self.rect = self.image.get_rect(topright=self.grand.mini_time_orb_ui.rect.bottomright)


class PlayerArmyList(UIGrand):
    def __init__(self):
        self._layer = 5
        UIGrand.__init__(self)
        self.font = self.game.large_generic_ui_font
        self.scroll = None  # got added later during scroll object __init__
        self.character_portraits = self.grand.character_portraits
        self.image = Surface((900 * self.screen_scale_width, 1050 * self.screen_scale_height), SRCALPHA)
        self.image.fill((80, 200, 100, 100))
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(topright=self.grand.player_army_list_sort_option_ui.rect.bottomright)
        self.empty_card_image = Surface((900 * self.screen_scale_width, 150 * self.screen_scale_height), SRCALPHA)
        self.empty_card_image.fill((200, 130, 130, 150))
        self.current_row = 0
        self.total_row = 0
        self.max_row_show = 1  # trick the scroller to use additional row instead of total
        self.scroll_total_row = self.total_row + 1

        self.army_card_list = []
        self.army_rects = [self.empty_card_image.get_rect() for index in range(6)]

    def draw_army_card(self, army):
        card_image = self.empty_card_image.copy()
        commander_image = self.character_portraits[army.commander_id]["tiny"]["right"]
        card_image.blit(commander_image, commander_image.get_rect(topleft=(0, 0)))

        for index, leader in enumerate(army.leader_group):
            leader_image = self.character_portraits[leader]["mini"]["left"]
            card_image.blit(leader_image, leader_image.get_rect(
                topleft=(((100 * index) + 150) * self.screen_scale_width, 0)))

        text_surface = self.font.render(self.localisation.grab_text(("region", army.current_region, "Name")),
                                        True, (0, 0, 0))
        card_image.blit(text_surface, text_surface.get_rect(topright=(card_image.get_width() -
                                                                      (50 * self.screen_scale_width), 0)))

        if army.game_id in self.grand.current_campaign_state["battle"]["armies"]:
            activity = self.localisation.grab_text(("ui", "info_text_combat"))
        elif len(army.travel_route) > 1:
            activity = ">" + self.localisation.grab_text(("region", army.travel_route[-1], "Name"))
        else:
            activity = self.localisation.grab_text(("ui", "info_text_idle"))
        text_surface = self.font.render(activity, True, (0, 0, 0))
        card_image.blit(text_surface, text_surface.get_rect(topright=(card_image.get_width() -
                                                                      (50 * self.screen_scale_width),
                                                                      70 * self.screen_scale_height)))

        selected_card_image = card_image.copy()
        draw.rect(selected_card_image, (0, 0, 0),
                  (0, 0, selected_card_image.get_width(), selected_card_image.get_height()),
                  width=int(10 * self.screen_scale_width))
        return card_image, selected_card_image

    def reset_card(self, index):
        """Reset only specific card based on input index"""
        self.army_card_list[index] = self.draw_army_card(
            self.grand.current_campaign_state["faction"][self.grand.player_faction]["army"][index])

    def reset_list(self):
        """Reset entire card list, draw card for each army"""
        current_army_list = self.grand.current_campaign_state["faction"][self.grand.player_faction]["army"]
        self.total_row = ceil(len(current_army_list) / 7)
        if self.total_row == 1:
            self.total_row = 0
        self.scroll_total_row = self.total_row + 1
        for army in current_army_list:
            self.army_card_list.append(self.draw_army_card(army))
        self.draw_list()

    def draw_list(self):
        self.image = self.base_image.copy()
        show_index = 0
        for index, army in enumerate(self.grand.current_campaign_state["faction"][self.grand.player_faction]["army"]):
            if index >= self.current_row:
                if army not in self.grand.player_selected_army:
                    self.image.blit(self.army_card_list[index][0], self.army_rects[show_index])
                else:
                    self.image.blit(self.army_card_list[index][1], self.army_rects[show_index])
                show_index += 1

    def update(self, dt):
        UIMenu.update(self, dt)
        if self.mouse_over:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))
            if self.cursor.scroll_up:
                if self.current_row > 0:
                    self.current_row -= 1
                    self.scroll.change_image(self.current_row, self.scroll_total_row)
                    self.draw_list()
            elif self.cursor.scroll_down:
                if self.current_row < self.total_row:
                    self.current_row += 1
                    self.scroll.change_image(self.current_row, self.scroll_total_row)
                    self.draw_list()
            else:
                for index, rect in enumerate(self.army_rects):
                    if rect.collidepoint(inside_mouse_pos) and index < len(self.army_card_list):
                        army = self.grand.current_campaign_state["faction"][self.grand.player_faction][
                            "army"][self.current_row + index]
                        if self.event_press:
                            if self.grand.shift_press:
                                if army not in self.grand.player_selected_army:
                                    self.grand.player_selected_army.append(army)
                            elif self.grand.ctrl_press:
                                if army in self.grand.player_selected_army:
                                    self.grand.player_selected_army.remove(army)
                            else:
                                self.grand.player_selected_army = [army]
                            self.draw_list()
                        elif self.event_alt_press:
                            # open army management ui
                            self.grand.outer_ui_updater.add()
                        elif self.event_middle_mouse_press:
                            self.grand.camera_pos = Vector2(
                                (army.base_pos[0] * self.grand.map_shown_to_actual_scale_width) - self.half_screen_width,
                                (army.base_pos[1] * self.grand.map_shown_to_actual_scale_height) - self.half_screen_height)
                            self.grand.fix_camera()
                        break


class PlayerFactionTechBar(UIGrand):
    def __init__(self):
        self._layer = 5
        UIGrand.__init__(self)
        self.image = Surface((600 * self.screen_scale_width, 80 * self.screen_scale_height), SRCALPHA)
        self.font = self.game.generic_ui_font

    def update(self, dt):
        pass


class MenuBar(UIGrand):
    def __init__(self):
        self._layer = 4
        UIGrand.__init__(self)
        self.image = Surface((600 * self.screen_scale_width, 100 * self.screen_scale_height), SRCALPHA)
        self.image.fill((50, 50, 200))
        self.button_rect = {"character": (), "diplomacy": (), "technology": (), "economy": (), "menu": ()}
        self.rect = self.image.get_rect(topright=(self.grand.mini_time_orb_ui.rect.topleft[0] +
                                                  (self.image.get_width() * 0.1),
                                                  (self.grand.time_setting_ui.rect.bottomleft[1])))

    def update(self, dt):
        UIMenu.update(self, dt)


class TimeInfoBar(UIGrand):
    def __init__(self):
        self._layer = 4
        UIGrand.__init__(self, player_cursor_interact=False)
        self.image = Surface((800 * self.screen_scale_width, 100 * self.screen_scale_height), SRCALPHA)
        self.image.fill((50, 50, 255))
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(topright=(self.grand.mini_time_orb_ui.rect.topleft[0] +
                                                  (self.image.get_width() * 0.05), 0))

    def update(self, dt):
        UIMenu.update(self, dt)


class TimeSettingOption(UIGrand):
    def __init__(self):
        self._layer = 5
        UIGrand.__init__(self)

        self.image = Surface((700 * self.screen_scale_width, 100 * self.screen_scale_height))
        self.image.fill((10, 100, 200))
        self.rect = self.image.get_rect(topright=((self.grand.mini_time_orb_ui.rect.topleft[0],
                                                   self.grand.time_info_bar_ui.rect.bottomleft[1])))

    def update(self, dt):
        UIMenu.update(self, dt)


class MiniTimeOrb(UIGrand):
    def __init__(self):
        self._layer = 5
        UIGrand.__init__(self)

        self.image = Surface((600 * self.screen_scale_width, 400 * self.screen_scale_height))
        self.image.fill((255, 255, 255))
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(topright=(self.screen_size[0], 0))

    def update_time(self):
        pass

    def update(self, dt):
        UIMenu.update(self, dt)
        if self.event_press:
            pass


class RegionManagement(UIGrand):
    def __init__(self):
        self._layer = 5
        UIGrand.__init__(self)
        self.font = self.game.generic_ui_font
        self.header_font = self.game.large_generic_ui_font
        self.image = Surface((2200 * self.screen_scale_width, 432 * self.screen_scale_height))
        self.image.fill((200, 50, 50))
        self.base_image = self.image.copy()
        self.building_slot_rects = {index: (200 * int(index / 5),) for index in range(10)}
        self.rect = self.image.get_rect(bottomleft=(0, self.screen_height))

    def change_selected_region(self, region):
        self.grand.player_selected_region = region
        if region:
            self.image = self.base_image.copy()
            self.outer_ui_updater.add(self)
        else:
            self.outer_ui_updater.remove(self)

    def update(self, dt):
        UIMenu.update(self, dt)
        if self.mouse_over:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))


class EventNotification(UIGrand):
    event_icons = {}

    def __init__(self):
        self._layer = 5
        UIGrand.__init__(self)
        self.font = self.game.generic_ui_font
        self.header_font = self.game.large_generic_ui_font
        self.image = Surface((0 * self.screen_scale_width, 0 * self.screen_scale_height))
        self.event_item_height = 100 * self.screen_scale_height
        self.image.fill((0, 200, 50))
        self.base_image = self.image.copy()
        self.all_event_rects = [Rect(0, index * 100 * self.screen_scale_height,
                                     800 * self.screen_scale_width, self.event_item_height) for index in range(10)]
        self.active_event_rects = []
        self.rect = self.image.get_rect(bottomleft=(0, self.grand.region_management_ui.rect.topleft[1]))

    def event_list_update(self):
        event_list = self.grand.current_campaign_state["eventlog"]
        self.image = Surface((800 * self.screen_scale_width, len(event_list[:10]) * self.event_item_height))
        self.image.fill((0, 200, 50))
        for index, event in enumerate(event_list[:10]):  # show only max 10 items
            event_icon = self.event_icons[event[0]]
            self.image.blit(event_icon, event_icon.get_rect(topleft=(0, index * self.event_item_height)))

            event_text = self.font.render(event[1], True, (0, 0, 0))
            self.image.blit(event_text, event_text.get_rect(topleft=(100 * self.screen_scale_width,
                                                                     index * self.event_item_height)))

            self.active_event_rects.append(Rect((0, index * 100) * self.screen_scale_height,
                                                800 * self.screen_scale_width, self.event_item_height))
        self.active_event_rects = self.all_event_rects[:len(event_list[:10])]
        self.rect = self.image.get_rect(bottomleft=(0, self.grand.region_management_ui.rect.topleft[1]))

    def update(self, dt):
        UIMenu.update(self, dt)
        if self.mouse_over:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))
            for index, rect in enumerate(self.active_event_rects):
                if rect.collidepoint(inside_mouse_pos):
                    if self.event_press:  # open event popup
                        self.grand.event_important_popup.event_popup(self.grand.current_campaign_state["eventlog"][index])
                        self.grand.current_campaign_state["eventlog"].pop(index)
                        self.event_list_update()
                    elif self.event_middle_mouse_press:  # go to event location
                        event = self.grand.current_campaign_state["eventlog"][index]
                        self.grand.camera_pos = Vector2(
                            (event[2][0] * self.grand.map_shown_to_actual_scale_width) - self.half_screen_width,
                            (event[2][1] * self.grand.map_shown_to_actual_scale_height) - self.half_screen_height)
                        self.grand.fix_camera()
                    elif self.event_alt_press:  # remove event
                        self.grand.current_campaign_state["eventlog"].pop(index)
                        self.event_list_update()


class TechManagement(UIGrand):
    def __init__(self):
        self._layer = 5
        UIGrand.__init__(self)

        self.image = Surface((3044 * self.screen_scale_width, 432 * self.screen_scale_height), SRCALPHA)
        self.rect = self.image.get_rect(center=(self.screen_width / 2, self.screen_height / 2))

    def update(self, dt):
        UIMenu.update(self, dt)
        if self.mouse_over:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))


class CultureManagement(UIGrand):
    def __init__(self):
        self._layer = 5
        UIGrand.__init__(self)

        self.image = Surface((3044 * self.screen_scale_width, 432 * self.screen_scale_height), SRCALPHA)
        # self.
        self.policy_icon_rect_x = {policy: (index + 1) * 200 for index, policy in
                                   enumerate(Culture_Policy_Integration.keys())}
        self.rect = self.image.get_rect(center=(self.screen_width / 2, self.screen_height / 2))

    def update(self, dt):
        UIMenu.update(self, dt)
        if self.mouse_over:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))


class MapSettingOption(UIGrand):
    def __init__(self):
        self._layer = 5
        UIGrand.__init__(self)

        self.image = Surface((150 * self.screen_scale_width, 432 * self.screen_scale_height))
        self.image.fill((150, 50, 80))
        self.rect = self.image.get_rect(topright=self.grand.mini_map.rect.topleft)

    def update(self, dt):
        UIMenu.update(self, dt)
        if self.mouse_over:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))


class RegionInfoBar(UIGrand):
    def __init__(self):
        self._layer = 4
        UIGrand.__init__(self, player_cursor_interact=False)

        self.image = Surface((800 * self.screen_scale_width, 1000 * self.screen_scale_height))
        self.image.fill((255, 255, 255))
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(center=(self.screen_width / 2, self.screen_height / 2))

    def update(self, dt):
        pass


class EventImportantPopup(UIGrand):
    def __init__(self):
        self._layer = 6
        UIGrand.__init__(self)

        self.image = Surface((800 * self.screen_scale_width, 1000 * self.screen_scale_height))
        self.image.fill((255, 255, 255))
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(center=(self.screen_width / 2, self.screen_height / 2))

    def popup(self, event_data):
        pass

    def update(self, dt):
        UIMenu.update(self, dt)
        if self.mouse_over:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))


class PlayerGrandInteract(UIGrand):
    def __init__(self):
        self._layer = 9999999999999999999999999999999999999998  # always 1 layer less than cursor so it get updated last but before cursor
        UIGrand.__init__(self, player_cursor_interact=False)
        self.grand_camera = self.grand.camera
        self.selection_start_pos = Vector2()
        self.current_pos = Vector2()
        self.line_size = int(10 * self.screen_scale_width)
        self.inner_line_size = int(20 * self.screen_scale_width)
        if self.line_size < 1:
            self.line_size = 1
        self.image = None
        self.rect = None
        # self.current_strategy_base_range = None
        # self.current_strategy_base_activate_range = None
        # self.current_strategy_range = None
        # self.current_strategy_activate_range = None
        # self.strategy_line_top = 500 * self.screen_scale_height
        # self.strategy_line_bottom = 2160 * self.screen_scale_height
        # self.strategy_line_width = int(20 * self.screen_scale_width)
        # self.strategy_line_inner_width = int(self.strategy_line_width / 2)
        # self.strategy_line_center = 900 * self.screen_scale_height
        # self.show_strategy_activate_line = False

    def reset(self):
        self.current_pos = None
        self.selection_start_pos = None
        self.rect = None

    def update(self, dt):
        self.event_press = False
        self.event_hold = False  # some UI differentiates between press release or holding, if not just use event
        self.event_alt_press = False
        self.event_alt_hold = True
        # self.show_strategy_activate_line = False
        if not self.cursor.mouse_over:
            # only consider if not mouse over any ui
            if self.cursor.is_alt_select_just_up:  # put alt (right) click first to prioritise it
                self.event_alt_press = True
                self.cursor.is_alt_select_just_up = False  # reset select button to prevent overlap interaction
            elif self.cursor.is_alt_select_down:
                self.event_alt_hold = True
                self.cursor.is_alt_select_just_down = False  # reset select button to prevent overlap interaction
            elif self.cursor.is_select_just_up:
                self.event_press = True
                self.cursor.is_select_just_up = False  # reset select button to prevent overlap interaction
            elif self.cursor.is_select_down:
                self.event_hold = True
                self.cursor.is_select_just_down = False  # reset select button to prevent overlap interaction
            # else:  # no mouse activity
            #     if self.battle.player_selected_strategy:
            #         # draw activation line
            #         commander = self.battle.team_commander[self.battle.player_team]
            #         line_start = (commander.pos[0] - self.current_strategy_activate_range) - (
            #                 self.battle.shown_camera_pos[0] - self.grand_camera.camera_w_center)
            #         line_end = (commander.pos[0] + self.current_strategy_activate_range) - (
            #                 self.battle.shown_camera_pos[0] - self.grand_camera.camera_w_center)
            #         if line_start > 0:
            #             draw.line(self.battle.camera.image, (80, 120, 200),
            #                       (line_start, self.strategy_line_top),
            #                       (line_start, self.strategy_line_bottom), width=self.strategy_line_width)
            #             draw.line(self.battle.camera.image, (20, 70, 50),
            #                       (line_start, self.strategy_line_top),
            #                       (line_start, self.strategy_line_bottom), width=self.strategy_line_inner_width)
            #         if line_end > 0:
            #             draw.line(self.battle.camera.image, (80, 120, 200),
            #                       (line_end, self.strategy_line_top),
            #                       (line_end, self.strategy_line_bottom), width=self.strategy_line_width)
            #             draw.line(self.battle.camera.image, (20, 70, 50),
            #                       (line_end, self.strategy_line_top),
            #                       (line_end, self.strategy_line_bottom), width=self.strategy_line_inner_width)

            # if not self.current_strategy_base_activate_range or \
            #         (abs(commander.base_pos[0] - self.battle.base_cursor_pos[0]) <
            #         self.current_strategy_base_activate_range):
            #     self.show_strategy_activate_line = True
            #
            # # draw strategy range if player cursor is within activation range, mean strategy can be used
            # # or strategy has no activation range, which mean activate only from commander
            # if not self.current_strategy_base_activate_range:
            #     pos_to_use = commander.pos[0]
            # else:
            #     pos_to_use = self.battle.cursor_pos[0]
            # line_start = (pos_to_use - self.current_strategy_range) - (
            #         self.battle.shown_camera_pos[0] - self.grand_camera.camera_w_center)
            # line_end = (pos_to_use + self.current_strategy_range) - (
            #         self.battle.shown_camera_pos[0] - self.grand_camera.camera_w_center)
            # if line_start > 0:
            #     draw.line(self.battle.camera.image, (120, 180, 80),
            #               (line_start, self.strategy_line_top),
            #               (line_start, self.strategy_line_bottom), width=self.strategy_line_width)
            #     draw.line(self.battle.camera.image, (70, 20, 50),
            #               (line_start, self.strategy_line_top),
            #               (line_start, self.strategy_line_bottom), width=self.strategy_line_inner_width)
            # if line_end > 0:
            #     draw.line(self.battle.camera.image, (120, 180, 80),
            #               (line_start, self.strategy_line_center),
            #               (line_end, self.strategy_line_center), width=self.strategy_line_width)
            #
            #     draw.line(self.battle.camera.image, (120, 180, 80),
            #               (line_end, self.strategy_line_top),
            #               (line_end, self.strategy_line_bottom), width=self.strategy_line_width)
            #     draw.line(self.battle.camera.image, (70, 20, 50),
            #               (line_end, self.strategy_line_top),
            #               (line_end, self.strategy_line_bottom), width=self.strategy_line_inner_width)

            if not self.event_hold and not self.event_press:
                if self.selection_start_pos:  # release hold while band exist
                    player_armies = self.grand.current_campaign_state["faction"][self.grand.player_faction]["army"]
                    army_select_list = list(set([army for index, army in enumerate(player_armies) if
                                          index in self.rect.collidelistall([army.commander_actor.rect for
                                                                             army in player_armies])]))
                    if army_select_list:
                        if self.grand.shift_press:
                            self.grand.player_selected_army += army_select_list
                            self.grand.player_selected_army = list(set(self.grand.player_selected_army))
                        elif self.grand.ctrl_press:
                            for army in army_select_list:
                                if army in self.grand.player_selected_army:
                                    self.grand.player_selected_army.remove(army)
                        else:
                            self.grand.player_selected_army = army_select_list
                    else:
                        for army in self.grand.player_selected_army:
                            self.grand.player_selected_army.remove(army)

                        region_colour = tuple(self.grand.grand_map.true_map_image.get_at(
                            (int(self.grand.base_cursor_pos[0]), int(self.grand.base_cursor_pos[1]))))[:3]
                        if region_colour in self.grand.region_by_colour_list:
                            region_id = self.grand.region_by_colour_list[region_colour]["ID"]
                            self.grand.region_management_ui.change_selected_region(region_id)
                        else:  # select at water region, remove region management ui
                            self.grand.region_management_ui.change_selected_region(None)

                    self.grand.player_army_list_ui.draw_list()
                    self.reset()

                elif self.event_alt_press:  # right click order selected leader to do something
                    # if self.battle.player_selected_strategy:
                    #     # has strategy selected, prioritise activate strategy for this input
                    #     if self.battle.activate_strategy(self.battle.player_team, self.battle.player_selected_strategy[0],
                    #                                      self.battle.player_selected_strategy[1],
                    #                                      self.battle.base_cursor_pos[0]):
                    #         # successfully activate strategy
                    #         self.battle.player_selected_strategy = None
                    # else:
                    pass
                    # if self.grand.player_selected_army:
                    #     for army in self.grand.player_selected_army:
                    #         army.issue_order(("move", self.grand.base_cursor_pos[0]))
            else:  # holding left click, manipulate band
                # if self.event_press and self.battle.player_selected_strategy:
                #     # deactivate strategy when there is one selected
                #     self.battle.player_selected_strategy = None

                self.current_pos = self.cursor.pos
                if not self.selection_start_pos:
                    self.selection_start_pos = self.current_pos
                else:
                    x1, y1 = self.selection_start_pos
                    x2, y2 = self.current_pos
                    # Calculate the top-left and dimensions of the selection rectangle
                    left = min(x1, x2)
                    top = min(y1, y2)
                    if self.current_pos != self.selection_start_pos:
                        width = abs(x1 - x2)
                        height = abs(y1 - y2)
                        selection_rect = Rect(left, top, width, height)
                        self.rect = Rect(left + self.grand.camera_pos[0],
                                         top + self.grand.camera_pos[1], width, height)  # rect for collision unit selection check
                        draw.rect(self.grand_camera.image, (0, 0, 0), selection_rect, self.inner_line_size)
                        draw.rect(self.grand_camera.image, (255, 255, 255), selection_rect, self.line_size)
                    else:
                        self.rect = Rect(left + self.grand.camera_pos[0],
                                         top + self.grand.camera_pos[1], 1, 1)  # rect for collision unit selection check
        else:
            self.reset()
#
# from math import cos, sin
# from pygame import Vector2, display, sprite, Surface
# from pygame.mask import from_surface
# from pygame.sprite import spritecollide, collide_mask
# import pygame
#
# pygame.init()
#
# screen_width, screen_height = 1920, 1080
# screen = display.set_mode((screen_width, screen_height))
# display.set_caption("Fantasy Universe")
#
# font = pygame.font.SysFont("Arial", 16)
# speed_font = pygame.font.SysFont("Arial", 32)
#
#
# def circle_orbit(center, radius, angle, *args):
#     """
#     Finding the x,y coordinates on circle, based on given angle
#     """
#     # center of circle, angle in degree and radius of circle
#     x = center[0] + (radius[0] * cos(angle))
#     y = center[1] + (radius[0] * sin(angle))
#     return x, y
#
#
# def custom_orbit(center, _, angle, movement_surface, collide_surface):
#     collide_surface.image = collide_surface.check_image.copy()
#
#     pygame.draw.line(collide_surface.image, (0, 0, 0), collide_surface.image_center,
#                      (collide_surface.image_center[0] + (10000 * cos(angle)),
#                       collide_surface.image_center[1] + (10000 * sin(angle))))
#     collide_surface.mask = from_surface(collide_surface.image)
#     collide_pos = collide_mask(collide_surface, movement_surface)
#     return (center[0] + (collide_pos[0] - collide_surface.image_center[0]),
#             center[1] + (collide_pos[1] - collide_surface.image_center[1]))
#
#
# def create_movement_image(shape, size):
#     base_image = Surface((size[0], size[1]), pygame.SRCALPHA)
#     collide_check_image = Surface((size[0], size[1]), pygame.SRCALPHA)
#     if shape == "square":
#         pygame.draw.rect(base_image, color=(255, 255, 255), rect=(0, 0, size[0], size[1]), width=2)
#     elif shape == "ellipse":
#         pygame.draw.ellipse(base_image, color=(255, 255, 255), rect=(0, 0, size[0], size[1]), width=2)
#
#     return base_image, collide_check_image
#
#
# class CollideSurface(sprite.Sprite):
#     def __init__(self, image):
#         sprite.Sprite.__init__(self)
#         self.image = image
#         self.check_image = image
#         self.image_center = (self.image.get_width() / 2, self.image.get_height() / 2)
#         self.rect = image.get_rect(center=(0, 0))
#         self.mask = from_surface(image)
#
#     def update(self, pos):
#         self.rect.center = Vector2(pos[0], pos[1])
#         self.mask = from_surface(self.image)
#
#
# class Planet(pygame.sprite.Sprite):
#     def __init__(self, start_angle, sprite_radius, color, name, orbit=None, epicycle=None, specific_pos=()):
#         self.sprite_radius = sprite_radius
#         self.color = color
#         self.name = name
#
#         self.last_path = ()
#         self.pos = ()
#
#         self.current_orbit_angle = start_angle
#         self.parent = None
#         self.parent_radius = 0
#         self.orbit_speed = 0
#         self.orbit_shape = "circle"
#         self.orbit_movement_check = None
#         self.orbit_collide_check = None
#         if orbit:
#             self.orbit_speed = orbit["speed"]
#             self.orbit_shape = orbit["shape"]
#             self.parent_radius = orbit["radius"]
#             self.parent = orbit["parent"]
#             orbit_movement_check_image, orbit_collide_check_image = create_movement_image(orbit["shape"],
#                                                                                           orbit["radius"])
#             self.orbit_movement_check = CollideSurface(orbit_movement_check_image)
#             self.orbit_collide_check = CollideSurface(orbit_collide_check_image)
#         elif not specific_pos:  # assume to be center of universe
#             self.pos = (screen_width / 2, screen_height / 2)
#         else:
#             self.pos = specific_pos
#         self.orbit_pos = self.pos
#         self.orbit_process = circle_orbit
#         if self.orbit_shape != "circle":
#             self.orbit_process = custom_orbit
#
#         self.current_epicycle_angle = 0
#         self.epicycle_speed = 0
#         self.epicycle_radius = 0
#         self.epicycle_shape = "circle"
#         self.epicycle_movement_check = None
#         self.epicycle_collide_check = None
#         if epicycle:
#             self.epicycle_speed = epicycle["speed"]
#             self.epicycle_radius = epicycle["radius"]
#             self.epicycle_shape = epicycle["shape"]
#             epicycle_movement_check_image, epicycle_collide_check_image = create_movement_image(epicycle["shape"],
#                                                                                                 epicycle["radius"])
#             self.epicycle_movement_check = CollideSurface(epicycle_movement_check_image)
#             self.epicycle_collide_check = CollideSurface(epicycle_collide_check_image)
#         self.epicycle_process = circle_orbit
#         if self.epicycle_shape != "circle":
#             self.epicycle_process = custom_orbit
#         self.update_position(0, 0)
#
#     def draw(self, win, background, show_base_shape):
#         # Draw the orbit path
#         if show_base_shape:
#             if self.orbit_movement_check:
#                 background.blit(self.orbit_movement_check.image, self.orbit_collide_check.rect)
#         else:
#             if self.last_path:
#                 pygame.draw.line(background, self.color, self.pos, self.last_path, 2)
#                 self.last_path = ()
#
#         # Draw the planet
#         pygame.draw.circle(win, self.color, self.pos, self.sprite_radius)
#
#         # Draw distance to the sun for planets other than the sun
#         # if not self.sun:
#         #     distance_text = font.render(f"{round(self.distance_to_sun / 1000, 1)} km", True, WHITE)
#         #     win.blit(distance_text, (int(x - distance_text.get_width() / 2), int(y - distance_text.get_height() / 2)))
#
#         # Draw name and additional info if planet is selected
#         info_text = font.render(self.name, True, (255, 255, 255))
#         win.blit(info_text, (int(self.pos[0] - info_text.get_width() / 2), int(self.pos[1] - self.sprite_radius - 20)))
#
#     def update_position(self, dt, speed):
#         self.last_path = self.pos
#         if self.orbit_speed:
#             self.current_orbit_angle += self.orbit_speed * dt * speed
#             # if self.current_orbit_angle >= 360:
#             #     self.current_orbit_angle -= 360
#             # elif self.current_orbit_angle < 0:
#             #     self.current_orbit_angle += 360
#             self.orbit_movement_check.update(self.parent.pos)
#             self.orbit_collide_check.update(self.parent.pos)
#             self.orbit_pos = self.orbit_process(self.parent.pos, self.parent_radius, self.current_orbit_angle,
#                                                 self.orbit_movement_check, self.orbit_collide_check)
#             self.pos = self.orbit_pos
#         if self.epicycle_speed:
#             self.current_epicycle_angle += self.epicycle_speed * dt * speed
#             self.epicycle_movement_check.update(self.orbit_pos)
#             self.epicycle_collide_check.update(self.orbit_pos)
#             self.pos = self.epicycle_process(self.orbit_pos, self.epicycle_radius, self.current_epicycle_angle,
#                                              self.epicycle_movement_check, self.epicycle_collide_check)
#
#
# def main():
#     run = True
#     clock = pygame.time.Clock()
#
#     background_base = Surface((screen_width, screen_height))
#     background = background_base.copy()
#
#     sun_helio = Planet(20, 20, (255, 0, 0), "Sol")
#     earth_helio = Planet(0,  8, (255, 0, 0), "Terra",
#                           orbit={"parent": sun_helio, "speed": 0.7, "shape": "circle", "radius": (200, 200)})
#     planets_helio = [Planet(180, 8, (30, 30, 150), "Lunar",
#                           orbit={"parent": earth_helio, "speed": 1, "shape": "circle", "radius": (50, 50)}),
#                    Planet(270,  8, (255, 255, 255), "Planar 1",
#                           orbit={"parent": sun_helio, "speed": 0.8, "shape": "circle", "radius": (500, 500)}),
#                    sun_helio, earth_helio]
#
#     # Create the sun with a smaller radius
#     terra_geo = Planet(20, 15, (50, 50, 200), "Terra")
#
#     # Add planets
#     planets_geo = [Planet(200, 10, (30, 30, 150), "Lunar",
#                           orbit={"parent": terra_geo, "speed": 1, "shape": "circle", "radius": (80, 80)}),
#                    Planet(150,  8, (255, 255, 255), "Planar 1",
#                           orbit={"parent": terra_geo, "speed": 0.8, "shape": "circle", "radius": (200, 200)},
#                           epicycle={"speed": 0.5, "shape": "circle", "radius": (150, 150)}),
#                    Planet(200,  12, (255, 0, 0), "Sol",
#                           orbit={"parent": terra_geo, "speed": 0.7, "shape": "circle", "radius": (300, 300)}),
#                    terra_geo]
#
#     sun_nonsense = Planet(20, 20, (255, 0, 0), "Sol",
#                           epicycle={"speed": 0.5, "shape": "square", "radius": (30, 100)})
#     earth_nonsense = Planet(200,  8, (255, 0, 0), "Our World",
#                           orbit={"parent": sun_nonsense, "speed": 0.7, "shape": "circle", "radius": (300, 300)})
#     planets_nonsense = [Planet(200, 8, (30, 30, 150), "Lunar",
#                           orbit={"parent": earth_nonsense, "speed": 1, "shape": "circle", "radius": (200, 200)}),
#                         Planet(150,  8, (255, 255, 255), "Planar 1",
#                                orbit={"parent": sun_nonsense, "speed": 3, "shape": "ellipse", "radius": (300, 200)}),
#                         sun_nonsense, earth_nonsense]
#
#     models = {
#         "Faux Heliocentric": planets_helio,
#         "Faux Geocentric": planets_geo,
#         "Nonsense": planets_nonsense
#     }
#     speed = 1
#     keypress_delay = 0
#     day = 0
#     current_model = 0
#     show_base_shape = False
#     planets = models[tuple(models.keys())[current_model]]
#     speed_text = speed_font.render("Speed: " + str(speed), True, (255, 255, 255))
#     speed_text_rect = speed_text.get_rect(topleft=(0, screen_height - 100))
#     model_text = speed_font.render("Model: " + tuple(models.keys())[current_model], True, (255, 255, 255))
#     model_text_rect = model_text.get_rect(topright=(screen_width, screen_height - 100))
#
#     while run:
#         clock.tick(1000)
#         screen.fill((0, 0, 0))
#         dt = clock.get_time() / 1000
#         if dt > 0.1:  # one frame update should not be longer than 0.1 second for calculation
#             dt = 0.1  # make it so stutter and lag does not cause overtime issue
#
#         # Handle events
#         shift_press = False
#         key_press = pygame.key.get_pressed()
#         if key_press is not None and not keypress_delay:
#             if key_press[pygame.K_LSHIFT] or key_press[pygame.K_RSHIFT]:
#                 shift_press = True
#             if key_press[pygame.K_KP_PLUS]:
#                 if shift_press:
#                     speed += 1
#                 else:
#                     speed += 0.1
#                 speed_text = speed_font.render("Speed: " + str(round(speed, 1)), True, (255, 255, 255))
#                 keypress_delay = 0.1
#             elif key_press[pygame.K_KP_MINUS]:
#                 if shift_press:
#                     speed -= 1
#                 else:
#                     speed -= 0.1
#                 speed_text = speed_font.render("Speed: " + str(round(speed, 1)), True, (255, 255, 255))
#                 keypress_delay = 0.1
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 run = False
#             elif event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_ESCAPE:
#                     run = False
#                 elif event.key == pygame.K_TAB:
#                     if show_base_shape:
#                         show_base_shape = False
#                     else:
#                         show_base_shape = True
#                     background = background_base.copy()
#                 elif event.key == pygame.K_p:  # Pause/Play
#                     speed = 0
#                     speed_text = speed_font.render("Speed: " + str(round(speed, 1)), True, (255, 255, 255))
#                 elif event.key == pygame.K_LEFTBRACKET:
#                     current_model -= 1
#                     if current_model < 0:
#                         current_model = len(models) - 1
#                     planets = models[tuple(models.keys())[current_model]]
#                     background = background_base.copy()
#                     model_text = speed_font.render("Model: " + tuple(models.keys())[current_model], True,
#                                                    (255, 255, 255))
#                 elif event.key == pygame.K_RIGHTBRACKET:
#                     current_model += 1
#                     if current_model == len(models):
#                         current_model = 0
#                     planets = models[tuple(models.keys())[current_model]]
#                     background = background_base.copy()
#                     model_text = speed_font.render("Model: " + tuple(models.keys())[current_model], True,
#                                                    (255, 255, 255))
#
#         if keypress_delay:
#             keypress_delay -= dt
#             if keypress_delay < 0:
#                 keypress_delay = 0
#
#         # Update and draw planets
#         screen.blit(background, (0, 0))
#         for planet in planets:
#             planet.update_position(dt, speed)
#             planet.draw(screen, background, show_base_shape)
#         screen.blit(speed_text, speed_text_rect)
#         screen.blit(model_text, model_text_rect)
#         display.update()
#
#     pygame.quit()
