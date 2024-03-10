from os.path import join as path_join


def write_all_player_save(self):
    for player, slot in self.profile_index.items():  # save data for all active player before start next mission
        if self.player_char_selectors[player].mode != "empty":
            self.save_data.make_save_file(path_join(self.main_dir, "save", str(slot) + ".dat"),
                                          self.battle.all_story_profiles[player])
