from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.grand.grand import Grand


def battle_no_player_input_grand(self: Grand):
    for key, pressed in self.player_key_hold.items():  # check for holding input
        if pressed and key in grand_key_hold:
            grand_key_hold[key](self)


def player_input_grand(self: Grand):
    if self.grand_reserve_army_list_ui not in self.outer_ui_updater:
        for key, pressed in self.player_key_press.items():
            if pressed and key in grand_key_input:
                grand_key_input[key](self)

        for key, pressed in self.player_key_hold.items():  # check for holding input
            if pressed and key in grand_key_hold:
                grand_key_hold[key](self)


def camera_go_left(self: Grand):
    self.camera_topleft_pos[0] -= (2000 * self.true_dt)
    self.fix_camera()


def camera_go_right(self: Grand):
    self.camera_topleft_pos[0] += (2000 * self.true_dt)
    self.fix_camera()


def camera_go_up(self: Grand):
    self.camera_topleft_pos[1] -= (2000 * self.true_dt)
    self.fix_camera()


def camera_go_down(self: Grand):
    self.camera_topleft_pos[1] += (2000 * self.true_dt)
    self.fix_camera()


grand_key_hold = {"Left": camera_go_left, "Right": camera_go_right, "Up": camera_go_up, "Down": camera_go_down}

grand_key_input = {}
