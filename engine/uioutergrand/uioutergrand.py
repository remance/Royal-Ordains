from math import ceil, floor

from pygame import Vector2, Surface, SRCALPHA, Rect, draw, Color
from pygame.transform import smoothscale

from engine.constants import Culture_Policy_Integration
from engine.uiouterbattle.uiouterbattle import EventNotification as BattleEventNotification
from engine.uimenu.uimenu import UIMenu
from engine.utils.text_making import add_plus_to_number, add_comma_number, text_render_with_bg


class UIOuterGrand(UIMenu):
    def __init__(self, player_cursor_interact=True, has_containers=False):
        """
        Parent class for all battle menu user interface that exist outside of grand camera
        """
        from engine.grand.grand import Grand
        UIMenu.__init__(self, player_cursor_interact=player_cursor_interact, has_containers=has_containers)
        self.grand = Grand.grand
        self.grand_ui_icons = self.grand.grand_ui_icons
        self.grand_ui_images = self.grand.grand_ui_images
        self.building_portraits = self.grand.building_portraits
        self.text_popup = self.grand.text_popup
        self.outer_ui_updater = self.grand.outer_ui_updater
        self.max_description_box_width = int(1000 * self.screen_scale_width)


class YesNo(UIOuterGrand):
    def __init__(self):
        UIOuterGrand.__init__(self)
        self._layer = 5
        self.yes_image = self.grand_ui_images["yes"]
        self.no_image = self.grand_ui_images["no"]

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


class PlayerTopBar(UIOuterGrand):
    def __init__(self):
        """UI Bar at the top of screen showing player's faction resource and turn time"""
        self._layer = 5
        UIOuterGrand.__init__(self)

        self.max_description_box_width = int(1500 * self.screen_scale_width)
        self.image = Surface((2600 * self.screen_scale_width, 80 * self.screen_scale_height))
        self.image.fill((80, 200, 255))
        self.image.blit(self.grand_ui_icons["gold"], (50 * self.screen_scale_width,
                                                      10 * self.screen_scale_height))
        self.image.blit(self.grand_ui_icons["supply"], (850 * self.screen_scale_width,
                                                        10 * self.screen_scale_height))
        self.image.blit(self.grand_ui_icons["happiness"], (1550 * self.screen_scale_width,
                                                           10 * self.screen_scale_height))
        self.image.blit(self.grand_ui_icons["turn"], (1950 * self.screen_scale_width,
                                                      10 * self.screen_scale_height))

        self.base_image = self.image.copy()
        self.font = self.game.large_generic_ui_font
        self.text_pos = {"gold": (150 * self.screen_scale_width, 10 * self.screen_scale_height),
                         "supply": (950 * self.screen_scale_width, 10 * self.screen_scale_height),
                         "happiness": (1650 * self.screen_scale_width, 10 * self.screen_scale_height),
                         "turn": (2050 * self.screen_scale_width, 10 * self.screen_scale_height)}
        self.blit_text_rect = {}
        self.player_faction_resource = {}
        self.rect = self.image.get_rect(topleft=(0, 0))

    def update(self, dt):
        current_campaign_state = self.grand.current_campaign_state

        resource = current_campaign_state["faction"][self.grand.player_faction]
        resource = ((int(resource["gold"]), int(resource["gold_income"])),
                    (int(resource["supply"]), int(resource["supply_income"])),
                    int(resource["happiness"]), str(current_campaign_state["turn"]) + "." +
                    str(current_campaign_state["phase"]))

        if self.player_faction_resource != resource:
            self.blit_text_rect = {}
            self.image = self.base_image.copy()
            self.player_faction_resource = resource

            for index, text in enumerate(self.text_pos):
                value = str(resource[index])
                if text in ("gold", "supply"):
                    value = (add_comma_number(resource[index][0]) + " (" +
                             add_plus_to_number(add_comma_number(resource[index][1])) + ")")
                value = text_render_with_bg(value, self.font)
                blit_text_rect = value.get_rect(topleft=self.text_pos[text])
                self.image.blit(value, blit_text_rect)
                self.blit_text_rect[text] = blit_text_rect

        UIOuterGrand.update(self, dt)

        if self.mouse_over:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))
            for key, rect in self.blit_text_rect.items():
                if rect.collidepoint(inside_mouse_pos):
                    text = [self.grab_text(("ui", "info_text_" + key)),
                            self.grab_text(("ui", "info_text_" + key + "_description")), ""]
                    if key != "turn":
                        resource_effect_list = self.grand.current_campaign_state["faction"][self.grand.player_faction][
                            key + "_effect"]
                        text_sum = {key: 0 for key in resource_effect_list}
                        for key2, value2 in resource_effect_list.items():
                            if type(value2) is list:
                                for value3 in value2:
                                    text_sum[key2] += value3[1]
                            else:
                                text_sum[key2] += value2
                        for key2, value2 in text_sum.items():
                            if value2:
                                text.append(self.grab_text(("ui", "info_header_" + key2)) +
                                            add_plus_to_number(add_comma_number(int(value2))))
                    self.text_popup.popup(self.cursor.rect.bottomright, text,
                                          width_text_wrapper=self.max_description_box_width)
                    self.outer_ui_updater.add(self.text_popup)
                    break


class MenuBar(UIOuterGrand):
    def __init__(self):
        self._layer = 4
        UIOuterGrand.__init__(self)
        button_images = self.grand.grand_ui_icons
        self.image = Surface((800 * self.screen_scale_width, 80 * self.screen_scale_height), SRCALPHA)
        self.image.fill((50, 50, 200))
        self.button_rects = {"character": button_images["character"].get_rect(topleft=(0, 0)),
                             "diplomacy": button_images["diplomacy"].get_rect(
                                 topleft=(150 * self.screen_scale_width, 0)),
                             "technology": button_images["technology"].get_rect(
                                 topleft=(300 * self.screen_scale_width, 0)),
                             "menu": button_images["menu"].get_rect(topleft=(450 * self.screen_scale_width, 0))}
        for key, value in self.button_rects.items():
            self.image.blit(button_images[key], self.button_rects[key])
        self.option_selected = None
        self.rect = self.image.get_rect(topleft=(self.grand.time_setting_ui.rect.topright[0], 0))

    def update(self, dt):
        UIOuterGrand.update(self, dt)
        if self.mouse_over:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))

            for key, rect in self.button_rects.items():
                if rect.collidepoint(inside_mouse_pos):
                    if self.event_press:
                        self.option_selected = key


class TimeSettingOption(UIOuterGrand):
    def __init__(self):
        self._layer = 5
        UIOuterGrand.__init__(self)

        self.image = Surface((600 * self.screen_scale_width, 80 * self.screen_scale_height))
        self.image.fill((10, 100, 200))

        battle_ui_images = self.game.battle.battle_ui_images
        self.time_select_image = battle_ui_images["time_select"]
        self.time_option_rects = {key: key.get_rect(
            topleft=((100 * (index + 1)) * self.screen_scale_width, 10 * self.screen_scale_height)) for index, key in
            enumerate([battle_ui_images["time_pause"],
                       battle_ui_images["time_normal"],
                       battle_ui_images["time_fast"],
                       battle_ui_images["time_faster"]])}
        for index, image in enumerate(self.time_option_rects):
            rect = self.time_option_rects[image]
            self.image.blit(battle_ui_images["time_unselect"], rect)
            self.image.blit(image, rect)

        self.base_image = self.image.copy()

        for index, image in enumerate(self.time_option_rects):  # add selected border after base image
            rect = self.time_option_rects[image]
            if not index:
                self.image.blit(battle_ui_images["time_select"], rect)
                self.image.blit(image, rect)
                break

        self.rect = self.image.get_rect(topleft=(self.grand.player_top_bar_ui.rect.topright[0], 0))

    def reset(self):
        self.image = self.base_image.copy()

        for index, image in enumerate(self.time_option_rects):  # add selected border after base image
            rect = self.time_option_rects[image]
            if not index:
                self.image.blit(self.time_select_image, rect)
                self.image.blit(image, rect)
                break

    def update(self, dt):
        UIOuterGrand.update(self, dt)
        if self.event_press:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))
            for index, image in enumerate(self.time_option_rects):
                rect = self.time_option_rects[image]
                if rect.collidepoint(inside_mouse_pos):
                    if index != self.grand.game_speed:
                        self.grand.game_speed = index
                        self.image = self.base_image.copy()
                        self.image.blit(self.time_select_image, rect)
                        self.image.blit(image, rect)
                    break


class PlayerFactionCultureList(UIOuterGrand):
    def __init__(self):
        self._layer = 5
        UIOuterGrand.__init__(self)
        self.font = self.game.medium_generic_ui_font
        self.value_text_font_cache = {}
        self.character_portraits = self.grand.character_portraits
        self.culture_coas = self.grand.sprite_data.culture_coas
        self.image = Surface((0, 0))
        self.image_width = self.image.get_width()
        self.image.fill((255, 255, 255))
        self.base_image = self.image.copy()
        self.culture_coa_rects = {}
        self.culture_value = {}
        self.rect = self.image.get_rect(topleft=self.grand.player_top_bar_ui.rect.bottomleft)

    def culture_change(self):
        culture_value = {}
        player_faction_state = self.grand.current_campaign_state["faction"][self.grand.player_faction]
        faction_culture_state = player_faction_state["culture"]

        for index, culture in enumerate(faction_culture_state):
            culture_state = faction_culture_state[culture]
            culture_value[culture] = {"integration": str(int(culture_state["integration"] * 100)) + "%",
                                      "influence": str(int(culture_state["influence"] * 100)) + "%",
                                      "weight": " (" + str(culture_state["weight"]) + "/" +
                                                str(player_faction_state["total_culture_weight"]) + ")"}

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
            self.culture_value = culture_value

            for index, culture in enumerate(faction_culture_state):
                culture_image = self.culture_coas[culture]["tiny"]
                culture_rect = culture_image.get_rect(topleft=(250 * self.screen_scale_width * index,
                                                               25 * self.screen_scale_height))
                self.image.blit(culture_image, culture_rect)

                integration_value = self.culture_value[culture]["integration"]
                if integration_value not in self.value_text_font_cache:
                    text_surface = text_render_with_bg(integration_value, self.font, Color("black"))
                    self.value_text_font_cache[integration_value] = text_surface
                else:
                    text_surface = self.value_text_font_cache[integration_value]
                self.image.blit(text_surface, text_surface.get_rect(midtop=culture_rect.topright))

                influence_value = self.culture_value[culture]["influence"]
                if influence_value not in self.value_text_font_cache:
                    text_surface = text_render_with_bg(influence_value, self.font, Color("black"))
                    self.value_text_font_cache[influence_value] = text_surface
                else:
                    text_surface = self.value_text_font_cache[influence_value]
                self.image.blit(text_surface, text_surface.get_rect(midbottom=culture_rect.bottomright))
                self.culture_coa_rects[culture] = culture_rect
            self.rect = self.image.get_rect(topleft=self.grand.player_top_bar_ui.rect.bottomleft)

    def update(self, dt):
        UIOuterGrand.update(self, dt)

        if self.mouse_over:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))
            for culture, rect in self.culture_coa_rects.items():
                if rect.collidepoint(inside_mouse_pos):
                    culture_state = self.grand.current_campaign_state["faction"][self.grand.player_faction]["culture"][
                        culture]
                    text = (
                        self.grab_text(("ui", "info_header_culture")) + self.grab_text(("culture", culture, "Name")),
                        self.grab_text(("ui", "info_header_policy")) + self.grab_text(
                            ("ui", "culture_" + culture_state["policy"])),
                        self.grab_text(("ui", "info_header_integration")) + self.culture_value[culture][
                            "integration"],
                        self.grab_text(("ui", "info_header_influence")) + self.culture_value[culture]["influence"] +
                        self.culture_value[culture]["weight"])
                    self.text_popup.popup(self.cursor.rect.bottomright, text,
                                          width_text_wrapper=self.max_description_box_width)
                    self.outer_ui_updater.add(self.text_popup)
                    break


class PlayerArmyListSortOption(UIOuterGrand):
    def __init__(self):
        self._layer = 5
        UIOuterGrand.__init__(self)
        self.image = Surface((950 * self.screen_scale_width, 100 * self.screen_scale_height))
        self.rect = self.image.get_rect(topright=self.grand.mini_cosmic_ui.rect.bottomright)
        button_width = self.grand_ui_icons["sort_number"].get_width()
        self.option_rects = {"commander": self.grand_ui_icons["sort_supply"].get_rect(topleft=(0, 0)),
                             "supply": self.grand_ui_icons["sort_number"].get_rect(topleft=(button_width, 0)),
                             "number": self.grand_ui_icons["sort_commander"].get_rect(topleft=(button_width * 2, 0)),
                             "region": self.grand_ui_icons["sort_region"].get_rect(topleft=(button_width * 3, 0))}
        self.option = ("region", "descend")
        for option, rect in self.option_rects.items():
            self.image.blit(self.grand_ui_icons["sort_" + option], rect)

        self.image.blit(self.grand_ui_icons["sort_" + self.option[0] + "_" + self.option[1]],
                        self.option_rects[self.option[0]])

    def update(self, dt):
        UIOuterGrand.update(self, dt)

        if self.mouse_over:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))
            for option, rect in self.option_rects.items():
                if rect.collidepoint(inside_mouse_pos):
                    if self.event_press:
                        if option == self.option[0]:  # change descend/ascend
                            if self.option[1] == "ascend":
                                self.option = (option, "descend")
                            else:
                                self.option = (option, "ascend")
                        else:
                            self.option = (option, "descend")
                        self.grand.sort_player_army_list()
                    else:
                        self.text_popup.popup(("topright", self.rect.topleft),
                                              self.grab_text(("ui", "info_text_sort_" + option)))
                        self.outer_ui_updater.add(self.text_popup)

                    # re-blit all buttons to reset
                    for option, rect in self.option_rects.items():
                        self.image.blit(self.grand_ui_icons["sort_" + option], rect)

                    self.image.blit(self.grand_ui_icons["sort_" + self.option[0] + "_" + self.option[1]],
                                    self.option_rects[self.option[0]])
                    break


class PlayerArmyList(UIOuterGrand):
    def __init__(self):
        self._layer = 5
        UIOuterGrand.__init__(self)
        self.font = self.game.medium_generic_ui_font
        self.value_text_font_cache = {}
        self.scroll = None  # got added later during scroll object __init__
        self.character_portraits = self.grand.character_portraits
        self.image = Surface((950 * self.screen_scale_width, 1050 * self.screen_scale_height), SRCALPHA)
        self.image.fill((80, 200, 100, 100))
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(topright=self.grand.player_army_list_sort_option_ui.rect.bottomright)
        self.empty_card_image = Surface((950 * self.screen_scale_width, 150 * self.screen_scale_height), SRCALPHA)
        self.empty_card_image.fill((200, 130, 130, 150))

        self.empty_selected_base_image = Surface((950 * self.screen_scale_width, 150 * self.screen_scale_height))
        self.empty_selected_base_image.fill((200, 100, 100))

        self.empty_card_image.blit(self.grand_ui_icons["supply"], (210 * self.screen_scale_width,
                                                                   10 * self.screen_scale_height))

        self.empty_card_image.blit(self.grand_ui_icons["number"], (210 * self.screen_scale_width,
                                                                   80 * self.screen_scale_height))

        self.card_icon_rects = {"resupply": self.grand_ui_images["army_resupply_disable"].get_rect(topleft=(
                                    10 * self.screen_scale_width, 10 * self.screen_scale_height)),
                                "assemble": self.grand_ui_images["army_resupply_disable"].get_rect(bottomleft=(
                                    10 * self.screen_scale_width,
                                    self.empty_card_image.get_height() - 10 * self.screen_scale_height))}
        self.current_row = 0
        self.total_row = 0
        self.max_row_show = 1  # trick the scroller to use additional row instead of total
        self.scroll_total_row = self.total_row + 1

        self.army_card_list = {}
        self.army_rects = [self.empty_card_image.get_rect(
            topleft=(0, self.empty_card_image.get_height() * index)) for index in range(8)]

    def add_assemble_resupply_to_card(self, army, which):
        rect = self.card_icon_rects[which]
        if which == "assemble":
            check = army.enable_assemble
        else:
            check = army.enable_resupply

        if check:
            check = "_enable"
        else:
            check = "_disable"

        image = self.grand_ui_images["army_" + which + check]
        self.army_card_list[army][0].blit(image, rect)
        self.army_card_list[army][1].blit(image, rect)

    def draw_army_card(self, army):
        card_image = self.empty_card_image.copy()

        commander_image = self.character_portraits[army.commander_id]["tiny"]["right"]
        commander_image_rect = commander_image.get_rect(topleft=(self.card_icon_rects["assemble"].topright[0],
                                                                 -10 * self.screen_scale_height))
        card_image.blit(commander_image, commander_image_rect)

        supply_text_colour = (255, 255, 255)
        if army.supply / army.max_supply < 0.2:
            supply_text_colour = (150, 20, 20)
        supply_text = (str(int(army.supply / army.max_supply * 100)) + "% (" +
                       str(int(army.supply / army.total_supply_usage * 100)) + "%)")
        if supply_text not in self.value_text_font_cache:
            text_surface = text_render_with_bg(supply_text,
                                               self.font, (0, 0, 0), supply_text_colour)
            self.value_text_font_cache[supply_text] = text_surface
        else:
            text_surface = self.value_text_font_cache[supply_text]
        card_image.blit(text_surface, text_surface.get_rect(topleft=((305 * self.screen_scale_width),
                                                                     10 * self.screen_scale_height)))

        total_number_text = (add_comma_number(army.total_number) + " (" +
                             str(int(army.assemble_percent[1] / sum(army.assemble_percent) * 100)) + "%)")
        if total_number_text not in self.value_text_font_cache:
            text_surface = text_render_with_bg(total_number_text,
                                               self.font, (0, 0, 0), (255, 255, 255))
            self.value_text_font_cache[total_number_text] = text_surface
        else:
            text_surface = self.value_text_font_cache[total_number_text]
        card_image.blit(text_surface, text_surface.get_rect(topleft=((305 * self.screen_scale_width),
                                                                     80 * self.screen_scale_height)))

        if army.current_region not in self.value_text_font_cache:
            text_surface = text_render_with_bg(self.grab_text(("region", army.current_region, "Name")),
                                               self.font, (0, 0, 0), supply_text_colour)
            self.value_text_font_cache[army.current_region] = text_surface
        else:
            text_surface = self.value_text_font_cache[army.current_region]
        card_image.blit(text_surface, text_surface.get_rect(topright=(card_image.get_width() -
                                                                      (50 * self.screen_scale_width),
                                                                      10 * self.screen_scale_height)))

        if army.game_id in self.grand.current_campaign_state["battle"]["armies"]:
            activity = self.grab_text(("ui", "info_text_combat"))
        elif "travel" in army.activity:
            activity = ">> " + self.grab_text(("region", army.activity["destination"], "Name"))
        elif "assemble" in army.activity:
            activity = self.grab_text(("ui", "info_text_assemble"))
        else:
            activity = self.grab_text(("ui", "info_text_idle"))
        text_surface = text_render_with_bg(activity,
                                           self.font, (0, 0, 0), (255, 255, 255))
        card_image.blit(text_surface, text_surface.get_rect(topright=(card_image.get_width() -
                                                                      (50 * self.screen_scale_width),
                                                                      80 * self.screen_scale_height)))

        selected_card_image = self.empty_selected_base_image.copy()
        selected_card_image.blit(card_image, (0, 0))
        draw.rect(selected_card_image, (0, 0, 0),
                  (0, 0, selected_card_image.get_width(), selected_card_image.get_height()),
                  width=int(8 * self.screen_scale_width))

        return card_image, selected_card_image

    def reset_card(self, army):
        """Reset only specific card based on input index"""
        self.army_card_list[army] = self.draw_army_card(army)
        self.add_assemble_resupply_to_card(army, "assemble")
        self.add_assemble_resupply_to_card(army, "resupply")
        if self.grand.current_campaign_state["faction"][self.grand.player_faction]["army"].index(
                army) >= self.current_row:
            # redraw list if card is being shown in ui
            self.draw_list()

    def reset(self):
        self.current_row = 0
        self.total_row = 0
        self.max_row_show = 1  # trick the scroller to use additional row instead of total
        self.scroll_total_row = self.total_row + 1
        self.army_card_list = {}

    def reset_list(self):
        """Reset entire card list, draw card for each army"""
        current_army_list = self.grand.current_campaign_state["faction"][self.grand.player_faction]["army"]
        self.army_card_list = {}
        self.total_row = ceil(len(current_army_list) / (len(self.army_rects) - 1))
        if self.total_row == 1:
            self.total_row = 0
        self.scroll_total_row = self.total_row + 1
        for army in current_army_list:
            self.army_card_list[army] = self.draw_army_card(army)
            self.add_assemble_resupply_to_card(army, "assemble")
            self.add_assemble_resupply_to_card(army, "resupply")
        self.draw_list()

    def draw_list(self):
        self.image = self.base_image.copy()
        show_index = 0
        len_army_rects_check = len(self.army_rects) - 1
        for index, army in enumerate(self.grand.current_campaign_state["faction"][self.grand.player_faction]["army"]):
            if index >= self.current_row:
                if army not in self.grand.player_selected_army:
                    self.image.blit(self.army_card_list[army][0], self.army_rects[show_index])
                else:
                    self.image.blit(self.army_card_list[army][1], self.army_rects[show_index])
                show_index += 1
            if show_index == len_army_rects_check:
                break

    def update(self, dt):
        UIOuterGrand.update(self, dt)
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
                    if rect.collidepoint(inside_mouse_pos) and self.current_row + index < len(self.army_card_list):
                        army = self.grand.current_campaign_state["faction"][self.grand.player_faction][
                            "army"][self.current_row + index]
                        for which, icon_rect in self.card_icon_rects.items():
                            inside_card_mouse_pos = Vector2(
                                (inside_mouse_pos[0] - rect.topleft[0]),
                                (inside_mouse_pos[1] - rect.topleft[1]))
                            if icon_rect.collidepoint(inside_card_mouse_pos):  # mouse at icon rather than card itself
                                if self.event_press:  # change enable/disable
                                    if which == "assemble":
                                        if army.enable_assemble:
                                            army.enable_assemble = False
                                        else:
                                            army.enable_assemble = True
                                    else:
                                        if army.enable_resupply:
                                            army.enable_resupply = False
                                        else:
                                            army.enable_resupply = True
                                    self.add_assemble_resupply_to_card(army, which)
                                    self.draw_list()

                                else:
                                    if which == "assemble":
                                        value = army.enable_assemble
                                    else:
                                        value = army.enable_resupply
                                    text = (self.grab_text(("ui", "info_header_" + which)) +
                                            self.grab_text(("ui", "info_text_" + str(value))))
                                    self.text_popup.popup(self.cursor.rect, text)
                                    self.outer_ui_updater.add(self.text_popup)
                                return

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
                        # elif self.event_alt_press:
                        #     # open army management ui
                        #     self.grand.player_grand_preset_army_setup.popup("", army)
                        #     self.grand.player_army_info_ui.add_info(army.to_preset_dict)
                        #     self.outer_ui_updater.add(self.grand.player_grand_preset_army_setup,
                        #                               self.grand.player_army_info_ui)
                        elif self.event_middle_mouse_press:
                            self.grand.camera_topleft_pos = Vector2(
                                (army.base_pos[
                                     0] * self.grand.map_shown_to_base_scale_width) - self.half_screen_width,
                                (army.base_pos[
                                     1] * self.grand.map_shown_to_base_scale_height) - self.half_screen_height)
                            self.grand.fix_camera()
                        else:
                            text = (self.grab_text(("ui", "info_header_commander")) + self.grab_text(
                                ("character", army.commander_id, "Name")),)
                            self.text_popup.popup(self.cursor.rect, text,
                                                  width_text_wrapper=self.max_description_box_width)
                            self.outer_ui_updater.add(self.text_popup)
                        break


class PlayerFactionTechBar(UIOuterGrand):
    def __init__(self):
        self._layer = 5
        UIOuterGrand.__init__(self)
        self.image = Surface((600 * self.screen_scale_width, 80 * self.screen_scale_height), SRCALPHA)
        self.font = self.game.generic_ui_font

    def update(self, dt):
        pass


class ArmyInfo(UIOuterGrand):
    def __init__(self, pos):
        """UI for showing stat detail of selected army"""
        self._layer = 7
        UIOuterGrand.__init__(self, player_cursor_interact=False)
        self.font = self.game.large_generic_ui_font
        self.image = Surface((700 * self.screen_scale_width, self.screen_height * 0.5))
        self.image.fill((200, 50, 50))
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(topright=pos)

    def add_info(self, army_dict):
        header_indent = 20 * self.screen_scale_width
        value_indent = 40 * self.screen_scale_width
        self.image = self.base_image.copy()

        text_surface = self.font.render(
            self.grab_text(("ui", "info_header_cost")), True, (0, 0, 0))
        self.image.blit(text_surface, text_surface.get_rect(topleft=(header_indent, 0)))

        text_surface = self.font.render(add_comma_number(int(army_dict["cost"])), True, (0, 0, 0))
        self.image.blit(text_surface, text_surface.get_rect(topleft=(value_indent, 60 * self.screen_scale_height)))

        text_surface = self.font.render(
            self.grab_text(("ui", "info_header_upkeep")), True, (0, 0, 0))
        self.image.blit(text_surface, text_surface.get_rect(topleft=(header_indent, 120 * self.screen_scale_height)))

        text_surface = self.font.render(add_comma_number(int(army_dict["upkeep"])), True, (0, 0, 0))
        self.image.blit(text_surface, text_surface.get_rect(topleft=(value_indent, 180 * self.screen_scale_height)))

        text_surface = self.font.render(
            self.grab_text(("ui", "info_header_supply_capacity")), True, (0, 0, 0))
        self.image.blit(text_surface, text_surface.get_rect(topleft=(header_indent, 240 * self.screen_scale_height)))

        text_surface = self.font.render(add_comma_number(int(army_dict["supply"])) + " (" +
                                        add_comma_number(
                                            int(army_dict["supply"] / army_dict["total_supply_usage"] * 100)) + "%)",
                                        True, (0, 0, 0))
        self.image.blit(text_surface, text_surface.get_rect(topleft=(value_indent, 300 * self.screen_scale_height)))

        text_surface = self.font.render(self.grab_text(("ui", "info_header_max_supply_capacity")), True, (0, 0, 0))
        self.image.blit(text_surface, text_surface.get_rect(topleft=(header_indent, 360 * self.screen_scale_height)))

        text_surface = self.font.render(add_comma_number(army_dict["max_supply"]) + " (" +
                                        add_comma_number(int(army_dict["max_supply"] /
                                                             army_dict["total_supply_usage"] * 100)) + "%)", True,
                                        (0, 0, 0))
        self.image.blit(text_surface, text_surface.get_rect(topleft=(value_indent, 420 * self.screen_scale_height)))

        text_surface = self.font.render(self.grab_text(("ui", "info_header_leadership")), True, (0, 0, 0))
        self.image.blit(text_surface, text_surface.get_rect(topleft=(header_indent, 480 * self.screen_scale_height)))

        text_surface = self.font.render(str(army_dict["leadership"]), True, (0, 0, 0))
        self.image.blit(text_surface, text_surface.get_rect(topleft=(value_indent, 540 * self.screen_scale_height)))

        text_surface = self.font.render(self.grab_text(("ui", "info_header_total_number")), True, (0, 0, 0))
        self.image.blit(text_surface, text_surface.get_rect(topleft=(header_indent, 600 * self.screen_scale_height)))

        text_surface = self.font.render(add_comma_number(army_dict["total_number"]), True, (0, 0, 0))
        self.image.blit(text_surface, text_surface.get_rect(topleft=(value_indent, 660 * self.screen_scale_height)))

        if army_dict["strategy"]:
            text_surface = self.font.render(
                self.grab_text(("ui", "info_header_strategy")), True, (0, 0, 0))
            self.image.blit(text_surface,
                            text_surface.get_rect(topleft=(header_indent, 720 * self.screen_scale_height)))

            for index, strategy in enumerate(army_dict["strategy"]):
                text_surface = self.font.render(
                    ">" + self.grab_text(("strategy", strategy, "Name")), True, (0, 0, 0))
                self.image.blit(text_surface, text_surface.get_rect(
                    topleft=(value_indent, (780 * self.screen_scale_height) + (index * 80 * self.screen_scale_height))))


class ArmyManagement(UIOuterGrand):
    def __init__(self):
        self._layer = 5
        UIOuterGrand.__init__(self)
        self.font = self.game.generic_ui_font
        self.header_font = self.game.large_generic_ui_font
        self.image = Surface((2200 * self.screen_scale_width, 432 * self.screen_scale_height))
        self.image.fill((200, 50, 50))
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(bottomleft=(0, self.screen_height))

    def update(self, dt):
        UIOuterGrand.update(self, dt)
        if self.mouse_over:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))


class RegionManagement(UIOuterGrand):
    def __init__(self):
        self._layer = 5
        UIOuterGrand.__init__(self)
        self.culture_coas = self.grand.sprite_data.culture_coas
        self.building_list = self.grand.stat_data.building_list
        self.font = self.game.medium_generic_ui_font
        self.header_font = self.game.large_generic_ui_font
        self.player_selected_region = None
        self.selected_building_index = None
        self.appear_repair_button = False
        self.appear_raze_button = False
        self.appear_pillage_button = False
        self.image = Surface((1500 * self.screen_scale_width, 1000 * self.screen_scale_height))
        self.image.fill((150, 150, 150))
        default_build_image_slot = self.building_portraits["default"]["building_ui"]
        self.building_slot_rects = ([default_build_image_slot.get_rect(center=(1000 * self.screen_scale_width, 500 * self.screen_scale_height))] +
                                    [default_build_image_slot.get_rect(center=(pos[0] * self.screen_scale_width,
                                                                               pos[1] * self.screen_scale_height))
                                     for pos in ((700, 200), (1000, 200), (1300, 200),
                                                 (700, 500), (1300, 500),
                                                 (700, 800), (1000, 800), (1300, 800))])

        self.resource_text_pos = {"gold_income": (150 * self.screen_scale_width, 130 * self.screen_scale_height),
                                  "supply_income": (150 * self.screen_scale_width, 230 * self.screen_scale_height),
                                  "happiness": (150 * self.screen_scale_width, 330 * self.screen_scale_height)}
        for key, pos in self.resource_text_pos.items():
            icon = self.grand_ui_images[key.replace("_income", "")]
            self.image.blit(icon, icon.get_rect(center=(50 * self.screen_scale_width, pos[1])))

        region_influence_surface = text_render_with_bg(self.grab_text(("ui", "info_header_influence_region")),
                                                       self.header_font)
        self.image.blit(region_influence_surface, region_influence_surface.get_rect(center=(
            250 * self.screen_scale_width, 400 * self.screen_scale_height)))

        culture_coa = self.culture_coas["default"]["tiny"]
        self.culture_coa_rects = [culture_coa.get_rect(topleft=(
            (30 + (50 * row)) * self.screen_scale_width, (450 + (50 * col)) * self.screen_scale_height)) for
            col in range(3) for row in range(3)]

        self.building_button_rects = {}

        self.rect = self.image.get_rect(center=(self.screen_width * 0.25, self.screen_height / 2))

        self.repair_button = self.grand_ui_images["building_repair"]
        self.raze_button_rect = self.grand_ui_images["building_raze"]

        self.repair_button_rect = self.repair_button.get_rect()

        self.base_image = self.image.copy()

    def add_building_icon(self, index, building):
        if building[0] in self.building_portraits:
            building_icon = self.building_portraits[building[0]]["building_ui"]
        else:
            building_icon = self.building_portraits["default"]["building_ui"]

        self.image.blit(building_icon, self.building_slot_rects[index])
        if building[1] is not True:
            if not building[1]:  # damaged building
                self.image.blit(self.building_portraits["damaged"],
                                self.building_slot_rects[index])
            else:  # building on progress with something
                self.image.blit(self.building_portraits["progress"],
                                self.building_slot_rects[index])
                if building[1] == "raze":
                    self.image.blit(self.building_portraits["unavailable_raze"],
                                    self.building_slot_rects[index])
                elif building[1] == "pillage":
                    self.image.blit(self.building_portraits["unavailable_pillage"],
                                    self.building_slot_rects[index])
                else:  # repair
                    self.image.blit(self.building_portraits["unavailable_repair"],
                                    self.building_slot_rects[index])

                turn_left = self.font.render(building[2], True, (255, 255, 255))
                self.image.blit(turn_left, turn_left.get_rect(midtop=self.building_slot_rects[index].midbottom))

    def change_selected_region(self, region):
        self.building_button_rects = {}
        self.selected_building_index = None
        self.appear_repair_button = False
        self.appear_raze_button = False
        self.appear_pillage_button = False
        self.outer_ui_updater.remove(self.grand.building_management_ui)
        self.player_selected_region = region
        if region:
            self.image = self.base_image.copy()
            for index, building in enumerate(self.grand.current_campaign_state["region"]["building"][region]):
                self.add_building_icon(index, building)

            region_name_surface = text_render_with_bg(self.grab_text(("region", region, "Name")), self.header_font)
            self.image.blit(region_name_surface, region_name_surface.get_rect(midtop=(
                250 * self.screen_scale_width, 10 * self.screen_scale_height)))
            self.update_leftbar()
            self.outer_ui_updater.add(self)
        else:
            self.outer_ui_updater.remove(self)

    def update_leftbar(self):
        region = self.player_selected_region
        campaign_region_state = self.grand.current_campaign_state["region"]
        resource = campaign_region_state["income"][region]
        culture = campaign_region_state["culture"][region]
        for key, pos in self.resource_text_pos.items():
            text_surface = text_render_with_bg(add_plus_to_number(int(resource[key])), self.font)
            self.image.blit(text_surface, text_surface.get_rect(midleft=pos))

        for index, culture_id in enumerate(culture):
            self.image.blit(self.culture_coas[culture_id]["tiny"], self.culture_coa_rects[index])
            text_surface = text_render_with_bg(add_plus_to_number(int(culture[culture_id])), self.font)
            self.image.blit(text_surface, text_surface.get_rect(bottomright=self.culture_coa_rects[index].bottomright))

    def change_selected_building(self, building_index):
        self.building_button_rects = {}
        self.appear_repair_button = False
        self.appear_raze_button = False
        self.appear_pillage_button = False
        if self.selected_building_index is not None:
            # reset previous selected building icon
            prev_building_state = self.grand.current_campaign_state["region"]["building"][self.player_selected_region][self.selected_building_index]
            building = prev_building_state[0]
            prev_selected_building_icon = self.building_portraits[building]["building_ui"]
            self.image.blit(prev_selected_building_icon, self.building_slot_rects[self.selected_building_index])

        building_state = self.grand.current_campaign_state["region"]["building"][self.player_selected_region][
            building_index]
        if building_state[1] is True and not building_state[2]:
            building = building_state[0]
            building_stat = self.building_list[building]
            self.grand.building_management_ui.player_selected_region = self.player_selected_region
            self.grand.building_management_ui.change_selected_building(building_index)
            if building_stat["Cost"]:
                # building has cost, add pillage button
                self.building_button_rects["pillage"] = self.grand_ui_images["building_repair"].get_rect(
                    midbottom=self.building_slot_rects[building_index].midtop)
                self.image.blit(self.grand_ui_images["building_pillage"], self.building_button_rects["pillage"])
                self.appear_pillage_button = True

            if building_stat["Precede"]:
                # add raze button if building can be downgrade
                self.building_button_rects["raze"] = self.grand_ui_images["building_repair"].get_rect(
                    midbottom=self.building_slot_rects[building_index].topright)
                self.image.blit(self.grand_ui_images["building_raze"], self.building_button_rects["raze"])
                self.appear_raze_button = True
        else:
            if not building_state[1]:  # add repair button
                self.building_button_rects["repair"] = self.grand_ui_images["building_repair"].get_rect(
                    midbottom=self.building_slot_rects[building_index].topleft)
                self.image.blit(self.grand_ui_images["building_repair"], self.building_button_rects["repair"])
                self.appear_repair_button = True

        selected_icon = self.building_portraits["selected"]["building_ui"]
        self.image.blit(selected_icon, self.building_slot_rects[building_index])

        self.selected_building_index = building_index

    def update(self, dt):
        UIOuterGrand.update(self, dt)
        if self.mouse_over:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))
            if self.appear_repair_button and self.building_button_rects["repair"].collidepoint(inside_mouse_pos):
                self.grand.start_building_construction_or_repair(self.grand.player_faction, self.player_selected_region,
                                                                 self.selected_building_index,
                                                                 self.grand.current_campaign_state["region"]["building"][self.player_selected_region][self.selected_building_index][0])
                return
            elif self.appear_raze_button and self.building_button_rects["raze"].collidepoint(inside_mouse_pos):

                return
            elif self.appear_pillage_button and self.building_button_rects["pillage"].collidepoint(inside_mouse_pos):
                return

            region_buildings = self.grand.current_campaign_state["region"]["building"][self.player_selected_region]
            for building_index, rect in enumerate(self.building_slot_rects):
                if rect.collidepoint(inside_mouse_pos) and building_index < len(region_buildings):
                    if self.event_press:
                        self.change_selected_building(building_index)
                    else:
                        self.text_popup.popup(self.cursor.rect.bottomright,
                                              self.grab_text(("building",
                                                              region_buildings[building_index][0],
                                                              "Name")),
                                              width_text_wrapper=self.max_description_box_width)
                        self.outer_ui_updater.add(self.text_popup)
                    break


class BuildingManagement(UIOuterGrand):
    building_type_bar_colouring = {"barrack": (255, 100, 100), "faith": (0, 100, 255), "food": (0, 127, 40),
                                   "fun": (255, 100, 255), "guard": (0, 152, 122), "money": (180, 169, 0),
                                   "tech": (0, 255, 255), "unique": (200, 0, 255), "settlement": (255, 127, 40)}

    def __init__(self):
        self._layer = 5
        UIOuterGrand.__init__(self)
        self.font = self.game.generic_ui_font
        self.header_font = self.game.large_generic_ui_font
        self.culture_coas = self.grand.sprite_data.culture_coas
        self.building_portraits = self.grand.building_portraits
        self.building_upgrade_list = self.grand.stat_data.building_upgrade_list
        self.building_list = self.grand.stat_data.building_list
        self.player_selected_region = None
        self.available_building_upgrade = {}
        self.unavailable_building_icon = self.building_portraits["unavailable"]["building_ui"]
        self.image = Surface((0, 0))
        self.building_slot_rects = []
        self.rect = self.image.get_rect(center=(self.screen_width / 2, self.screen_height / 2))

    def change_selected_building(self, building_index):
        self.building_slot_rects = []
        building_list = self.building_list
        region_buildings = self.grand.current_campaign_state["region"]["building"][self.player_selected_region]
        region_active_building = [item[0] for item in region_buildings if item[1] and not item[2]]
        faction_culture = self.grand.current_campaign_state["faction"][self.grand.player_faction]["culture"]
        selected_building_state = region_buildings[building_index]

        # show building management for active building
        exist_building_upgrade = self.building_upgrade_list[selected_building_state[0]]

        available_building_upgrade = {}
        player_faction_gold = self.grand.current_campaign_state["faction"][self.grand.player_faction]["gold"]
        for building, requirement in exist_building_upgrade.items():
            this_building_stat = building_list[building]
            building_type = this_building_stat["Type"]
            if this_building_stat["Culture"] in faction_culture and faction_culture[this_building_stat["Culture"]]["policy"] != "reject":
                no_build = False
                for require_building in requirement:
                    if require_building not in region_active_building:  # required building condition not met
                        no_build = True
                        break
                if not no_build:
                    if building_type not in available_building_upgrade:
                        available_building_upgrade[building_type] = {}
                    if this_building_stat["Cost"] > player_faction_gold:
                        available_building_upgrade[building_type][building] = False
                    else:
                        available_building_upgrade[building_type][building] = True

        if available_building_upgrade:
            # show building management ui only for active building
            self.outer_ui_updater.add(self)

            self.image = Surface((1200 * self.screen_scale_width, sum([
                ceil(len(available_building_list) / 5) for available_building_list in
                available_building_upgrade.values()]) * 240 * self.screen_scale_height))
            self.rect = self.image.get_rect(midleft=self.grand.region_management_ui.rect.midright)
            image_width = self.image.get_width()
            prev_bar_rect = None
            for building_type, available_building_list in available_building_upgrade.items():
                building_bar_image = Surface((image_width, ceil(len(available_building_list) / 5) * 200 * self.screen_scale_height))
                building_bar_image.fill(self.building_type_bar_colouring[building_type])
                slot_rects = {}
                for building_index, building in enumerate(available_building_list):
                    if building in self.building_portraits:
                        building_icon = self.building_portraits[building]["building_ui"]
                    else:
                        building_icon = self.building_portraits["default"]["building_ui"]
                    col = floor(building_index / 5)
                    row = building_index - (5 * col)
                    rect = building_icon.get_rect(topleft=((20 + (150 * row)) * self.screen_scale_width,
                                                           (20 + (150 * col)) * self.screen_scale_height))
                    slot_rects[building] = rect
                    building_bar_image.blit(building_icon, rect)
                    if not available_building_upgrade[building_type][building]:
                        building_bar_image.blit(self.unavailable_building_icon, rect)
                    if building_list[building]["Culture"] in self.culture_coas:
                        culture_coa = self.culture_coas[building_list[building]["Culture"]]["mini"]
                    else:
                        culture_coa = self.culture_coas["default"]["mini"]
                    building_bar_image.blit(culture_coa, culture_coa.get_rect(topleft=rect.topleft))
                if not prev_bar_rect:
                    new_bar_rect = building_bar_image.get_rect(topleft=(0, 0))
                else:
                    new_bar_rect = building_bar_image.get_rect(topleft=(0, prev_bar_rect.bottomleft[1]))
                self.image.blit(building_bar_image, new_bar_rect)
                self.building_slot_rects.append((new_bar_rect, slot_rects))
                prev_bar_rect = new_bar_rect

            self.available_building_upgrade = available_building_upgrade
            return
        self.outer_ui_updater.remove(self)

    def update(self, dt):
        UIOuterGrand.update(self, dt)
        if self.mouse_over:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))

            for bar_rect, building_slot_list in self.building_slot_rects:
                if bar_rect.collidepoint(inside_mouse_pos):
                    bar_inside_mouse_pos = Vector2((inside_mouse_pos[0] - bar_rect.topleft[0]),
                                                   (inside_mouse_pos[1] - bar_rect.topleft[1]))
                    for building, rect in building_slot_list.items():
                        if rect.collidepoint(bar_inside_mouse_pos):
                            if self.event_press:
                                if self.building_list[building]["cost"] > self.grand.current_campaign_state["faction"][self.grand.player_faction]["gold"]:
                                    self.grand.start_building_construction_or_repair(self.grand.player_faction, self.player_selected_region,
                                                                                     self.grand.region_management_ui.selected_building_index,
                                                                                     building)
                            else:
                                self.text_popup.popup(self.cursor.rect.bottomright,
                                                      self.grab_text(("building",
                                                                      building,
                                                                      "Name")),
                                                      width_text_wrapper=self.max_description_box_width)
                                self.outer_ui_updater.add(self.text_popup)
                            break
                    break


class EventNotification(BattleEventNotification, UIOuterGrand):
    event_icons = {}

    def __init__(self):
        self._layer = 5
        BattleEventNotification.__init__(self, (0, 0))
        UIOuterGrand.__init__(self)
        self.all_event_rects = [Rect(0, index * 100 * self.screen_scale_height,
                                     800 * self.screen_scale_width, self.event_item_height) for index in range(10)]
        self.active_event_rects = []
        self.rect = self.image.get_rect(bottomleft=(0, self.grand.region_management_ui.rect.topleft[1]))

    def update_image(self):
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

    def event_list_update(self):
        pass

    def update(self, dt):
        UIOuterGrand.update(self, dt)
        if self.mouse_over:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))
            for index, rect in enumerate(self.active_event_rects):
                if rect.collidepoint(inside_mouse_pos):
                    if self.event_press:  # open event popup
                        self.grand.event_important_popup.event_popup(
                            self.grand.current_campaign_state["eventlog"][index])
                        self.grand.current_campaign_state["eventlog"].pop(index)
                        self.event_list_update()
                    elif self.event_middle_mouse_press:  # go to event location
                        event = self.grand.current_campaign_state["eventlog"][index]
                        self.grand.camera_topleft_pos = Vector2(
                            (event[2][0] * self.grand.map_shown_to_base_scale_width) - self.half_screen_width,
                            (event[2][1] * self.grand.map_shown_to_base_scale_height) - self.half_screen_height)
                        self.grand.fix_camera()
                    elif self.event_alt_press:  # remove event
                        self.grand.current_campaign_state["eventlog"].pop(index)
                        self.event_list_update()
                    break


class TechManagement(UIOuterGrand):
    def __init__(self):
        self._layer = 5
        UIOuterGrand.__init__(self)

        self.image = Surface((3044 * self.screen_scale_width, 432 * self.screen_scale_height), SRCALPHA)
        self.rect = self.image.get_rect(center=(self.screen_width / 2, self.screen_height / 2))

    def update(self, dt):
        UIOuterGrand.update(self, dt)
        if self.mouse_over:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))


class CultureManagement(UIOuterGrand):
    def __init__(self):
        self._layer = 5
        UIOuterGrand.__init__(self)

        self.image = Surface((3044 * self.screen_scale_width, 432 * self.screen_scale_height), SRCALPHA)
        # self.
        self.policy_icon_rect_x = {policy: (index + 1) * 200 for index, policy in
                                   enumerate(Culture_Policy_Integration.keys())}
        self.rect = self.image.get_rect(center=(self.screen_width / 2, self.screen_height / 2))

    def update(self, dt):
        UIOuterGrand.update(self, dt)
        if self.mouse_over:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))


class MapSettingOption(UIOuterGrand):
    def __init__(self):
        self._layer = 5
        UIOuterGrand.__init__(self)

        self.image = Surface((150 * self.screen_scale_width, 432 * self.screen_scale_height))
        self.image.fill((150, 50, 80))
        self.rect = self.image.get_rect(topright=self.grand.mini_map.rect.topleft)

    def update(self, dt):
        UIOuterGrand.update(self, dt)
        if self.mouse_over:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))


class RegionInfoBar(UIOuterGrand):
    def __init__(self):
        self._layer = 4
        UIOuterGrand.__init__(self, player_cursor_interact=False)

        self.image = Surface((800 * self.screen_scale_width, 1000 * self.screen_scale_height))
        self.image.fill((255, 255, 255))
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(center=(self.screen_width / 2, self.screen_height / 2))

    def update(self, dt):
        pass


class EventImportantPopup(UIOuterGrand):
    def __init__(self):
        self._layer = 6
        UIOuterGrand.__init__(self)

        self.image = Surface((800 * self.screen_scale_width, 1000 * self.screen_scale_height))
        self.image.fill((255, 255, 255))
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(center=(self.screen_width / 2, self.screen_height / 2))

    def popup(self, event_data):
        pass

    def update(self, dt):
        UIOuterGrand.update(self, dt)
        if self.mouse_over:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))


class PlayerGrandInteract(UIOuterGrand):
    def __init__(self):
        self._layer = 9999999999999999999999999999999999999998  # always 1 layer less than cursor so it get updated last but before cursor
        UIOuterGrand.__init__(self, player_cursor_interact=False)
        self.base_world_map = self.grand.base_world_map
        self.grand_camera = self.grand.camera
        self.selection_start_pos = Vector2()
        self.current_pos = Vector2()
        self.line_size = int(10 * self.screen_scale_width)
        self.inner_line_size = int(20 * self.screen_scale_width)
        if self.line_size < 1:
            self.line_size = 1
        self.image = None
        self.rect = None

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

            if not self.event_hold and not self.event_press:
                if self.selection_start_pos:  # release hold while band exist
                    player_armies = self.grand.current_campaign_state["faction"][self.grand.player_faction]["army"]
                    army_select_list = list(set([army for index, army in enumerate(player_armies) if
                                                 index in self.rect.collidelistall([army.commander_actor.rect for
                                                                                    army in player_armies])]))
                    if self.rect.width <= 1 and self.rect.height <= 1:  # no band, player click only 1 army
                        army_select_list.sort(key=lambda x: x.commander_actor._layer, reverse=True)  # get only top army
                        army_select_list = army_select_list[:1]
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
                        self.grand.player_selected_army = []

                        region_colour = tuple(self.grand.base_world_map.get_at(
                            (int(self.grand.base_cursor_pos[0]), int(self.grand.base_cursor_pos[1]))))[:3]
                        if region_colour in self.grand.region_by_colour_index:
                            region_id = self.grand.region_by_colour_index[region_colour]
                            if (self.grand.player_faction and region_id in
                                    self.grand.current_campaign_state["faction"][self.grand.player_faction]["region"]):
                                self.grand.region_management_ui.change_selected_region(region_id)
                        else:  # select at water region, remove region management ui
                            self.grand.region_management_ui.change_selected_region(None)

                    self.grand.player_army_list_ui.draw_list()
                    self.reset()

                elif self.event_alt_press:  # right click order selected leader to do something
                    if self.grand.player_selected_army:  # order selected army to move to region at mouse pos
                        region_colour = tuple(self.grand.base_world_map.get_at(
                            (int(self.grand.base_cursor_pos[0]), int(self.grand.base_cursor_pos[1]))))[:3]
                        if region_colour in self.grand.region_by_colour_index:
                            region_id = self.grand.region_by_colour_index[region_colour]
                            if any([army.game_id in self.grand.current_campaign_state["battle"]["armies"] for army in
                                    self.grand.player_selected_army]):
                                # player army in battle, this will cause battle lost and armies retreat from battle,
                                # ask for confirmation first
                                if any([army.can_assemble for army in self.grand.player_selected_army]):
                                    # there is also army assembling, this will cause assemble to be cancelled,
                                    # ask for confirmation with both warning
                                    self.grand.activate_input_popup(("confirm_input", "assemble",
                                                                     (region_id, self.grand.shift_press)),
                                                                    self.grab_text(("ui", "warn_input_assemble")),
                                                                    self.game.confirm_popup_uis)
                                else:
                                    self.grand.activate_input_popup(("confirm_input", "retreat_assemble",
                                                                     (region_id, self.grand.shift_press)),
                                                                    self.grab_text(
                                                                        ("ui", "warn_input_retreat_assemble")),
                                                                    self.game.confirm_popup_uis)
                            elif any([army.can_assemble for army in self.grand.player_selected_army]):
                                # there is army assembling, this will cause assemble to be cancelled,
                                # ask for confirmation first
                                self.grand.activate_input_popup(("confirm_input", "assemble",
                                                                 (region_id, self.grand.shift_press)),
                                                                self.grab_text(("ui", "warn_input_assemble")),
                                                                self.game.confirm_popup_uis)
                            else:  # no problem, issue move command
                                for army in self.grand.player_selected_army:
                                    if self.grand.shift_press:
                                        army.issue_move_command(region_id, direct=True)
                                    else:
                                        army.issue_move_command(region_id)

            else:  # holding left click, manipulate band
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
                        self.rect = Rect(left + self.grand.camera_topleft_pos[0],
                                         top + self.grand.camera_topleft_pos[1], width,
                                         height)  # rect for collision unit selection check
                        draw.rect(self.grand_camera.image, (0, 0, 0), selection_rect, self.inner_line_size)
                        draw.rect(self.grand_camera.image, (255, 255, 255), selection_rect, self.line_size)
                    else:
                        self.rect = Rect(left + self.grand.camera_topleft_pos[0],
                                         top + self.grand.camera_topleft_pos[1], 1,
                                         1)  # rect for collision unit selection check
        else:
            self.reset()
