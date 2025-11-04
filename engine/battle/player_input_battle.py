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
    """Order retreat to selected leaders"""
    for leader in self.player_selected_leaders:
        if "broken" not in leader.commander_order:
            leader.issue_commander_order(("broken", ))
        else:
            leader.issue_commander_order(("move", leader.base_pos[0]))


def key_clear(self):
    """Remove current order to selected leaders"""
    for leader in self.player_selected_leaders:
        leader.issue_commander_order(())


def key_select_leader(self, index):
    if index <= len(self.player_control_leaders):
        leader = self.player_control_leaders[index - 1]
        if self.shift_press:
            if leader not in self.player_selected_leaders:
                self.player_selected_leaders.append(leader)
        elif self.ctrl_press:
            if leader in self.player_selected_leaders:
                self.player_selected_leaders.remove(leader)
        else:
            self.player_selected_leaders = [leader]


def key_select_leader_1(self):
    key_select_leader(self, 1)


def key_select_leader_2(self):
    key_select_leader(self, 2)


def key_select_leader_3(self):
    key_select_leader(self, 3)


def key_select_leader_4(self):
    key_select_leader(self, 4)


def key_select_leader_5(self):
    key_select_leader(self, 5)


def key_select_strategy(self, index):
    if self.battle.team_stat[1]["strategy"] and index < len(self.battle.team_stat[1]["strategy"]):
        this_strategy = self.battle.team_stat[1]["strategy"][index]
        if not self.battle.team_stat[1]["strategy_cooldown"][index]:
            # strategy exist and not in cooldown
            self.battle.player_selected_strategy = (this_strategy, index)
            strategy_stat = self.battle.strategy_list[this_strategy]
            self.battle.player_battle_interact.current_strategy_base_range = strategy_stat["Range"]
            self.battle.player_battle_interact.current_strategy_base_activate_range = strategy_stat["Activate Range"]
            self.battle.player_battle_interact.current_strategy_range = strategy_stat["Range"] * self.screen_scale[0]
            self.battle.player_battle_interact.current_strategy_activate_range = (strategy_stat["Activate Range"] *
                                                                                  self.screen_scale[0])
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
                    "Select 1": key_select_leader_1, "Select 2": key_select_leader_2,
                    "Select 3": key_select_leader_3, "Select 4": key_select_leader_4,
                    "Select 5": key_select_leader_5, "Strategy 1": key_select_strategy_1,
                    "Strategy 2": key_select_strategy_2,
                    "Strategy 3": key_select_strategy_3, "Strategy 4": key_select_strategy_4,
                    "Strategy 5": key_select_strategy_5}
