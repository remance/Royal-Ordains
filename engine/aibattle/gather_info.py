from random import sample

"""Battle commander AI act and plan depend on their personality stat
Cleverness 0 = does nothing
Cleverness 1 = add own commander, closest enemy position, strategy cooldown info
Cleverness 2 = add power scale, useful for retreat planning
Cleverness 3 = add density info, useful for strategy placement calculation
Cleverness 4 = add enemy commander position and health, useful for consider focus strategy on it for kill
Cleverness 5 = add supply consideration, useful for long term plan
Cleverness 6 = check for negative statuses of troops and self, useful for using strategy that can cure them
Cleverness 7 = add weather info, useful for choosing weather strategy
Cleverness 8 = add air group type info, useful for counter air
Cleverness 9 = add enemy strategy info, useful for distancing placement
"""


def clever0_gather_info(self):
    pass


def clever1_gather_info(self):
    return gather_info_basic(self)


def clever2_gather_info(self):
    info_dict = clever1_gather_info(self)
    return info_dict | gather_info_enemy_air(self)


def clever3_gather_info(self):
    info_dict = clever2_gather_info(self)
    return info_dict | gather_info_power(self)


def clever4_gather_info(self):
    info_dict = clever3_gather_info(self)
    return info_dict | gather_info_density(self)


def clever5_gather_info(self):
    info_dict = clever4_gather_info(self)
    return info_dict | gather_info_enemy_commander(self)


def clever6_gather_info(self):
    info_dict = clever5_gather_info(self)
    return info_dict | gather_info_status(self)


def clever7_gather_info(self):
    info_dict = clever6_gather_info(self)
    return info_dict | gather_info_weather(self)


def clever8_gather_info(self):
    info_dict = clever7_gather_info(self)
    return info_dict | gather_info_enemy_strategy(self)


def clever9_gather_info(self):
    info_dict = clever8_gather_info(self)
    return info_dict | gather_info_supply(self)


clever_gather_info_level = {0: clever0_gather_info, 1: clever1_gather_info, 2: clever2_gather_info,
                            3: clever3_gather_info, 4: clever4_gather_info, 5: clever5_gather_info,
                            6: clever6_gather_info, 7: clever7_gather_info, 8: clever8_gather_info,
                            9: clever9_gather_info, 10: clever8_gather_info}


def gather_info_basic(self):  # clever 1
    """Gather basic information of their own commander
    Shuffle strategy list so available strategies are given random priority to be used"""
    start_pos = self.commander.start_pos
    strategy_list = [(index, strategy) for index, strategy in enumerate(self.own_strategy) if
                                   not self.team_stat["strategy_cooldown"][index] and
                                   self.strategy_list[strategy]["Resource Cost"] <= self.team_stat[
                                       "strategy_resource"]]
    info = {"commander_health": self.commander.health / self.commander.base_health,
            "available_strategy": sample(strategy_list, len(strategy_list)),
            }

    if self.battle.all_team_enemy_check[self.team]:
        info["closest_enemy_pos_to_camp"] = sorted([abs(start_pos - enemy.base_pos[0]) for enemy in
                                                    self.battle.all_team_enemy_check[self.team]])[0]

    if self.air_group:
        info["own_air_group"] = check_air_group(self, self.team)
    return info


def gather_info_enemy_air(self):  # clever 2
    air_group = check_air_group(self, self.enemy_team)
    if air_group:
        return {"enemy_air_group": air_group}
    return {}


def gather_info_power(self):  # clever 3
    # battle_scale = self.battle.battle_scale[self.team] / sum(self.battle.battle_scale)

    # offence_power_comparison = [1, 1]
    # defence_power_comparison = [1, 1]
    # range_power_comparison = [1, 1]
    total_power_comparison = [1, 1]
    # total_enemy = 0
    #
    # total_enemy += 1 + self.enemy_commander.max_followers_len_check
    if self.enemy_commander and self.enemy_commander.alive:
        # offence_power_comparison[1] += self.enemy_commander.total_offence_power_score
        # defence_power_comparison[1] += self.enemy_commander.total_defence_power_score
        # range_power_comparison[1] += self.enemy_commander.total_range_power_score
        total_power_comparison[1] += self.enemy_commander.total_power_score

    if self.commander and self.commander.alive:
        # offence_power_comparison[0] += self.commander.total_offence_power_score
        # defence_power_comparison[1] += self.commander.total_defence_power_score
        # range_power_comparison[0] += self.commander.total_range_power_score
        total_power_comparison[0] += self.commander.total_power_score

    # offence_power_comparison = offence_power_comparison[0] / offence_power_comparison[1]
    # defence_power_comparison = defence_power_comparison[0] / defence_power_comparison[1]
    # range_power_comparison = range_power_comparison[0] / range_power_comparison[1]

    # "melee_power_comparison": offence_power_comparison,
    # "defence_power_comparison": defence_power_comparison,
    # "range_power_comparison": range_power_comparison,

    return {"total_power_comparison": total_power_comparison[0] / total_power_comparison[1] * 100}


def gather_info_density(self):  # clever 4
    enemy_ground_density = {key: len(value) for key, value in
                            self.battle.all_team_ground_enemy_collision_grids[self.team].items()}
    enemy_air_density = {key: len(value) for key, value in
                         self.battle.all_team_air_enemy_collision_grids[self.team].items()}

    # below roughly work only with 2 teams, will also count team 0 neutral as ally = enemy of enemy
    own_density = {key: len(value) for key, value in
                   self.battle.all_team_ground_enemy_collision_grids[self.enemy_team].items()}
    own_density = {key: value + len(self.battle.all_team_air_enemy_collision_grids[self.enemy_team][key]) for key, value
                   in
                   own_density.items()}
    both_density = {key: value + own_density[key] for key, value in enemy_ground_density.items()}
    both_density = {key: value + enemy_air_density[key] for key, value in both_density.items()}
    return {"enemy_ground_density": enemy_ground_density, "enemy_air_density": enemy_air_density,
            "own_density": own_density, "both_density": both_density}


def gather_info_enemy_commander(self):  # clever 5
    if self.enemy_commander.alive:
        return {"enemy_commander_pos": self.enemy_commander.base_pos[0],
                "enemy_commander_health": self.enemy_commander.health / self.enemy_commander.base_health}
    return {}


def gather_info_status(self):  # clever 6
    can_cure = []
    can_clear = []
    if self.has_cure_strategy and self.has_clear_strategy:
        for ally in self.battle.all_team_ally[self.team]:
            for status in ally.status_duration:
                if status in self.can_cure_status_list and self.has_cure_strategy:
                    can_cure.append(ally)
                if status in self.can_clear_status_list and self.has_clear_strategy:
                    can_clear.append(ally)

    return {"can_cure": can_cure, "can_clear": can_clear}


def gather_info_supply(self):  # clever 7
    return {"future_supply": self.team_stat["supply_reserve"],
            "enemy_supply": (self.enemy_team_stat["supply_resource"], self.enemy_team_stat["supply_reserve"])}


def gather_info_weather(self):  # clever 8
    return {"weather": self.battle.current_weather.weather_type}


def gather_info_enemy_strategy(self):  # clever 9
    return {"available_enemy_strategy": [strategy for index, strategy in enumerate(self.enemy_strategy) if
                                         not self.enemy_team_stat["strategy_cooldown"][index] and
                                         self.strategy_list[strategy]["Resource Cost"] <=
                                         self.enemy_team_stat["strategy_resource"]]}


def check_air_group(self, team):
    air_group = {True: {"interceptor": {}, "fighter": {}, "bomber": {}},
                 False: {"interceptor": {}, "fighter": {}, "bomber": {}}}
    for index, group in enumerate(self.battle.team_stat[team]["air_group"]):
        if group:
            air_group[group[0].active][group[0].ai_behaviour] = {
                index: (len(group), sum([character.power_score for character in group]), group)}
    air_group[True]["interceptor"]["power"] = sum([value[1] for value in air_group[True]["interceptor"].values()] +
                                                  [value[1] for value in air_group[True]["fighter"].values()])
    return air_group

# def gather_info_reinforcement(self):  # clever
#     return {"enemy_reinforcement": self.enemy_team_stat["leader_call_list"] + self.enemy_team_stat["troop_call_list"]}
#


# def gather_info_enemy_type_density(self):  # clever 10
#     enemy_ground_type_density = {key: [character for character in value] for key, value in
#                                  self.battle.all_team_ground_enemy_collision_grids[self.team].items()}
#     for key, value in enemy_ground_type_density.items():
#         melee = [character for character in value if character.ai_behaviour == "melee"]
#         enemy_ground_type_density[key] = [melee, tuple(set(value).difference(melee))]
#     return {"enemy_ground_type_density": enemy_ground_type_density}
