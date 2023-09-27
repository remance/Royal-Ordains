from random import randint

from engine.character.character import Character, AICharacter, PlayableCharacter


def setup_battle_character(self, player_list, stage_char_list, add_helper=True):
    if player_list:
        for key, data in player_list.items():
            self.players[key]["Object"] = PlayableCharacter(key, data | self.character_data.character_list[data["ID"]] |
                                                            {"POS": (key * 100, Character.original_ground_pos),
                                                             "Arrive Condition": []}, key)
    for data in stage_char_list:
        AICharacter(data["Object ID"] + 4, data | self.character_data.character_list[data["ID"]] |
                    {"Sprite Ver": self.chapter})  # id continue after player chars

    last_id = stage_char_list[-1]["Object ID"] + 1  # id continue from last stage chars
    if self.player_team_followers:
        for value in self.player_team_followers.values():
            for key, data in value.items():
                for number in range(int(data)):
                    last_id += 1
                    AICharacter(last_id, {"ID": key, "Sprite Ver": 1, "Team": 1, "Start Health": 100,
                                          "POS": (randint(100, 400), Character.original_ground_pos),
                                          "Arrive Condition": ()} |
                                self.character_data.character_list[key], leader=self.players[1]["Object"])

    if add_helper:
        self.helper = AICharacter(99999999, self.character_data.character_list["Dashisi"] |
                                  {"ID": "Dashisi", "POS": (1000, 140 * self.screen_scale[1]),
                                   "Team": 1, "Sprite Ver": self.chapter,
                                   "Arrive Condition": [], "Start Health": 100})  # add pixie helper character
