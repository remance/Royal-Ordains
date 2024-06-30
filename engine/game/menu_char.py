import copy
from datetime import datetime
from os.path import join as path_join

from engine.data.datasave import empty_character_save

inf = float("inf")

playable_character = {"Vraesier": 0, "Rodhinbar": 1, "Iri": 2, "Duskuksa": 3, "Nayedien": 4}  # , "Orsanoas": 5
new_start = {"Sprite Ver": 1, "skill allocation": {}}


def menu_char(self, esc_press):
    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    if self.char_back_button.event_press or esc_press:  # back to start_set menu
        self.player_char_select = {1: None, 2: None, 3: None, 4: None}
        self.profile_page = {1: 0, 2: 0, 3: 0, 4: 0}
        self.profile_index = {1: 1, 2: 1, 3: 1, 4: 1}
        for selector in self.player_char_selectors.values():
            selector.change_mode("empty")
        self.remove_ui_updater(self.char_menu_buttons, self.player_char_selectors.values(),
                               self.player_char_interfaces.values(),
                               [item2 for item in self.char_profile_boxes.values() for item2 in item.values()],
                               self.char_profile_page_text.values(),
                               self.char_interface_text_popup.values())
        self.back_mainmenu()

    elif self.start_button.event:
        all_ready = True
        if len([player for player in self.player_char_selectors.values() if player.mode == "empty"]) == 4:  # all empty
            all_ready = False
        else:
            for player, item in self.player_char_select.items():
                if self.player_char_selectors[player].mode not in ("ready", "readymain", "empty"):
                    all_ready = False  # some not ready
                    break
        if all_ready:
            main_story_player = 1  # find which player has the lowest progress to use as main
            last_check_progress = inf
            self.battle.all_story_profiles = {1: None, 2: None, 3: None, 4: None}
            for key, selector in self.player_char_selectors.items():
                if selector.mode in ("ready", "readymain"):
                    progress = (int(self.save_data.save_profile["character"][self.profile_index[key]][
                                        "chapter"]) * 100) + \
                               int(self.save_data.save_profile["character"][self.profile_index[key]][
                                       "mission"])
                    if progress < last_check_progress:  # found player with lower progress
                        main_story_player = key
                        last_check_progress = progress
                    self.battle.all_story_profiles[key] = self.save_data.save_profile["character"][
                        self.profile_index[key]]

            self.battle.main_story_profile = self.save_data.save_profile["character"][
                self.profile_index[main_story_player]]
            self.battle.main_player = main_story_player
            players = {key: self.save_data.save_profile["character"][self.profile_index[key]]["character"] for
                       key, value in
                       self.player_char_select.items() if value}

            self.start_battle("1", "1", "1", players=players)

            # start in throne room of current chapter and mission of the lowest progress player
            # self.start_battle(
            #     self.save_data.save_profile["character"][self.profile_index[main_story_player]]["chapter"],
            #     self.save_data.save_profile["character"][self.profile_index[main_story_player]]["mission"],
            #     "0", players=players, scene="throne")

            # self.start_battle(
            #     self.save_data.save_profile["character"][self.profile_index[main_story_player]]["chapter"],
            #     self.save_data.save_profile["character"][self.profile_index[main_story_player]]["mission"],
            #     "0", players=players, scene="peace")

            # self.start_battle(
            #     self.save_data.save_profile["character"][self.profile_index[main_story_player]]["chapter"],
            #     self.save_data.save_profile["character"][self.profile_index[main_story_player]]["mission"],
            #     "training", players=players)

    else:
        for key_list in (self.player_key_press, self.player_key_hold):  # check key holding for stat mode as well
            for player in key_list:
                for key, pressed in key_list[player].items():
                    if pressed:
                        selector = self.player_char_selectors[player]
                        if selector.mode == "stat":
                            self.player_char_interfaces[player].player_input(key)

        for player in self.player_key_press:
            for key_press, pressed in self.player_key_press[player].items():
                if pressed:
                    selector = self.player_char_selectors[player]
                    if selector.mode == "empty":  # empty player become active with any button press
                        selector.change_mode("profile")
                        last_page = "2"
                        if tuple(self.save_data.save_profile["character"].keys()):
                            last = tuple(self.save_data.save_profile["character"].keys())[-1]
                            last_page = str(int(last / 4) + 2)
                        self.char_profile_page_text[player].rename(str(self.profile_page[player] + 1) + "/" + last_page)
                        self.add_ui_updater([item for item in self.char_profile_boxes[player].values()],
                                            self.char_profile_page_text[player])
                        # check and find non-occupied slot
                        self.profile_index[player] = check_other_player_select_slot(self, player)
                        for player2 in self.profile_page:
                            self.update_profile_slots(player2)

                    elif key_press == "Left":
                        if selector.mode == "profile":
                            new_page = self.profile_page[player] - 1
                            if new_page < 0:  # go to last page
                                if tuple(self.save_data.save_profile["character"].keys()):
                                    new_page = int((tuple(self.save_data.save_profile["character"].keys())[-1]) / 4) + 1
                                else:
                                    new_page = 1
                            self.profile_index[player] = ((new_page * 4) + self.profile_index[player]) - (
                                    self.profile_page[player] * 4)
                            self.profile_page[player] = new_page
                            self.profile_index[player] = check_other_player_select_slot(self, player)

                            last_page = "2"
                            if tuple(self.save_data.save_profile["character"].keys()):
                                last = tuple(self.save_data.save_profile["character"].keys())[-1]
                                last_page = str(int(last / 4) + 2)
                            self.char_profile_page_text[player].rename(
                                str(self.profile_page[player] + 1) + "/" + last_page)
                            for player2 in self.profile_page:
                                self.update_profile_slots(player2)
                        elif selector.mode not in (
                                "stat", "ready", "readymain"):  # switch to previous in playable_character list
                            if "1" in selector.mode:  # currently in description mode, go to normal
                                selector.change_mode(selector.mode[:-1])
                            current_id = tuple(playable_character.keys()).index(selector.mode)
                            if current_id - 1 < 0:
                                current_id = tuple(playable_character.values())[-1]
                            else:
                                current_id -= 1
                            selector.change_mode(tuple(playable_character.keys())[current_id])

                    elif key_press == "Right":
                        if selector.mode == "profile":
                            new_page = self.profile_page[player] + 1
                            if not tuple(self.save_data.save_profile["character"].keys()):
                                if new_page > 1:
                                    new_page = 0
                            elif new_page > int((tuple(self.save_data.save_profile["character"].keys())[
                                -1]) / 4) + 1:  # go to first page
                                new_page = 0
                            self.profile_index[player] = ((new_page * 4) + self.profile_index[player]) - (
                                    self.profile_page[player] * 4)
                            self.profile_page[player] = new_page
                            self.profile_index[player] = check_other_player_select_slot(self, player)
                            last_page = "2"
                            if tuple(self.save_data.save_profile["character"].keys()):
                                last = tuple(self.save_data.save_profile["character"].keys())[-1]
                                last_page = str(int(last / 4) + 2)
                            self.char_profile_page_text[player].rename(
                                str(self.profile_page[player] + 1) + "/" + last_page)
                            for player2 in self.profile_page:
                                self.update_profile_slots(player2)
                        elif selector.mode not in (
                                "stat", "ready", "readymain"):  # switch to next in playable_character list
                            if "1" in selector.mode:  # currently in description mode, go to normal
                                selector.change_mode(selector.mode[:-1])
                            current_id = tuple(playable_character.keys()).index(selector.mode)
                            if current_id + 1 > len(
                                    playable_character) - 1:  # reach the end of char list, go back to first
                                current_id = 0
                            else:
                                current_id += 1
                            selector.change_mode(tuple(playable_character.keys())[current_id])

                    elif key_press == "Down":
                        if selector.mode == "profile":
                            self.profile_index[player] += 1
                            if self.profile_index[player] > (self.profile_page[player] * 4) + 4:
                                self.profile_index[player] = (self.profile_page[player] * 4) + 1
                            self.profile_index[player] = check_other_player_select_slot(self, player)
                            for player2 in self.profile_page:
                                self.update_profile_slots(player2)
                        elif selector.mode not in ("stat", "ready", "readymain"):  # switch to character description
                            if "1" in selector.mode:  # currently in description mode, go to normal
                                selector.change_mode(selector.mode[:-1])
                            else:
                                selector.change_mode(selector.mode + "1")

                    elif key_press == "Up":
                        if selector.mode == "profile":
                            self.profile_index[player] -= 1
                            if self.profile_index[player] < (self.profile_page[player] * 4) + 1:
                                self.profile_index[player] = (self.profile_page[player] * 4) + 4
                            self.profile_index[player] = check_other_player_select_slot(self, player, descend=False)
                            for player2 in self.profile_page:
                                self.update_profile_slots(player2)

                    elif key_press == "Weak" and not selector.delay:  # confirm
                        if selector.mode == "profile":
                            self.remove_ui_updater([item for item in self.char_profile_boxes[player].values()],
                                                   self.char_profile_page_text[player])
                            if self.profile_index[player] in self.save_data.save_profile["character"]:
                                save_profile = self.save_data.save_profile["character"][self.profile_index[player]]
                                selector.change_mode("stat")
                                self.add_ui_updater(self.player_char_interfaces[player])
                                self.player_char_interfaces[player].add_profile(save_profile)
                            else:  # start character selection for empty profile slot
                                self.player_char_interfaces[player].profile = {}
                                selector.change_mode(tuple(playable_character.keys())[0])

                        elif selector.mode not in ("stat", "ready", "readymain"):  # go to stat allocation
                            if "1" in selector.mode:  # currently in description mode, go to normal first
                                selector.mode = selector.mode[:-1]
                            start_stat = self.character_data.character_list[selector.mode]
                            skill_list = {}
                            for key, value in self.character_data.character_list[selector.mode]["Skill UI"].items():
                                if ".1" in key and "C" in key:  # starting character skill
                                    skill_list[value["Name"]] = 0
                            start_stat = {key: value for key, value in start_stat.items() if
                                          key in self.player_char_interfaces[player].stat_row} | \
                                         {key: value for key, value in start_stat.items() if
                                          key in self.player_char_interfaces[player].common_skill_row} | skill_list
                            start_stat["Status Remain"] = 100
                            start_stat["Skill Remain"] = 2
                            start_stat["ID"] = selector.mode

                            selector.change_mode("stat")
                            self.add_ui_updater(self.player_char_interfaces[player])
                            self.player_char_interfaces[player].add_stat(start_stat)

                        else:  # stat to ready
                            self.battle.remove_ui_updater(self.player_char_interfaces[player].text_popup)
                            self.player_char_select[player] = {"ID": self.player_char_interfaces[player].stat["ID"]} | \
                                                              new_start | {key: value for key, value in
                                                                           self.player_char_interfaces[
                                                                               player].stat.items() if
                                                                           key not in self.player_char_interfaces[
                                                                               player].all_skill_row} | \
                                                              {"skill allocation": {key: value for key, value in
                                                                                    self.player_char_interfaces[
                                                                                        player].stat.items() if
                                                                                    key in self.player_char_interfaces[
                                                                                        player].all_skill_row}}
                            slot = self.profile_index[player]  # make save data when ready but not write yet
                            if slot not in self.save_data.save_profile["character"]:  # new profile data
                                self.save_data.save_profile["character"][slot] = copy.deepcopy(empty_character_save)
                            self.save_data.save_profile["character"][slot]["character"] = self.player_char_select[
                                player]
                            # save when press ready
                            self.save_data.save_profile["character"][slot]["last save"] = dt_string
                            self.save_data.make_save_file(path_join(self.main_dir, "save", str(slot) + ".dat"),
                                                          self.save_data.save_profile["character"][slot])
                            selector.change_mode("ready", delay=False)
                            self.remove_ui_updater(self.player_char_interfaces[player].text_popup)
                            main_story_player = 1
                            last_check_progress = inf
                            for key, selector in self.player_char_selectors.items():
                                if selector.mode in ("ready", "readymain"):
                                    progress = (int(self.save_data.save_profile["character"][self.profile_index[key]][
                                                        "chapter"]) * 100) + \
                                               int(self.save_data.save_profile["character"][self.profile_index[key]][
                                                       "mission"])
                                    if progress < last_check_progress:  # found player with lower progress
                                        main_story_player = key
                                        last_check_progress = progress

                            for key, selector in self.player_char_selectors.items():
                                # change mode for all player ready to indicate who get to be main progress
                                if selector.mode in ("ready", "readymain"):
                                    selector.change_mode("ready", delay=False)
                                    if key == main_story_player:
                                        selector.change_mode("readymain", delay=False)
                            for player2 in self.profile_page:
                                self.update_profile_slots(player2)

                            self.player_char_interfaces[player].add_profile(
                                self.save_data.save_profile["character"][slot])

                    elif key_press == "Strong" and not selector.delay:  # cancel, go back to previous state
                        if selector.mode in ("ready", "readymain"):
                            selector.change_mode("stat")

                            main_story_player = 1
                            last_check_progress = inf
                            for key, selector in self.player_char_selectors.items():
                                if selector.mode in ("ready", "readymain"):
                                    progress = (int(self.save_data.save_profile["character"][self.profile_index[key]][
                                                        "chapter"]) * 100) + \
                                               int(self.save_data.save_profile["character"][self.profile_index[key]][
                                                       "mission"])
                                    if progress < last_check_progress:  # found player with lower progress
                                        main_story_player = key
                                        last_check_progress = progress

                            for key, selector in self.player_char_selectors.items():
                                # change mode for all player ready to indicate who get to be main progress
                                if selector.mode in ("ready", "readymain"):
                                    selector.change_mode("ready", delay=False)
                                    if key == main_story_player:
                                        selector.change_mode("readymain", delay=False)
                            for player2 in self.profile_page:
                                self.update_profile_slots(player2)

                        elif selector.mode == "profile":
                            selector.change_mode("empty")
                            self.remove_ui_updater([item for item in self.char_profile_boxes[player].values()],
                                                   self.char_profile_page_text[player])
                        elif selector.mode == "stat":
                            self.player_char_select[player] = None
                            self.remove_ui_updater(self.player_char_interfaces[player],
                                                   self.player_char_interfaces[player].text_popup)
                            if self.profile_index[player] in self.save_data.save_profile["character"]:
                                # back to profile select
                                selector.change_mode("profile")
                                self.add_ui_updater([item for item in self.char_profile_boxes[player].values()],
                                                    self.char_profile_page_text[player])
                                self.profile_index[player] = check_other_player_select_slot(self, player)
                                for player2 in self.profile_page:
                                    self.update_profile_slots(player2)
                            else:  # go back to select char, for new profile
                                selector.change_mode(tuple(playable_character.keys())[0])
                        else:
                            selector.change_mode("profile")
                            self.add_ui_updater([item for item in self.char_profile_boxes[player].values()],
                                                self.char_profile_page_text[player])
                            self.profile_index[player] = check_other_player_select_slot(self, player)
                            for player2 in self.profile_page:
                                self.update_profile_slots(player2)

                    elif key_press == "Guard":
                        if selector.mode == "profile":  # remove profile and save
                            slot = self.profile_index[player]
                            if slot in self.save_data.save_profile["character"]:
                                self.activate_input_popup(("confirm_input", "delete profile", slot),
                                                          "Remove Save " + str(slot) + "?", self.confirm_ui_popup)


def check_other_player_select_slot(self, check_player, descend=True):
    # check if profile slot already selected by another local player
    new_slot = self.profile_index[check_player]
    for player in self.profile_page:
        if player != check_player and self.player_char_selectors[player].mode != "empty":
            # only check for player that is not empty
            if self.profile_index[player] == self.profile_index[check_player]:
                # conflicted with another player, find new unoccupied slot
                search = range(4)
                if not descend:  # move to below slot when occupied
                    search = reversed(search)
                for slot in search:
                    slot_index = slot + 1 + (self.profile_page[player] * 4)
                    if new_slot != slot_index:
                        found_slot = True
                        for player2 in self.profile_page:
                            if self.player_char_selectors[player2].mode != "empty" and \
                                    self.profile_index[player2] == slot_index:
                                found_slot = False
                        if found_slot:
                            new_slot = slot_index
                            break
    return new_slot
