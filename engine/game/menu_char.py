playable_character = {"Vraesier": 0, "Rodhinbar": 1}
default_stat = {"Sprite Ver": 1, "Team": 1, "Playable": True, "Skill Allocation": {}}


def menu_char(self, esc_press):
    if self.back_button.event_press or esc_press:  # back to start_set menu
        self.player_char_select = {1: None, 2: None, 3: None, 4: None}
        for selector in self.player_char_selectors.values():
            selector.image = selector.images["Empty"]
        self.remove_ui_updater(self.char_menu_button)
        self.back_mainmenu()

    elif self.start_button.event and any(item is not None for item in self.player_char_select.values()):
        self.start_battle(1, 1, 1, players={key: value for key, value in self.player_char_select.items() if value})

    else:
        for player in self.player_key_press:
            for key, pressed in self.player_key_press[player].items():
                if pressed:
                    if not self.player_char_select[player]:
                        self.player_char_select[player] = {"ID": "Vraesier"} | default_stat
                        self.player_char_selectors[player].image = self.player_char_selectors[player].images["Vraesier"]
                    elif key == "Left":  # switch to previous in playable_character list
                        current_id = playable_character[self.player_char_select[player]["ID"]]
                        if current_id - 1 < 0:
                            current_id = tuple(playable_character.values())[-1]
                        else:
                            current_id -= 1
                        self.player_char_select[player] = {"ID": tuple(playable_character.keys())[current_id]} | \
                                                          default_stat
                        self.player_char_selectors[player].image = \
                            self.player_char_selectors[player].images[self.player_char_select[player]["ID"]]
                    elif key == "Right":  # switch to next in playable_character list
                        current_id = playable_character[self.player_char_select[player]["ID"]]
                        if current_id + 1 > len(playable_character) - 1:  # reach the end of char list, go back to first
                            current_id = 0
                        else:
                            current_id += 1
                        self.player_char_select[player] = {"ID": tuple(playable_character.keys())[current_id]} | default_stat
                        self.player_char_selectors[player].image = \
                            self.player_char_selectors[player].images[self.player_char_select[player]["ID"]]
                    elif key == "Strong":
                        self.player_char_select[player] = None
                        self.player_char_selectors[player].image = self.player_char_selectors[player].images["Empty"]
