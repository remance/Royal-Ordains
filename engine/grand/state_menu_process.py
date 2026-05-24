import sys
import pygame
from pygame import quit as pg_quit

from engine.utils.common import edit_config


def state_menu_process(self):
    self.ui_menu_updater.update(self.true_dt)
    self.grand_map.update()

    self.camera.update(self.grand_camera_object_drawer)
    self.camera.out_update(self.outer_ui_updater)
    self.camera.out_update(self.ui_menu_drawer)

    if self.input_popup:  # currently, have input text pop up on screen, stop everything else until done.
        if self.input_ok_button.event_press:
            self.change_pause_update(False)
            self.input_box.render_text("")
            input_popup = self.input_popup[1]
            self.input_popup = None
            self.remove_from_ui_menu_updater(self.input_popup_uis, self.confirm_popup_uis, self.all_input_popup_uis)

            if input_popup == "quit":
                pygame.time.wait(1000)
                pg_quit()
                sys.exit()

            elif input_popup == "end_grand":
                self.back_to_grand_state()
                return False

        elif self.input_cancel_button.event_press or self.input_close_button.event_press or self.esc_press:
            self.change_pause_update(False)
            self.input_box.render_text("")
            self.input_popup = None
            self.remove_from_ui_menu_updater(self.all_input_popup_uis)
    else:
        if self.esc_press and self.esc_menu_mode == "menu":  # in menu or option
            self.back_to_grand_state()

        elif self.esc_menu_mode == "menu":  # esc menu
            for key, button in self.grand_menu_button.items():
                if button.event_press:
                    if key == "resume":  # resume battle
                        self.back_to_grand_state()

                    elif key == "option":  # open option menu
                        self.esc_menu_mode = "option"  # change to option menu mode
                        self.remove_from_ui_menu_updater(self.grand_menu_button.values())  # remove start_set esc menu button
                        self.add_to_ui_menu_updater(self.esc_option_menu_button, self.esc_slider_menu.values(),
                                                    self.esc_value_boxes.values(), self.esc_option_text.values())

                    elif key == "save":  # open save menu
                        self.esc_menu_mode = "save"  # change to option menu mode
                        self.remove_from_ui_menu_updater(self.grand_menu_button.values())  # remove start_set esc menu button
                        self.add_to_ui_menu_updater()

                    elif key == "end":  # end battle
                        self.activate_input_popup(("confirm_input", "end_grand"),
                                                  self.localisation.grab_text(("ui", "input_leave_grand")),
                                                  self.confirm_popup_uis)

                    elif key == "quit":  # quit game
                        self.activate_input_popup(("confirm_input", "quit"),
                                                  self.localisation.grab_text(("ui", "input_quit_game")),
                                                  self.confirm_popup_uis)
                    break  # found clicked button, break loop

        elif self.esc_menu_mode == "battle":  # battle log
            if self.esc_dialogue_button.event_press or self.esc_press:  # confirm or esc, close option menu
                self.esc_menu_mode = "menu"  # go back to start_set esc menu
                self.remove_from_ui_menu_updater(self.esc_dialogue_button, self.dialogue_box)  # remove option menu sprite
                self.add_to_ui_menu_updater(self.grand_menu_button.values())  # add start_set esc menu buttons back

        elif self.esc_menu_mode == "option":  # option menu
            for key, value in self.esc_slider_menu.items():
                if value.event:  # press on slider bar
                    value.player_input(self.esc_value_boxes[key])  # update slider button based on mouse value
                    edit_config("USER", key + "_volume", value.value, self.game.config_path,
                                self.config)
                    self.game.change_sound_volume()

            if self.esc_option_menu_button.event_press or self.esc_press:  # confirm or esc, close option menu
                self.esc_menu_mode = "menu"  # go back to start_set esc menu
                self.remove_from_ui_menu_updater(self.esc_option_menu_button, self.esc_slider_menu.values(),
                                                 self.esc_value_boxes.values(),
                                                 self.esc_option_text.values())  # remove option menu sprite
                self.add_to_ui_menu_updater(self.grand_menu_button.values())  # add start_set esc menu buttons back


def back_to_grand_state(self):
    self.remove_from_ui_menu_updater(self.grand_menu_button.values(), self.esc_option_menu_button,
                                     self.esc_slider_menu.values(),
                                     self.esc_value_boxes.values(), self.esc_option_text.values())
    if self.current_music:
        self.music_channel.unpause()
    for sound_ch in self.effect_sound_channels:
        if sound_ch.get_busy():  # unpause all sound playing
            sound_ch.unpause()
    self.change_game_state("grand")
