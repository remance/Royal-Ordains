import sys

from pygame import quit as pg_quit

from engine.uimenu.uimenu import ListAdapter
from engine.utils.common import edit_config


def state_menu_process(self):
    # update battle scene first here
    self.ui_menu_updater.update(self.true_dt)  # update ui before more specific update

    self.scene.update()
    self.camera.update(self.battle_camera_object_drawer)

    self.camera.update(self.battle_camera_ui_drawer)
    self.camera.out_update(self.outer_ui_updater)
    self.ui_menu_drawer.draw(self.screen)  # draw the UI

    if self.input_popup:  # currently, have input pop up on screen, stop everything else until done
        if self.input_ok_button.event_press:
            self.change_pause_update(False)
            self.input_box.render_text("")
            input_popup = self.input_popup[1]
            self.input_popup = None
            self.remove_from_ui_menu_updater(self.input_popup_uis, self.confirm_popup_uis)

            if input_popup == "quit":  # quit game
                pg_quit()
                sys.exit()
            elif input_popup == "end_battle":
                self.back_to_battle_state()
                if self.grand:
                    return  # TODO add here updated battle state to return for auto battle state
                return False

        elif self.input_cancel_button.event_press or self.esc_press:
            self.change_pause_update(False)
            self.input_box.render_text("")
            self.input_popup = None
            self.remove_from_ui_menu_updater(self.input_popup_uis, self.confirm_popup_uis)

    else:
        if self.esc_press and self.esc_menu_mode == "menu":  # in menu or option
            self.back_to_battle_state()

        elif self.esc_menu_mode == "menu":  # esc menu
            for key, button in self.battle_menu_button.items():
                if button.event_press:
                    if key == "resume":  # resume battle
                        self.back_to_battle_state()

                    elif key == "log":  # open battle log
                        self.esc_menu_mode = "battle"  # change to dialogue menu mode
                        self.remove_from_ui_menu_updater(self.battle_menu_button.values(),
                                                         self.scene_translation_text_popup)  # remove start_set esc menu button
                        self.dialogue_box.__init__(self.dialogue_box.origin, self.dialogue_box.pivot,
                                                   self.dialogue_box.relative_size_inside_container,
                                                   ListAdapter([" ".join(item[0]) + item[1] for item in
                                                                self.save_data.save_profile["battle log"]]),
                                                   self.dialogue_box.parent,
                                                   self.dialogue_box.visible_list_capacity,
                                                   layer=self.dialogue_box._layer)
                        self.add_to_ui_menu_updater(self.esc_dialogue_button, self.dialogue_box)

                    elif key == "option":  # open option menu
                        self.esc_menu_mode = "option"  # change to option menu mode

                        self.remove_from_ui_menu_updater(self.battle_menu_button.values(),
                                                         self.scene_translation_text_popup)  # remove start_set esc menu button
                        self.add_to_ui_menu_updater(self.esc_option_menu_button, self.esc_slider_menu.values(),
                                                    self.esc_value_boxes.values(), self.esc_option_text.values())

                    elif key == "end":  # end battle
                        self.activate_input_popup(("confirm_input", "end_battle"),
                                                  self.grab_text(("ui", "input_leave_battle")),
                                                  self.confirm_popup_uis)

                    elif key == "quit":  # quit game
                        self.activate_input_popup(("confirm_input", "quit"),
                                                  self.grab_text(("ui", "input_quit_game")),
                                                  self.confirm_popup_uis)
                    break  # found clicked button, break loop

        elif self.esc_menu_mode == "battle":  # battle log
            if self.esc_dialogue_button.event_press or self.esc_press:  # confirm or esc, close option menu
                self.esc_menu_mode = "menu"  # go back to start_set esc menu
                self.remove_from_ui_menu_updater(self.esc_dialogue_button,
                                                 self.dialogue_box)  # remove option menu sprite
                self.add_to_ui_menu_updater(self.battle_menu_button.values(),
                                            self.scene_translation_text_popup)  # add start_set esc menu buttons back

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
                self.add_to_ui_menu_updater(self.battle_menu_button.values(),
                                            self.scene_translation_text_popup)  # add start_set esc menu buttons back


def back_to_battle_state(self):
    self.remove_from_ui_menu_updater(self.battle_menu_button.values(), self.esc_option_menu_button,
                                     self.esc_slider_menu.values(),
                                     self.esc_value_boxes.values(), self.esc_option_text.values(), self.cursor,
                                     self.scene_translation_text_popup)
    self.outer_ui_updater.add(self.battle_cursor)

    self.music_channel.set_volume(self.play_music_volume)
    self.music_channel.unpause()

    self.ambient_channel.set_volume(self.play_effect_volume)
    self.ambient_channel.unpause()

    self.weather_ambient_channel.set_volume(self.play_effect_volume)
    self.weather_ambient_channel.unpause()

    for sound_ch in self.effect_sound_channels:
        if sound_ch.get_busy():  # unpause all sound playing
            sound_ch.set_volume(self.play_effect_volume)
            sound_ch.unpause()
    self.change_game_state("battle")
