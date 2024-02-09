import copy
from random import randint

from engine.character.character import Character, AICharacter, PlayerCharacter, CityAICharacter

from engine.uibattle.uibattle import ScoreBoard


def setup_battle_character(self, player_list, stage_char_list, add_helper=True):
    object_id_list = [item["Object ID"] for item in stage_char_list]
    if player_list:
        for key, data in player_list.items():
            additional_data = {"POS": (key * 100, Character.original_ground_pos),
                               "Scene": 1, "Team": 1, "Arrive Condition": []}
            if "p" + str(key) in object_id_list:  # player stage data exist
                additional_data = copy.deepcopy(stage_char_list[object_id_list.index("p" + str(key))])
                additional_data.pop("ID")
            self.players[key]["Object"] = PlayerCharacter("p" + str(key), key,
                                                          data | self.character_data.character_list[data["ID"]] |
                                                          additional_data)

    self.player_objects = {key: value["Object"] for key, value in self.players.items()}
    player_team = {1: 0, 2: 0, 3: 0, 4: 0}
    for player in self.player_objects.values():  # increase AI health of opposite player team depending on player number
        for team in player_team:
            if team != player.team:
                player_team[team] += 1
    for data in stage_char_list:
        if type(data["Object ID"]) is not str:  # only data with int object id created as AI
            if "no_player_pick" not in data["Stage Property"] or \
                    data["ID"] not in [player.sprite_id for player in self.player_objects.values()]:
                # check if no_player_pick and player with same character exist
                health_scaling = player_team[data["Team"]] * 2
                if not player_team[data["Team"]] or player_team[data["Team"]] == 1:
                    # 0 player is considered x1 same as 1 player
                    health_scaling = 1
                if "city_npc" in data["Stage Property"]:  # city AI, has different combat update
                    specific_behaviour = None
                    if "specific_behaviour" in data["Stage Property"]:
                        specific_behaviour = data["Stage Property"]["specific_behaviour"]
                    CityAICharacter(data["Object ID"], data["Object ID"],
                                    data | self.character_data.character_list[data["ID"]] |
                                    {"Sprite Ver": self.chapter}, specific_behaviour=specific_behaviour)
                else:
                    AICharacter(data["Object ID"], data["Object ID"],
                                data | self.character_data.character_list[data["ID"]] |
                                {"Sprite Ver": self.chapter}, health_scaling=health_scaling)

    last_id = stage_char_list[-1]["Object ID"] + 1  # id continue from last stage chars
    if self.player_team_followers:  # player AI follower
        for value in self.player_team_followers.values():
            for key, data in value.items():
                for number in range(int(data)):
                    last_id += 1
                    AICharacter(last_id, last_id, self.character_data.character_list[key] |
                                {"ID": key, "Sprite Ver": 1, "Team": 1, "Start Health": 1,
                                 "POS": (randint(100, 400), Character.original_ground_pos), "Scene": 1,
                                 "Arrive Condition": ()}, leader=self.players[1]["Object"])

    if add_helper:
        self.helper = AICharacter("helper", 99999999, self.character_data.character_list["Dashisi"] |
                                  {"ID": "Dashisi", "POS": (1000, 140 * self.screen_scale[1]), "Scene": 1,
                                   "Team": 1, "Sprite Ver": self.chapter,
                                   "Arrive Condition": (), "Start Health": 1})  # add pixie helper character
        # Score board in animation must always be p1_special_10 part
        self.score_board = ScoreBoard(self.helper.body_parts["p1_special_10"])
        self.helper.body_parts["p1_special_10"].base_image_update_contains.append(self.score_board)
