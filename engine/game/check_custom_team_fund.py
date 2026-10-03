from random import choice


def check_custom_team_fund(self, create_random=False, specific_team=None):
    # remade team army to include only those with at least 1 existing character and or made random one
    custom_team_army = {team: [] for team in (1, 2)}
    removed_team_army_index = {team: [] for team in (1, 2)}
    remain_gold = {1: self.team1_gold_limit_custom_battle, 2: self.team2_gold_limit_custom_battle}
    for team in custom_team_army:
        if not specific_team or team == specific_team:
            for index in range(5):
                add_army = self.custom_team_army[team][index]
                if add_army.commander_id:
                    if remain_gold[team] >= add_army.cost:
                        # only include if has enough fund
                        remain_gold[team] -= add_army.cost
                        custom_team_army[team].append(add_army)
                    else:
                        removed_team_army_index[team].append(index)
                elif create_random and self.custom_battle_team_setup[team].team_setup[index]["culture"] == "random":
                    culture = choice(
                        [key for key in self.sprite_data.culture_coas if key not in ("random", "free")])
                    new_random_army = self.custom_team_army[team][index]

                    preset_list = self.stat_data.custom_army_preset_list[culture]
                    if culture in self.save_data.player_custom_army_preset_save:
                        preset_list = {key: value for key, value in self.save_data.player_custom_army_preset_save[
                            culture].items() if None not in value["commander"]} | preset_list

                    preset = choice(tuple(preset_list.keys()))

                    army_preset = self.convert_custom_army_to_deployable(preset_list[preset], culture)
                    new_random_army.__init__("", army_preset["culture"], army_preset["culture"],
                                             army_preset["commander"],
                                             army_preset["followers"])
                    custom_team_army[team].append(new_random_army)
    return custom_team_army, removed_team_army_index
