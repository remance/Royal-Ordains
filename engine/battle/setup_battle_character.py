from engine.character.character import Character, AICharacter, PlayableCharacter


def setup_battle_character(self, player_list, stage_char_list, add_helper=True):
    if player_list:
        for key, data in player_list.items():
            self.players[key]["Object"] = PlayableCharacter(key, data | self.character_data.character_list[data["ID"]] |
                                                            {"POS": (300, Character.original_ground_pos),
                                                             "Arrive Condition": []}, key)
    for data in stage_char_list:
        AICharacter(data["Object ID"], data | self.character_data.character_list[data["ID"]] |
                    {"Sprite Ver": self.chapter})

    if add_helper:
        self.helper = AICharacter(99999999, self.character_data.character_list["Dashisi"] |
                                  {"ID": "Dashisi", "POS": (1000, 140 * self.screen_scale[1]),
                                   "Team": 1, "Sprite Ver": self.chapter,
                                   "Arrive Condition": []})  # add pixie helper character
