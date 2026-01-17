from copy import deepcopy
from random import choice

from engine.constants import Custom_Default_Faction


def menu_custom_setup(self):
    self.remove_from_ui_updater(self.custom_army_info_popup, self.custom_army_title_popup)
    for team, team_bars in self.custom_team_army_button_bars.items():
        for index, bar in enumerate(team_bars):
            if bar.mouse_over and bar.hover_index is not None:
                setup_ui = self.custom_battle_team1_setup
                if team == 2:
                    setup_ui = self.custom_battle_team2_setup
                preset_list = self.character_data.preset_list[setup_ui.team_setup[index]["faction"]]
                if setup_ui.team_setup[index]["faction"] in self.save_data.custom_army_preset_save:
                    preset_list = {key: value for key, value in self.save_data.custom_army_preset_save[
                        setup_ui.team_setup[index]["faction"]].items() if
                                   None not in value["commander"]} | preset_list
                preset = tuple(preset_list.keys())[bar.hover_index]
                if self.last_shown_custom_army != preset:
                    self.last_shown_custom_army = preset
                    army_preset = self.convert_army_to_deployable(preset_list[preset])
                    self.custom_army_title_popup.change_text(preset_list[preset]["Name"], army_preset["cost"])
                    self.custom_army_info_popup.popup(army_preset)
                self.add_to_ui_updater(self.custom_army_info_popup, self.custom_army_title_popup)
                if team == 1:
                    self.custom_army_info_popup.rect.midright = self.custom_battle_team2_setup.rect.midright
                else:
                    self.custom_army_info_popup.rect.midright = self.custom_battle_team1_setup.rect.midright
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
                    preset_list = {key: value for key, value in self.save_data.custom_army_preset_save[
                        setup_ui.team_setup[index]["faction"]].items() if
                                   None not in value["commander"]} | preset_list

                if self.custom_team_army[team][index].custom_preset_id:  # has preset selected
                    preset = preset_list[self.custom_team_army[team][index].custom_preset_id]
                    if self.last_shown_custom_army != preset:
                        self.last_shown_custom_army = preset
                        army_preset = self.convert_army_to_deployable(preset)
                        self.custom_army_title_popup.change_text(preset["Name"], army_preset["cost"])
                        self.custom_army_info_popup.popup(army_preset)
                    self.add_to_ui_updater(self.custom_army_info_popup, self.custom_army_title_popup)
                    if team == 1:
                        self.custom_army_info_popup.rect.midright = self.custom_battle_team2_setup.rect.midright
                    else:
                        self.custom_army_info_popup.rect.midright = self.custom_battle_team1_setup.rect.midright
                    self.custom_army_title_popup.rect.midbottom = self.custom_army_info_popup.rect.midtop
                if button.event_press:
                    if self.custom_team_army_button_bars[team][index] in self.ui_updater:
                        self.remove_from_ui_updater(self.custom_team_army_button_bars[team][index])
                    else:  # add bar list
                        self.add_to_ui_updater(self.custom_team_army_button_bars[team][index])

                        bar_preset_list = []

                        for key, value in preset_list.items():
                            bar_preset_list.append((0, str(value["Name"])))
                        self.custom_team_army_button_bars[team][index].adapter.__init__(bar_preset_list)
                        self.remove_from_ui_updater([item for item in self.all_custom_battle_bars if
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
                        preset_list = {key: value for key, value in self.save_data.custom_army_preset_save[
                            setup_ui.team_setup[index]["faction"]].items() if
                                       None not in value["commander"]} | preset_list
                    preset = tuple(preset_list.keys())[bar.hover_index]
                    army_preset = self.convert_army_to_deployable(preset_list[preset])
                    self.custom_team_army[team][index].__init__(army_preset["commander"][0], army_preset["leader"],
                                                                army_preset["troop"], army_preset["air"],
                                                                army_preset["retinue"], custom_preset_id=preset)
                    setup_ui.change_cost(index, self.custom_team_army[team][index].cost)
                    self.custom_team_army_buttons[team][index].change_state(
                        bar.adapter.actual_list[bar.adapter.last_click[1]], no_localisation=True)
                    bar.adapter.last_click = ()
                    return
                elif not bar.mouse_over:  # click somewhere else
                    self.remove_from_ui_updater(bar)

        if self.custom_map_bar.adapter.last_click and self.custom_map_bar.adapter.last_click[0] == "click":
            self.custom_battle_map_button.change_state(self.custom_map_list[self.custom_map_bar.adapter.last_click[1]])
            self.selected_custom_map_battle = self.custom_map_list[self.custom_map_bar.adapter.last_click[1]]
            self.custom_map_bar.adapter.last_click = ()

        elif not self.custom_map_bar.mouse_over:  # click somewhere else
            self.remove_from_ui_updater(self.custom_map_bar)

        if self.custom_weather_strength_bar.adapter.last_click and self.custom_weather_strength_bar.adapter.last_click[
            0] == "click":
            self.custom_battle_weather_strength_button.change_state(
                self.custom_weather_strength_list[self.custom_weather_strength_bar.adapter.last_click[1]])
            self.selected_weather_strength_custom_battle = self.custom_weather_strength_bar.adapter.last_click[1]
            self.custom_weather_strength_bar.adapter.last_click = ()

        elif not self.custom_weather_strength_bar.mouse_over:  # click somewhere else
            self.remove_from_ui_updater(self.custom_weather_strength_bar)

        if self.custom_weather_bar.adapter.last_click and self.custom_weather_bar.adapter.last_click[0] == "click":
            self.custom_battle_weather_type_button.change_state(
                "weather_" + str(self.custom_weather_list[self.custom_weather_bar.adapter.last_click[1]]))
            self.selected_weather_custom_battle = self.custom_weather_list[
                self.custom_weather_bar.adapter.last_click[1]]
            self.custom_weather_bar.adapter.last_click = ()

        elif not self.custom_weather_bar.mouse_over:  # click somewhere else
            self.remove_from_ui_updater(self.custom_weather_bar)

        if self.setup_back_button.event_press or self.esc_press:  # back to start_set menu
            self.remove_from_ui_updater(self.custom_battle_menu_uis_remove)
            for index in range(0, 4):
                self.custom_battle_team1_setup.change_faction(None, index)
                self.custom_battle_team2_setup.change_faction(None, index)
            self.back_mainmenu()

        elif self.custom_battle_preset_button.event_press:
            self.menu_state = "preset"
            self.before_save_preset_army_setup = deepcopy(self.save_data.custom_army_preset_save)
            self.faction_selector.change_faction(Custom_Default_Faction)
            self.custom_preset_army_setup.change_faction(Custom_Default_Faction)
            self.custom_preset_list_box.adapter.__init__()
            self.custom_preset_army_title.change_text("", self.custom_preset_army_setup.total_gold_cost)
            self.add_to_ui_updater(self.custom_preset_menu_uis)
            self.remove_from_ui_updater(self.custom_battle_menu_uis_remove)
            for index in range(0, 4):
                self.custom_battle_team1_setup.change_faction(None, index)
                self.custom_battle_team2_setup.change_faction(None, index)

        elif self.custom_battle_map_button.event_press:
            if self.custom_map_bar in self.ui_updater:  # remove the bar list if click again
                self.remove_from_ui_updater(self.custom_map_bar)
            else:  # add bar list
                self.add_to_ui_updater(self.custom_map_bar)
                self.remove_from_ui_updater(
                    [item for item in self.all_custom_battle_bars if item != self.custom_map_bar])

        elif self.custom_battle_weather_strength_button.event_press:
            if self.custom_weather_strength_bar in self.ui_updater:  # remove the bar list if click again
                self.remove_from_ui_updater(self.custom_weather_strength_bar)
            else:  # add bar list
                self.add_to_ui_updater(self.custom_weather_strength_bar)
                self.remove_from_ui_updater(
                    [item for item in self.all_custom_battle_bars if item != self.custom_weather_strength_bar])

        elif self.custom_battle_weather_type_button.event_press:  # click on resolution bar
            if self.custom_weather_bar in self.ui_updater:  # remove the bar list if click again
                self.remove_from_ui_updater(self.custom_weather_bar)
            else:  # add bar list
                self.add_to_ui_updater(self.custom_weather_bar)
                self.remove_from_ui_updater(
                    [item for item in self.all_custom_battle_bars if item != self.custom_weather_bar])

        elif self.custom_battle_team1_gold_button.event_press:
            self.activate_input_popup(("text_input", "custom_gold", 1),
                                      self.localisation.grab_text(("ui", "input_gold_team1")), self.input_popup_uis)

        elif self.custom_battle_team2_gold_button.event_press:
            self.activate_input_popup(("text_input", "custom_gold", 2),
                                      self.localisation.grab_text(("ui", "input_gold_team2")), self.input_popup_uis)

        elif self.custom_battle_team1_supply_button.event_press:
            self.activate_input_popup(("text_input", "custom_supply", 1),
                                      self.localisation.grab_text(("ui", "input_supply_team1")), self.input_popup_uis)

        elif self.custom_battle_team2_supply_button.event_press:
            self.activate_input_popup(("text_input", "custom_supply", 2),
                                      self.localisation.grab_text(("ui", "input_supply_team2")), self.input_popup_uis)


        elif self.custom_battle_setup_start_battle_button.event_press:
            # do quick check whether army assigned for both teams
            team_exist = {1: False, 2: False}
            for team in (1, 2):
                setup_ui = self.custom_battle_team1_setup
                if team == 2:
                    setup_ui = self.custom_battle_team2_setup
                for index in (0, 4):
                    if self.custom_team_army[team][index].commander_id or setup_ui.team_setup[index][
                        "faction"] == "Random":
                        team_exist[team] = True
            if False in tuple(team_exist.values()):
                self.activate_input_popup(("confirm_input", "no_army"),
                                          self.localisation.grab_text(("ui", "no_army_warn")),
                                          self.inform_popup_uis)
            else:
                # recreate army with fund cut
                team_exist = {1: False, 2: False}
                # remade team army to include only those with at least 1 existing character and or made random one
                custom_team_army = {team: [] for team in (1, 2)}
                for team in custom_team_army:
                    setup_ui = self.custom_battle_team1_setup
                    if team == 2:
                        setup_ui = self.custom_battle_team2_setup
                    for index in range(5):
                        if self.custom_team_army[team][index].commander_id:
                            custom_team_army[team].append(deepcopy(self.custom_team_army[team][index]))
                        elif setup_ui.team_setup[index]["faction"] == "Random":
                            faction = choice([key for key in self.sprite_data.faction_coas if key != "Random"])
                            new_random_army = deepcopy(self.custom_team_army[team][index])

                            preset_list = self.character_data.preset_list[faction]
                            if faction in self.save_data.custom_army_preset_save:
                                preset_list = {key: value for key, value in self.save_data.custom_army_preset_save[
                                    setup_ui.team_setup[index]["faction"]].items() if
                                               None not in value["commander"]} | preset_list

                            preset = choice(tuple(preset_list.keys()))

                            army_preset = self.convert_army_to_deployable(preset_list[preset])
                            new_random_army.__init__(army_preset["commander"][0], army_preset["leader"],
                                                     army_preset["troop"], army_preset["air"],
                                                     army_preset["retinue"], custom_preset_id=preset)
                            custom_team_army[team].append(new_random_army)

                remain_gold = {1: self.team1_gold_limit_custom_battle, 2: self.team2_gold_limit_custom_battle}
                for team in (1, 2):
                    for army in tuple(custom_team_army[team]):
                        if remain_gold[team] >= army.cost:
                            remain_gold[team] -= army.cost
                        else:  # cut units
                            if remain_gold[team] >= army.character_list[army.commander_id]["Cost"]:
                                remain_gold[team] -= army.character_list[army.commander_id]["Cost"]

                                for index, character in enumerate(army.leader_group.copy()):
                                    if remain_gold[team] >= army.character_list[character]["Cost"]:
                                        remain_gold[team] -= army.character_list[character]["Cost"]
                                    else:
                                        army.leader_group.remove(character)
                                for index, character in enumerate(army.ground_group.copy()):
                                    if remain_gold[team] >= army.character_list[character]["Cost"]:
                                        remain_gold[team] -= army.character_list[character]["Cost"]
                                    else:
                                        army.ground_group.remove(character)
                                for index, character in enumerate(army.air_group.copy()):
                                    if remain_gold[team] > army.character_list[character]["Cost"]:
                                        remain_gold[team] -= army.character_list[character]["Cost"]
                                    else:
                                        army.air_group.remove(character)
                                army.reset_stat()
                            else:  # cut entire army if commander cannot be added
                                custom_team_army[team].remove(army)

                for team in (1, 2):
                    for army in custom_team_army[team]:
                        if army.commander_id:
                            team_exist[team] = True
                if False in tuple(team_exist.values()):
                    self.activate_input_popup(("confirm_input", "no_army"),
                                              self.localisation.grab_text(("ui", "no_army_warn")),
                                              self.inform_popup_uis)
                else:
                    custom_team_army[1][0].supply = self.team1_supply_limit_custom_battle
                    custom_team_army[2][0].supply = self.team2_supply_limit_custom_battle
                    team_stat = {0: {"strategy_resource": 0, "start_pos": 0.5, "air_group": [], "retinue": (),
                                     "strategy": [], "strategy_cooldown": {},
                                     "main_army": None, "reinforcement_army": []},
                                 1: {"strategy_resource": 0, "start_pos": 0, "air_group": [], "retinue": (),
                                     "strategy": [], "strategy_cooldown": {},
                                     "main_army": custom_team_army[1][0],
                                     "reinforcement_army": custom_team_army[1][1:]},
                                 2: {"strategy_resource": 100, "start_pos": 1, "air_group": [],
                                     "retinue": (), "strategy": [], "strategy_cooldown": {},
                                     "main_army": custom_team_army[2][0],
                                     "reinforcement_army": custom_team_army[2][1:]}}
                    player = None
                    if self.custom_team1_player == "player":
                        player = 1
                    elif self.custom_team2_player == "player":
                        player = 2
                    self.start_battle("main", self.selected_custom_map_battle, team_stat, player,
                                      custom_stage_data={
                                          "weather": (self.selected_weather_custom_battle,
                                                      self.selected_weather_strength_custom_battle)})
