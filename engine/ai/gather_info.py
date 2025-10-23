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


clever_gather_info_level = {0: clever0_gather_info, 1: clever1_gather_info, 2: clever1_gather_info}


def gather_info_basic(self):
    """Gather basic information of their own commander"""
    return {"commander_health": self.commander.health / self.commander.base_health,
            "own_air_group": self.check_air_group(self.team),
            "available_strategy": [strategy for strategy, timer in self.strategy.items() if not timer and
                                   self.strategy_list[strategy]["Resource Cost"] <= self.team_stat["strategy_resource"]],
            "closest_enemy_distance": self.team_commander.nearest_enemy_distance,
            "closest_enemy_pos": self.team_commander.nearest_enemy_pos
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
    own_ground_density = {key: len(value) for key, value in
                          self.battle.all_team_ground_enemy_collision_grids[self.enemy_team].items()}
    own_air_density = {key: len(value) for key, value in
                       self.battle.all_team_air_enemy_collision_grids[self.enemy_team].items()}
    combat_ground_density = {key: value + own_ground_density[key] for key, value in enemy_ground_density}
    combat_air_density = {key: value + own_air_density[key] for key, value in enemy_air_density}


def gather_info_advance(self):
    return {"weather": self.battle.current_weather.weather_type,
            "enemy_air_group": self.check_air_group(self.team)}


def check_air_group(self, team):
    air_group = {"interceptor": {True: {}, False: {}}, "bomber": {True: {}, False: {}}}
    for group in self.battle.team_stat[team]["air_group"]:
        air_group[group[0].ai_behaviour][group[0].active] = {
            group: (len(group), sum([character.power_score for character in group]))}
    return air_group
