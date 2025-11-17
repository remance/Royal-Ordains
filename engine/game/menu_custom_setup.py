from copy import deepcopy
from engine.constants import (Custom_Default_Faction, Default_Selected_Map_Custom_Battle,
                              Default_Gold_limit_Custom_Battle, Default_Weather_Custom_Battle,
                              Default_Weather_Strength_Custom_Battle)


def menu_custom_setup(self):
    self.remove_ui_updater(self.custom_army_info_popup, self.custom_army_title_popup)
    for team, team_bars in self.custom_team_army_button_bars.items():
        for index, bar in enumerate(team_bars):
            if bar.mouse_over and bar.hover_index is not None:
                setup_ui = self.custom_battle_team1_setup
                if team == 2:
                    setup_ui = self.custom_battle_team2_setup
                preset_list = self.character_data.preset_list[setup_ui.team_setup[index]["faction"]]
                if setup_ui.team_setup[index]["faction"] in self.save_data.custom_army_preset_save:
                    preset_list = self.save_data.custom_army_preset_save[
                                      setup_ui.team_setup[index]["faction"]] | preset_list
                preset = tuple(preset_list.keys())[bar.hover_index]
                if self.last_shown_custom_army != preset:
                    self.last_shown_custom_army = preset
                    army_preset = self.convert_army_to_deployable(preset_list[preset])
                    self.custom_army_title_popup.change_text(preset_list[preset]["Name"],
                                                             army_preset["cost"], army_preset["total"])
                    self.custom_army_info_popup.popup(army_preset)
                self.add_ui_updater(self.custom_army_info_popup, self.custom_army_title_popup)
                if team == 1:
                    self.custom_army_info_popup.rect.center = self.custom_battle_team2_setup.rect.center
                else:
                    self.custom_army_info_popup.rect.center = self.custom_battle_team1_setup.rect.center
                self.custom_army_title_popup.rect.midbottom = self.custom_army_info_popup.rect.midtop
                break

    for team, team_buttons in self.custom_team_army_buttons.items():
        for index, button in enumerate(team_buttons):
            if button.mouse_over:
                setup_ui = self.custom_battle_team1_setup
                if team == 2:
                    setup_ui = self.custom_battle_team2_setup
                preset_list = self.character_data.preset_list[setup_ui.team_setup[index]["faction"]]
                if setup_ui.team_setup[index]["faction"] in self.save_data.custom_army_preset_save:
                    preset_list = self.save_data.custom_army_preset_save[
                                      setup_ui.team_setup[index]["faction"]] | preset_list
                if button.text in preset_list:  # has preset selected
                    preset = preset_list[tuple(preset_list.keys()).index(button.text)]
                    if self.last_shown_custom_army != preset:
                        self.last_shown_custom_army = preset
                        army_preset = self.convert_army_to_deployable(preset)
                        self.custom_army_title_popup.change_text(preset["Name"],
                                                                 army_preset["cost"], army_preset["total"])
                        self.custom_army_info_popup.popup(army_preset)
                    self.add_ui_updater(self.custom_army_info_popup, self.custom_army_title_popup)
                    if team == 1:
                        self.custom_army_info_popup.rect.center = self.custom_battle_team2_setup.rect.center
                    else:
                        self.custom_army_info_popup.rect.center = self.custom_battle_team1_setup.rect.center
                    self.custom_army_title_popup.rect.midbottom = self.custom_army_info_popup.rect.midtop
                if button.event_press:
                    if self.custom_team_army_button_bars[team][index] in self.ui_updater:
                        self.remove_ui_updater(self.custom_team_army_button_bars[team][index])
                    else:  # add bar list
                        self.add_ui_updater(self.custom_team_army_button_bars[team][index])

                        bar_preset_list = []
                        setup_ui = self.custom_battle_team1_setup
                        if team == 2:
                            setup_ui = self.custom_battle_team2_setup
                        preset_list = self.character_data.preset_list[setup_ui.team_setup[index]["faction"]]
                        if setup_ui.team_setup[index]["faction"] in self.save_data.custom_army_preset_save:
                            preset_list = self.save_data.custom_army_preset_save[
                                              setup_ui.team_setup[index]["faction"]] | preset_list
                        for key, value in preset_list.items():
                            bar_preset_list.append((0, str(value["Name"])))
                        self.custom_team_army_button_bars[team][index].adapter.__init__(bar_preset_list)
                        self.remove_ui_updater([item for item in self.all_custom_battle_bars if
                                                item != self.custom_team_army_button_bars[team][index]])
                return

    if self.cursor.select_up or self.cursor.alt_select_up or self.esc_press:
        for team, team_bars in self.custom_team_army_button_bars.items():
            for index, bar in enumerate(team_bars):
                if bar.adapter.last_click and bar.adapter.last_click[0] == "click":
                    setup_ui = self.custom_battle_team1_setup
                    if team == 2:
                        setup_ui = self.custom_battle_team2_setup
                    preset_list = self.character_data.preset_list[setup_ui.team_setup[index]["faction"]]
                    if setup_ui.team_setup[index]["faction"] in self.save_data.custom_army_preset_save:
                        preset_list = self.save_data.custom_army_preset_save[
                                          setup_ui.team_setup[index]["faction"]] | preset_list
                    preset = tuple(preset_list.keys())[bar.hover_index]
                    army_preset = self.convert_army_to_deployable(preset_list[preset])
                    self.custom_team_army[team][index].__init__(army_preset["ground"], army_preset["air"],
                                                                army_preset["retinue"])
                    self.custom_team_army_buttons[team][index].change_state(
                        bar.adapter.actual_list[bar.adapter.last_click[1]], no_localisation=True)
                    # self.selected_custom_map_battle = self.custom_map_list[self.custom_map_bar.adapter.last_click[1]]
                    bar.adapter.last_click = ()
                    return
                elif not bar.mouse_over:  # click somewhere else
                    self.remove_ui_updater(bar)

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

            self.remove_ui_updater(self.custom_battle_menu_uis_remove)
            for index in range(0, 4):
                self.custom_battle_team1_setup.change_faction(None, index)
                self.custom_battle_team2_setup.change_faction(None, index)
            self.back_mainmenu()

        elif self.custom_battle_preset_button.event_press:
            self.menu_state = "preset"
            self.before_save_preset_army_setup = deepcopy(self.save_data.custom_army_preset_save)
            self.faction_selector.change_coa(Custom_Default_Faction)
            self.custom_preset_army_setup.change_coa(Custom_Default_Faction)
            self.custom_preset_list_box.adapter.__init__()
            self.custom_preset_army_title.change_text("", self.custom_preset_army_setup.total_gold_cost,
                                                      self.custom_preset_army_setup.total_character_number)
            self.add_ui_updater(self.custom_preset_menu_uis)
            self.remove_ui_updater(self.custom_battle_menu_uis_remove)
            for index in range(0, 4):
                self.custom_battle_team1_setup.change_faction(None, index)
                self.custom_battle_team2_setup.change_faction(None, index)

        elif self.custom_battle_map_button.event_press:
            if self.custom_map_bar in self.ui_updater:  # remove the bar list if click again
                self.remove_ui_updater(self.custom_map_bar)
            else:  # add bar list
                self.add_ui_updater(self.custom_map_bar)
                self.remove_ui_updater([item for item in self.all_custom_battle_bars if item != self.custom_map_bar])

        elif self.custom_battle_weather_strength_button.event_press:
            if self.custom_weather_strength_bar in self.ui_updater:  # remove the bar list if click again
                self.remove_ui_updater(self.custom_weather_strength_bar)
            else:  # add bar list
                self.add_ui_updater(self.custom_weather_strength_bar)
                self.remove_ui_updater([item for item in self.all_custom_battle_bars if item != self.custom_weather_strength_bar])

        elif self.custom_battle_weather_type_button.event_press:  # click on resolution bar
            if self.custom_weather_bar in self.ui_updater:  # remove the bar list if click again
                self.remove_ui_updater(self.custom_weather_bar)
            else:  # add bar list
                self.add_ui_updater(self.custom_weather_bar)
                self.remove_ui_updater([item for item in self.all_custom_battle_bars if item != self.custom_weather_bar])

        elif self.custom_battle_team1_gold_button.event_press:
            self.activate_input_popup(("text_input", "custom_gold", 1), "Input total gold for team 1", self.input_popup_uis)

        elif self.custom_battle_team2_gold_button.event_press:
            self.activate_input_popup(("text_input", "custom_gold", 2), "Input total gold for team 2", self.input_popup_uis)

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
