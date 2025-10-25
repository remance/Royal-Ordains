"""Battle commander AI act depend on their personality stat
Cleverness 0 = does nothing
Cleverness 1 = add  own commander consideration, closest enemy position, strategy cooldown
Cleverness 2 = add power scale, retreat
Cleverness 3 = add density consideration
Cleverness 4 = add reinforcement consideration
Cleverness 5 = add enemy strategy consideration
Cleverness 6 = add
Cleverness 7 =
Cleverness 8 =
Cleverness 9 =
Cleverness 10 =
"""


def clever0_gather_info(self):
    pass


def clever1_gather_info(self):
    return gather_info_basic(self)


def clever2_gather_info(self):
    info_dict = clever1_gather_info(self)
    return info_dict | gather_info_power(self)


def clever3_gather_info(self):
    info_dict = clever2_gather_info(self)
    return info_dict | gather_info_density(self)


def clever4_gather_info(self):
    info_dict = clever3_gather_info(self)
    return info_dict | gather_info_reinforcement(self)


# TODO keep add below until ai reach level 10
clever_gather_info_level = ({0: clever0_gather_info, 1: clever1_gather_info, 2: clever2_gather_info} |
                            {index: clever1_gather_info for index in range(3, 11)})


def gather_info_basic(self):
    """Gather basic information of their own commander"""
    return {"commander_health": self.commander.health / self.commander.base_health,
            "own_air_group": check_air_group(self, self.team),
            "available_strategy": [strategy for index, strategy in enumerate(self.own_strategy) if
                                   not self.team_stat["strategy_cooldown"][index] and
                                   self.strategy_list[strategy]["Resource Cost"] <= self.team_stat["strategy_resource"]]
            }


def gather_info_power(self):
    battle_scale = self.battle.battle_scale[self.team] / sum(self.battle.battle_scale)
    own_general_power = {}
    own_general_health = {}

    melee_power_comparison = [0, 0]
    range_power_comparison = [0, 0]
    total_power_comparison = [0, 0]

    for team in self.battle.all_team_general:
        if team != self.team:
            for general in self.battle.all_team_general[team]:
                melee_power_comparison[1] += general.total_melee_power_score
                range_power_comparison[1] += general.total_range_power_score
                total_power_comparison[1] += general.total_power_score
        else:
            for general in self.battle.all_team_general[team]:
                melee_power_comparison[0] += general.total_melee_power_score
                range_power_comparison[0] += general.total_range_power_score
                total_power_comparison[0] += general.total_power_score
                own_general_power[general] = (general.total_melee_power_score, general.total_range_power_score,
                                              general.total_power_score)
                own_general_health[general] = general.health / general.base_health

    melee_power_comparison = melee_power_comparison[0] / melee_power_comparison[1]
    range_power_comparison = range_power_comparison[0] / range_power_comparison[1]
    total_power_comparison = total_power_comparison[0] / total_power_comparison[1]

    return {"battle_scale": battle_scale, "melee_power_comparison": melee_power_comparison,
            "range_power_comparison": range_power_comparison, "total_power_comparison": total_power_comparison}


def gather_info_density(self):
    enemy_ground_density = {key: len(value) for key, value in
                            self.battle.all_team_ground_enemy_collision_grids[self.team].items()}
    enemy_air_density = {key: len(value) for key, value in
                         self.battle.all_team_air_enemy_collision_grids[self.team].items()}
    # below own variable roughly work only with 2 teams, will also count team 0 neutral as ally = enemy of enemy
    own_density = {key: len(value) for key, value in
                   self.battle.all_team_ground_enemy_collision_grids[self.enemy_team].items()}
    own_density = {key: value + len(self.battle.all_team_air_enemy_collision_grids[self.enemy_team][key]) for key, value in
                   own_density.items()}
    both_density = {key: value + own_density[key] for key, value in enemy_ground_density}
    both_density = {key: value + enemy_air_density[key] for key, value in both_density}
    return {"enemy_ground_density": enemy_ground_density, "enemy_air_density": enemy_air_density,
            "own_density": own_density, "both_density": both_density}


def gather_info_reinforcement(self):
    return {"own_reinforcement": self.later_reinforcement[self.team],
            "enemy_reinforcement": self.later_reinforcement[self.enemy_team]}


def gather_info_advance(self):
    return {"weather": self.battle.current_weather.weather_type,
            "enemy_air_group": self.check_air_group(self, self.enemy_team)}


def check_air_group(self, team):
    air_group = {("interceptor", "fighter"): {True: {}, False: {}}, ("bomber", "fighter"): {True: {}, False: {}}}
    for index, group in enumerate(self.battle.team_stat[team]["air_group"]):
        for air_type in air_group:
            if group[0].ai_behaviour in air_type:
                air_group[air_type][group[0].active] = {
                    index: (len(group), sum([character.power_score for character in group]), group)}
    return air_group
