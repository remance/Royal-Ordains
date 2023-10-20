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
        all_ready = True
        for player, item in self.player_char_select.items():
            if self.player_char_selectors[player].mode not in ("ready", "empty"):
                all_ready = False
                break
        if all_ready:
            self.start_battle(1, 1, 1, players={key: value for key, value in
                                                self.player_char_select.items() if value})

    else:

        for key_list in (self.player_key_press, self.player_key_hold):
            for player in key_list:
                for key, pressed in key_list[player].items():
                    if pressed:
                        selector = self.player_char_selectors[player]
                        if selector.mode == "stat" and key in ("Up", "Down", "Left", "Right"):
                            self.player_char_stats[player].player_input(key)

        for player in self.player_key_press:
            for key, pressed in self.player_key_press[player].items():
                if pressed:
                    selector = self.player_char_selectors[player]
                    if selector.mode == "empty":
                        selector.change_mode("Vraesier")
                    elif key == "Left" and selector.mode != "stat":  # switch to previous in playable_character list
                        if selector.mode != "ready":
                            current_id = tuple(playable_character.keys()).index(selector.mode)
                            if current_id - 1 < 0:
                                current_id = tuple(playable_character.values())[-1]
                            else:
                                current_id -= 1
                            selector.change_mode(tuple(playable_character.keys())[current_id])
                    elif key == "Right" and selector.mode != "stat":  # switch to next in playable_character list
                        if selector.mode != "ready":
                            current_id = tuple(playable_character.keys()).index(selector.mode)
                            if current_id + 1 > len(playable_character) - 1:  # reach the end of char list, go back to first
                                current_id = 0
                            else:
                                current_id += 1
                            selector.change_mode(tuple(playable_character.keys())[current_id])
                    elif key == "Weak":
                        if selector.mode not in ("stat", "ready"):  # go to stat allocation
                            start_stat = self.character_data.character_list[selector.mode]
                            skill_list = {}
                            for skill in self.character_data.character_list[selector.mode]["Skill"].values():
                                for key, value in skill.items():
                                    if ".1" in key and "C" in key:
                                        skill_list[value["Name"]] = 0
                            start_stat = {key: value for key, value in start_stat.items() if
                                          key in self.player_char_stats[player].stat_row} | \
                                         {key: value for key, value in start_stat.items() if
                                          key in self.player_char_stats[player].common_skill_row} | skill_list
                            start_stat["Status Remain"] = 100
                            start_stat["Skill Remain"] = 2
                            start_stat["ID"] = selector.mode

                            selector.change_mode("stat")
                            self.add_ui_updater(self.player_char_stats[player])
                            self.player_char_stats[player].add_stat(start_stat)

                        else:
                            self.player_char_select[player] = {"ID": self.player_char_stats[player].stat["ID"]} | \
                                                              default_start | self.player_char_stats[player].stat | \
                                                              {"Skill Allocation": {key: value for key, value in
                                                                self.player_char_stats[player].stat.items() if key in self.player_char_stats[player].all_skill_row}}
                            selector.change_mode("ready")

                    elif key == "Strong":
                        if selector.mode == "ready":
                            selector.change_mode("stat")
                        elif selector.mode != "stat":  # remove player
                            self.player_char_select[player] = None
                            selector.change_mode("empty")
                        else:  # go back to select char
                            self.player_char_select[player] = None
                            selector.change_mode("Vraesier")
                            self.remove_ui_updater(self.player_char_stats[player])
