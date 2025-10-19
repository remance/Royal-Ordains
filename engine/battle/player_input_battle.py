"""No need for menu/cancel input check here, already done in battle update"""


def player_input_battle(self):
    for key, pressed in self.player_key_press.items():
        if pressed and key in battle_key_input:
            battle_key_input[key](self)

    for key, pressed in self.player_key_hold.items():  # check for holding input
        if pressed and key in battle_key_hold:
            battle_key_hold[key](self)


def camera_go_left(self):
    self.camera_pos[0] -= (2000 * self.true_dt)
    self.fix_camera()


def camera_go_right(self):
    self.camera_pos[0] += (2000 * self.true_dt)
    self.fix_camera()


def key_retreat(self):
    """Order retreat to selected generals"""
    for general in self.player_selected_generals:
        if "broken" not in general.commander_order:
            general.issue_commander_order(("broken", ))
        else:
            general.issue_commander_order(("move", general.base_pos[0]))


def key_clear(self):
    """Remove current order to selected generals"""
    for general in self.player_selected_generals:
        general.issue_commander_order(())


def key_select_general(self, index):
    if index <= len(self.player_control_generals):
        general = self.player_control_generals[index - 1]
        if self.shift_press:
            if general not in self.player_selected_generals:
                self.player_selected_generals.append(general)
        elif self.ctrl_press:
            if general in self.player_selected_generals:
                self.player_selected_generals.remove(general)
        else:
            self.player_selected_generals = [general]


def key_select_general_1(self):
    key_select_general(self, 1)


def key_select_general_2(self):
    key_select_general(self, 2)


def key_select_general_3(self):
    key_select_general(self, 3)


def key_select_general_4(self):
    key_select_general(self, 4)


def key_select_general_5(self):
    key_select_general(self, 5)


def key_select_strategy(self, index):
    if index <= len(self.battle.team_stat[1]["strategy"]):
        this_strategy = tuple(self.battle.team_stat[1]["strategy"].keys())[index]
        if not self.battle.team_stat[1]["strategy"][this_strategy]:
            # strategy exist and not in cooldown
            self.battle.player_selected_strategy = tuple(self.battle.team_stat[1]["strategy"].keys())[index]
            self.battle.player_battle_interact.current_strategy_base_range = self.battle.strategy_list[this_strategy][
                "Range"]
            self.battle.player_battle_interact.current_strategy_base_activate_range = \
            self.battle.strategy_list[this_strategy]["Activate Range"]
            self.battle.player_battle_interact.current_strategy_range = self.battle.strategy_list[this_strategy]["Range"] * \
                                                                        self.screen_scale[0]
            self.battle.player_battle_interact.current_strategy_activate_range = self.battle.strategy_list[this_strategy][
                                                                                     "Activate Range"] * self.screen_scale[
                                                                                     0]
            self.battle.tactical_map_ui.current_strategy_base_range = self.battle.player_battle_interact.current_strategy_base_range
            self.battle.tactical_map_ui.current_strategy_base_activate_range = self.battle.player_battle_interact.current_strategy_base_activate_range


def key_select_strategy_1(self):
    key_select_strategy(self, 0)


def key_select_strategy_2(self):
    key_select_strategy(self, 1)


def key_select_strategy_3(self):
    key_select_strategy(self, 2)


def key_select_strategy_4(self):
    key_select_strategy(self, 3)


def key_select_strategy_5(self):
    key_select_strategy(self, 4)


battle_key_hold = {"Left": camera_go_left, "Right": camera_go_right}

battle_key_input = {"Retreat": key_retreat, "Clear": key_clear,
                    "Select 1": key_select_general_1, "Select 2": key_select_general_2,
                    "Select 3": key_select_general_3, "Select 4": key_select_general_4,
                    "Select 5": key_select_general_5, "Strategy 1": key_select_strategy_1,
                    "Strategy 2": key_select_strategy_2,
                    "Strategy 3": key_select_strategy_3, "Strategy 4": key_select_strategy_4,
                    "Strategy 5": key_select_strategy_5}
