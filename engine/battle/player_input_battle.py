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
    for general in self.player_selected_generals:
        if "broken" not in general.commander_order:
            general.issue_commander_order(("broken", ))
        else:
            general.issue_commander_order(("move", general.base_pos[0]))


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


battle_key_hold = {"Left": camera_go_left, "Right": camera_go_right}

battle_key_input = {"Retreat": key_retreat, "Select 1": key_select_general_1, "Select 2": key_select_general_2,
                    "Select 3": key_select_general_3, "Select 4": key_select_general_4,
                    "Select 5": key_select_general_5}
