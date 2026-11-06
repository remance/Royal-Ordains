from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.battle.battle import Battle


def battle_no_player_input_battle(self: Battle):
    for key, pressed in self.player_key_hold.items():  # check for holding input
        if pressed and key in battle_key_hold:
            battle_key_hold[key](self)


def player_input_battle(self: Battle):
    for key, pressed in self.player_key_press.items():
        if pressed and key in battle_key_input:
            battle_key_input[key](self)

    for key, pressed in self.player_key_hold.items():  # check for holding input
        if pressed and key in battle_key_hold:
            battle_key_hold[key](self)


def camera_go_left(self: Battle):
    self.camera_center_pos[0] -= (2000 * self.true_dt)
    self.fix_camera()


def camera_go_right(self: Battle):
    self.camera_center_pos[0] += (2000 * self.true_dt)
    self.fix_camera()


def change_pause(self: Battle):
    if self.game_speed:
        self.before_pause_game_speed = self.game_speed
        self.game_speed = 0
    else:
        self.game_speed = self.before_pause_game_speed
    self.battle_helper_ui.time_option = self.battle_helper_ui.time_choice.index(self.game_speed)
    self.battle_helper_ui.reset_image()


def key_call_leader(self: Battle, index: int):
    if index < len(self.team_state[self.player_team]["leader_call_list"]):
        self.call_reinforcement(self.player_team, "leader", index)


def key_call_leader_1(self: Battle):
    key_call_leader(self, 0)


def key_call_leader_2(self: Battle):
    key_call_leader(self, 1)


def key_call_leader_3(self: Battle):
    key_call_leader(self, 2)


def key_call_troop(self: Battle, index: int):
    if index < len(self.team_state[self.player_team]["troop_call_list"]):
        self.call_reinforcement(self.player_team, "troop", index)


def key_call_troop_1(self: Battle):
    key_call_troop(self, 0)


def key_call_troop_2(self: Battle):
    key_call_troop(self, 1)


def key_call_troop_3(self: Battle):
    key_call_troop(self, 2)


def key_call_troop_4(self: Battle):
    key_call_troop(self, 3)


def key_call_troop_5(self: Battle):
    key_call_troop(self, 4)


def key_call_air(self: Battle, index: int):
    if self.team_state[self.player_team]["air_group"] and index < len(self.team_state[self.player_team]["air_group"]):
        self.call_in_air_group(self.player_team, (index,), self.team_state[self.player_enemy_team]["start_pos"])


def key_call_air_1(self: Battle):
    key_call_air(self, 0)


def key_call_air_2(self: Battle):
    key_call_air(self, 1)


def key_call_air_3(self: Battle):
    key_call_air(self, 2)


def key_call_air_4(self: Battle):
    key_call_air(self, 3)


def key_call_air_5(self: Battle):
    key_call_air(self, 4)


def key_select_strategy(self: Battle, index: int):
    player_team_state = self.team_state[self.player_team]
    player_team_state_strategy = player_team_state["strategy_cooldown"]
    if player_team_state_strategy and index < len(player_team_state_strategy):
        this_strategy = tuple(player_team_state_strategy.keys())[index]
        if not min(player_team_state_strategy[this_strategy]):
            # strategy exist and not in cooldown
            self.player_selected_strategy = this_strategy
            strategy_stat = self.strategy_list[this_strategy]
            self.player_interact.current_strategy_base_range = strategy_stat["Range"]
            self.player_interact.current_strategy_base_activate_range = strategy_stat["Activate Range"]
            self.player_interact.current_strategy_range = strategy_stat["Range"] * self.screen_scale_width
            self.player_interact.current_strategy_activate_range = (strategy_stat["Activate Range"] *
                                                                    self.screen_scale_width)
            self.tactical_map_ui.current_strategy_base_range = self.player_interact.current_strategy_base_range
            self.tactical_map_ui.current_strategy_base_activate_range = self.player_interact.current_strategy_base_activate_range


def key_select_strategy_1(self: Battle):
    key_select_strategy(self, 0)


def key_select_strategy_2(self: Battle):
    key_select_strategy(self, 1)


def key_select_strategy_3(self: Battle):
    key_select_strategy(self, 2)


def key_select_strategy_4(self: Battle):
    key_select_strategy(self, 3)


def key_select_strategy_5(self: Battle):
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
                    "Strategy 5": key_select_strategy_5, "Change Pause": change_pause}
