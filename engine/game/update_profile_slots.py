def update_profile_slots(self, player):
    for key, value in self.char_profile_boxes[player].items():
        # update all profile slot showing
        selected = False
        if key + (self.profile_page[player] * 4) == self.profile_index[player]:
            selected = True
        else:  # check for taken slots
            for player2 in self.profile_page:
                if player != player2 and key + (self.profile_page[player] * 4) == self.profile_index[player2] and \
                        self.player_char_selectors[player2].mode != "empty":  # marked as taken by another player
                    selected = 1
                    break
        if key + (self.profile_page[player] * 4) in self.save_data.save_profile["character"]:
            data = self.save_data.save_profile["character"][key + (self.profile_page[player] * 4)]
            value.change_profile(str(key + (self.profile_page[player] * 4)), data, selected)
        else:
            value.change_profile(str(key + (self.profile_page[player] * 4)), {}, selected)
