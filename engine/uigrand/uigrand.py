from math import ceil

from pygame import Vector2, Surface, SRCALPHA, Rect, draw, Color
from pygame.transform import smoothscale

from engine.constants import Culture_Policy_Integration
from engine.uibattle.uibattle import EventNotification as BattleEventNotification
from engine.uimenu.uimenu import UIMenu
from engine.utils.text_making import add_plus_to_number, add_comma_number, text_render_with_bg, minimise_number_text


class UIGrand(UIMenu):
    def __init__(self, player_cursor_interact=True, has_containers=False):
        """
        Parent class for all battle menu user interface
        """
        from engine.grand.grand import Grand
        UIMenu.__init__(self, player_cursor_interact=player_cursor_interact, has_containers=has_containers)
        self.grand = Grand.grand
        self.grand_ui_icons = self.grand.grand_ui_icons
        self.cursor = Grand.cursor  # use battle cursor for battle ui
        self.text_popup = self.grand.text_popup
        self.outer_ui_updater = self.grand.outer_ui_updater
        self.max_description_box_width = int(1000 * self.screen_scale_width)


class YesNo(UIGrand):
    def __init__(self):
        UIGrand.__init__(self)
        self._layer = 5
        self.yes_image = self.grand.grand_ui_images["yes"]
        self.no_image = self.grand.grand_ui_images["no"]

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
        self.image = Surface((1400 * self.screen_scale_width, 80 * self.screen_scale_height), SRCALPHA)
        self.image.fill((80, 200, 255))
        self.image.blit(self.grand_ui_icons["gold"], (50 * self.screen_scale_width,
                                                      20 * self.screen_scale_height))
        self.image.blit(self.grand_ui_icons["supply"], (600 * self.screen_scale_width,
                                                        20 * self.screen_scale_height))
        self.image.blit(self.grand_ui_icons["happiness"], (1150 * self.screen_scale_width,
                                                           20 * self.screen_scale_height))

        self.base_image = self.image.copy()
        self.font = self.game.large_generic_ui_font
        self.text_rect = {"gold": (150 * self.screen_scale_width, 20 * self.screen_scale_height),
                          "supply": (700 * self.screen_scale_width, 20 * self.screen_scale_height),
                          "happiness": (1250 * self.screen_scale_width, 20 * self.screen_scale_height)}
        self.blit_text_rect = {}
        self.player_faction_resource = {}
        self.rect = self.image.get_rect(topleft=(0, 0))

    def update(self, dt):
        resource = self.grand.current_campaign_state["faction"][self.grand.player_faction]
        resource = ((int(resource["gold"]), int(resource["gold_income"])),
                    (int(resource["supply"]), int(resource["supply_income"])),
                    int(resource["happiness"]))
        if self.player_faction_resource != resource:
            self.blit_text_rect = {}
            self.image = self.base_image.copy()
            self.player_faction_resource = resource

            for index, text in enumerate(self.text_rect):
                value = str(resource[index])
                if text != "happiness":
                    value = (add_comma_number(resource[index][0]) + " (" +
                             add_plus_to_number(add_comma_number(resource[index][1])) + ")")
                value = text_render_with_bg(value, self.font)
                blit_text_rect = value.get_rect(topleft=self.text_rect[text])
                self.image.blit(value, blit_text_rect)
                self.blit_text_rect[text] = blit_text_rect

        UIGrand.update(self, dt)

        if self.mouse_over:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))
            for key, rect in self.blit_text_rect.items():
                if rect.collidepoint(inside_mouse_pos):
                    text = [self.grab_text(("ui", "info_text_" + key)), ""]
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
                    self.text_popup.popup(self.cursor.rect.bottomright, text)
                    self.outer_ui_updater.add(self.text_popup)
                    break


class PlayerFactionCultureList(UIGrand):
    def __init__(self):
        self._layer = 5
        UIGrand.__init__(self)
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
            self.rect = self.image.get_rect(topleft=self.grand.player_faction_resource_bar_ui.rect.bottomleft)

    def update(self, dt):
        UIGrand.update(self, dt)

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
                        self.grab_text(("ui", "info_header_influence")) + self.culture_value[culture]["influence"])
                    self.text_popup.popup(self.cursor.rect.bottomright, text,
                                          width_text_wrapper=self.max_description_box_width)
                    self.outer_ui_updater.add(self.text_popup)
                    break


class RegionInfoBanner(UIGrand):
    def __init__(self):
        self._layer = 5
        UIGrand.__init__(self)
        self.font = self.game.medium_generic_ui_font


class DotInfoBanner(UIGrand):
    base_image = Surface((0, 0))

    def __init__(self, base_pos, pos):
        self._layer = 5
        UIGrand.__init__(self, has_containers=True, player_cursor_interact=False)
        self.font = self.game.medium_generic_ui_font
        self.base_pos = base_pos
        self.dots_army_occupation = self.grand.dots_army_occupation
        self.grand_camera_ui_drawer = self.grand.grand_camera_ui_drawer
        self.previous_state_value_list = {}
        self.pos = pos
        self.image = self.base_image
        self.rect = self.image.get_rect(midtop=pos)

    def make_text_image(self, surface_colour, text):
        text_image = text_render_with_bg(text, self.font)
        image_size = (int(text_image.get_width() * 1.2), int(text_image.get_height() * 1.2))
        self.image = Surface(image_size)
        self.image.fill(surface_colour,
                        (image_size[0] * 0.05, image_size[1] * 0.1,
                         image_size[0] * 0.92, image_size[1] * 0.85))
        self.image.blit(text_image, text_image.get_rect(center=(image_size[0] / 2, image_size[1] / 2)))

    def update(self, dt):
        pass


class DotInfoBannerSettlement(DotInfoBanner):
    def __init__(self, base_pos, pos, region):
        DotInfoBanner.__init__(self, base_pos, pos)
        self.region = region
        self.reset(self.grand.current_campaign_state["region"]["control"][region])

    def reset(self, faction_owner):
        if faction_owner == self.grand.player_faction:
            surface_colour = (100, 100, 220)
        elif self.grand.player_faction and faction_owner in self.grand.current_campaign_state["faction"][
            self.grand.player_faction]["hostile"]:
            surface_colour = (220, 100, 100)
        else:
            surface_colour = (180, 180, 180)

        self.make_text_image(surface_colour, self.grab_text(("region", self.region, "name")))
        self.rect = self.image.get_rect(midtop=self.pos)


class DotInfoBannerArmy(DotInfoBanner):
    def __init__(self, base_pos, pos):
        DotInfoBanner.__init__(self, base_pos, pos)

    def reset(self, state_value_list):
        if "battle" in state_value_list:
            text = " VS "
            surface_colour = (100, 100, 220)
        else:
            if state_value_list["player"][0]:
                text = (minimise_number_text(state_value_list["player"][0]) + "/" +
                        minimise_number_text(
                            state_value_list["player"][1] / state_value_list["player"][2] * 100) + "%")
                surface_colour = (100, 100, 220)
            elif state_value_list["enemy"][0]:
                text = (minimise_number_text(state_value_list["enemy"][0]) + "/" +
                        minimise_number_text(
                            state_value_list["enemy"][1] / state_value_list["enemy"][2] * 100) + "%")
                surface_colour = (220, 100, 100)
            else:
                # neutral only shown when no player or enemy army in this dot
                text = (minimise_number_text(state_value_list["neutral"][0]) + "/" +
                        minimise_number_text(
                            state_value_list["neutral"][1] / state_value_list["neutral"][2] * 100) + "%")
                surface_colour = (180, 180, 180)

        self.make_text_image(surface_colour, text)
        self.rect = self.image.get_rect(midtop=self.pos)

    def update(self, dt):
        if self.base_pos in self.grand.current_campaign_state["battle"]["dot"]:  # battle going on
            state_value_list = ([0, 0, 0], [0, 0, 0])
            for army in self.grand.current_campaign_state["battle"]["auto"][self.base_pos][""].values():
                if army.faction == self.grand.player_faction:
                    state_value_list[0][0] += army.total_number
                    state_value_list["player"][1] += army.max_supply
                    state_value_list["player"][2] += army.total_supply_usage
                elif self.grand.player_faction and army.faction in self.grand.current_campaign_state["faction"][
                    self.grand.player_faction]["hostile"]:
                    state_value_list["enemy"][0] += army.total_number
                    state_value_list["enemy"][1] += army.max_supply
                    state_value_list["enemy"][2] += army.total_supply_usage
                else:
                    state_value_list["neutral"][0] += army.total_number
                    state_value_list["neutral"][1] += army.max_supply
                    state_value_list["neutral"][2] += army.total_supply_usage
            if self not in self.grand_camera_ui_drawer:
                self.grand_camera_ui_drawer.add(self)
        elif self.dots_army_occupation[self.base_pos]:
            state_value_list = {"player": [0, 0, 0], "enemy": [0, 0, 0], "neutral": [0, 0, 0]}
            for army in self.dots_army_occupation[self.base_pos].values():
                if army.faction == self.grand.player_faction:
                    state_value_list["player"][0] += army.total_number
                    state_value_list["player"][1] += army.max_supply
                    state_value_list["player"][2] += army.total_supply_usage
                elif self.grand.player_faction and army.faction in self.grand.current_campaign_state["faction"][
                    self.grand.player_faction]["hostile"]:
                    state_value_list["enemy"][0] += army.total_number
                    state_value_list["enemy"][1] += army.max_supply
                    state_value_list["enemy"][2] += army.total_supply_usage
                else:
                    state_value_list["neutral"][0] += army.total_number
                    state_value_list["neutral"][1] += army.max_supply
                    state_value_list["neutral"][2] += army.total_supply_usage
            if state_value_list != self.previous_state_value_list:
                self.previous_state_value_list = state_value_list
                self.reset(state_value_list)
            if self not in self.grand_camera_ui_drawer:
                self.grand_camera_ui_drawer.add(self)
        else:
            if self in self.grand_camera_ui_drawer:
                self.grand_camera_ui_drawer.remove(self)


class PlayerArmyListSortOption(UIGrand):
    def __init__(self):
        self._layer = 5
        UIGrand.__init__(self)
        self.image = Surface((900 * self.screen_scale_width, 100 * self.screen_scale_height))
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
        UIGrand.update(self, dt)

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


class PlayerArmyList(UIGrand):
    def __init__(self):
        self._layer = 5
        UIGrand.__init__(self)
        self.font = self.game.medium_generic_ui_font
        self.value_text_font_cache = {}
        self.scroll = None  # got added later during scroll object __init__
        self.character_portraits = self.grand.character_portraits
        self.image = Surface((900 * self.screen_scale_width, 1050 * self.screen_scale_height), SRCALPHA)
        self.image.fill((80, 200, 100, 100))
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(topright=self.grand.player_army_list_sort_option_ui.rect.bottomright)
        self.empty_card_image = Surface((900 * self.screen_scale_width, 150 * self.screen_scale_height), SRCALPHA)
        self.empty_card_image.fill((200, 130, 130, 150))

        self.empty_selected_base_image = Surface((900 * self.screen_scale_width, 150 * self.screen_scale_height))
        self.empty_selected_base_image.fill((200, 100, 100))

        self.empty_card_image.blit(self.grand_ui_icons["supply"], (145 * self.screen_scale_width,
                                                                   10 * self.screen_scale_height))

        self.empty_card_image.blit(self.grand_ui_icons["number"], (145 * self.screen_scale_width,
                                                                   80 * self.screen_scale_height))

        self.current_row = 0
        self.total_row = 0
        self.max_row_show = 1  # trick the scroller to use additional row instead of total
        self.scroll_total_row = self.total_row + 1

        self.army_card_list = {}
        self.army_rects = [self.empty_card_image.get_rect(
            topleft=(0, self.empty_card_image.get_height() * index)) for index in range(8)]

    def draw_army_card(self, army):
        card_image = self.empty_card_image.copy()
        commander_image = self.character_portraits[army.commander_id]["tiny"]["right"]
        card_image.blit(commander_image, commander_image.get_rect(topleft=(0, 0)))

        # for index, leader in enumerate(army.leader_group):
        #     leader_image = self.character_portraits[leader]["mini"]["left"]
        #     card_image.blit(leader_image, leader_image.get_rect(
        #         topleft=(((100 * index) + 150) * self.screen_scale_width, 0)))

        supply_text_colour = (255, 255, 255)
        if army.supply / army.max_supply < 0.2:
            supply_text_colour = (150, 20, 20)
        supply_text = (str(int(army.supply / army.max_supply * 100)) + "%(" +
                       str(int(army.supply / army.total_supply_usage * 100)) + "%)")
        if supply_text not in self.value_text_font_cache:
            text_surface = text_render_with_bg(supply_text,
                                               self.font, (0, 0, 0), supply_text_colour)
            self.value_text_font_cache[supply_text] = text_surface
        else:
            text_surface = self.value_text_font_cache[supply_text]
        card_image.blit(text_surface, text_surface.get_rect(topleft=((240 * self.screen_scale_width),
                                                                     10 * self.screen_scale_height)))

        total_number_text = add_comma_number(army.total_number)
        if total_number_text not in self.value_text_font_cache:
            text_surface = text_render_with_bg(total_number_text,
                                               self.font, (0, 0, 0), (255, 255, 255))
            self.value_text_font_cache[total_number_text] = text_surface
        else:
            text_surface = self.value_text_font_cache[total_number_text]
        card_image.blit(text_surface, text_surface.get_rect(topleft=((240 * self.screen_scale_width),
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
        elif army.travelling:
            activity = ">> " + self.grab_text(("region", army.travelling["destination"], "Name"))
        elif army.assembling:
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
        UIGrand.update(self, dt)
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
                            army_preset_dict = army.to_preset_dict
                            self.grand.player_grand_preset_army_setup.popup(army_preset_dict)
                            self.grand.player_army_info_ui.add_info(army_preset_dict)
                            self.outer_ui_updater.add(self.grand.player_grand_preset_army_setup,
                                                      self.grand.player_army_info_ui)
                        elif self.event_middle_mouse_press:
                            self.grand.camera_pos = Vector2(
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
        button_images = self.grand.grand_ui_icons
        self.image = Surface((600 * self.screen_scale_width, 100 * self.screen_scale_height), SRCALPHA)
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
        self.rect = self.image.get_rect(topright=(self.grand.mini_cosmic_ui.rect.topleft[0] +
                                                  (self.image.get_width() * 0.1),
                                                  (self.grand.time_setting_ui.rect.bottomleft[1])))

    def update(self, dt):
        UIGrand.update(self, dt)
        if self.mouse_over:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))

            for key, rect in self.button_rects.items():
                if rect.collidepoint(inside_mouse_pos):
                    if self.event_press:
                        self.option_selected = key


class TimeInfoBar(UIGrand):
    def __init__(self):
        self._layer = 4
        UIGrand.__init__(self, player_cursor_interact=False)
        self.font = self.game.large_generic_ui_font
        self.image = Surface((800 * self.screen_scale_width, 80 * self.screen_scale_height), SRCALPHA)
        self.image.fill((150, 150, 255))
        self.base_image = self.image.copy()
        self.turn = 0
        self.phase = 0
        self.rect = self.image.get_rect(topright=(self.grand.mini_cosmic_ui.rect.topleft[0] +
                                                  (self.image.get_width() * 0.05), 0))

    def reset(self):
        self.turn = 0
        self.phase = 0

    def update(self, dt):
        UIGrand.update(self, dt)
        current_campaign_state = self.grand.current_campaign_state
        if self.turn != current_campaign_state["turn"] or self.phase != current_campaign_state["phase"]:
            self.turn = current_campaign_state["turn"]
            self.phase = current_campaign_state["phase"]
            self.image = self.base_image.copy()
            text_surface = text_render_with_bg("Turn: " + str(self.turn) + "." + str(self.phase), self.font)
            self.image.blit(text_surface, (150 * self.screen_scale_width, 20 * self.screen_scale_height))


class TimeSettingOption(UIGrand):
    def __init__(self):
        self._layer = 5
        UIGrand.__init__(self)

        self.image = Surface((600 * self.screen_scale_width, 80 * self.screen_scale_height))
        self.image.fill((10, 100, 200))

        battle_ui_images = self.game.battle.battle_ui_images
        self.time_select_image = battle_ui_images["time_select"]
        self.time_option_rects = {key: key.get_rect(
            topleft=((100 * index) * self.screen_scale_width, 0)) for index, key in
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

        self.rect = self.image.get_rect(topright=((self.grand.mini_cosmic_ui.rect.topleft[0],
                                                   self.grand.time_info_bar_ui.rect.bottomleft[1])))

    def reset(self):
        self.image = self.base_image.copy()

        for index, image in enumerate(self.time_option_rects):  # add selected border after base image
            rect = self.time_option_rects[image]
            if not index:
                self.image.blit(self.time_select_image, rect)
                self.image.blit(image, rect)
                break

    def update(self, dt):
        UIGrand.update(self, dt)
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


class ArmyInfo(UIGrand):
    def __init__(self, pos):
        """UI for showing stat detail of selected army"""
        self._layer = 7
        UIGrand.__init__(self, player_cursor_interact=False)
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


class ArmyManagement(UIGrand):
    def __init__(self):
        self._layer = 5
        UIGrand.__init__(self)
        self.font = self.game.generic_ui_font
        self.header_font = self.game.large_generic_ui_font
        self.image = Surface((2200 * self.screen_scale_width, 432 * self.screen_scale_height))
        self.image.fill((200, 50, 50))
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(bottomleft=(0, self.screen_height))

    def update(self, dt):
        UIGrand.update(self, dt)
        if self.mouse_over:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))


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
        UIGrand.update(self, dt)
        if self.mouse_over:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))


class EventNotification(BattleEventNotification, UIGrand):
    event_icons = {}

    def __init__(self):
        self._layer = 5
        BattleEventNotification.__init__(self, (0, 0))
        UIGrand.__init__(self)
        self.all_event_rects = [Rect(0, index * 100 * self.screen_scale_height,
                                     800 * self.screen_scale_width, self.event_item_height) for index in range(10)]
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

    def update(self, dt):
        UIGrand.update(self, dt)
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
                        self.grand.camera_pos = Vector2(
                            (event[2][0] * self.grand.map_shown_to_base_scale_width) - self.half_screen_width,
                            (event[2][1] * self.grand.map_shown_to_base_scale_height) - self.half_screen_height)
                        self.grand.fix_camera()
                    elif self.event_alt_press:  # remove event
                        self.grand.current_campaign_state["eventlog"].pop(index)
                        self.event_list_update()
                    break


class TechManagement(UIGrand):
    def __init__(self):
        self._layer = 5
        UIGrand.__init__(self)

        self.image = Surface((3044 * self.screen_scale_width, 432 * self.screen_scale_height), SRCALPHA)
        self.rect = self.image.get_rect(center=(self.screen_width / 2, self.screen_height / 2))

    def update(self, dt):
        UIGrand.update(self, dt)
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
        UIGrand.update(self, dt)
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
        UIGrand.update(self, dt)
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
        UIGrand.update(self, dt)
        if self.mouse_over:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))


class PlayerGrandInteract(UIGrand):
    def __init__(self):
        self._layer = 9999999999999999999999999999999999999998  # always 1 layer less than cursor so it get updated last but before cursor
        UIGrand.__init__(self, player_cursor_interact=False)
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
                                if any([army.assembling for army in self.grand.player_selected_army]):
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
                            elif any([army.assembling for army in self.grand.player_selected_army]):
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
                        self.rect = Rect(left + self.grand.camera_pos[0],
                                         top + self.grand.camera_pos[1], width,
                                         height)  # rect for collision unit selection check
                        draw.rect(self.grand_camera.image, (0, 0, 0), selection_rect, self.inner_line_size)
                        draw.rect(self.grand_camera.image, (255, 255, 255), selection_rect, self.line_size)
                    else:
                        self.rect = Rect(left + self.grand.camera_pos[0],
                                         top + self.grand.camera_pos[1], 1,
                                         1)  # rect for collision unit selection check
        else:
            self.reset()
