import webbrowser

browser = webbrowser.get()


def menu_main(self, esc_press):
    if self.start_game_button.event:  # preset map list menu
        self.menu_state = "char"
        self.play_map_type = "preset"

        self.remove_ui_updater(self.mainmenu_button)
        self.add_ui_updater(self.char_menu_buttons)

    elif self.lore_button.event:  # open lorebook
        self.menu_state = "lorebook"
        self.add_ui_updater(self.lorebook_stuff)  # add sprite related to lorebook
        self.lorebook.change_section(0, self.lore_name_list, self.subsection_name, self.tag_filter_name,
                                     self.lore_name_list.scroll, self.filter_tag_list, self.filter_tag_list.scroll)

    elif self.option_button.event:  # change main menu to option menu
        self.menu_state = "option"
        self.remove_ui_updater(self.mainmenu_button)

        self.add_ui_updater(self.option_menu_button, self.option_menu_sliders.values(), self.value_boxes.values(),
                            self.option_text_list, self.hide_background)

    elif self.quit_button.event or esc_press:  # open quit game confirmation input
        self.activate_input_popup(("confirm_input", "quit"), "Quit Game?", self.confirm_ui_popup)

    elif self.discord_button.event_press and not self.url_delay:
        browser.open(self.discord_button.url)
        self.url_delay = 2

    elif self.github_button.event_press and not self.url_delay:
        browser.open(self.github_button.url)
        self.url_delay = 2

    elif self.youtube_button.event_press and not self.url_delay:
        browser.open(self.youtube_button.url)
        self.url_delay = 2
