from pygame.mixer import Channel

from engine.uimenu.uimenu import ListAdapter
from engine.utils.common import edit_config


def escmenu_process(self):
    """
    User interaction processing for ESC menu during battle
    :param self: Battle object
    :return: special command that process in battle loop
    """
    if self.esc_press and self.esc_menu_mode == "menu":  # in menu or option
        self.back_to_battle_state()

    elif self.esc_menu_mode == "menu":  # esc menu
        for key, button in self.battle_menu_button.items():
            if button.event_press:
                if key == "resume":  # resume battle
                    self.back_to_battle_state()

                elif key == "log":  # open dialogue log
                    self.esc_menu_mode = "dialogue"  # change to dialogue menu mode
                    self.remove_from_ui_updater(self.battle_menu_button.values(),
                                                self.scene_translation_text_popup)  # remove start_set esc menu button
                    self.dialogue_box.__init__(self.dialogue_box.origin, self.dialogue_box.pivot,
                                               self.dialogue_box.relative_size_inside_container,
                                               ListAdapter([" ".join(item[0]) + self.localisation.grab_text(
                                                   ("event", item[1], "Text")) for item in
                                                            self.save_data.save_profile["dialogue log"]]),
                                               self.dialogue_box.parent,
                                               self.dialogue_box.visible_list_capacity,
                                               layer=self.dialogue_box._layer)
                    self.add_to_ui_updater(self.esc_dialogue_button, self.dialogue_box)

                elif key == "option":  # open option menu
                    self.esc_menu_mode = "option"  # change to option menu mode
                    self.remove_from_ui_updater(self.battle_menu_button.values(),
                                                self.scene_translation_text_popup)  # remove start_set esc menu button
                    self.add_to_ui_updater(self.esc_option_menu_button, self.esc_slider_menu.values(),
                                           self.esc_value_boxes.values(), self.esc_option_text.values())

                elif key == "end":  # end battle
                    self.activate_input_popup(("confirm_input", "end_battle"),
                                              self.localisation.grab_text(("ui", "Leave Battle?")),
                                              self.confirm_popup_uis)

                elif key == "quit":  # quit game
                    self.activate_input_popup(("confirm_input", "quit"),
                                              self.localisation.grab_text(("ui", "Quit Game?")),
                                              self.confirm_popup_uis)
                break  # found clicked button, break loop

    elif self.esc_menu_mode == "dialogue":  # dialogue log
        if self.esc_dialogue_button.event_press or self.esc_press:  # confirm or esc, close option menu
            self.esc_menu_mode = "menu"  # go back to start_set esc menu
            self.remove_from_ui_updater(self.esc_dialogue_button, self.dialogue_box)  # remove option menu sprite
            self.add_to_ui_updater(self.battle_menu_button.values(),
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
            self.remove_from_ui_updater(self.esc_option_menu_button, self.esc_slider_menu.values(),
                                        self.esc_value_boxes.values(),
                                        self.esc_option_text.values())  # remove option menu sprite
            self.add_to_ui_updater(self.battle_menu_button.values(),
                                   self.scene_translation_text_popup)  # add start_set esc menu buttons back


def back_to_battle_state(self):
    self.remove_from_ui_updater(self.battle_menu_button.values(), self.esc_option_menu_button,
                                self.esc_slider_menu.values(),
                                self.esc_value_boxes.values(), self.esc_option_text.values(), self.cursor,
                                self.scene_translation_text_popup)
    self.outer_ui_updater.add(self.battle_cursor)
    if self.current_music:
        self.music.unpause()
    for sound_ch in range(0, 1000):
        if Channel(sound_ch).get_busy():  # unpause all sound playing
            Channel(sound_ch).unpause()
    self.change_game_state("battle")
