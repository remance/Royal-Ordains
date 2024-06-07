import copy
from random import uniform

from engine.character.character import Character, AICharacter, PlayerCharacter, BattleAICharacter
from engine.uibattle.uibattle import ScoreBoard


def spawn_character(self, player_list, stage_char_list, add_helper=True):
    object_id_list = [item["Object ID"] for item in stage_char_list]
    if player_list:
        for key, data in player_list.items():
            additional_data = {"POS": (key * 100, Character.base_ground_pos),
                               "Scene": 1, "Team": 1, "Arrive Condition": []}
            if "p" + str(key) in object_id_list:  # player stage data exist
                additional_data = copy.deepcopy(stage_char_list[object_id_list.index("p" + str(key))])
                additional_data.pop("ID")
            self.players[key]["Object"] = PlayerCharacter("p" + str(key), key,
                                                          self.character_data.character_list[data["ID"]] |
                                                          data | additional_data)

        self.player_objects = {key: value["Object"] for key, value in self.players.items()}
        self.player_team = {key: value["Object"].team for key, value in self.players.items()}

    player_team = {1: 0, 2: 0, 3: 0, 4: 0}
    for player in self.player_objects.values():  # increase AI health of opposite player team depending on player number
        for team in player_team:
            if team != player.team:
                player_team[team] += 1

    for data in stage_char_list:
        if type(data["Object ID"]) is not str:  # only data with int object id created as AI
            if "story choice" in data["Stage Property"]:
                mission_choice_appear = data["Stage Property"]["story choice"].split("_")[0]
            if ("no player pick" not in data["Stage Property"] or \
                    data["ID"] not in [player.char_id for player in self.player_objects.values()]) and \
                ("story choice" not in data["Stage Property"] or
                 data["Stage Property"]["story choice"] ==
                 mission_choice_appear + "_" + self.main_story_profile["story choice"][mission_choice_appear]):
                # check if no_player_pick and player with same character exist
                if "city npc" in data["Stage Property"]:  # city AI, has different combat update
                    specific_behaviour = None
                    if "specific behaviour" in data["Stage Property"]:
                        specific_behaviour = data["Stage Property"]["specific behaviour"]
                    AICharacter(data["Object ID"], data["Object ID"],
                                data | self.character_data.character_list[data["ID"]] |
                                {"Sprite Ver": self.chapter}, specific_behaviour=specific_behaviour)
                else:
                    team_scaling = player_team[data["Team"]] * 2
                    if not player_team[data["Team"]] or player_team[data["Team"]] == 1:
                        # 0 player is considered x1 same as 1 player
                        team_scaling = 1
                    BattleAICharacter(data["Object ID"], data["Object ID"],
                                      data | self.character_data.character_list[data["ID"]] |
                                      {"Sprite Ver": self.chapter}, team_scaling=team_scaling)

    if player_list and not self.city_mode:  # add AI followers for added player in battle
        last_id = stage_char_list[-1]["Object ID"] + 1  # id continue from last stage chars
        for player in player_list:
            max_follower_allowance = (int(self.chapter) * 20) + self.all_story_profiles[player]["character"]["Charisma"]
            for key, number in self.all_story_profiles[player]["follower preset"][
                self.all_story_profiles[player]["selected follower preset"]].items():
                for _ in range(int(number)):
                    if max_follower_allowance >= self.character_data.character_list[key]["Follower Cost"]:
                        # if cost exceed fund will not be added
                        max_follower_allowance -= self.character_data.character_list[key]["Follower Cost"]
                        last_id += 1
                        BattleAICharacter(last_id, last_id, self.character_data.character_list[key] |
                                          {"ID": key, "Sprite Ver": self.chapter, "Team": 1, "Start Health": 1,
                                           "POS": (uniform(100, 400), Character.base_ground_pos), "Scene": 1,
                                           "Arrive Condition": ()}, leader=self.players[player]["Object"])

    self.last_char_id = max([this_char.layer_id for this_char in self.all_chars if this_char.layer_id != 99999999])

    if add_helper:
        self.helper = BattleAICharacter("helper", 99999999, self.character_data.character_list["Dashisi"] |
                                        {"ID": "Dashisi", "POS": (1000, 140 * self.screen_scale[1]), "Scene": 1,
                                         "Team": 1, "Sprite Ver": self.chapter,
                                         "Arrive Condition": (), "Start Health": 1})  # add pixie helper character
        # Score board in animation must always be p1_special_10 part
        self.score_board = ScoreBoard(self.helper.team, self.helper.body_parts["p1_special_10"])
        self.helper.body_parts["p1_special_10"].base_image_update_contains.append(self.score_board)
