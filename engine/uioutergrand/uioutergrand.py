from math import ceil

from pygame import Vector2, Surface, SRCALPHA, Rect, draw, Color, Font
from pygame.sprite import spritecollideany

from engine.uimenu.uimenu import UIMenu, UIScroll
from engine.uibattle.uibattle import CharacterSpeechBox
from engine.uiouterbattle.drama import TextDrama
from engine.utils.text_making import (add_plus_to_number, add_comma_number, text_render_with_bg,
                                      make_long_text)


class UIOuterGrand(UIMenu):
    def __init__(self, player_cursor_interact=True, has_containers=False):
        """
        Parent class for all battle menu user interface that exist outside of grand camera
        """
        from engine.grand.grand import Grand
        UIMenu.__init__(self, player_cursor_interact=player_cursor_interact, has_containers=has_containers)
        self.grand = Grand.grand
        self.character_portraits = self.grand.character_portraits
        self.character_recruit_building_list = self.grand.stat_data.character_recruit_building_list
        self.text_popup = self.grand.text_popup
        self.add_to_outer_ui_menu_updater = self.grand.add_to_outer_ui_menu_updater
        self.remove_from_outer_ui_menu_updater = self.grand.remove_from_outer_ui_menu_updater
        self.max_description_box_width = int(1000 * self.screen_scale_width)


class OuterGrandUIScroll(UIScroll):
    def __init__(self, ui, pos):
        self._layer = 6
        UIScroll.__init__(self, ui, pos)

    def update(self, dt):
        UIScroll.update(self, dt)
        if self.event_press:
            if self.current_row is not None:
                self.ui.current_row = self.current_row
                self.ui.draw_card_list_to_ui()


class GrandListUI:
    def __init__(self):
        """UI with list that can be scrolling up and down"""
        self.max_row = 0
        self.current_row = 0
        self.total_row = 0
        self.max_row_show = 1  # trick the scroller to use additional row instead of total
        self.scroll_total_row = self.total_row + 1
        self.card_list = {}
        self.card_rects = []
        self.scroll = OuterGrandUIScroll(self, self.rect.topright)

    def create_cards_surface(self):
        """Create image for all existing cards"""
        pass

    def reset(self):
        """Reset all cards and recreate them"""
        self.current_row = 0
        self.card_list = {}
        self.create_cards_surface()
        self.scroll.change_image(self.current_row, self.scroll_total_row)

    def draw_card_list_to_ui(self, item_list, selected_list=()):
        """Recreate ui and draw showing cards to ui image"""
        self.image = self.base_image.copy()
        show_index = 0
        len_rects_check = len(self.card_rects) - 1
        for index, item in enumerate(item_list):
            if index >= self.current_row:
                if item not in selected_list:
                    self.image.blit(self.card_list[item][0], self.card_rects[show_index])
                else:
                    self.image.blit(self.card_list[item][1], self.card_rects[show_index])
                show_index += 1
            if show_index == len_rects_check:
                return


class Button(UIOuterGrand):
    def __init__(self, images, text):
        """Button that player can click"""
        self._layer = 5
        UIOuterGrand.__init__(self)
        self.font = self.game.large_generic_ui_font
        text_surface = text_render_with_bg(text, self.font)
        self.images = {key: value.copy() for key, value in images.items()}
        for value in self.images.values():
            value.blit(text_surface, text_surface.get_rect(center=(value.get_width() / 2, value.get_height() / 2)))


class ToggleButton(Button):
    def __init__(self, images, text, pos):
        """Button that player click to toggle selected/unselected"""
        self._layer = 5
        Button.__init__(self, images, text)

        self.images = images
        self.image = images["unselected"]
        self.selected = False
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, dt):
        if UIOuterGrand.update(self, dt) and self.event_press:
            if self.selected:
                self.selected = True
                self.image = self.images["unselected"]
            else:
                self.selected = False
                self.image = self.images["selected"]


class DiplomacyHead(UIOuterGrand):
    simple_font = False

    def __init__(self, font_size):
        """UI showing AI faction ruler talk to player"""
        self._layer = 5
        UIOuterGrand.__init__(self, player_cursor_interact=False)
        self.character_list = self.grand.character_list

        self.font_size = int(font_size * self.screen_scale_height)
        self.image = Surface((1000 * self.screen_scale_width, 200 * self.screen_scale_height))

        self.talk_timer = 0
        self.culture = "default"
        self.rect = self.image.get_rect(topright=self.grand.mini_cosmic_ui.rect.topleft)

    def start_speak(self, character, speech_id):
        self.culture = self.character_list[character]["Culture"]
        self.culture = "default"
        #
        # font = "simple"
        # if not self.simple_font and self.game.language in ("en", "es", "it", "fr", "de",):
        #     # culture font only available for latin alphabet sadly
        #     font = "culture_" + character.culture
        #
        # font = Font(self.ui_font[font], self.font_size)
        # max_text_width = 800 * self.screen_scale_width
        # text = self.grab_text(("diplomacy", character))
        # long_text_surface = make_long_text(text, (0, 0), self.font)
        # text_surface = Surface(long_text_surface.get_size())
        # text_surface.fill((224, 224, 224))
        # text_surface.blit(long_text_surface, (0, 0))
        #
        # images = self.grand.battle_ui_images
        # start_top = images["speech_start_top"]
        # start_mid = smoothscale(images["speech_start_mid"], (images["speech_start_mid"].get_width(),
        #                                                           text_surface.get_height()))
        # start_bottom = images["speech_start_bottom"]
        #
        # end_top = images["speech_end_top"]
        # end_mid = smoothscale(images["speech_end_mid"], (images["speech_end_mid"].get_width(),
        #                                                       text_surface.get_height()))
        # end_bottom = images["speech_end_bottom"]
        #
        # body_top = smoothscale(images["speech_body_top"], (text_surface.get_width(),
        #                                                         images["speech_body_top"].get_height()))
        # body_bottom = smoothscale(images["speech_body_bottom"], (text_surface.get_width(),
        #                                                               images["speech_body_bottom"].get_height()))
        #
        # self.base_image = Surface((text_surface.get_width() + start_top.get_width() + end_top.get_width(),
        #                            text_surface.get_height() + start_top.get_height() + start_bottom.get_height()),
        #                           SRCALPHA)
        #
        # start_top_rect = start_top.get_rect()
        # self.base_image.blit(start_top, start_top_rect)
        #
        # start_bottom_rect = start_bottom.get_rect(bottomleft=(0, self.base_image.get_height()))
        # self.base_image.blit(start_bottom, start_bottom_rect)
        #
        # start_mid_rect = start_mid.get_rect(topleft=(0, start_top_rect.height))
        # self.base_image.blit(start_mid, start_mid_rect)
        #
        # end_top_rect = end_top.get_rect(topright=(self.base_image.get_width(), 0))
        # self.base_image.blit(end_top, end_top_rect)
        #
        # end_bottom_rect = end_bottom.get_rect(bottomright=(self.base_image.get_width(), self.base_image.get_height()))
        # self.base_image.blit(end_bottom, end_bottom_rect)
        #
        # end_mid_rect = end_mid.get_rect(topright=(self.base_image.get_width(), end_top_rect.height))
        # self.base_image.blit(end_mid, end_mid_rect)
        #
        # body_top_rect = body_top.get_rect(topleft=(start_top_rect.width, 0))
        # self.base_image.blit(body_top, body_top_rect)
        #
        # body_bottom_rect = body_bottom.get_rect(bottomleft=(start_bottom_rect.width, self.base_image.get_height()))
        # self.base_image.blit(body_bottom, body_bottom_rect)
        #
        # self.right_image = self.base_image
        # self.left_image = flip(self.base_image, 1, 0)
        #
        # text_rect = text_surface.get_rect(topleft=start_mid_rect.topright)
        # self.right_image.blit(text_surface, text_rect)
        #
        # text_rect = text_surface.get_rect(topright=(self.base_image.get_width() - start_mid_rect.topright[0],
        #                                             start_mid_rect.topright[1]))
        # self.left_image.blit(text_surface, text_rect)
        #
        # self.base_pos = character.base_pos.copy()
        # self.finish_unfolding = False
        # self.direction_left = False
        # self.current_length = start_top.get_width()
        #
        # self.max_length = self.base_image.get_width()
        #
        # self.image = self.base_image.subsurface((0, 0, self.current_length, self.base_image.get_height()))
        # self.rect = self.image.get_rect(midleft=character.rect.center)
        #
        # if voice:
        #     self.battle.add_sound_effect_queue(choice(self.battle.sound_effect_pool[voice[0]]),
        #                                        character.base_pos, voice[1],
        #                                        voice[2], volume="voice")
        # elif voice is False:  # None will play no sound
        #     self.battle.add_sound_effect_queue(choice(self.battle.sound_effect_pool["parchment_write"]),
        #                                        character.base_pos, 1000,
        #                                        0, volume="voice")


    # def update(self, dt):


class PlayerTopBar(UIOuterGrand):
    def __init__(self):
        """UI Bar at the top of screen showing player's faction resource and turn time"""
        self._layer = 5
        UIOuterGrand.__init__(self)

        self.max_description_box_width = int(1500 * self.screen_scale_width)
        self.image = Surface((2400 * self.screen_scale_width, 80 * self.screen_scale_height))
        self.image.fill((80, 200, 255))
        self.image.blit(self.grand_ui_images["gold"], (50 * self.screen_scale_width,
                                                       10 * self.screen_scale_height))
        self.image.blit(self.grand_ui_images["supply"], (850 * self.screen_scale_width,
                                                         10 * self.screen_scale_height))
        self.image.blit(self.grand_ui_images["happiness"], (1550 * self.screen_scale_width,
                                                            10 * self.screen_scale_height))
        self.image.blit(self.grand_ui_images["turn"], (1950 * self.screen_scale_width,
                                                       10 * self.screen_scale_height))

        self.base_image = self.image.copy()
        self.font = self.game.large_generic_ui_font
        self.text_pos = {"gold": (150 * self.screen_scale_width, 10 * self.screen_scale_height),
                         "supply": (950 * self.screen_scale_width, 10 * self.screen_scale_height),
                         "happiness": (1650 * self.screen_scale_width, 10 * self.screen_scale_height),
                         "turn": (2050 * self.screen_scale_width, 10 * self.screen_scale_height)}
        self.blit_text_rect = {}
        self.player_faction_resource = {}
        self.rect = self.image.get_rect()

    def update(self, dt):
        current_campaign_state = self.grand.current_campaign_state

        resource = current_campaign_state["faction"][self.grand.player_faction]
        resource = ((int(resource["gold"]), int(resource["gold_income"])),
                    (int(resource["supply"]), int(resource["supply_income"])),
                    int(resource["happiness"]),
                    str(current_campaign_state["turn"]) + "." + str(current_campaign_state["phase"]))

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

        if UIOuterGrand.update(self, dt):
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))
            for key, rect in self.blit_text_rect.items():
                if rect.collidepoint(inside_mouse_pos):
                    text = [self.grab_text(("ui", "info_text_" + key)), "",
                            self.grab_text(("ui", "info_text_" + key + "_description")), ""]
                    if key != "turn":
                        resource_effect_list = self.grand.current_campaign_state["faction"][self.grand.player_faction][
                            key + "_effect"]
                        text_sum = {key: 0 for key in resource_effect_list}
                        for key2, value2 in resource_effect_list.items():
                            if type(value2) is list:
                                for value3 in value2:
                                    text_sum[key2] += value3[1]
                            elif type(value2) is str:
                                text_sum[key2] = value2
                            else:
                                text_sum[key2] += value2
                        for key2, value2 in text_sum.items():
                            if value2:
                                if type(value2) is str:
                                    text.append(self.grab_text(("ui", "info_header_" + key2)) + value2)
                                else:
                                    text.append(self.grab_text(("ui", "info_header_" + key2)) +
                                                add_plus_to_number(add_comma_number(int(value2))))
                    self.text_popup.popup(self.cursor.rect, text,
                                          width_text_wrapper=self.max_description_box_width)
                    self.add_to_outer_ui_menu_updater(self.text_popup)
                    break


class PlayerFactionCultureList(UIOuterGrand):
    def __init__(self):
        self._layer = 5
        UIOuterGrand.__init__(self)
        self.font = self.game.medium_generic_ui_font
        self.value_text_font_cache = self.game.font_text_cache[self.font]
        self.culture_coas = self.grand.sprite_data.culture_coas
        self.image = Surface((0, 0))
        self.image_width = self.image.get_width()
        self.image.fill((255, 255, 255))
        self.base_image = self.image.copy()
        self.culture_coa_rects = {}
        self.faction_culture_value = {}
        self.culture_management_button_rect = Rect((0, 0, 0, 0))
        self.rect = self.image.get_rect(topleft=self.grand.player_top_bar_ui.rect.bottomleft)

    def add_culture_portrait(self, surface, culture, culture_value, pos):
        culture_image = self.culture_coas[culture]["tiny"]
        culture_rect = culture_image.get_rect(topleft=pos)
        surface.blit(culture_image, culture_rect)

        policy_image = self.grand_ui_images["policy_small_" + culture_value["policy"]]
        surface.blit(policy_image, policy_image.get_rect(midtop=culture_rect.topleft))

        if int(culture_value["penalty"]):
            penalty_image = self.grand_ui_images["culture_value_bad"]
        else:
            penalty_image = self.grand_ui_images["culture_value_good"]
        surface.blit(penalty_image, penalty_image.get_rect(midbottom=culture_rect.bottomleft))

        integration_value = culture_value["integration"]
        if integration_value not in self.value_text_font_cache:
            text_surface = text_render_with_bg(integration_value, self.font, Color("black"))
            self.value_text_font_cache[integration_value] = text_surface
        else:
            text_surface = self.value_text_font_cache[integration_value]
        surface.blit(text_surface, text_surface.get_rect(midtop=culture_rect.topright))

        influence_value = culture_value["influence"]
        if influence_value not in self.value_text_font_cache:
            text_surface = text_render_with_bg(influence_value, self.font, Color("black"))
            self.value_text_font_cache[influence_value] = text_surface
        else:
            text_surface = self.value_text_font_cache[influence_value]
        surface.blit(text_surface, text_surface.get_rect(midbottom=culture_rect.bottomright))
        return culture_rect

    def get_culture_stat(self, culture, player_faction_state):
        culture_state = player_faction_state["culture"][culture]
        return {"policy": culture_state["policy"],
                "integration": str(int(culture_state["integration"] * 100)) + "%",
                "influence": str(int(culture_state["influence"] * 100)) + "%",
                "weight": " (" + str(culture_state["weight"]) + "/" +
                          str(player_faction_state["total_culture_weight"]) + ")",
                "penalty": str(culture_state["penalty"])}

    def culture_change(self):
        faction_culture_value = {}
        player_faction_state = self.grand.current_campaign_state["faction"][self.grand.player_faction]
        faction_culture_state = player_faction_state["culture"]

        for index, culture in enumerate(faction_culture_state):
            faction_culture_value[culture] = self.get_culture_stat(culture, player_faction_state)

        if self.faction_culture_value != faction_culture_value:
            if len(faction_culture_state) > 7:
                self.image = Surface(((2000 + 300) * self.screen_scale_width, 400 * self.screen_scale_height))
                self.image_width = self.image.get_width()
                self.image.fill((255, 255, 255))
            else:
                self.image = Surface((((250 * len(faction_culture_state)) + 300) * self.screen_scale_width,
                                      200 * self.screen_scale_height))
                self.image_width = self.image.get_width()
                self.image.fill((255, 255, 255))
            self.culture_management_button_rect = self.grand_ui_images["policy_management"].get_rect(midright=(
                                self.image.get_width(), 100 * self.screen_scale_height))
            self.image.blit(self.grand_ui_images["policy_management"], self.culture_management_button_rect)

            self.culture_coa_rects = {}
            self.faction_culture_value = faction_culture_value

            for index, culture in enumerate(faction_culture_state):
                culture_rect = self.add_culture_portrait(self.image, culture, faction_culture_value[culture],
                                                         (((300 * index) + 50) * self.screen_scale_width,
                                                          25 * self.screen_scale_height))

                self.culture_coa_rects[culture] = culture_rect
            self.rect = self.image.get_rect(topleft=self.grand.player_top_bar_ui.rect.bottomleft)

    def update(self, dt):
        if UIOuterGrand.update(self, dt):
            grand = self.grand
            grab_text = self.grab_text
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))
            if self.culture_management_button_rect.collidepoint(inside_mouse_pos):
                if self.event_press:
                    self.remove_from_outer_ui_menu_updater(grand.player_collapsable_uis)
                    grand.culture_management_ui.reset()
                    self.add_to_outer_ui_menu_updater(grand.culture_management_uis)
                else:
                    self.text_popup.popup(self.cursor.rect, grab_text(("ui", "info_text_policy_management")),
                                          width_text_wrapper=self.max_description_box_width)
                    self.add_to_outer_ui_menu_updater(self.text_popup)
            else:
                for culture, rect in self.culture_coa_rects.items():
                    if rect.collidepoint(inside_mouse_pos):
                        this_culture_value = self.faction_culture_value[culture]
                        culture_state = grand.current_campaign_state["faction"][grand.player_faction]["culture"][
                            culture]
                        text = [
                            grab_text(("ui", "info_header_culture")) + grab_text(("culture", culture, "Name")),
                            grab_text(("ui", "info_header_policy")) + grab_text(
                                ("ui", "info_text_culture_" + culture_state["policy"])),
                            grab_text(("ui", "info_header_integration")) + this_culture_value[
                                "integration"],
                            grab_text(("ui", "info_header_influence")) + this_culture_value["influence"] + this_culture_value["weight"]]
                        if int(this_culture_value["penalty"]):
                            text.append(grab_text(("ui", "info_header_happiness_penalty")) + this_culture_value[
                                "penalty"])
                        self.text_popup.popup(self.cursor.rect, text,
                                              width_text_wrapper=self.max_description_box_width)
                        self.add_to_outer_ui_menu_updater(self.text_popup)
                        break


class MenuBar(UIOuterGrand):
    def __init__(self):
        self._layer = 4
        UIOuterGrand.__init__(self)
        button_images = self.grand.grand_ui_images
        self.image = Surface((1000 * self.screen_scale_width, 80 * self.screen_scale_height), SRCALPHA)
        self.image.fill((50, 50, 200))
        self.button_rects = {"army_reserve": button_images["army_reserve"].get_rect(
            topleft=(50 * self.screen_scale_width, 0)),
            "court": button_images["court"].get_rect(
                topleft=(200 * self.screen_scale_width, 0)),
            "diplomacy": button_images["diplomacy"].get_rect(
                topleft=(350 * self.screen_scale_width, 0)),
            "technology": button_images["technology"].get_rect(
                topleft=(500 * self.screen_scale_width, 0)),
            "menu": button_images["menu"].get_rect(
                topleft=(650 * self.screen_scale_width, 0))}
        for key, value in self.button_rects.items():
            self.image.blit(button_images[key], self.button_rects[key])
        self.rect = self.image.get_rect(topleft=(self.grand.time_setting_ui.rect.topright[0], 0))

    def update(self, dt):
        if UIOuterGrand.update(self, dt):

            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))

            for key, rect in self.button_rects.items():
                if rect.collidepoint(inside_mouse_pos):
                    if self.event_press:
                        self.grand.remove_from_outer_ui_menu_updater(self.grand.player_collapsable_uis)
                        if key == "menu":
                            self.grand.esc_press = True
                        elif key == "army_reserve":
                            self.grand.player_grand_reserve_army_setup_ui.reset(active=False)
                            self.grand.player_grand_character_selector_ui.add(None)
                            self.grand.player_grand_reserve_army_list_ui.reset()
                            self.add_to_outer_ui_menu_updater(self.grand.player_army_reserve_setup_uis)
                        elif key == "court":
                            self.grand.court_management_ui.reset()
                            self.add_to_outer_ui_menu_updater(self.grand.court_management_uis)
                        elif key == "diplomacy":
                            self.grand.diplomacy_management_ui.reset()
                            self.add_to_outer_ui_menu_updater(self.grand.diplomacy_management_uis)
                        elif key == "technology":
                            pass

                    else:
                        self.text_popup.popup(self.cursor.rect, self.grab_text(("ui", "info_text_" + key)))
                        self.add_to_outer_ui_menu_updater(self.text_popup)


class TimeSettingOption(UIOuterGrand):
    def __init__(self):
        self._layer = 5
        UIOuterGrand.__init__(self)

        self.image = Surface((600 * self.screen_scale_width, 80 * self.screen_scale_height))
        self.image.fill((10, 100, 200))

        battle_ui_images = self.battle_ui_images
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
        if UIOuterGrand.update(self, dt) and self.event_press:
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


class PlayerArmyListSortOption(UIOuterGrand):
    def __init__(self):
        self._layer = 5
        UIOuterGrand.__init__(self)
        self.image = Surface((950 * self.screen_scale_width, 100 * self.screen_scale_height))
        self.rect = self.image.get_rect(topright=self.grand.mini_cosmic_ui.rect.bottomright)
        button_width = self.grand_ui_images["sort_number"].get_width()
        self.option_rects = {"commander": self.grand_ui_images["sort_supply"].get_rect(),
                             "supply": self.grand_ui_images["sort_number"].get_rect(topleft=(button_width, 0)),
                             "number": self.grand_ui_images["sort_commander"].get_rect(topleft=(button_width * 2, 0)),
                             "region": self.grand_ui_images["sort_region"].get_rect(topleft=(button_width * 3, 0))}
        self.option = ("region", "descend")
        for option, rect in self.option_rects.items():
            self.image.blit(self.grand_ui_images["sort_" + option], rect)

        self.image.blit(self.grand_ui_images["sort_" + self.option[0] + "_" + self.option[1]],
                        self.option_rects[self.option[0]])

    def update(self, dt):
        if UIOuterGrand.update(self, dt):
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
                        self.text_popup.popup(self.cursor.rect, self.grab_text(("ui", "info_text_sort_" + option)))
                        self.add_to_outer_ui_menu_updater(self.text_popup)

                    # re-blit all buttons to reset
                    for option2, rect2 in self.option_rects.items():
                        self.image.blit(self.grand_ui_images["sort_" + option2], rect2)

                    self.image.blit(self.grand_ui_images["sort_" + self.option[0] + "_" + self.option[1]],
                                    self.option_rects[self.option[0]])
                    break


class EventNotification(UIOuterGrand):

    def __init__(self):
        self._layer = 5
        UIOuterGrand.__init__(self)

        self.event_item_height = 120 * self.screen_scale_height
        self.event_item_height_center = self.event_item_height / 2
        self.font = self.game.large_generic_ui_font
        self.image = Surface((1000 * self.screen_scale_width, 1100 * self.screen_scale_height), SRCALPHA)
        self.base_image = self.image.copy()
        self.before_hover_image = self.image
        self.event_card_rects = [Rect(0, index * self.event_item_height,
                                      1000 * self.screen_scale_width, self.event_item_height) for index in range(10)]
        self.event_cards = {}
        self.current_hover_index = None
        self.rect = self.image.get_rect(midleft=(0, self.half_screen_height))

    def update_image(self):
        self.current_hover_index = None
        self.image = self.base_image.copy()
        to_show_events = self.grand.current_campaign_state["eventlog"][-10:]  # show only last 10 items

        for index, event in enumerate(to_show_events):
            if event not in self.event_cards:  # create new card
                card_image = Surface((1000 * self.screen_scale_width, self.event_item_height), SRCALPHA)
                hover_card_image = card_image.copy()
                hover_card_image.fill((200, 200, 200))
                event_icon = self.grand_ui_images[event[0]]
                for card in (card_image, hover_card_image):
                    card.blit(event_icon, event_icon.get_rect(midleft=(0, self.event_item_height_center)))

                    event_text = make_long_text((self.grand_ui_images["turn"], ":" + event[2], event[1]), (0, 0),
                                                self.font, specific_width=700 * self.screen_scale_width)
                    card.blit(event_text, event_text.get_rect(topleft=(100 * self.screen_scale_width, 0)))
                self.event_cards[event] = (card_image, hover_card_image)
            self.image.blit(self.event_cards[event][0],
                            self.event_cards[event][0].get_rect(topleft=(0, index * self.event_item_height)))
        self.before_hover_image = self.image.copy()

    def hover_over_card(self, index):
        if self.current_hover_index != index:
            self.image = self.before_hover_image.copy()
            showing_events = self.grand.current_campaign_state["eventlog"][-10:]
            if index < len(showing_events):
                event = self.grand.current_campaign_state["eventlog"][-10:][index]
                self.image.blit(self.event_cards[event][1],
                                self.event_cards[event][0].get_rect(topleft=(0, index * self.event_item_height)))
            self.current_hover_index = index

    def add_new_event(self, event):
        self.grand.current_campaign_state["eventlog"].append(event)
        if len(self.grand.current_campaign_state["eventlog"]) > 100:
            self.grand.current_campaign_state["eventlog"] = self.grand.current_campaign_state["eventlog"][1:]
        self.update_image()

    def remove_event(self, event):
        self.grand.current_campaign_state["eventlog"].remove(event)
        self.event_cards.pop(event)
        self.update_image()

    def update(self, dt):
        if self.event_cards and UIOuterGrand.update(self, dt):
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))
            for index, rect in enumerate(self.event_card_rects):
                if rect.collidepoint(inside_mouse_pos):
                    if self.event_press:  # go to event
                        showing_events = self.grand.current_campaign_state["eventlog"][-10:]
                        if index < len(showing_events):
                            event = showing_events[index]
                            if event[3]:
                                self.grand.camera_topleft_pos = Vector2(
                                    (event[3][0] * self.grand.map_shown_to_base_scale_width) - self.half_screen_width,
                                    (event[3][1] * self.grand.map_shown_to_base_scale_height) - self.half_screen_height)
                                self.grand.fix_camera()
                    elif self.event_alt_press:  # remove event
                        showing_events = self.grand.current_campaign_state["eventlog"][-10:]
                        if index < len(showing_events):
                            self.remove_event(showing_events[index])
                    else:
                        self.hover_over_card(index)
                    break


class TechManagement(UIOuterGrand):
    def __init__(self):
        self._layer = 5
        UIOuterGrand.__init__(self)

        self.image = Surface((3044 * self.screen_scale_width, 432 * self.screen_scale_height), SRCALPHA)
        self.rect = self.image.get_rect(center=self.screen_center)

    def update(self, dt):
        if UIOuterGrand.update(self, dt):
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
        if UIOuterGrand.update(self, dt):
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
        self.rect = self.image.get_rect(center=self.screen_center)

    def update(self, dt):
        pass


class EventDetailPopup(UIOuterGrand):
    def __init__(self):
        self._layer = 6
        UIOuterGrand.__init__(self)

        self.image = Surface((800 * self.screen_scale_width, 1000 * self.screen_scale_height))
        self.image.fill((255, 255, 255))
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(center=self.screen_center)

    def popup(self, event_data):
        pass

    def update(self, dt):
        if UIOuterGrand.update(self, dt):
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))


class PlayerArmyList(GrandListUI, UIOuterGrand):
    def __init__(self):
        self._layer = 5
        UIOuterGrand.__init__(self)

        self.image = Surface((950 * self.screen_scale_width, 1050 * self.screen_scale_height), SRCALPHA)
        self.rect = self.image.get_rect(topright=self.grand.player_army_list_sort_option_ui.rect.bottomright)

        GrandListUI.__init__(self)
        self.font = self.game.medium_generic_ui_font
        self.value_text_font_cache = self.game.font_text_cache[self.font]
        self.image.fill((80, 200, 100, 100))
        self.base_image = self.image.copy()
        self.empty_card_image = Surface((950 * self.screen_scale_width, 150 * self.screen_scale_height), SRCALPHA)
        self.empty_card_image.fill((200, 130, 130, 150))

        self.empty_selected_base_image = Surface((950 * self.screen_scale_width, 150 * self.screen_scale_height))
        self.empty_selected_base_image.fill((200, 100, 100))

        self.empty_card_image.blit(self.grand_ui_images["supply"], (210 * self.screen_scale_width,
                                                                    10 * self.screen_scale_height))

        self.empty_card_image.blit(self.grand_ui_images["number"], (210 * self.screen_scale_width,
                                                                    80 * self.screen_scale_height))

        self.card_icon_rects = {"resupply": self.grand_ui_images["army_resupply_disable"].get_rect(topleft=(
            10 * self.screen_scale_width, 10 * self.screen_scale_height)),
            "assemble": self.grand_ui_images["army_resupply_disable"].get_rect(bottomleft=(
                10 * self.screen_scale_width,
                self.empty_card_image.get_height() - 10 * self.screen_scale_height))}

        self.card_rects = [self.empty_card_image.get_rect(
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
        self.card_list[army][0].blit(image, rect)
        self.card_list[army][1].blit(image, rect)

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
        self.card_list[army] = self.draw_army_card(army)
        self.add_assemble_resupply_to_card(army, "assemble")
        self.add_assemble_resupply_to_card(army, "resupply")

        if self.grand.current_campaign_state["faction"][self.grand.player_faction]["army"].index(
                army) >= self.current_row:
            # redraw list if card is being shown in ui
            self.draw_card_list_to_ui(self.grand.current_campaign_state["faction"][self.grand.player_faction]["army"],
                                      self.grand.player_selected_army)

    def create_cards_surface(self):
        """Reset entire card list, draw card for each army"""
        current_army_list = self.grand.current_campaign_state["faction"][self.grand.player_faction]["army"]
        self.card_list = {}
        self.total_row = ceil(len(current_army_list) / (len(self.card_rects) - 1))
        if self.total_row == 1:
            self.total_row = 0
        self.scroll_total_row = self.total_row + 1
        for army in current_army_list:
            self.card_list[army] = self.draw_army_card(army)
            self.add_assemble_resupply_to_card(army, "assemble")
            self.add_assemble_resupply_to_card(army, "resupply")
        self.draw_card_list_to_ui(current_army_list)

    def update(self, dt):
        if UIOuterGrand.update(self, dt):
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))
            if self.cursor.scroll_up:
                if self.current_row > 0:
                    self.current_row -= 1
                    self.scroll.change_image(self.current_row, self.scroll_total_row)
                    self.draw_card_list_to_ui(self.grand.current_campaign_state["faction"][self.grand.player_faction]["army"],
                                              self.grand.player_selected_army)
            elif self.cursor.scroll_down:
                if self.current_row < self.total_row:
                    self.current_row += 1
                    self.scroll.change_image(self.current_row, self.scroll_total_row)
                    self.draw_card_list_to_ui(self.grand.current_campaign_state["faction"][self.grand.player_faction]["army"],
                                              self.grand.player_selected_army)
            else:
                grand = self.grand
                for index, rect in enumerate(self.card_rects):
                    if rect.collidepoint(inside_mouse_pos) and self.current_row + index < len(self.card_list):
                        army = grand.current_campaign_state["faction"][grand.player_faction][
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
                                    self.draw_card_list_to_ui(
                                        self.grand.current_campaign_state["faction"][self.grand.player_faction]["army"],
                                        self.grand.player_selected_army)

                                else:
                                    if which == "assemble":
                                        value = army.enable_assemble
                                    else:
                                        value = army.enable_resupply
                                    text = (self.grab_text(("ui", "info_header_" + which)) +
                                            self.grab_text(("ui", "info_text_" + str(value))))
                                    self.text_popup.popup(self.cursor.rect, text)
                                    self.add_to_outer_ui_menu_updater(self.text_popup)
                                return

                        if self.event_press:
                            if grand.shift_press:
                                if army not in grand.player_selected_army:
                                    grand.player_selected_army.append(army)
                            elif grand.ctrl_press:
                                if army in grand.player_selected_army:
                                    grand.player_selected_army.remove(army)
                            else:
                                grand.player_selected_army = [army]
                            self.draw_card_list_to_ui(
                                self.grand.current_campaign_state["faction"][self.grand.player_faction]["army"],
                                self.grand.player_selected_army)
                        # elif self.event_alt_press:
                        #     # open army management ui
                        #     grand.player_grand_preset_army_setup.popup("", army)
                        #     grand.player_army_info_ui.add_info(army.to_preset_dict)
                        #     self.outer_ui_updater.add(grand.player_grand_preset_army_setup,
                        #                               grand.player_army_info_ui)
                        elif self.event_middle_mouse_press:
                            grand.camera_topleft_pos = Vector2(
                                (army.base_pos[
                                     0] * grand.map_shown_to_base_scale_width) - self.half_screen_width,
                                (army.base_pos[
                                     1] * grand.map_shown_to_base_scale_height) - self.half_screen_height)
                            grand.fix_camera()
                        else:
                            text = (self.grab_text(("ui", "info_header_commander")) + self.grab_text(
                                ("character", army.commander_id, "Name")),)
                            self.text_popup.popup(self.cursor.rect, text,
                                                  width_text_wrapper=self.max_description_box_width)
                            self.add_to_outer_ui_menu_updater(self.text_popup)
                        break


class GrandTextDrama(TextDrama, UIOuterGrand):
    def __init__(self, grand):
        UIOuterGrand.__init__(self, player_cursor_interact=False)
        TextDrama.__init__(self, grand)


class PlayerGrandInteract(UIOuterGrand):
    def __init__(self):
        self._layer = 1
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
        cursor = self.cursor
        if not cursor.mouse_over:
            grand = self.grand
            # only consider if not mouse over any ui
            if cursor.is_alt_select_just_up:  # put alt (right) click first to prioritise it
                self.event_alt_press = True
                cursor.is_alt_select_just_up = False  # reset select button to prevent overlap interaction
            elif cursor.is_alt_select_down:
                self.event_alt_hold = True
                cursor.is_alt_select_just_down = False  # reset select button to prevent overlap interaction
            elif cursor.is_select_just_up:
                self.event_press = True
                cursor.is_select_just_up = False  # reset select button to prevent overlap interaction
            elif cursor.is_select_down:
                self.event_hold = True
                cursor.is_select_just_down = False  # reset select button to prevent overlap interaction

            if not self.event_hold and not self.event_press:
                if self.selection_start_pos and self.rect:  # release hold while band exist
                    player_faction = grand.player_faction
                    if player_faction:
                        player_armies = grand.current_campaign_state["faction"][player_faction]["army"]
                        army_select_list = list(set([army for index, army in enumerate(player_armies) if
                                                     index in self.rect.collidelistall([army.commander_actor.rect for
                                                                                        army in player_armies])]))
                        if self.rect.width <= 1 and self.rect.height <= 1:  # no band, player click only 1 army
                            army_select_list.sort(key=lambda x: x.commander_actor._layer,
                                                  reverse=True)  # get only top army
                            army_select_list = army_select_list[:1]
                        if army_select_list:
                            if grand.shift_press:
                                grand.player_selected_army += army_select_list
                                grand.player_selected_army = list(set(grand.player_selected_army))
                            elif grand.ctrl_press:
                                for army in army_select_list:
                                    if army in grand.player_selected_army:
                                        grand.player_selected_army.remove(army)
                            else:
                                grand.player_selected_army = army_select_list
                        else:
                            grand.player_selected_army = []
                            all_settlement_objects = self.grand.grand_settlement_objects
                            selected_settlement_object = spritecollideany(self, all_settlement_objects)
                            if (selected_settlement_object and selected_settlement_object.region in
                                    grand.current_campaign_state["faction"][player_faction]["region"]):
                                # click on player owned settlement
                                self.grand.remove_from_outer_ui_menu_updater(self.grand.player_collapsable_uis)
                                grand.region_management_ui.change_selected_region(selected_settlement_object.region)
                            else:  # select at no settlement, remove region management ui
                                grand.region_management_ui.change_selected_region(None)

                        grand.player_army_list_ui.draw_card_list_to_ui(player_armies, grand.player_selected_army)
                        self.reset()

                elif self.event_alt_press:  # right click order selected leader to do something
                    if grand.player_selected_army:  # order selected army to move to region at mouse pos
                        region_colour = tuple(grand.base_world_map.get_at(
                            (int(grand.base_cursor_pos[0]), int(grand.base_cursor_pos[1]))).rgb)
                        if region_colour in grand.region_by_colour_index:
                            region_id = grand.region_by_colour_index[region_colour]
                            if any([army.game_id in grand.current_campaign_state["battle"]["armies"] for army in
                                    grand.player_selected_army]):
                                # player army in battle, this will cause battle lost and armies retreat from battle,
                                # ask for confirmation first
                                grand.activate_input_popup(("confirm_input", "retreat",
                                                            (region_id, grand.shift_press)),
                                                           self.grab_text(
                                                               ("ui", "warn_input_retreat")),
                                                           self.grand.confirm_popup_uis)

                            else:  # no problem, issue move command
                                for army in grand.player_selected_army:
                                    if grand.shift_press:
                                        army.issue_move_command(region_id, direct=True)
                                    else:
                                        army.issue_move_command(region_id)

            else:  # holding left click, manipulate band
                self.current_pos = cursor.pos
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
                        self.rect = Rect(left + grand.camera_topleft_pos[0],
                                         top + grand.camera_topleft_pos[1], width,
                                         height)  # rect for collision unit selection check
                        draw.rect(self.grand_camera.image, (0, 0, 0), selection_rect, self.inner_line_size)
                        draw.rect(self.grand_camera.image, (255, 255, 255), selection_rect, self.line_size)
                    else:
                        self.rect = Rect(left + grand.camera_topleft_pos[0],
                                         top + grand.camera_topleft_pos[1], 1,
                                         1)  # rect for collision unit selection check

