from engine.utils.common import stat_allocation_check

playable_character = {"Vraesier": 0, "Rodhinbar": 1}
default_start = {"Sprite Ver": 1, "Team": 1, "Playable": True, "Skill Allocation": {}, "Start Health": 100}


def menu_char(self, esc_press):
    if self.char_back_button.event_press or esc_press:  # back to start_set menu
        self.player_char_select = {1: None, 2: None, 3: None, 4: None}
        for selector in self.player_char_selectors.values():
            selector.change_mode("empty")
        self.remove_ui_updater(self.char_menu_button, self.player1_char_selector, self.player2_char_selector,
                               self.player3_char_selector, self.player4_char_selector, self.player1_char_stat,
                               self.player2_char_stat, self.player3_char_stat, self.player4_char_stat)
        self.back_mainmenu()

    elif self.start_button.event:
        for player, item in self.player_char_select.items():
            all_ready = True
            if (self.player_char_selectors[player].mode == "complete" and not item) or \
                    self.player_char_selectors[player].mode != "empty":
                all_ready = False
            if all_ready:
                self.start_battle(1, 1, 1, players={key: value for key, value in
                                                    self.player_char_select.items() if value})

    else:
        for player in self.player_key_press:
            for key, pressed in self.player_key_press[player].items():
                if pressed:
                    selector = self.player_char_selectors[player]
                    if selector.mode == "empty":
                        selector.change_mode("Vraesier")
                    elif key == "Up":
                        if selector.mode == "stat":
                            self.player_char_stats[player].current_row -= 1
                            if self.player_char_stats[player].current_row < 0:
                                self.player_char_stats[player].current_row = 6
                            self.player_char_stats[player].add_stat(self.player_char_stats[player].stat)
                    elif key == "Down":
                        if selector.mode == "stat":
                            self.player_char_stats[player].current_row += 1
                            if self.player_char_stats[player].current_row > 6:
                                self.player_char_stats[player].current_row = 0
                            self.player_char_stats[player].add_stat(self.player_char_stats[player].stat)
                    elif key == "Left":  # switch to previous in playable_character list
                        if selector.mode != "stat":
                            current_id = tuple(playable_character.keys()).index(selector.mode)
                            if current_id - 1 < 0:
                                current_id = tuple(playable_character.values())[-1]
                            else:
                                current_id -= 1
                            selector.change_mode(tuple(playable_character.keys())[current_id])
                        else:
                            self.player_char_stats[player].change_stat(
                                self.player_char_stats[player].stat_row[self.player_char_stats[player].current_row], "down")
                    elif key == "Right":  # switch to next in playable_character list
                        if selector.mode != "stat":
                            current_id = tuple(playable_character.keys()).index(selector.mode)
                            if current_id + 1 > len(playable_character) - 1:  # reach the end of char list, go back to first
                                current_id = 0
                            else:
                                current_id += 1
                            selector.change_mode(tuple(playable_character.keys())[current_id])
                        else:
                            self.player_char_stats[player].change_stat(
                                self.player_char_stats[player].stat_row[self.player_char_stats[player].current_row], "up")
                    elif key == "Weak":
                        if selector.mode != "stat":  # go to stat allocation
                            start_stat = self.character_data.character_list[selector.mode]
                            start_stat = {key: value for key, value in start_stat.items() if
                                          key in self.player_char_stats[player].stat_row}
                            start_stat["Remain"] = 100
                            selector.change_mode("stat")
                            self.add_ui_updater(self.player_char_stats[player])
                            self.player_char_stats[player].add_stat(start_stat)

                        else:
                            self.player_char_select[player] = {"ID": self.player_char_stats[player].stat["ID"]} | \
                                                              default_start | self.player_char_stats[player].stat
                            selector.mode = "complete"

                    elif key == "Strong":
                        if selector.mode != "stat":  # remove player
                            self.player_char_select[player] = None
                            selector.change_mode("empty")
                        else:  # go back to select char
                            self.player_char_select[player] = None
                            selector.change_mode("Vraesier")
                            self.remove_ui_updater(self.player_char_stats[player])
