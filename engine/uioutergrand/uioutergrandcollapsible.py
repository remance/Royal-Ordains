from math import ceil, floor

from pygame import Vector2, Surface, SRCALPHA, draw
from pygame.transform import flip

from uuid import uuid4
from engine.army.army import Army
from engine.constants import Culture_Policy_Integration
from engine.uimenu.uimenu import PresetArmySetupUI, CharacterSelector
from engine.uioutergrand.uioutergrand import (GrandListUI, UIOuterGrand, ToggleButton, OuterGrandUIScroll,
                                              PlayerFactionCultureList)
from engine.utils.text_making import (add_plus_to_number, text_render_with_bg,
                                      convert_modifier_number_to_percent_text)
from engine.utils.common import empty_method


class CourtManagement(GrandListUI, UIOuterGrand):
    def __init__(self):
        self._layer = 5
        UIOuterGrand.__init__(self)
        self.image = Surface((2000 * self.screen_scale_width, 1700 * self.screen_scale_height))
        self.image.fill((170, 170, 170))

        self.info_button_rect = self.grand_ui_images["info"].get_rect(topright=(
            self.image.get_width() - (100 * self.screen_scale_width), 0))
        self.image.blit(self.grand_ui_images["info"], self.info_button_rect)

        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(center=self.screen_center)
        GrandListUI.__init__(self)

        self.font = self.game.large_generic_ui_font
        self.selected_character = None

        self.max_row = 3
        self.max_col = 4
        self.max_character_show = self.max_col * self.max_row
        self.max_row_show = 1  # trick the scroller to use additional row instead of total

        self.character_selected_slot = Surface((300 * self.screen_scale_width, 300 * self.screen_scale_height),
                                               SRCALPHA)
        draw.circle(self.character_selected_slot, (189, 148, 217),
                    self.character_selected_slot.get_rect().center,
                    (self.character_selected_slot.get_width() / 2) - (3 * self.screen_scale_width))

        self.character_slot_rects = [self.character_portraits["default"]["medium"]["right"].get_rect(center=pos) for
                                     pos in [(self.image.get_width() / 2, 200 * self.screen_scale_height)] + [
                                         ((250 + (500 * col)) * self.screen_scale_width,
                                          (600 + (400 * row)) * self.screen_scale_height) for
                                         row in range(self.max_row) for col in range(self.max_col)]]

        self.fire_button = self.grand_ui_images["court_fire"]
        self.fire_button_rect = self.fire_button.get_rect()
        self.create_cards_surface = self.draw_card_list_to_ui  # court management ui use specific method for drawing ui

    def draw_card_list_to_ui(self, *args):
        self.image = self.base_image.copy()

        player_faction_state = self.grand.current_campaign_state["faction"][self.grand.player_faction]
        character_state_list = player_faction_state["character"]

        self.total_row = ceil(len(character_state_list) / ((self.max_row * 3) + 1))
        if self.total_row == 1:
            self.total_row = 0
        self.scroll_total_row = self.total_row + 1

        court_limit_text = text_render_with_bg \
            (self.grab_text(("ui", "info_header_court_limit")) + str
            (len(character_state_list)) + "/" + str(len(player_faction_state["region"])), self.font)
        self.image.blit(court_limit_text, court_limit_text.get_rect())

        first_to_show = (self.current_row * self.max_col) + 1
        last_to_show = first_to_show + self.max_character_show
        for index, character in enumerate(character_state_list):
            if not index or (first_to_show <= index < last_to_show):
                character_state = character_state_list[character]
                showing_index = 0
                if index:
                    showing_index = index - (self.current_row * self.max_col)
                    role_image = self.grand_ui_images["court_" + character_state[1]]
                else:  # first character always ruler
                    role_image = self.grand_ui_images["court_ruler"]

                role_rect = role_image.get_rect(center=self.character_slot_rects[showing_index].center)

                if character == self.selected_character:
                    self.image.blit(self.character_selected_slot,
                                    self.character_selected_slot.get_rect(
                                        center=self.character_slot_rects[showing_index].center))

                    if character_state[1] != "commander":  # cannot dismiss commander
                        self.fire_button_rect.midright = role_rect.midleft
                        self.image.blit(self.fire_button, self.fire_button_rect)

                self.image.blit(self.character_portraits[character]["medium"]["right"],
                                self.character_slot_rects[showing_index])

                self.image.blit(role_image, role_rect)

                text_surface = text_render_with_bg(self.grab_text(("character", character, "Name")), self.font)
                self.image.blit(text_surface, text_surface.get_rect(midtop=role_rect.midbottom))

                if character_state[0]:  # in army, add current army detail
                    pass

    def update(self, dt):
        if UIOuterGrand.update(self, dt):
            cursor = self.cursor
            if cursor.scroll_up:
                if self.current_row > 0:
                    self.current_row -= 1
                    self.scroll.change_image(self.current_row, self.scroll_total_row)
                    self.draw_card_list_to_ui()
            elif cursor.scroll_down:
                if self.current_row < self.total_row:
                    self.current_row += 1
                    self.scroll.change_image(self.current_row, self.scroll_total_row)
                    self.draw_card_list_to_ui()
            else:
                grab_text = self.grab_text
                text_popup = self.text_popup
                inside_mouse_pos = Vector2(
                    (cursor.pos[0] - self.rect.topleft[0]),
                    (cursor.pos[1] - self.rect.topleft[1]))
                if self.selected_character is not None and self.fire_button_rect.collidepoint(inside_mouse_pos):
                    if self.event_press:
                        self.grand.activate_input_popup(("confirm_input", "dismiss", self.selected_character),
                                                        grab_text(("ui", "info_text_dismiss")) +
                                                        grab_text
                                                        (("character", self.selected_character, "Name")) + "?",
                                                        self.grand.confirm_popup_uis)
                    else:
                        text_popup.popup(cursor.rect, grab_text(("ui", "info_text_court_fire")))
                        self.add_to_outer_ui_menu_updater(text_popup)
                elif self.info_button_rect.collidepoint(inside_mouse_pos):
                    text_popup = self.text_popup
                    grab_text = self.grab_text
                    text_popup.popup(cursor.rect,
                                     (grab_text(("ui", "info_text_court_management")), "",
                                      grab_text(("ui", "info_text_court_management_description"))),
                                     width_text_wrapper=self.max_description_box_width)
                    self.add_to_outer_ui_menu_updater(text_popup)
                else:
                    for rect_index, rect in enumerate(self.character_slot_rects):
                        if rect.collidepoint(inside_mouse_pos):
                            character_state_list = \
                                self.grand.current_campaign_state["faction"][self.grand.player_faction][
                                    "character"]
                            index = 0
                            if rect_index:  # non-ruler rect
                                index = rect_index + (self.current_row * self.max_col)
                            if index < len(character_state_list):
                                character = tuple(character_state_list.keys())[index]
                                character_state = character_state_list[character]
                                if self.event_press:
                                    if index:  # click at non-ruler character, show character management button
                                        self.selected_character = character
                                        self.draw_card_list_to_ui()
                                else:
                                    character_name_text = [grab_text(("character", character, "Name")), "", ]

                                    role_text = ""
                                    if character_state[1]:
                                        role_text += grab_text(("ui", "info_text_" + character_state[1]))
                                        if character_state[0]:
                                            if character_state[0].current_region:  # active
                                                role_text += (grab_text(("ui", "info_text_in_description")) +
                                                              grab_text(("character", character_state[0].commander_id,
                                                                         "Name")) +
                                                              grab_text(("ui", "info_text_army_description")) +
                                                              grab_text(("ui", "info_text_at_description")) +
                                                              grab_text(("region", character_state[0].current_region,
                                                                         "Name")))
                                            else:
                                                role_text += (grab_text(("ui", "info_text_in_description")) +
                                                              grab_text(("character", character_state[0].commander_id,
                                                                         "Name")) +
                                                              grab_text(("ui", "info_text_reserve_army_description")))

                                    else:
                                        if index:
                                            role_text += grab_text(("ui", "info_text_courtier"))
                                        else:
                                            role_text += grab_text(("ui", "info_text_ruler"))
                                    character_name_text.append(role_text)

                                    text_popup.popup(cursor.rect, character_name_text,
                                                     width_text_wrapper=self.max_description_box_width)
                                    self.add_to_outer_ui_menu_updater(text_popup)
                            break
        elif self.cursor.event:
            self.remove_from_outer_ui_menu_updater(self.grand.court_management_uis)


class DiplomacyManagement(GrandListUI, UIOuterGrand):
    def __init__(self):
        self._layer = 5
        UIOuterGrand.__init__(self)
        self.image = Surface((1800 * self.screen_scale_width, 1500 * self.screen_scale_height))
        self.rect = self.image.get_rect(center=self.screen_center)

        GrandListUI.__init__(self)
        self.font = self.game.large_generic_ui_font

        self.image.fill((170, 170, 170))
        self.info_button_rect = self.grand_ui_images["info"].get_rect(topright=(
            self.image.get_width() - (100 * self.screen_scale_width), 0))
        self.image.blit(self.grand_ui_images["info"], self.info_button_rect)

        self.base_image = self.image.copy()

        self.empty_card_image = Surface((1800 * self.screen_scale_width, 300 * self.screen_scale_height), SRCALPHA)

        draw.rect(self.empty_card_image, (0, 0, 0), self.empty_card_image.get_rect(),
                  width=int(10 * self.screen_scale_height))

        # card war/alliance, gift button
        gift_gold_button = self.grand_ui_images["diplomacy_gift_gold"]
        gift_supply_button = self.grand_ui_images["diplomacy_gift_supply"]
        diplomacy_value_button = self.grand_ui_images["diplomacy_value_good"]
        diplomacy_status_button = self.grand_ui_images["diplomacy_status"]

        card_image_center_y = self.empty_card_image.get_height() / 2

        self.diplomacy_ai_hand_rect = self.grand_ui_images["diplomacy_offer_castle"].get_rect(center=(
            self.grand_ui_images["diplomacy_status"].get_width() * 0.3,
            self.grand_ui_images["diplomacy_status"].get_height() * 0.5))
        self.diplomacy_player_hand_rect = self.grand_ui_images["diplomacy_offer_castle"].get_rect(center=(
            self.grand_ui_images["diplomacy_status"].get_width() * 0.7,
            self.grand_ui_images["diplomacy_status"].get_height() * 0.5))

        self.card_button_rects = {"portrait": self.character_portraits["default"]["medium"]["right"].get_rect(midleft=(
            50 * self.screen_scale_width, card_image_center_y)),
            "diplomacy_value": diplomacy_value_button.get_rect(
                center=(400 * self.screen_scale_width, card_image_center_y)),
            "diplomacy_status": diplomacy_status_button.get_rect
            (center=(800 * self.screen_scale_width, card_image_center_y)),
            "gift_gold": gift_gold_button.get_rect(center=(1300 * self.screen_scale_width, card_image_center_y)),
            "gift_supply": gift_supply_button.get_rect(center=(1600 * self.screen_scale_width, card_image_center_y))}

        for button, button_rect in self.card_button_rects.items():
            if button in ("gold", "supply"):
                self.empty_card_image.blit(self.grand_ui_images["diplomacy_" + button], button_rect)

        self.max_row = 4
        self.max_row_show = 1  # trick the scroller to use additional row instead of total

        self.card_rects = [self.empty_card_image.get_rect(midleft=(0, (400 + (310 * y)) * self.screen_scale_height)) for
                           y in range(self.max_row)]

        self.card_list = {}
        self.faction_diplomacy_value = {}

    def create_cards_surface(self):
        self.card_list = {}
        campaign_faction_state = self.grand.current_campaign_state["faction"]
        faction_list = [faction for faction in campaign_faction_state if
                        faction not in ("free", self.grand.player_faction)]
        self.total_row = ceil(len(faction_list) / (len(self.card_rects) - 1))
        if self.total_row == 1:
            self.total_row = 0
        self.scroll_total_row = self.total_row + 1
        if self.current_row > self.total_row:
            self.current_row = self.total_row

        for faction in faction_list:
            self.create_faction_card(faction, campaign_faction_state[faction])
        self.draw_card_list_to_ui(faction_list)

    def create_faction_card(self, faction, faction_state):
        """Create card image for new faction"""
        self.faction_diplomacy_value[faction] = None

        card_image = Surface(self.empty_card_image.get_size())
        card_image.fill(self.grand.faction_list[faction]["Colour"])  # add faction colour to card background
        # card_image.blit(self.grand_ui_images["diplomacy_status"], self.card_button_rects["diplomacy_status"])
        card_image.blit(self.empty_card_image, (0, 0))

        card_image.blit(self.grand_ui_images["diplomacy_gift_gold"], self.card_button_rects["gift_gold"])
        card_image.blit(self.grand_ui_images["diplomacy_gift_supply"], self.card_button_rects["gift_supply"])

        ruler = tuple(faction_state["character"].keys())[0]
        card_image.blit(self.character_portraits[ruler]["medium"]["right"], self.card_button_rects["portrait"])

        self.card_list[faction] = (card_image, card_image)

        self.update_card(faction, change_ally_status=True)

    def update_card(self, ai_faction, change_ally_status=None):
        """Update diplomacy value and ally status on card"""
        card_image = self.card_list[ai_faction][0]
        grand = self.grand
        player_faction = grand.player_faction
        player_faction_campaign_state = grand.current_campaign_state["faction"][player_faction]
        ai_faction_campaign_state = grand.current_campaign_state["faction"][ai_faction]
        player_faction_diplomacy_state = player_faction_campaign_state["diplomacy"]
        ai_faction_diplomacy_state = ai_faction_campaign_state["diplomacy"]

        new_diplomacy_value = ai_faction_diplomacy_state[player_faction]["value"]
        if new_diplomacy_value > 50:
            new_diplomacy_value = "diplomacy_value_good"
        elif new_diplomacy_value > -50:
            new_diplomacy_value = "diplomacy_value_neutral"
        else:
            new_diplomacy_value = "diplomacy_value_bad"
        if self.faction_diplomacy_value[ai_faction] != new_diplomacy_value:
            self.faction_diplomacy_value[ai_faction] = new_diplomacy_value
            card_image.blit(self.grand_ui_images[new_diplomacy_value],
                            self.card_button_rects["diplomacy_value"])

        if change_ally_status is not None:
            diplomacy_status_image = self.grand_ui_images["diplomacy_status"].copy()
            if ai_faction_diplomacy_state[player_faction]["offer"]:
                # show ai hand offer alliance to player
                # use faction main culture
                diplomacy_status_image.blit(self.grand_ui_images["diplomacy_offer_" +
                                                                 tuple(ai_faction_campaign_state["culture"].keys())[0]],
                                            self.diplomacy_ai_hand_rect)

            if player_faction_diplomacy_state[ai_faction]["offer"]:
                # show player hand offer alliance to this ai
                diplomacy_status_image.blit(flip(self.grand_ui_images["diplomacy_offer_" +
                                                                 tuple(player_faction_campaign_state["culture"].keys())
                                                                 [0]], True, False),
                                            self.diplomacy_player_hand_rect)

            card_image.blit(diplomacy_status_image, self.card_button_rects["diplomacy_status"])

    def update(self, dt):
        cursor = self.cursor
        grand = self.grand
        if UIOuterGrand.update(self, dt):
            current_campaign_state = grand.current_campaign_state
            campaign_faction_state = current_campaign_state["faction"]
            player_faction = grand.player_faction
            if cursor.scroll_up:
                if self.current_row > 0:
                    self.current_row -= 1
                    self.scroll.change_image(self.current_row, self.scroll_total_row)
                    self.draw_card_list_to_ui(
                        [item for item in campaign_faction_state if item not in
                         ("free", player_faction)])
            elif cursor.scroll_down:
                if self.current_row < self.total_row:
                    self.current_row += 1
                    self.scroll.change_image(self.current_row, self.scroll_total_row)
                    self.draw_card_list_to_ui(
                        [item for item in campaign_faction_state if item not in
                         ("free", player_faction)])
            else:
                inside_mouse_pos = Vector2(
                    (cursor.pos[0] - self.rect.topleft[0]),
                    (cursor.pos[1] - self.rect.topleft[1]))

                if self.info_button_rect.collidepoint(inside_mouse_pos):
                    text_popup = self.text_popup
                    grab_text = self.grab_text
                    text_popup.popup(cursor.rect,
                                     (grab_text(("ui", "info_text_diplomacy_management")), "",
                                      grab_text(("ui", "info_text_diplomacy_management_description"))),
                                     width_text_wrapper=self.max_description_box_width)
                    self.add_to_outer_ui_menu_updater(text_popup)

                else:
                    for rect_index, rect in enumerate(self.card_rects):
                        if rect.collidepoint(inside_mouse_pos) and rect_index + self.current_row < len(self.card_list):
                            index = rect_index + self.current_row
                            inside_card_mouse_pos = Vector2(
                                (inside_mouse_pos[0] - rect.topleft[0]),
                                (inside_mouse_pos[1] - rect.topleft[1]))
                            for button_key, button_rect in self.card_button_rects.items():
                                if button_rect.collidepoint(inside_card_mouse_pos):
                                    if self.event_press:
                                        faction = [item for item in campaign_faction_state if
                                                   item not in ("free", player_faction)][index]
                                        if button_key == "gift_gold":
                                            if campaign_faction_state[player_faction]["gold"] >= 100:
                                                self.grand.give_faction_gift(player_faction, faction, "gold")
                                        elif button_key == "gift_supply":
                                            if campaign_faction_state[player_faction]["supply"] >= 100:
                                                self.grand.give_faction_gift(player_faction, faction, "supply")
                                        elif button_key == "diplomacy_status":
                                            offer = True
                                            if campaign_faction_state[player_faction]["diplomacy"][faction]["offer"]:
                                                # remove ally offer
                                                offer = False
                                            self.grand.offer_faction_ally(player_faction, faction, offer)
                                        self.draw_card_list_to_ui \
                                            ([item for item in campaign_faction_state if item not in
                                              ("free", player_faction)])
                                    else:
                                        text_popup = self.text_popup
                                        grab_text = self.grab_text
                                        if button_key == "gift_gold":
                                            text_popup.popup(cursor.rect,
                                                             (grab_text(("ui", "info_text_gift_gold")), "",
                                                              grab_text(("ui", "info_text_gift_gold_description"))),
                                                             width_text_wrapper=self.max_description_box_width)
                                            self.add_to_outer_ui_menu_updater(text_popup)
                                        elif button_key == "gift_supply":
                                            text_popup.popup(cursor.rect,
                                                             (grab_text(("ui", "info_text_gift_supply")), "",
                                                              grab_text(("ui", "info_text_gift_supply_description"))),
                                                             width_text_wrapper=self.max_description_box_width)
                                            self.add_to_outer_ui_menu_updater(text_popup)
                                        elif button_key == "diplomacy_status":
                                            text_popup.popup(cursor.rect,
                                                             (grab_text(("ui", "info_text_offer_ally")), "",
                                                              grab_text(("ui", "info_text_offer_ally_description"))),
                                                             width_text_wrapper=self.max_description_box_width)
                                            self.add_to_outer_ui_menu_updater(text_popup)
                                        elif button_key == "diplomacy_value":
                                            faction = [item for item in campaign_faction_state if
                                                       item not in ("free", player_faction)][index]

                                            value_text = [grab_text(("ui", "info_text_diplomacy_value")), "",
                                                          grab_text(("ui", "info_header_diplomacy_value")) +
                                                          str(campaign_faction_state[faction]["diplomacy"][
                                                                  player_faction]["value"]), "",
                                                          ]
                                            # merge same event type together for show
                                            history_value = {}
                                            for history in campaign_faction_state[faction]["diplomacy"][
                                                player_faction]["history"]:
                                                if history[0] not in history_value:
                                                    history_value[history[0]] = history[1]
                                                else:
                                                    history_value[history[0]] += history[1]
                                            for history, history_value in history_value.items():
                                                value_text.append(" -" + grab_text(("diplomacy_event", history,
                                                                                    "Name")) + ": " + str(history_value))

                                            text_popup.popup(cursor.rect, value_text,
                                                             width_text_wrapper=self.max_description_box_width)
                                            self.add_to_outer_ui_menu_updater(text_popup)
                                        elif button_key == "portrait":
                                            text_popup.popup(cursor.rect,
                                                             grab_text(("faction", tuple(self.card_list.keys())[index],
                                                                        "Name")))
                                            self.add_to_outer_ui_menu_updater(text_popup)
                                    break
                            break
        elif cursor.event:
            self.remove_from_outer_ui_menu_updater(grand.diplomacy_management_uis)


class PresetArmyReserveList(GrandListUI, UIOuterGrand):
    def __init__(self, pos):
        self._layer = 5
        UIOuterGrand.__init__(self)
        self.character_list = self.grand.character_list
        self.image = Surface((800 * self.screen_scale_width, 1080 * self.screen_scale_height))
        self.rect = self.image.get_rect(topright=pos)
        GrandListUI.__init__(self)
        self.font = self.game.large_generic_ui_font
        self.image.fill((240, 240, 240))
        self.base_image = self.image.copy()

        self.empty_card_image = Surface((800 * self.screen_scale_width, 200 * self.screen_scale_height))
        self.empty_card_image.fill((239, 238, 176))
        draw.rect(self.empty_card_image, (0, 0, 0), self.empty_card_image.get_rect(),
                  width=int(10 * self.screen_scale_height))

        self.new_preset_card_image = self.empty_card_image.copy()
        self.new_preset_card_image.blit(self.grand_ui_images["reserve_preset_new"],
                                        self.grand_ui_images["reserve_preset_new"].get_rect(
                                            center=self.new_preset_card_image.get_rect().center))

        delete_button = self.grand_ui_images["reserve_preset_delete"]
        copy_button = self.grand_ui_images["reserve_preset_copy"]

        card_image_center_y = self.empty_card_image.get_height() / 2

        default_portrait = self.character_portraits["default"]["mini"]["right"]
        self.card_button_rects = {"commander": default_portrait.get_rect(midleft=(30 * self.screen_scale_width, card_image_center_y)),
                                  "leader1": default_portrait.get_rect(
                                      midleft=(150 * self.screen_scale_width, card_image_center_y)),
                                  "leader2": default_portrait.get_rect(
                                      midleft=(250 * self.screen_scale_width, card_image_center_y)),
                                  "leader3": default_portrait.get_rect(
                                      midleft=(350 * self.screen_scale_width, card_image_center_y)),
                                  "delete": delete_button.get_rect(center=(580 * self.screen_scale_width,
                                                                           card_image_center_y)),
                                  "copy": copy_button.get_rect(center=(700 * self.screen_scale_width,
                                                                       card_image_center_y))}
        for button, button_rect in self.card_button_rects.items():
            if button in ("delete", "copy"):
                self.empty_card_image.blit(self.grand_ui_images["reserve_preset_" + button], button_rect)
            else:
                self.empty_card_image.blit(self.character_portraits["empty"]["mini"]["right"], button_rect)

        self.max_row = 6
        self.max_row_show = 1  # trick the scroller to use additional row instead of total

        self.card_rects = [self.empty_card_image.get_rect(midleft=(0, (100 + (200 * y)) * self.screen_scale_height)) for
                           y in range(self.max_row)]

        self.card_list = {}
        self.showing_army = None

    def create_cards_surface(self):
        self.card_list = {}
        campaign_faction_state = self.grand.current_campaign_state["faction"]
        player_reserve_army_list = ["new"] + campaign_faction_state[self.grand.player_faction]["reserve"]
        self.total_row = ceil((len(player_reserve_army_list) + 1) / (len(self.card_rects) - 1))
        if self.total_row == 1:
            self.total_row = 0
        self.scroll_total_row = self.total_row + 1
        if self.current_row > self.total_row:
            self.current_row = self.total_row

        for army in player_reserve_army_list:
            self.create_army_card(army)

        self.draw_card_list_to_ui([army.game_id if army != "new" else army for army in player_reserve_army_list],
                                  (self.showing_army, ))

    def create_army_card(self, army):
        """Create card image for new faction"""
        if army == "new":
            card_id = army
            card_image = self.new_preset_card_image
        else:
            card_id = army.game_id
            character_rect = {}
            for character_header in ("commander", "leader1", "leader2", "leader3"):
                if character_header == "commander":
                    character = army.commander_id
                else:
                    char_index = int(character_header[-1]) - 1
                    character = None
                    if char_index < len(army.army_followers["leader"]) and army.army_followers["leader"][char_index]:
                        character = army.army_followers["leader"][char_index][0]

                if character:
                    character_rect[character_header] = character

            card_image = self.empty_card_image.copy()

            for character_header, character in character_rect.items():
                if not character:
                    character = "empty"
                card_image.blit(self.character_portraits[character]["mini"]["right"],
                                self.card_button_rects[character_header])

        selected_card = card_image.copy()
        draw.rect(selected_card, (120, 120, 240), selected_card.get_rect(),
                  width=int(10 * self.screen_scale_height))

        self.card_list[card_id] = (card_image, selected_card)

    def reset(self):
        GrandListUI.reset(self)
        self.showing_army = None

    def update(self, dt):
        grand = self.grand
        cursor = self.cursor
        if UIOuterGrand.update(self, dt):
            player_reserve_army_list = grand.current_campaign_state["faction"][grand.player_faction]["reserve"]
            if cursor.scroll_up:
                if self.current_row > 0:
                    self.current_row -= 1
                    self.scroll.change_image(self.current_row, self.scroll_total_row)
                    self.draw_card_list_to_ui(["new"] + [army.game_id for army in player_reserve_army_list],
                                              (self.showing_army, ))
            elif cursor.scroll_down:
                if self.current_row < self.total_row:
                    self.current_row += 1
                    self.scroll.change_image(self.current_row, self.scroll_total_row)
                    self.draw_card_list_to_ui(["new"] + [army.game_id for army in player_reserve_army_list],
                                              (self.showing_army, ))
            else:
                text_popup = self.text_popup
                grab_text = self.grab_text
                inside_mouse_pos = Vector2(
                    (cursor.pos[0] - self.rect.topleft[0]),
                    (cursor.pos[1] - self.rect.topleft[1]))

                for rect_index, rect in enumerate(self.card_rects):
                    if rect.collidepoint(inside_mouse_pos) and rect_index + self.current_row < len(self.card_list):
                        index = rect_index + self.current_row
                        inside_card_mouse_pos = Vector2(
                            (inside_mouse_pos[0] - rect.topleft[0]),
                            (inside_mouse_pos[1] - rect.topleft[1]))
                        if index:
                            hover_over_army = player_reserve_army_list[index - 1]
                            for button_key, button_rect in self.card_button_rects.items():
                                if button_rect.collidepoint(inside_card_mouse_pos):
                                    if self.event_press:
                                        if button_key == "delete":
                                            if hover_over_army.game_id == self.showing_army:
                                                grand.player_grand_reserve_army_setup_ui.showing_army = None
                                                self.showing_army = None
                                                grand.player_grand_reserve_army_setup_ui.reset(active=False)
                                                grand.player_reserve_army_title.change_text("", 0, 0, 0)
                                            hover_over_army.remove_army_from_reserve()
                                            self.create_cards_surface()
                                            return
                                        elif button_key == "copy":
                                            copy_commander = hover_over_army.commander_id
                                            if self.character_list[copy_commander]["Is Unique"]:
                                                copy_commander = ""
                                            copy_army_followers = hover_over_army.army_followers.copy()
                                            for index, leader in enumerate(copy_army_followers["leader"]):
                                                if self.character_list[leader]["Is Unique"]:
                                                    copy_army_followers["leader"][index] = []
                                            hover_over_army = Army(str(uuid4()), grand.player_faction, hover_over_army.culture,
                                                                   copy_commander, hover_over_army.army_followers)
                                            player_reserve_army_list.insert(0, hover_over_army)
                                            self.create_cards_surface()
                                            return
                                    else:
                                        if index:
                                            if button_key == "delete":
                                                text_popup.popup(cursor.rect,
                                                                 (grab_text(("ui", "info_text_delete_reserve")), "",
                                                                  grab_text(("ui", "info_text_delete_reserve_description"))),
                                                                 width_text_wrapper=self.max_description_box_width)
                                                self.add_to_outer_ui_menu_updater(text_popup)
                                            elif button_key == "copy":
                                                text_popup.popup(cursor.rect,
                                                                 (grab_text(("ui", "info_text_copy_reserve")), "",
                                                                  grab_text(("ui", "info_text_copy_reserve_description"))),
                                                                 width_text_wrapper=self.max_description_box_width)
                                                self.add_to_outer_ui_menu_updater(text_popup)
                                            elif button_key == "commander":
                                                if hover_over_army.commander_id:
                                                    text_popup.popup(cursor.rect,
                                                                     (grab_text(("ui", "info_header_commander")) +
                                                                     grab_text(("character", hover_over_army.commander_id, "Name"))),
                                                                     width_text_wrapper=self.max_description_box_width)
                                                    self.add_to_outer_ui_menu_updater(text_popup)
                                            else:
                                                index = int(button_key[-1]) - 1
                                                if hover_over_army.army_followers["leader"][index]:
                                                    text_popup.popup(cursor.rect,
                                                                     (grab_text(("ui", "info_header_leader")) +
                                                                     grab_text(("character", hover_over_army.army_followers["leader"][index][0], "Name"))),
                                                                     width_text_wrapper=self.max_description_box_width)
                                                    self.add_to_outer_ui_menu_updater(text_popup)

                            if self.event_press:
                                # click at card itself
                                grand.player_grand_reserve_army_setup_ui.showing_army = hover_over_army.game_id
                                self.showing_army = hover_over_army.game_id
                                self.create_cards_surface()
                                grand.player_grand_reserve_army_setup_ui.reset(active=True)
                                grand.player_grand_reserve_army_setup_ui.popup("", hover_over_army)
                                grand.player_reserve_army_title.change_text("", hover_over_army.cost,
                                                                            hover_over_army.total_supply_usage,
                                                                            hover_over_army.leadership)
                        else:
                            if self.event_press:  # click at first new army card, create new reserve army
                                hover_over_army = Army(str(uuid4()), grand.player_faction, "", "",
                                                       {"leader": [[], [], []],
                                                        "troop": [[], [], [], [], []],
                                                        "air": [[], [], [], [], []]})
                                player_reserve_army_list.insert(0, hover_over_army)

                                self.create_cards_surface()
                                grand.player_grand_reserve_army_setup_ui.showing_army = hover_over_army.game_id
                                self.showing_army = hover_over_army.game_id
                                grand.player_grand_reserve_army_setup_ui.reset(active=True)
                                grand.player_grand_reserve_army_setup_ui.popup("", hover_over_army)
                                grand.player_reserve_army_title.change_text("", 0, 0, 0)
                                self.scroll.change_image(self.current_row, self.scroll_total_row)
                            else:
                                text_popup.popup(cursor.rect,
                                                 (grab_text(("ui", "info_text_new_reserve"))),
                                                 width_text_wrapper=self.max_description_box_width)
                                self.add_to_outer_ui_menu_updater(text_popup)

                        self.draw_card_list_to_ui(["new"] + [army.game_id for army in player_reserve_army_list],
                                                  (self.showing_army,))
                        return
        elif (cursor.event and not grand.player_grand_reserve_army_setup_ui.rect.collidepoint(cursor.pos) and
              not grand.player_grand_character_selector_ui.rect.collidepoint(cursor.pos)):
            self.remove_from_outer_ui_menu_updater(grand.player_army_reserve_setup_uis)


class PresetArmyReserveSetup(PresetArmySetupUI, UIOuterGrand):
    # disable player keyboard input for grand

    def __init__(self, pos, layer=10):
        """UI for setting up reserve preset army setup"""
        self._layer = layer
        UIOuterGrand.__init__(self)
        PresetArmySetupUI.__init__(self, pos, True)
        self.showing_army = None

    def change_portrait_selection(self, character_type, new_index):
        self.selected_portrait_index = (character_type, new_index)
        self.reset()
        self.grand.player_grand_character_selector_ui.add(character_type)

    def change_character(self, slot, character, change_selector=False, reset_now=False):
        grand = self.grand
        player_faction_state = grand.current_campaign_state["faction"][grand.player_faction]
        for army in player_faction_state["reserve"]:
            if army.game_id == self.showing_army:
                old_character = None
                if "Commander" in slot:
                    slot = "Commander"
                self.army_preset[slot] = character

                role = slot.lower().split(" ")[0]

                if role == "commander":
                    if army.commander_id:
                        old_character = army.commander_id
                    army.commander_id = character
                else:
                    index = int(slot.split(" ")[-1]) - 1
                    if army.army_followers[role] and army.army_followers[role][index]:
                        old_character = army.army_followers[role][index][0]
                    army.army_followers[role][index] = [character, False]

                if role in ("commander", "leader"):  # redraw reserve army list
                    grand.player_grand_reserve_army_list_ui.create_cards_surface()

                army.reset_stat()
                grand.player_reserve_army_title.change_text("", army.cost, army.total_supply_usage,
                                                            army.leadership)

                if character != old_character:
                    if character in player_faction_state["character"]:
                        player_faction_state["character"][character] = (army, role)
                    if old_character:
                        player_faction_state["character"][old_character] = (None, "courtier")

                if reset_now:
                    self.reset()
                else:
                    index = 0
                    if "Commander" not in slot:
                        index = int(slot.split(" ")[1]) - 1
                    if character:
                        self.image.blit(self.character_portraits[character]["setup_ui"],
                                        self.portrait_type_rects[slot.split(" ")[0].lower()][index])
                return

    def reset(self, active=True):
        self.image.fill((100, 100, 100))
        if active:
            self.pause = False
            for header in self.army_header:
                character_type = header.split(" ")[0].lower()
                index = 0
                if header != "Commander":
                    index = int(header.split(" ")[1]) - 1
                character = self.army_preset[header]
                rect = self.portrait_type_rects[character_type][index]
                self.image.blit(self.circle, self.portrait_type_rects[character_type][index])

                if self.selected_portrait_index and self.selected_portrait_index == (character_type, index):
                    self.image.blit(self.selected_circle, rect)
                if character:
                    self.image.blit(self.character_portraits[character]["setup_ui"], rect)
        else:
            self.pause = True

        self.preset_cost = self.game.showcase_army.cost
        self.preset_supply = self.game.showcase_army.total_supply_usage
        self.preset_leadership = self.game.showcase_army.leadership

    def update(self, dt):
        grand = self.grand
        cursor = self.cursor
        if not self.input_delay:
            if not self.pause:
                for key, pressed in grand.player_key_hold.items():
                    if pressed and key in self.key_hold_method:
                        self.key_hold_method[key]()
                        self.input_delay = 0.15
        else:
            self.input_delay -= dt
            if self.input_delay < 0:
                self.input_delay = 0

        if UIOuterGrand.update(self, dt):
            inside_mouse_pos = Vector2(
                (cursor.pos[0] - self.rect.topleft[0]),
                (cursor.pos[1] - self.rect.topleft[1]))
            for character_type in ("commander", "leader", "troop", "air"):
                for index, rect in enumerate(self.portrait_type_rects[character_type]):
                    if rect.collidepoint(inside_mouse_pos):
                        if self.event_press:
                            self.change_portrait_selection(character_type, index)
                        elif self.event_alt_press:
                            if character_type == "commander":
                                character = self.army_preset["Commander"]
                                self.army_preset["Commander"] = None
                            else:
                                character = self.army_preset[character_type.capitalize() + " " + str(index + 1)]
                                self.army_preset[character_type.capitalize() + " " + str(index + 1)] = None
                            for army in grand.current_campaign_state["faction"][grand.player_faction]["reserve"]:
                                if army.game_id == self.showing_army:
                                    army.remove_follower(character_type, character)
                                    break
                            if character_type in ("commander", "leader"):
                                grand.player_grand_reserve_army_list_ui.create_cards_surface()
                            self.change_portrait_selection(character_type, index)

                        if character_type == "commander":
                            character = self.army_preset[character_type.capitalize()]
                        else:
                            character = self.army_preset[character_type.capitalize() + " " + str(index + 1)]

                        if character:
                            character_name_text = self.grab_text(("character", character, "Name"))
                        else:
                            character_name_text = self.grab_text(("ui", "info_text_empty_" + character_type))
                            if character_type == "commander":
                                character_name_text = (character_name_text,
                                                       self.grab_text(("ui", "warn_grand_no_commander")))
                            else:
                                character_name_text = (character_name_text,
                                                       self.grab_text(("ui", "warn_empty_slot")))

                        self.text_popup.popup(cursor.rect, character_name_text)
                        self.add_to_outer_ui_menu_updater(self.text_popup)
                        return

        elif (cursor.event and not grand.player_grand_character_selector_ui.rect.collidepoint(cursor.pos) and
              not grand.player_grand_reserve_army_list_ui.rect.collidepoint(cursor.pos)):
            self.remove_from_outer_ui_menu_updater(grand.player_army_reserve_setup_uis)


class PresetArmyGrandCharacterSelector(CharacterSelector, UIOuterGrand):
    def __init__(self, pos, layer=10):
        """UI for setting up reserve preset army setup"""
        self._layer = layer
        UIOuterGrand.__init__(self)
        CharacterSelector.__init__(self, pos)
        self.scroll.kill()  # remove UIMenu scroll
        self.scroll = OuterGrandUIScroll(self, self.rect.topright)

    def add(self, character_type):
        grand = self.grand
        true_selector_character_list = ()
        player_faction_state = grand.current_campaign_state["faction"][grand.player_faction]
        if character_type in ("commander", "leader"):
            selector_character_list = player_faction_state["recruit"]["leader"].copy()
            # add unique hero
            print(player_faction_state["character"])
            selector_character_list += [character for character, character_state in
                                        player_faction_state["character"].items() if not character_state[0] and
                                        self.character_list[character]["Is Leader"]]
            if character_type == "commander":  # exclude leader that cannot be commander
                selector_character_list = [value for value in selector_character_list
                                           if not self.character_list[value]["No Commander"]]

            # sort characters, based on unique leader, common leader
            true_selector_character_list = [item for item in selector_character_list if
                                            self.character_list[item]["Is Unique"]]
            true_selector_character_list += [item for item in selector_character_list if
                                             self.character_list[item]["Is Leader"] and item not in true_selector_character_list]
        elif character_type:  # ground or air troop
            true_selector_character_list = player_faction_state["recruit"][character_type].copy()

        self.selector_character_list = true_selector_character_list

        additional_character = len(self.selector_character_list) - self.max_total_character_show
        if additional_character < 0:
            additional_character = 0
        self.total_row = ceil(additional_character / 6)
        self.scroll_total_row = self.total_row + 1
        self.current_row = 0  # reset showing row
        self.scroll.change_image(self.current_row, self.scroll_total_row)
        self.add_character()

    def update(self, dt):
        grand = self.grand
        cursor = self.cursor
        if UIOuterGrand.update(self, dt):
            if cursor.scroll_up:
                if self.current_row > 0:
                    self.current_row -= 1
                    self.scroll.change_image(self.current_row, self.scroll_total_row)
                    self.add_character()
            elif cursor.scroll_down:
                if self.current_row < self.total_row:
                    self.current_row += 1
                    self.scroll.change_image(self.current_row, self.scroll_total_row)
                    self.add_character()

            inside_mouse_pos = Vector2(
                (cursor.pos[0] - self.rect.topleft[0]),
                (cursor.pos[1] - self.rect.topleft[1]))
            start_index = (self.current_row * 6)
            for index, rect in enumerate(self.portrait_rects):
                if rect.collidepoint(inside_mouse_pos):
                    shown_index = index + start_index
                    if shown_index < len(self.selector_character_list):
                        character_id = self.selector_character_list[shown_index]
                        character_data = self.character_list[character_id]
                        if self.event_press:
                            player_grand_reserve_army_setup_ui = grand.player_grand_reserve_army_setup_ui
                            selected_portrait = player_grand_reserve_army_setup_ui.selected_portrait_index
                            player_grand_reserve_army_setup_ui.change_character(selected_portrait[0].capitalize() + " " +
                                                                                str(selected_portrait[1] + 1),
                                                                                character_id)
                            if selected_portrait[0] in ("leader", "commander"):
                                self.add(selected_portrait[0])  # reset character list to update hero adding if any
                        elif self.event_alt_press:  # remove character from reserved army
                            pass

                        else:
                            char_stat = self.grab_character_stat_text(character_id, character_data)

                            self.text_popup.popup(cursor.rect, char_stat,
                                                  width_text_wrapper=int(1400 * self.screen_scale_width))

                            self.add_to_outer_ui_menu_updater(self.text_popup)

                    return
        elif (cursor.event and not grand.player_grand_reserve_army_setup_ui.rect.collidepoint(cursor.pos) and
              not grand.player_grand_reserve_army_list_ui.rect.collidepoint(cursor.pos)):
            self.remove_from_outer_ui_menu_updater(grand.player_army_reserve_setup_uis)


class PlayerFactionTechBar(UIOuterGrand):
    def __init__(self):
        self._layer = 5
        UIOuterGrand.__init__(self)
        self.image = Surface((600 * self.screen_scale_width, 80 * self.screen_scale_height), SRCALPHA)
        self.font = self.game.generic_ui_font

    def update(self, dt):
        pass


class CultureManagement(GrandListUI, UIOuterGrand):
    add_culture_portrait = PlayerFactionCultureList.add_culture_portrait
    get_culture_stat = PlayerFactionCultureList.get_culture_stat

    def __init__(self):
        self._layer = 5

        UIOuterGrand.__init__(self)
        self.font = self.game.medium_generic_ui_font
        self.value_text_font_cache = self.game.font_text_cache[self.font]
        self.culture_coas = self.grand.culture_coas
        self.image = Surface((1800 * self.screen_scale_width, 1500 * self.screen_scale_height))
        self.image.fill((150, 150, 150))

        self.info_button_rect = self.grand_ui_images["info"].get_rect(topright=(
            self.image.get_width() - (100 * self.screen_scale_width), 0))
        self.image.blit(self.grand_ui_images["info"], self.info_button_rect)

        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(center=self.screen_center)
        GrandListUI.__init__(self)
        self.empty_card_image = Surface((2000 * self.screen_scale_width, 250 * self.screen_scale_height))
        self.empty_card_image.fill((200, 200, 200))
        draw.rect(self.empty_card_image, (110, 0, 0), self.empty_card_image.get_rect(),
                  width=int(10 * self.screen_scale_height))
        card_center_y = self.empty_card_image.get_rect().centery

        self.card_button_rects = {"portrait": self.culture_coas["default"]["tiny"].get_rect(
            midleft=(100 * self.screen_scale_width, card_center_y))}
        self.card_button_rects |= {
            policy: self.grand_ui_images["policy_" + policy].get_rect(center=(
                ((200 * (index + 1)) + 600) * self.screen_scale_width, card_center_y))
            for index, policy in enumerate(Culture_Policy_Integration.keys())}
        selected_policy_size = self.card_button_rects[tuple(self.card_button_rects.keys())[-1]].size
        self.selected_policy_image = Surface((selected_policy_size[0] * 1.2, selected_policy_size[1] * 1.2), SRCALPHA)
        draw.circle(self.selected_policy_image, (255, 255, 255), self.selected_policy_image.get_rect().center,
                    self.selected_policy_image.get_width() / 2)

        self.max_row = 5
        self.max_row_show = 1  # trick the scroller to use additional row instead of total

        self.card_rects = [self.empty_card_image.get_rect(topleft=(0, (250 + (100 * y)) * self.screen_scale_height)) for
                           y in range(self.max_row)]

    def create_cards_surface(self):
        self.card_list = {}
        faction_culture_state = self.grand.current_campaign_state["faction"][self.grand.player_faction]["culture"]
        self.total_row = ceil(len(faction_culture_state) / (len(self.card_rects) - 1))
        if self.total_row == 1:
            self.total_row = 0
        self.scroll_total_row = self.total_row + 1
        if self.current_row > self.total_row:
            self.current_row = self.total_row

        for culture, culture_state in faction_culture_state.items():
            self.create_culture_card(culture, culture_state)
        self.draw_card_list_to_ui(faction_culture_state)

    def create_culture_card(self, culture, culture_state):
        """Create card image for culture"""
        card_image = self.empty_card_image.copy()

        for key, rect in self.card_button_rects.items():
            if key == "portrait":
                culture_value = self.get_culture_stat(culture, self.grand.current_campaign_state["faction"][self.grand.player_faction])
                self.add_culture_portrait(card_image, culture, culture_value, rect.topleft)
                # card_image.blit(self.culture_coas[culture]["culture_ui"], rect)
            else:
                if culture_state["policy"] == key:  # add selected image
                    card_image.blit(self.selected_policy_image, self.selected_policy_image.get_rect(center=rect.center))
                card_image.blit(self.grand_ui_images["policy_" + key], rect)

        self.card_list[culture] = (card_image, card_image)

    def update(self, dt):
        if UIOuterGrand.update(self, dt):
            cursor = self.cursor
            grand = self.grand
            if cursor.scroll_up:
                if self.current_row > 0:
                    self.current_row -= 1
                    self.scroll.change_image(self.current_row, self.scroll_total_row)
                    self.draw_card_list_to_ui(grand.current_campaign_state["faction"][grand.player_faction]["culture"])
            elif cursor.scroll_down:
                if self.current_row < self.total_row:
                    self.current_row += 1
                    self.scroll.change_image(self.current_row, self.scroll_total_row)
                    self.draw_card_list_to_ui(grand.current_campaign_state["faction"][grand.player_faction]["culture"])
            else:
                inside_mouse_pos = Vector2(
                    (cursor.pos[0] - self.rect.topleft[0]),
                    (cursor.pos[1] - self.rect.topleft[1]))
                if self.info_button_rect.collidepoint(inside_mouse_pos):
                    text_popup = self.text_popup
                    grab_text = self.grab_text
                    text_popup.popup(cursor.rect,
                                     (grab_text(("ui", "info_text_culture_management")), "",
                                      grab_text(("ui", "info_text_culture_management_description")), "",
                                      grab_text(("ui", "info_text_culture_management_description2"))),
                                     width_text_wrapper=self.max_description_box_width)
                    self.add_to_outer_ui_menu_updater(text_popup)
                else:
                    for rect_index, rect in enumerate(self.card_rects):
                        index = rect_index + self.current_row
                        inside_card_mouse_pos = Vector2(
                            (inside_mouse_pos[0] - rect.topleft[0]),
                            (inside_mouse_pos[1] - rect.topleft[1]))
                        for button_key, button_rect in self.card_button_rects.items():
                            if button_rect.collidepoint(inside_card_mouse_pos):
                                if self.event_press:
                                    if button_key not in ("portrait", "info"):
                                        player_state_culture = grand.current_campaign_state["faction"][grand.player_faction]["culture"]
                                        culture = tuple(player_state_culture.keys())[index]
                                        if player_state_culture[culture]["policy"] != button_key:
                                            player_state_culture[culture]["policy"] = button_key
                                            grand.player_faction_culture_list_ui.culture_change()
                                            self.create_culture_card(culture, player_state_culture[culture])
                                            self.draw_card_list_to_ui(
                                                grand.current_campaign_state["faction"][grand.player_faction]["culture"])
                                else:
                                    text_popup = self.text_popup
                                    grab_text = self.grab_text
                                    if button_key == "portrait":
                                        player_state_culture = \
                                        grand.current_campaign_state["faction"][grand.player_faction]["culture"]
                                        culture = tuple(player_state_culture.keys())[index]
                                        text_popup.popup(cursor.rect,
                                                         (grab_text(("culture", culture, "Name")), "",
                                                          grab_text(("culture", culture, "Description"))),
                                                         width_text_wrapper=self.max_description_box_width)
                                        self.add_to_outer_ui_menu_updater(text_popup)
                                    else:
                                        text_popup.popup(cursor.rect,
                                                         (grab_text(("ui", "info_text_culture_" + button_key)), "",
                                                          grab_text(("ui", "info_text_culture_" + button_key + "_description")), "",
                                                          grab_text(("ui", "info_header_integration_capacity")) +
                                                                     str(convert_modifier_number_to_percent_text(Culture_Policy_Integration[button_key]) + "%")),
                                                         width_text_wrapper=self.max_description_box_width)

                                        self.add_to_outer_ui_menu_updater(text_popup)
                                return
                        return

        elif self.cursor.event:
            self.remove_from_outer_ui_menu_updater(self.grand.culture_management_uis)


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
        # TODO add copy for reserve button
        if UIOuterGrand.update(self, dt):
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

        self.unavailable_building_icon = self.building_portraits["unavailable"]["building_ui"]
        default_build_image_slot = self.building_portraits["default"]["building_ui"]
        self.building_slot_rects = ([default_build_image_slot.get_rect(
            center=(1000 * self.screen_scale_width, 500 * self.screen_scale_height))] +
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
        self.before_selected_image = self.base_image.copy()

    def add_building_icon(self, index, building_state):
        if building_state[0] in self.building_portraits:
            building_icon = self.building_portraits[building_state[0]]["building_ui"]
        else:
            building_icon = self.building_portraits["default"]["building_ui"]

        self.image.blit(building_icon, self.building_slot_rects[index])
        additional_building_type_file_head = ""
        if self.building_list[building_state[0]]["Type"] == "unique":
            additional_building_type_file_head = "unique_"
        if building_state[1] is not True or building_state[2]:
            if not building_state[1]:  # damaged building
                self.image.blit(self.building_portraits[additional_building_type_file_head + "damaged"]["building_ui"],
                                self.building_slot_rects[index])

            if building_state[2]:  # building on progress with something
                self.image.blit(self.building_portraits[additional_building_type_file_head + "progress"]["building_ui"],
                                self.building_slot_rects[index])
                if building_state[1] == "raze":
                    self.image.blit(self.building_portraits["unavailable_raze"]["building_ui"],
                                    self.building_slot_rects[index])
                elif building_state[1] == "pillage":
                    self.image.blit(self.building_portraits["unavailable_pillage"]["building_ui"],
                                    self.building_slot_rects[index])
                else:  # repair
                    self.image.blit(self.building_portraits["unavailable_repair"]["building_ui"],
                                    self.building_slot_rects[index])

                turn_left = self.header_font.render(str(building_state[2]), True, (255, 255, 255))
                self.image.blit(turn_left, turn_left.get_rect(midbottom=self.building_slot_rects[index].midbottom))

    def change_selected_region(self, region):
        if self.player_selected_region != region:
            self.selected_building_index = None
            self.player_selected_region = region
            self.remove_from_outer_ui_menu_updater(self.grand.building_management_ui)

        self.building_button_rects = {}
        self.appear_repair_button = False
        self.appear_raze_button = False
        self.appear_pillage_button = False

        if region:
            self.image = self.base_image.copy()
            for index, building in enumerate(self.grand.current_campaign_state["region"][region]["building"]):
                self.add_building_icon(index, building)

            region_name_surface = text_render_with_bg(self.grab_text(("region", region, "Name")), self.header_font)
            self.image.blit(region_name_surface, region_name_surface.get_rect(midtop=(
                250 * self.screen_scale_width, 10 * self.screen_scale_height)))

            self.before_selected_image = self.image.copy()
            self.update_region_stat()
            if self.selected_building_index is not None:
                self.change_selected_building(self.selected_building_index)
            self.add_to_outer_ui_menu_updater(self.grand.player_region_management_uis)
        else:
            self.remove_from_outer_ui_menu_updater(self.grand.player_region_management_uis)

    def update_region_stat(self):
        region = self.player_selected_region
        campaign_region_state = self.grand.current_campaign_state["region"]
        resource = campaign_region_state[region]["income"]
        culture = campaign_region_state[region]["culture"]
        for key, pos in self.resource_text_pos.items():
            text_surface = text_render_with_bg(add_plus_to_number(int(resource[key])), self.font)
            self.image.blit(text_surface, text_surface.get_rect(midleft=pos))

        for index, culture_id in enumerate(culture):
            self.image.blit(self.culture_coas[culture_id]["tiny"], self.culture_coa_rects[index])
            text_surface = text_render_with_bg(add_plus_to_number(int(culture[culture_id])), self.font)
            self.image.blit(text_surface, text_surface.get_rect(bottomright=self.culture_coa_rects[index].bottomright))

    def change_selected_building(self, building_index):
        self.image = self.before_selected_image.copy()
        self.update_region_stat()
        self.building_button_rects = {}
        self.appear_repair_button = False
        self.appear_raze_button = False
        self.appear_pillage_button = False
        if self.selected_building_index is not None:
            # reset previous selected building icon
            self.add_building_icon(self.selected_building_index,
                                   self.grand.current_campaign_state["region"][self.player_selected_region]["building"][
                                       self.selected_building_index])
        self.remove_from_outer_ui_menu_updater(self.grand.building_management_ui)
        building_state = self.grand.current_campaign_state["region"][self.player_selected_region]["building"][
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

    def popup_building_info(self, building):
        building_stat = self.building_list[building]
        grab_text = self.grab_text
        text = [grab_text(("building", building, "Name")), "",
                (grab_text(("ui", "info_header_cost")) + str(building_stat["Cost"]),
                 self.grand_ui_images["gold"]),
                (grab_text(("ui", "info_header_build_time")) + str(building_stat["Build Time"]),
                 self.grand_ui_images["turn"])]

        if building_stat["Precede"]:
            text.append(grab_text(("ui", "info_header_precede")) +
                        grab_text(("building", building_stat["Precede"], "Name")))

        if building_stat["Requirement"]:
            text.append(grab_text(("ui", "info_header_requirement")) + str([
                grab_text(("building", require_building, "Name")) for require_building in
                building_stat["Requirement"]]).replace("'", ""))

        garrison = False
        garrison_text = grab_text(("ui", "info_header_garrison"))
        garrison_count = {}

        for garrison_stat in ("Leader Reinforcement", "Troop Reinforcement", "Air Reinforcement"):
            for item in building_stat[garrison_stat]:
                garrison_count[item] = garrison_count.get(item, 0) + 1

        for key, value in garrison_count.items():
            garrison = True
            garrison_text += grab_text(("character", key, "Name")) + "x" + str(value) + ", "
        if building_stat["Garrison Strategy"]:
            garrison_text += grab_text(("strategy", building_stat["Garrison Strategy"], "Name")) + ", "
            garrison = True
        if garrison:
            text.append(garrison_text[:-2])

        recruit = False
        recruit_text = grab_text(("ui", "info_header_recruit"))
        for recruit_stat in ("Leader Recruit", "Troop Recruit", "Air Recruit"):
            for item in building_stat[recruit_stat]:
                recruit_text += item + ", "
                recruit = True
        if recruit:
            text.append(recruit_text[:-2])

        for other_stat in ("Gold Income", "Supply Income", "Happiness"):
            if building_stat[other_stat]:
                text.append((grab_text(("ui", "info_header_" + other_stat.lower().replace(" ", "_"))) +
                             add_plus_to_number(str(building_stat[other_stat])),
                             self.grand_ui_images[other_stat.lower().split(" ")[0]]))

        if building_stat["Income Boost"]:
            boost_text = [grab_text(("ui", "info_header_income_boost"))]
            for boost_stat, value in building_stat["Income Boost"].items():
                boost_text.append((add_plus_to_number(convert_modifier_number_to_percent_text(value))) + "%")
                boost_text.append(self.grand_ui_images[boost_stat])
                boost_text.append(" ")
            text.append(boost_text)

        if building_stat["Influence"]:
            text.append((grab_text(("ui", "info_header_influence")) +
                         add_plus_to_number(str(building_stat["Influence"])),
                         self.culture_coas[building_stat["Culture"]]["text"]))
        self.text_popup.popup(self.cursor.rect, text,
                              width_text_wrapper=self.max_description_box_width)
        self.add_to_outer_ui_menu_updater(self.text_popup)

    def update(self, dt):
        if UIOuterGrand.update(self, dt):
            grand = self.grand
            current_campaign_state = grand.current_campaign_state
            player_faction = grand.player_faction
            cursor = self.cursor
            inside_mouse_pos = Vector2(
                (cursor.pos[0] - self.rect.topleft[0]),
                (cursor.pos[1] - self.rect.topleft[1]))
            if self.appear_repair_button and self.building_button_rects["repair"].collidepoint(inside_mouse_pos):
                if self.event_press:
                    building_state = current_campaign_state["region"][self.player_selected_region]["building"][
                        self.selected_building_index]
                    building = building_state[0]
                    building_stat = self.building_list[building]
                    if (building_stat["Cost"] <=
                            current_campaign_state["faction"][player_faction]["gold"]):
                        grand.start_building_construction_or_repair(player_faction,
                                                                    self.player_selected_region,
                                                                    self.selected_building_index,
                                                                    building)
                else:
                    self.text_popup.popup(cursor.rect.bottomright,
                                          (self.grab_text(("ui", "info_text_repair")), "",
                                           self.grab_text(("ui", "info_text_repair_description"))),
                                          width_text_wrapper=self.max_description_box_width)
                    self.add_to_outer_ui_menu_updater(self.text_popup)
                return
            elif self.appear_raze_button and self.building_button_rects["raze"].collidepoint(inside_mouse_pos):
                if self.event_press:
                    grand.start_building_raze_or_pillage(player_faction,
                                                         self.player_selected_region,
                                                         self.selected_building_index,
                                                         current_campaign_state["region"][
                                                             self.player_selected_region]["building"][
                                                             self.selected_building_index][0])
                else:
                    self.text_popup.popup(cursor.rect.bottomright,
                                          (self.grab_text(("ui", "info_text_raze")), "",
                                           self.grab_text(("ui", "info_text_raze_description"))),
                                          width_text_wrapper=self.max_description_box_width)
                    self.add_to_outer_ui_menu_updater(self.text_popup)
                return
            elif self.appear_pillage_button and self.building_button_rects["pillage"].collidepoint(inside_mouse_pos):
                if self.event_press:
                    grand.start_building_raze_or_pillage(player_faction, self.player_selected_region,
                                                         self.selected_building_index,
                                                         current_campaign_state["region"][
                                                             self.player_selected_region]
                                                         ["building"][
                                                             self.selected_building_index][0],
                                                         pillage=True)
                else:
                    self.text_popup.popup(cursor.rect.bottomright,
                                          (self.grab_text(("ui", "info_text_pillage")), "",
                                           self.grab_text(("ui", "info_text_pillage_description"))),
                                          width_text_wrapper=self.max_description_box_width)
                    self.add_to_outer_ui_menu_updater(self.text_popup)
                return

            if self.player_selected_region:
                region_buildings = current_campaign_state["region"][self.player_selected_region]["building"]
                for building_index, rect in enumerate(self.building_slot_rects):
                    if rect.collidepoint(inside_mouse_pos) and building_index < len(region_buildings):
                        if self.event_press:
                            self.change_selected_building(building_index)
                        elif self.event_alt_press:
                            region_building_state = region_buildings[building_index]
                            if region_building_state[1] is False or (
                                    region_building_state[1] is True and region_building_state[2]):
                                # stop construction or repair on damaged building
                                grand.cancel_building_construction_or_repair(player_faction,
                                                                             self.player_selected_region,
                                                                             building_index,
                                                                             region_building_state[0])
                            elif region_building_state[1] is not True:  # stop pillaging or razing
                                grand.cancel_building_raze_or_pillage(player_faction,
                                                                      self.player_selected_region,
                                                                      building_index)
                            self.change_selected_building(building_index)
                        else:
                            self.popup_building_info(region_buildings[building_index][0])
                        break


class RegionManagementToggleButton(ToggleButton):
    def __init__(self, images, text, pos):
        ToggleButton.__init__(self, images, text, pos)
        self.rect = self.image.get_rect(bottomleft=pos)

    def update(self, dt):
        ToggleButton.update(self, dt)
        if self.event_press:
            region_management_tab_button = self.grand.region_management_tab_button
            if region_management_tab_button.selected:
                self.selected = True
                region_management_tab_button.selected = False


class ArmyDeployToggleButton(ToggleButton):
    def __init__(self, images, text, pos):
        ToggleButton.__init__(self, images, text, pos)
        self.rect = self.image.get_rect(bottomleft=pos)

    def update(self, dt):
        ToggleButton.update(self, dt)
        if self.event_press:
            army_deploy_tab_button = self.grand.army_deploy_tab_button
            if army_deploy_tab_button.selected:
                self.selected = True
                army_deploy_tab_button.selected = False


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
        self.building_list = self.grand.stat_data.building_list
        self.player_selected_region = None
        self.selected_building_index = None
        self.all_available_building_upgrade = {}
        self.unavailable_building_icon = self.building_portraits["unavailable"]["building_ui"]
        self.image = Surface((0, 0))
        self.building_slot_rects = []
        self.rect = self.image.get_rect(center=self.screen_center)

    def change_selected_building(self, building_index):
        grand = self.grand
        player_faction = grand.player_faction
        self.selected_building_index = building_index
        self.building_slot_rects = []
        building_list = self.building_list
        region_buildings = grand.current_campaign_state["region"][self.player_selected_region]["building"]
        # building is active if it is not damaged, in progress, all requirement buildings are active
        selected_building_state = region_buildings[building_index]

        # show building management for active building
        available_building_upgrade_by_type, self.all_available_building_upgrade = (
            grand.check_region_building_available_upgrade(player_faction, self.player_selected_region,
                                                          selected_building_state[0]))

        if self.all_available_building_upgrade:
            # show building management ui only for active building
            self.add_to_outer_ui_menu_updater(self)

            self.image = Surface((1400 * self.screen_scale_width, sum([
                ceil(len(available_building_list) / 5) for available_building_list in
                available_building_upgrade_by_type.values()]) * 240 * self.screen_scale_height))
            self.rect = self.image.get_rect(midleft=grand.region_management_ui.rect.midright)
            image_width = self.image.get_width()
            building_portraits = self.building_portraits
            culture_coas = self.culture_coas
            prev_bar_rect = None
            for building_type, available_building_list in available_building_upgrade_by_type.items():
                building_bar_image = Surface(
                    (image_width, ceil(len(available_building_list) / 5) * 240 * self.screen_scale_height))
                building_bar_image.fill(self.building_type_bar_colouring[building_type])
                slot_rects = {}
                for building_index, building in enumerate(available_building_list):
                    if building in building_portraits:
                        building_icon = building_portraits[building]["building_ui"]
                    else:
                        building_icon = building_portraits["default"]["building_ui"]
                    col = floor(building_index / 5)
                    row = building_index - (5 * col)
                    rect = building_icon.get_rect(topleft=((20 + (220 * row)) * self.screen_scale_width,
                                                           (20 + (150 * col)) * self.screen_scale_height))
                    slot_rects[building] = rect
                    building_bar_image.blit(building_icon, rect)
                    if not available_building_upgrade_by_type[building_type][building]:
                        building_bar_image.blit(self.unavailable_building_icon, rect)
                    if building_list[building]["Culture"] in culture_coas:
                        culture_coa = culture_coas[building_list[building]["Culture"]]["mini"]
                    else:
                        culture_coa = culture_coas["default"]["mini"]
                    building_bar_image.blit(culture_coa, culture_coa.get_rect(topleft=rect.topleft))
                if not prev_bar_rect:
                    new_bar_rect = building_bar_image.get_rect()
                else:
                    new_bar_rect = building_bar_image.get_rect(topleft=(0, prev_bar_rect.bottomleft[1]))
                self.image.blit(building_bar_image, new_bar_rect)
                self.building_slot_rects.append((new_bar_rect, slot_rects))
                prev_bar_rect = new_bar_rect

            return

        self.remove_from_outer_ui_menu_updater(self)

    def update(self, dt):
        if UIOuterGrand.update(self, dt):
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))

            for bar_rect, building_slot_list in self.building_slot_rects:
                if bar_rect.collidepoint(inside_mouse_pos):
                    grand = self.grand
                    bar_inside_mouse_pos = Vector2((inside_mouse_pos[0] - bar_rect.topleft[0]),
                                                   (inside_mouse_pos[1] - bar_rect.topleft[1]))
                    for building, rect in building_slot_list.items():
                        if rect.collidepoint(bar_inside_mouse_pos):
                            if self.event_press and building in self.all_available_building_upgrade:
                                grand.start_building_construction_or_repair(
                                    grand.player_faction, self.player_selected_region,
                                    grand.region_management_ui.selected_building_index, building)
                                grand.region_management_ui.change_selected_region(self.player_selected_region)
                            else:
                                grand.region_management_ui.popup_building_info(building)
                            return
                    return
