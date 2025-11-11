from copy import deepcopy
from engine.constants import (Custom_Default_Faction, Default_Selected_Map_Custom_Battle,
                              Default_Gold_limit_Custom_Battle, Default_Weather_Custom_Battle,
                              Default_Weather_Strength_Custom_Battle)


def menu_custom_setup(self):
    if self.cursor.select_up or self.esc_press:
        if self.custom_map_bar.adapter.last_click and self.custom_map_bar.adapter.last_click[0] == "click":
            self.custom_battle_map_button.change_state(self.custom_map_list[self.custom_map_bar.adapter.last_click[1]])
            self.selected_custom_map_battle = self.custom_map_list[self.custom_map_bar.adapter.last_click[1]]
            self.custom_map_bar.adapter.last_click = ()

        elif not self.custom_map_bar.mouse_over:  # click somewhere else
            self.remove_ui_updater(self.custom_map_bar)

        if self.custom_weather_strength_bar.adapter.last_click and self.custom_weather_strength_bar.adapter.last_click[0] == "click":
            self.custom_battle_weather_strength_button.change_state(self.custom_weather_strength_list[self.custom_weather_strength_bar.adapter.last_click[1]])
            self.selected_weather_strength_custom_battle = self.custom_weather_strength_bar.adapter.last_click[1]
            self.custom_weather_strength_bar.adapter.last_click = ()

        elif not self.custom_weather_strength_bar.mouse_over:  # click somewhere else
            self.remove_ui_updater(self.custom_weather_strength_bar)

        if self.custom_weather_bar.adapter.last_click and self.custom_weather_bar.adapter.last_click[0] == "click":
            self.custom_battle_weather_type_button.change_state("weather_" + str(self.custom_weather_list[self.custom_weather_bar.adapter.last_click[1]]))
            self.selected_weather_custom_battle = self.custom_weather_list[self.custom_weather_bar.adapter.last_click[1]]
            self.custom_weather_bar.adapter.last_click = ()

        elif not self.custom_weather_bar.mouse_over:  # click somewhere else
            self.remove_ui_updater(self.custom_weather_bar)

        if self.setup_back_button.event_press or self.esc_press:  # back to start_set menu
            self.selected_custom_map_battle = Default_Selected_Map_Custom_Battle
            self.team1_gold_limit_custom_battle = Default_Gold_limit_Custom_Battle
            self.team2_gold_limit_custom_battle = Default_Gold_limit_Custom_Battle
            self.selected_weather_custom_battle = Default_Weather_Custom_Battle
            self.selected_weather_strength_custom_battle = Default_Weather_Strength_Custom_Battle

            self.remove_ui_updater(self.custom_battle_menu_uis)
            self.back_mainmenu()

        elif self.custom_battle_preset_button.event_press:
            self.menu_state = "preset"
            self.before_save_preset_army_setup = deepcopy(self.save_data.custom_army_preset_save)
            self.faction_selector.change_coa(Custom_Default_Faction)
            self.custom_preset_list_box.adapter.__init__()
            self.custom_preset_army_title.change_text("", self.custom_preset_army_setup.total_gold_cost,
                                                      self.custom_preset_army_setup.total_character_number)
            self.add_ui_updater(self.custom_preset_menu_uis)
            self.remove_ui_updater(self.custom_battle_menu_uis)

        elif self.custom_battle_map_button.event_press:  # click on resolution bar
            if self.custom_map_bar in self.ui_updater:  # remove the bar list if click again
                self.remove_ui_updater(self.custom_map_bar)
            else:  # add bar list
                self.add_ui_updater(self.custom_map_bar)
                self.remove_ui_updater((self.custom_weather_strength_bar, self.custom_weather_bar))

        elif self.custom_battle_weather_strength_button.event_press:  # click on resolution bar
            if self.custom_weather_strength_bar in self.ui_updater:  # remove the bar list if click again
                self.remove_ui_updater(self.custom_weather_strength_bar)
            else:  # add bar list
                self.add_ui_updater(self.custom_weather_strength_bar)
                self.remove_ui_updater((self.custom_map_bar, self.custom_weather_bar))

        elif self.custom_battle_weather_type_button.event_press:  # click on resolution bar
            if self.custom_weather_bar in self.ui_updater:  # remove the bar list if click again
                self.remove_ui_updater(self.custom_weather_bar)
            else:  # add bar list
                self.add_ui_updater(self.custom_weather_bar)
                self.remove_ui_updater((self.custom_weather_strength_bar, self.custom_map_bar))

        elif self.custom_battle_team1_gold_button.event_press:
            self.activate_input_popup(("text_input", "custom_gold", 1), "Input total gold for team 1", self.input_popup_uis)

        elif self.custom_battle_team2_gold_button.event_press:
            self.activate_input_popup(("text_input", "custom_gold", 2), "Input total gold for team 2", self.input_popup_uis)

        # elif :
        #     , self.custom_team1_army_buttons,
        #     self.custom_team1_army_button_bars, self.custom_team2_army_buttons,
        #     self.custom_team2_army_button_bars

        elif self.custom_battle_setup_start_battle_button.event_press:
            pass
            # all_ready = True
            # if len([player for player in self.player_char_selectors.values() if player.mode == "empty"]) == 2:  # all empty
            #     all_ready = False
            # else:
            #     for player, item in self.player_char_select.items():
            #         if self.player_char_selectors[player].mode not in ("ready", "empty"):
            #             all_ready = False  # some not ready
            #             break
            # self.mission_selected = "0"
            # if all_ready and self.mission_selected:
            #     self.battle.main_player = 1
            #     if self.player_char_selectors[1].mode == "empty":
            #         self.battle.main_player = 2
            #
            #     self.start_battle(self.mission_selected)
