from pygame.mixer import Channel

from engine.uimenu.uimenu import ListAdapter
from engine.utils.common import edit_config


def escmenu_process(self, esc_press: bool):
    """
    User interaction processing for ESC menu during battle
    :param self: Battle object
    :param esc_press: esc button
    :return: special command that process in battle loop
    """
    if esc_press and self.esc_menu_mode == "menu":  # in menu or option
        self.back_to_battle_state()

    elif self.esc_menu_mode == "menu":  # esc menu
        if self.city_mode:  # check for keyboard input with char stat
            for key_list in (self.player_key_press, self.player_key_hold):
                # check key holding for stat mode as well
                for player in key_list:
                    if player in self.player_objects:
                        for key, pressed in key_list[player].items():
                            if pressed:
                                self.player_char_interfaces[player].player_input(key)

        for button in self.battle_menu_button:
            if button.event_press:
                if button.text == "Resume":  # resume battle
                    self.back_to_battle_state()

                elif button.text == "Encyclopedia":  # open lorebook
                    self.esc_menu_mode = "lorebook"  # change to enclycopedia mode
                    self.add_ui_updater(self.lorebook_stuff)  # add sprite related to lorebook
                    self.lorebook.change_section(0, self.lore_name_list, self.subsection_name,
                                                 self.tag_filter_name,
                                                 self.lore_name_list.scroll, self.filter_tag_list,
                                                 self.filter_tag_list.scroll)
                    self.remove_ui_updater(self.battle_menu_button, self.esc_slider_menu.values(),
                                           self.esc_value_boxes.values(),
                                           self.esc_option_text.values(),
                                           self.stage_translation_text_popup)  # remove menu sprite

                elif button.text == "Dialogue Log":  # open dialogue log
                    self.esc_menu_mode = "dialogue"  # change to dialogue menu mode
                    self.remove_ui_updater(self.battle_menu_button,
                                           self.stage_translation_text_popup)  # remove start_set esc menu button
                    self.dialogue_box.__init__(self.dialogue_box.origin, self.dialogue_box.pivot,
                                               self.dialogue_box.relative_size_inside_container,
                                               ListAdapter([" ".join(item) for item in
                                                            self.main_story_profile["dialogue log"]]),
                                               self.dialogue_box.parent,
                                               self.dialogue_box.visible_list_capacity,
                                               layer=self.dialogue_box._layer)
                    self.add_ui_updater(self.esc_dialogue_button, self.dialogue_box)

                elif button.text == "Option":  # open option menu
                    self.esc_menu_mode = "option"  # change to option menu mode
                    self.remove_ui_updater(self.battle_menu_button,
                                           self.stage_translation_text_popup)  # remove start_set esc menu button
                    self.add_ui_updater(self.esc_option_menu_button, self.esc_slider_menu.values(),
                                        self.esc_value_boxes.values(), self.esc_option_text.values())

                elif button.text == "End Battle":  # back to city
                    self.activate_input_popup(("confirm_input", "end_battle"), "Leave Battle?", self.confirm_ui_popup)

                elif button.text == "Main Menu":  # back to start_set menu
                    self.activate_input_popup(("confirm_input", "main_menu"), "To Main Menu?", self.confirm_ui_popup)

                elif button.text == "Desktop":  # quit self
                    self.activate_input_popup(("confirm_input", "quit"), "Quit Game?", self.confirm_ui_popup)
                break  # found clicked button, break loop
            else:
                button.image = button.images[0]

    elif self.esc_menu_mode == "lorebook":  # lore book
        command = self.lorebook_process(esc_press)
        if command == "exit":
            self.esc_menu_mode = "menu"  # go back to start_set esc menu
            self.add_ui_updater(self.battle_menu_button,
                                self.stage_translation_text_popup)  # add start_set esc menu buttons back

    elif self.esc_menu_mode == "dialogue":  # dialogue log
        if self.esc_dialogue_button.event_press or esc_press:  # confirm or esc, close option menu
            self.esc_menu_mode = "menu"  # go back to start_set esc menu
            self.remove_ui_updater(self.esc_dialogue_button, self.dialogue_box)  # remove option menu sprite
            self.add_ui_updater(self.battle_menu_button,
                                self.stage_translation_text_popup)  # add start_set esc menu buttons back

    elif self.esc_menu_mode == "option":  # option menu
        for key, value in self.esc_slider_menu.items():
            if value.event:  # press on slider bar
                value.player_input(self.esc_value_boxes[key])  # update slider button based on mouse value
                edit_config("USER", key + "_volume", value.value, self.game.config_path,
                            self.config)
                self.game.change_sound_volume()

        if self.esc_option_menu_button.event_press or esc_press:  # confirm or esc, close option menu
            self.esc_menu_mode = "menu"  # go back to start_set esc menu
            self.remove_ui_updater(self.esc_option_menu_button, self.esc_slider_menu.values(),
                                   self.esc_value_boxes.values(),
                                   self.esc_option_text.values())  # remove option menu sprite
            self.add_ui_updater(self.battle_menu_button,
                                self.stage_translation_text_popup)  # add start_set esc menu buttons back


def back_to_battle_state(self):
    for interface in self.player_char_interfaces.values():
        interface.change_mode("stat")

    self.remove_ui_updater(self.battle_menu_button, self.esc_option_menu_button,
                           self.esc_slider_menu.values(),
                           self.esc_value_boxes.values(), self.esc_option_text.values(), self.cursor,
                           self.stage_translation_text_popup, self.player_char_base_interfaces.values(),
                           self.player_char_interfaces.values())
    self.realtime_ui_updater.add(self.main_player_battle_cursor)
    for sound_ch in range(0, 1000):
        if Channel(sound_ch).get_busy():  # pause all sound playing
            Channel(sound_ch).unpause()
    self.change_game_state("battle")


def popout_encyclopedia(self, section, subsection):
    self.esc_menu_mode = "lorebook"  # change to enclycopedia mode
    self.add_ui_updater(self.lorebook_stuff)  # add sprite related to lorebook
    self.lorebook.change_section(section, self.lore_name_list,
                                 self.subsection_name, self.tag_filter_name,
                                 self.lore_name_list.scroll, self.filter_tag_list,
                                 self.filter_tag_list.scroll)
    self.lorebook.change_subsection(subsection)
    self.remove_ui_updater(self.battle_menu_button, self.esc_slider_menu.values(),
                           self.esc_value_boxes.values(), self.esc_option_text.values(),
                           self.stage_translation_text_popup)  # remove menu sprite
