"""No need for menu/cancel input check here, already done in battle update"""


def battle_no_player_input_battle(self):
    for key, pressed in self.player_key_hold.items():  # check for holding input
        if pressed and key in battle_key_hold:
            battle_key_hold[key](self)


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


def key_call_leader(self, index):
    if index < len(self.team_stat[self.player_team]["leader_call_list"]):
        self.call_reinforcement(self.player_team, "leader", index)


def key_call_leader_1(self):
    key_call_leader(self, 0)


def key_call_leader_2(self):
    key_call_leader(self, 1)


def key_call_leader_3(self):
    key_call_leader(self, 2)


def key_call_troop(self, index):
    if index < len(self.team_stat[self.player_team]["troop_call_list"]):
        self.call_reinforcement(self.player_team, "troop", index)


def key_call_troop_1(self):
    key_call_troop(self, 0)


def key_call_troop_2(self):
    key_call_troop(self, 1)


def key_call_troop_3(self):
    key_call_troop(self, 2)


def key_call_troop_4(self):
    key_call_troop(self, 3)


def key_call_troop_5(self):
    key_call_troop(self, 4)


def key_call_air(self, index):
    if self.team_stat[self.player_team]["air_group"] and index < len(self.team_stat[self.player_team]["air_group"]):
        self.call_in_air_group(self.player_team, (index,), self.team_stat[self.player_enemy_team]["start_pos"])


def key_call_air_1(self):
    key_call_air(self, 0)


def key_call_air_2(self):
    key_call_air(self, 1)


def key_call_air_3(self):
    key_call_air(self, 2)


def key_call_air_4(self):
    key_call_air(self, 3)


def key_call_air_5(self):
    key_call_air(self, 4)


def key_select_strategy(self, index):
    if self.battle.team_stat[self.battle.player_team]["strategy"] and index < len(
            self.battle.team_stat[self.battle.player_team]["strategy"]):
        this_strategy = self.battle.team_stat[self.battle.player_team]["strategy"][index]
        if not self.battle.team_stat[self.battle.player_team]["strategy_cooldown"][index]:
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

battle_key_input = {"Call Leader 1": key_call_leader_1, "Call Leader 2": key_call_leader_2,
                    "Call Leader 3": key_call_leader_3, "Call Troop 1": key_call_troop_1,
                    "Call Troop 2": key_call_troop_2,
                    "Call Troop 3": key_call_troop_3, "Call Troop 4": key_call_troop_4,
                    "Call Troop 5": key_call_troop_5, "Call Air 1": key_call_air_1, "Call Air 2": key_call_air_2,
                    "Call Air 3": key_call_air_3, "Call Air 4": key_call_air_4,
                    "Call Air 5": key_call_air_5, "Strategy 1": key_select_strategy_1,
                    "Strategy 2": key_select_strategy_2,
                    "Strategy 3": key_select_strategy_3, "Strategy 4": key_select_strategy_4,
                    "Strategy 5": key_select_strategy_5}
