import webbrowser

browser = webbrowser.get()


def menu_main(self):
    if self.custom_battle_button.event:
        self.start_battle("test")

    # if self.start_game_button.event:  # start new game
    #     self.menu_state = "char"
    #     self.play_map_type = "preset"
    #     self.background = self.background_image["char_background"]
    #     for interface in self.player_char_interfaces.values():
    #         interface.remake()
    #     self.remove_ui_updater(self.mainmenu_button, self.main_menu_actor)
    #     self.add_ui_updater(self.char_menu_buttons)
    #
    # elif self.load_game_button.event:  # load save
    #     self.start_battle(self.mission_selected)

    elif self.option_button.event:  # change main menu to option menu
        self.menu_state = "option"
        self.remove_ui_updater(self.mainmenu_button)

        self.add_ui_updater(self.option_menu_button, self.option_menu_sliders.values(), self.value_boxes.values(),
                            self.option_text_list, self.hide_background)

    elif self.quit_button.event or self.esc_press:  # open quit game confirmation input
        self.activate_input_popup(("confirm_input", "quit"), "Quit Game?", self.confirm_ui_popup)
