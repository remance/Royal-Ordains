import pygame

from engine.uibattle.uibattle import CharacterSpeechBox
from engine.utils.common import edit_config


def menu_option(self, esc_press):
    bar_press = False
    for bar in self.resolution_bar:  # loop to find which resolution bar is selected, this happens outside of clicking check below
        if bar.event_press:
            self.resolution_drop.change_state(bar.text)  # change button value based on new selected value
            resolution_change = bar.text.split()
            change_resolution(self, resolution_change=resolution_change)
            self.remove_ui_updater(self.resolution_bar)
            bar_press = True

    if not bar_press and self.cursor.is_select_just_up:
        self.remove_ui_updater(self.resolution_bar)

    if self.back_button.event_press or esc_press:  # back to start_set menu
        self.remove_ui_updater(self.option_menu_button, self.option_text_list, self.option_menu_sliders.values(),
                               self.value_boxes.values(), self.resolution_bar)
        self.back_mainmenu()

    elif self.keybind_button.event_press:
        self.menu_state = "keybind"

        if 1 in self.player_joystick:
            if self.config["USER"]["control player 1"] == "joystick":  # player has joystick when first enter option
                self.control_switch.change_control("joystick" + str(self.player_joystick[1]), 1)
                self.player_key_control[1] = self.config["USER"]["control player 1"]
                for key, value in self.keybind_icon.items():
                    value.change_key(self.config["USER"]["control player 1"],
                                     self.player_key_bind_list[1][self.config["USER"]["control player 1"]][key],
                                     self.joystick_bind_name[
                                         self.joystick_name[self.player_joystick[1]]])

        else:  # no joystick, reset player 1 to keyboard
            self.config["USER"]["control player 1"] = "keyboard"
            edit_config("USER", "control player 1", "keyboard", self.config_path, self.config)
            self.control_switch.change_control("keyboard", 1)
            self.player_key_control[1] = self.config["USER"]["control player 1"]
            for key, value in self.keybind_icon.items():
                value.change_key(self.config["USER"]["control player 1"],
                                 self.player_key_bind_list[1][self.config["USER"]["control player 1"]][key],
                                 None)

        self.remove_ui_updater(*self.option_text_list, *self.option_menu_sliders.values(),
                               *self.value_boxes.values(), self.option_menu_button)
        self.add_ui_updater(*self.keybind_text.values(), *self.keybind_icon.values(), self.control_switch,
                            self.back_button, self.default_button, self.control_player_back, self.control_player_next)

    elif self.default_button.event_press:  # revert all setting to original
        for setting in self.config["DEFAULT"]:
            if setting not in ("language", "keybind"):
                edit_config("USER", setting, self.config["DEFAULT"][setting], self.config_path, self.config)

        change_resolution(self, resolution_change=(int(self.config["DEFAULT"]["screen_width"]), "",
                                                   int(self.config["DEFAULT"]["screen_height"])))

    elif self.resolution_drop.event_press:  # click on resolution bar
        if self.resolution_bar in self.ui_updater:  # remove the bar list if click again
            self.remove_ui_updater(self.resolution_bar)
        else:  # add bar list
            self.add_ui_updater(self.resolution_bar)

    elif self.fullscreen_box.event_press:
        if self.fullscreen_box.tick is False:
            self.fullscreen_box.change_tick(True)
            self.full_screen = 1
        else:
            self.fullscreen_box.change_tick(False)
            self.full_screen = 0
        edit_config("USER", "full_screen", self.full_screen, self.config_path,
                    self.config)
        change_resolution(self)

    elif self.fps_box.event_press:
        if self.fps_box.tick is False:
            self.fps_box.change_tick(True)
            self.show_fps = 1
            self.battle.realtime_ui_updater.add(self.battle.fps_count)
            self.add_ui_updater(self.fps_count)
        else:
            self.fps_box.change_tick(False)
            self.show_fps = 0
            self.battle.realtime_ui_updater.remove(self.battle.fps_count)
            self.remove_ui_updater(self.fps_count)
        edit_config("USER", "fps", self.show_fps, self.config_path,
                    self.config)

    elif self.easy_text_box.event_press:
        if self.easy_text_box.tick is False:
            self.easy_text_box.change_tick(True)
            CharacterSpeechBox.simple_font = True
            edit_config("USER", "easy_text", 1, self.config_path,
                        self.config)
        else:
            self.easy_text_box.change_tick(False)
            CharacterSpeechBox.simple_font = False
            edit_config("USER", "easy_text", 0, self.config_path,
                        self.config)

    for key, value in self.option_menu_sliders.items():
        if value.event:  # press on slider bar
            value.player_input(self.value_boxes[key])  # update slider button based on mouse value
            edit_config("USER", key + "_volume", value.value, self.config_path,
                        self.config)
            self.change_sound_volume()


def change_resolution(self, resolution_change=None):
    from engine.game.game import Game
    if resolution_change:
        self.screen_width = resolution_change[0]
        self.screen_height = resolution_change[2]

        edit_config("USER", "screen_width", resolution_change[0], self.config_path,
                    self.config)
        edit_config("USER", "screen_height", resolution_change[2], self.config_path,
                    self.config)

    pygame.time.wait(1000)
    if pygame.mixer:
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
    pygame.quit()
    Game(self.main_dir, self.error_log)  # restart game when change resolution
