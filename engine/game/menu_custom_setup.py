from copy import deepcopy

from engine.constants import *


def menu_custom_setup(self):
    self.remove_from_ui_menu_updater(self.custom_army_info_popup, self.custom_army_title_popup)
    for team, team_bars in self.custom_team_army_button_bars.items():
        for index, bar in enumerate(team_bars):
            if bar.mouse_over and bar.hover_index is not None:  # hover over
                setup_ui = self.custom_battle_team_setup[team]
                preset_list = self.character_data.custom_army_preset_list[setup_ui.team_setup[index]["culture"]]
                # add player custom army preset list
                if setup_ui.team_setup[index]["culture"] in self.save_data.player_custom_army_preset_save:
                    preset_list = {key: value for key, value in self.save_data.player_custom_army_preset_save[
                        setup_ui.team_setup[index]["culture"]].items() if value["Commander"]} | preset_list
                hover_preset = tuple(preset_list.keys())[bar.hover_index]
                if self.last_shown_custom_army != hover_preset:
                    self.last_shown_custom_army = hover_preset
                    army_preset = self.convert_custom_army_to_deployable(preset_list[hover_preset],
                                                                         setup_ui.team_setup[index]["culture"])
                    self.showcase_army.__init__("", army_preset["culture"],
                                                army_preset["culture"],
                                                army_preset["commander"],
                                                army_preset["followers"])
                    self.custom_army_info_popup.popup(preset_list[hover_preset]["Name"], self.showcase_army)
                self.add_to_ui_menu_updater(self.custom_army_info_popup, self.custom_army_title_popup)
                self.custom_army_info_popup.rect.midright = self.custom_battle_team_setup[
                    Opposite_Team[team]].rect.midright
                self.custom_army_title_popup.rect.midbottom = self.custom_army_info_popup.rect.midtop

                if self.cursor.select_up and bar.adapter.last_click:
                    if bar.adapter.last_click[0] == "click":
                        army_preset = self.convert_custom_army_to_deployable(preset_list[hover_preset],
                                                                             setup_ui.team_setup[index][
                                                                                 "culture"])
                        self.custom_team_army[team][index].__init__("", army_preset["culture"],
                                                                    army_preset["culture"],
                                                                    army_preset["commander"],
                                                                    army_preset["followers"])
                        setup_ui.change_cost(index, self.custom_team_army[team][index].cost,
                                             self.custom_team_army[team][index].total_supply_usage)
                        self.custom_team_army_buttons[team][index].change_state(
                            bar.adapter.actual_list[bar.adapter.last_click[1]], no_localisation=True)
                        bar.adapter.last_click = ()
                return
            elif (self.cursor.select_up or self.cursor.alt_select_up or self.esc_press) and not bar.mouse_over:
                # click somewhere else
                self.remove_from_ui_menu_updater(bar)

    for team, team_buttons in self.custom_team_army_buttons.items():
        for index, button in enumerate(team_buttons):  # hover over
            if button.mouse_over:
                setup_ui = self.custom_battle_team_setup[team]
                preset_list = self.character_data.custom_army_preset_list[setup_ui.team_setup[index]["culture"]]
                if setup_ui.team_setup[index]["culture"] in self.save_data.player_custom_army_preset_save:
                    preset_list = {key: value for key, value in self.save_data.player_custom_army_preset_save[
                        setup_ui.team_setup[index]["culture"]].items() if value["Commander"]} | preset_list

                if self.custom_team_army[team][index].custom_preset_id:  # has preset selected
                    selected_preset = preset_list[self.custom_team_army[team][index].custom_preset_id]
                    if self.last_shown_custom_army != selected_preset:
                        self.last_shown_custom_army = selected_preset
                        army_preset = self.convert_custom_army_to_deployable(selected_preset,
                                                                             setup_ui.team_setup[index]["culture"])
                        self.showcase_army.__init__("", army_preset["culture"],
                                                    army_preset["culture"],
                                                    army_preset["commander"],
                                                    army_preset["followers"])
                        self.custom_army_info_popup.popup(selected_preset["Name"], self.showcase_army)
                    self.add_to_ui_menu_updater(self.custom_army_info_popup, self.custom_army_title_popup)
                    self.custom_army_info_popup.rect.midright = self.custom_battle_team_setup[
                        Opposite_Team[team]].rect.midright
                    self.custom_army_title_popup.rect.midbottom = self.custom_army_info_popup.rect.midtop

                if button.event_press:
                    if self.custom_team_army_button_bars[team][index] in self.ui_menu_updater:
                        self.remove_from_ui_menu_updater(self.custom_team_army_button_bars[team][index])
                    else:  # add bar list
                        self.add_to_ui_menu_updater(self.custom_team_army_button_bars[team][index])

                        bar_preset_list = []

                        for key, value in preset_list.items():
                            bar_preset_list.append((0, str(value["Name"])))
                        self.custom_team_army_button_bars[team][index].adapter.__init__(bar_preset_list)
                        self.remove_from_ui_menu_updater([item for item in self.all_custom_battle_bars if
                                                          item != self.custom_team_army_button_bars[team][index]])
                return

    if self.cursor.select_up or self.cursor.alt_select_up or self.esc_press:
        if self.custom_stage_bar.adapter.last_click and self.custom_stage_bar.adapter.last_click[0] == "click":
            self.custom_battle_stage_button.change_state(
                self.custom_stage_list[self.custom_stage_bar.adapter.last_click[1]])
            self.selected_custom_stage_battle = self.custom_stage_list[self.custom_stage_bar.adapter.last_click[1]]
            self.custom_stage_bar.adapter.last_click = ()

        elif not self.custom_stage_bar.mouse_over:  # click somewhere else
            self.remove_from_ui_menu_updater(self.custom_stage_bar)

        if (self.custom_weather_strength_bar.adapter.last_click and
                self.custom_weather_strength_bar.adapter.last_click[0] == "click"):
            self.custom_battle_weather_strength_button.change_state(
                self.custom_weather_strength_list[self.custom_weather_strength_bar.adapter.last_click[1]])
            self.selected_weather_strength_custom_battle = self.custom_weather_strength_bar.adapter.last_click[1]
            self.custom_weather_strength_bar.adapter.last_click = ()

        elif not self.custom_weather_strength_bar.mouse_over:  # click somewhere else
            self.remove_from_ui_menu_updater(self.custom_weather_strength_bar)

        if self.custom_weather_bar.adapter.last_click and self.custom_weather_bar.adapter.last_click[0] == "click":
            self.custom_battle_weather_type_button.change_state(
                "weather_" + str(self.custom_weather_list[self.custom_weather_bar.adapter.last_click[1]]))
            self.selected_weather_custom_battle = self.custom_weather_list[
                self.custom_weather_bar.adapter.last_click[1]]
            self.custom_weather_bar.adapter.last_click = ()

        elif not self.custom_weather_bar.mouse_over:  # click somewhere else
            self.remove_from_ui_menu_updater(self.custom_weather_bar)

        if self.setup_back_button.event_press or self.esc_press:  # back to start_set menu
            self.remove_from_ui_menu_updater(self.custom_battle_menu_uis_remove)
            for index in range(0, 4):
                self.custom_battle_team_setup[1].change_culture_preset(None, index)
                self.custom_battle_team_setup[2].change_culture_preset(None, index)
            self.back_mainmenu()

        elif self.custom_battle_preset_button.event_press:
            self.menu_state = "preset"
            self.before_save_preset_army_setup = deepcopy(self.save_data.player_custom_army_preset_save)
            self.custom_preset_culture_selector.change_culture_preset(Custom_Default_Culture)
            self.custom_preset_army_setup.change_culture_preset(Custom_Default_Culture)
            self.custom_preset_list_box.adapter.__init__()
            self.custom_preset_army_title.change_text("", 0, 0, 0)
            self.add_to_ui_menu_updater(self.custom_preset_menu_uis)
            self.remove_from_ui_menu_updater(self.custom_battle_menu_uis_remove)
            for index in range(0, 4):
                self.custom_battle_team_setup[1].change_culture_preset(None, index)
                self.custom_battle_team_setup[2].change_culture_preset(None, index)

        elif self.custom_battle_reset_button.event_press:
            self.selected_custom_stage_battle = Default_Selected_Stage_Custom_Battle
            self.team1_supply_limit_custom_battle = Default_Supply_limit_Custom_Battle
            self.team2_supply_limit_custom_battle = Default_Supply_limit_Custom_Battle
            self.team1_gold_limit_custom_battle = Default_Gold_limit_Custom_Battle
            self.team2_gold_limit_custom_battle = Default_Gold_limit_Custom_Battle
            self.selected_weather_custom_battle = Default_Weather_Custom_Battle
            self.selected_weather_strength_custom_battle = Default_Weather_Strength_Custom_Battle

            self.custom_battle_team1_gold_button.change_state(
                ("info_header_gold_limit", self.team1_gold_limit_custom_battle))
            self.custom_battle_team_setup[1].change_cost(0, self.custom_team_army[1][0].cost,
                                                         self.custom_team_army[1][0].total_supply_usage)
            self.custom_battle_team2_gold_button.change_state(
                ("info_header_gold_limit", self.team2_gold_limit_custom_battle))
            self.custom_battle_team_setup[2].change_cost(0, self.custom_team_army[2][0].cost,
                                                         self.custom_team_army[2][0].total_supply_usage)
            self.custom_battle_team1_supply_button.change_state(
                ("info_header_supply_limit", self.team1_supply_limit_custom_battle))
            self.custom_battle_team2_supply_button.change_state(
                ("info_header_supply_limit", self.team2_supply_limit_custom_battle))
            self.custom_battle_stage_button.change_state(self.selected_custom_stage_battle)
            self.custom_battle_weather_type_button.change_state(
                "weather_" + str(self.selected_weather_custom_battle))
            self.custom_battle_weather_strength_button.change_state(
                self.custom_weather_strength_list[self.selected_weather_strength_custom_battle])
            self.custom_battle_team_setup[1].change_cost(0, self.custom_team_army[1][0].cost,
                                                         self.custom_team_army[1][0].total_supply_usage)
            self.custom_battle_team_setup[2].change_cost(0, self.custom_team_army[2][0].cost,
                                                         self.custom_team_army[2][0].total_supply_usage)

        elif self.custom_battle_stage_button.event_press:
            if self.custom_stage_bar in self.ui_menu_updater:  # remove the bar list if click again
                self.remove_from_ui_menu_updater(self.custom_stage_bar)
            else:  # add bar list
                self.add_to_ui_menu_updater(self.custom_stage_bar)
                self.remove_from_ui_menu_updater(
                    [item for item in self.all_custom_battle_bars if item != self.custom_stage_bar])

        elif self.custom_battle_weather_strength_button.event_press:
            if self.custom_weather_strength_bar in self.ui_menu_updater:  # remove the bar list if click again
                self.remove_from_ui_menu_updater(self.custom_weather_strength_bar)
            else:  # add bar list
                self.add_to_ui_menu_updater(self.custom_weather_strength_bar)
                self.remove_from_ui_menu_updater(
                    [item for item in self.all_custom_battle_bars if item != self.custom_weather_strength_bar])

        elif self.custom_battle_weather_type_button.event_press:  # click on resolution bar
            if self.custom_weather_bar in self.ui_menu_updater:  # remove the bar list if click again
                self.remove_from_ui_menu_updater(self.custom_weather_bar)
            else:  # add bar list
                self.add_to_ui_menu_updater(self.custom_weather_bar)
                self.remove_from_ui_menu_updater(
                    [item for item in self.all_custom_battle_bars if item != self.custom_weather_bar])

        elif self.custom_battle_team1_gold_button.event_press:
            self.activate_input_popup(("text_input", "custom_gold", 1),
                                      self.grab_text(("ui", "input_gold_team1")), self.input_popup_uis)

        elif self.custom_battle_team2_gold_button.event_press:
            self.activate_input_popup(("text_input", "custom_gold", 2),
                                      self.grab_text(("ui", "input_gold_team2")), self.input_popup_uis)

        elif self.custom_battle_team1_supply_button.event_press:
            self.activate_input_popup(("text_input", "custom_supply", 1),
                                      self.grab_text(("ui", "input_supply_team1")), self.input_popup_uis)

        elif self.custom_battle_team2_supply_button.event_press:
            self.activate_input_popup(("text_input", "custom_supply", 2),
                                      self.grab_text(("ui", "input_supply_team2")), self.input_popup_uis)

        elif self.custom_battle_setup_start_battle_button.event_press:  # player click start button
            # do quick check whether army assigned for both teams
            self.change_custom_battle_config()
            team_exist = {1: False, 2: False}
            for team in (1, 2):
                setup_ui = self.custom_battle_team_setup[team]
                for index in (0, 4):
                    if (self.custom_team_army[team][index].commander_id or
                            setup_ui.team_setup[index]["culture"] == "random"):
                        team_exist[team] = True
            if False in tuple(team_exist.values()):  # no army exist, output warning
                self.activate_input_popup(("confirm_input", "no_army"),
                                          self.grab_text(("ui", "warn_no_army")),
                                          self.inform_popup_uis)
            else:
                custom_team_army, _ = self.check_custom_team_fund(create_random=True)

                for team in (1, 2):
                    if custom_team_army[team]:
                        team_exist[team] = True
                    else:
                        team_exist[team] = False
                if False in tuple(team_exist.values()):
                    self.activate_input_popup(("confirm_input", "no_army"),
                                              self.grab_text(("ui", "warn_no_army")),
                                              self.inform_popup_uis)
                else:
                    custom_team_army[1][0].supply = self.team1_supply_limit_custom_battle
                    custom_team_army[2][0].supply = self.team2_supply_limit_custom_battle
                    team_state = {0: {"faction": "free", "culture": "free",
                                      "strategy_resource": 0, "start_pos": 0.5, "air_group": [],
                                      "active_retinue": (), "strategy": [], "strategy_cooldown": {},
                                      "main_army": None, "reinforcement_army": []},
                                  1: {"faction": custom_team_army[1][0].faction,
                                      "culture": custom_team_army[1][0].culture,
                                      "strategy_resource": 0,
                                      "start_pos": 0, "air_group": [],
                                      "active_retinue": (), "strategy": [], "strategy_cooldown": {},
                                      "main_army": custom_team_army[1][0],
                                      "reinforcement_army": custom_team_army[1][1:]},
                                  2: {"faction": custom_team_army[2][0].faction,
                                      "culture": custom_team_army[2][0].culture,
                                      "strategy_resource": 0,
                                      "start_pos": 1, "air_group": [],
                                      "active_retinue": (), "strategy": [], "strategy_cooldown": {},
                                      "main_army": custom_team_army[2][0],
                                      "reinforcement_army": custom_team_army[2][1:]}}
                    player = None
                    if self.custom_team_players[1] == "player":
                        player = 1
                    elif self.custom_team_players[2] == "player":
                        player = 2
                    self.start_battle(None, "main", self.selected_custom_stage_battle, team_state, player,
                                      self.grab_text(("ui", "info_text_custom_battle")),
                                      custom_stage_data={
                                          "weather": (self.selected_weather_custom_battle,
                                                      self.selected_weather_strength_custom_battle)},
                                      setup_battle=True)
