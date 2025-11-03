import pygame

from engine.character.character import BattleCharacter
from engine.uibattle.uibattle import CharacterSpeechBox
from engine.utils.common import edit_config


def menu_option(self):
    bar_press = False
    for bar in self.resolution_bar:
        # loop to find which resolution bar is selected, this happens outside of clicking check below
        if bar.mouse_over:
            if bar.event:
                self.resolution_drop.change_state(bar.text)  # change button value based on new selected value
                resolution_change = bar.text.split()

                change_resolution(self, resolution_change=resolution_change)
                self.remove_ui_updater(self.resolution_bar)
                bar_press = True
            break

    if not bar_press and self.cursor.is_select_just_up:
        self.remove_ui_updater(self.resolution_bar)

    if self.back_button.event_press or self.esc_press:  # back to start_set menu
        self.remove_ui_updater(self.option_menu_buttons, self.option_text_list, self.option_menu_sliders.values(),
                               self.value_boxes.values(), self.resolution_bar)
        self.back_mainmenu()

    elif self.keybind_button.event_press:
        self.menu_state = "keybind"

        self.remove_ui_updater(*self.option_text_list, *self.option_menu_sliders.values(),
                               *self.value_boxes.values(), self.option_menu_buttons)
        self.add_ui_updater(*self.keybind_text.values(), *self.keybind_icon.values(),
                            self.back_button, self.default_button)

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
        if not self.fullscreen_box.tick:
            self.fullscreen_box.change_tick(True)
            self.full_screen = 1
        else:
            self.fullscreen_box.change_tick(False)
            self.full_screen = 0
        edit_config("USER", "full_screen", self.full_screen, self.config_path,
                    self.config)
        change_resolution(self)

    elif self.fps_box.event_press:
        if not self.fps_box.tick:
            self.fps_box.change_tick(True)
            self.show_fps = 1
            self.battle.battle_outer_ui_updater.add(self.battle.fps_count)
            self.add_ui_updater(self.fps_count)
        else:
            self.fps_box.change_tick(False)
            self.show_fps = 0
            self.battle.battle_outer_ui_updater.remove(self.battle.fps_count)
            self.remove_ui_updater(self.fps_count)
        edit_config("USER", "fps", self.show_fps, self.config_path,
                    self.config)

    elif self.easy_text_box.event_press:
        if not self.easy_text_box.tick:
            self.easy_text_box.change_tick(True)
            CharacterSpeechBox.simple_font = True
            edit_config("USER", "easy_text", 1, self.config_path,
                        self.config)
        else:
            self.easy_text_box.change_tick(False)
            CharacterSpeechBox.simple_font = False
            edit_config("USER", "easy_text", 0, self.config_path,
                        self.config)

    elif self.show_dmg_box.event_press:
        if not self.show_dmg_box.tick:
            self.show_dmg_box.change_tick(True)
            BattleCharacter.show_dmg_number = True
            edit_config("USER", "show_dmg_number", 1, self.config_path,
                        self.config)
        else:
            self.show_dmg_box.change_tick(False)
            BattleCharacter.show_dmg_number = False
            edit_config("USER", "show_dmg_number", 0, self.config_path,
                        self.config)

    else:
        for key, value in self.option_menu_sliders.items():
            if value.event:  # press on slider bar
                value.player_input(self.value_boxes[key])  # update slider button based on mouse value
                edit_config("USER", key + "_volume", value.value, self.config_path,
                            self.config)
                self.change_sound_volume()
                break


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
