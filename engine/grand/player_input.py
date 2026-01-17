"""No need for menu/cancel input check here, already done in battle update"""


def battle_no_player_input_grand(self):
    for key, pressed in self.player_key_hold.items():  # check for holding input
        if pressed and key in grand_key_hold:
            grand_key_hold[key](self)


def player_input_grand(self):
    for key, pressed in self.player_key_press.items():
        if pressed and key in grand_key_input:
            grand_key_input[key](self)

    for key, pressed in self.player_key_hold.items():  # check for holding input
        if pressed and key in grand_key_hold:
            grand_key_hold[key](self)


def camera_go_left(self):
    self.camera_pos[0] -= (2000 * self.true_dt)
    self.fix_camera()


def camera_go_right(self):
    self.camera_pos[0] += (2000 * self.true_dt)
    self.fix_camera()


def camera_go_up(self):
    self.camera_pos[1] -= (2000 * self.true_dt)
    self.fix_camera()


def camera_go_down(self):
    self.camera_pos[1] += (2000 * self.true_dt)
    self.fix_camera()


grand_key_hold = {"Left": camera_go_left, "Right": camera_go_right, "Up": camera_go_up, "Down": camera_go_down}

grand_key_input = {}
