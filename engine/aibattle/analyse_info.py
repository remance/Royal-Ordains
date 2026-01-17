def analyse_info(self):
    """Analyse information to create recommended plan"""
    # attack = AI should prioritise calling high offensive troops
    # bombard = AI should prioritise calling ranged troops
    # defend = AI should prioritise calling heavy melee troops
    recommended_troop_call_plan_score = {"attack": 1, "bombard": 1, "defend": 1, "preserve": 1}

    # danger = danger of being killed based on health
    # support = how useful commander can support troop
    # attack = how useful commander can attack at the frontline
    # rush = how useful commander can rush enemy commander
    recommended_commander_plan_score = {"danger": 1, "support": 1, "attack": 1, "rush": 1}

    victory_chance = 1
    strategy_at_ally = 0
    strategy_at_ground_enemy = 0
    strategy_at_air_enemy = 0
    # if self.current_info:  # clever 1
    #     if "melee_power_comparison" in self.current_info:  # clever 2
    #         own_power_scale = (self.current_info["total_power_comparison"][0] /
    #                            self.current_info["total_power_comparison"][1])
    #         enemy_power_scale = (self.current_info["total_power_comparison"][1] /
    #                              self.current_info["total_power_comparison"][0])
    #         "melee_power_comparison"
    #
    #         "range_power_comparison"
    #         recommended_troop_call_plan_score
    #         self.current_info["defend"] += enemy_power_scale * 100
    #         self.current_info["attack"] += own_power_scale * 100
    #         self.current_info["skirmish"] += (self.current_info["range_power_comparison"] * 100) - self.current_info["defend"]
    #         self.current_info["retreat"] += enemy_power_scale
    #
    #         if "enemy_ground_density" in self.current_info:  # clever 3
    #             if "enemy_commander_pos" in self.current_info:  # clever 4
    #                 if "future_supply" in self.current_info:  # clever 5
    #                     if "weather" in self.current_info:  # clever 6
    #                         if "enemy_air_group" in self.current_info:  # clever 7
    #
    #                             if "own_reinforcement" in self.current_info:  # clever 8
    #                                 if "available_enemy_strategy" in self.current_info:  # clever 9
    #                                     if "enemy_ground_type_density" in self.current_info:  # clever 10
    #                                         pass

    # "own_reinforcement": self.team_stat["leader_call_list"] + self.team_stat["troop_call_list"],
    #         "enemy_reinforcement": self.enemy_team_stat["leader_call_list"] + self.enemy_team_stat[
    #             "troop_call_list"]
    #
    # "supply": (self.team_stat["supply_resource"], self.team_stat["supply_reserve"]),
    #         "enemy_supply": (self.enemy_team_stat["supply_resource"], self.enemy_team_stat["supply_reserve"])
    #     recommended_commander_plan_score["danger"] = ((100 / self.current_info["commander_health"]) - 100)
    #     recommended_commander_plan_score["attack"] = self.current_info["commander_health"]
    #     recommended_commander_plan_score["support"] = commander_danger
    #     recommended_commander_plan_score["observe"] = commander_danger
    #
    #     if "enemy_commander_health" in self.current_info:
    #         health_difference = self.current_info["commander_health"] - self.current_info["enemy_commander_health"]
    #         pos_distance = abs(self.commander.base_pos[0] - self.current_info["enemy_commander_pos"])
    #         recommended_commander_plan_score["rush"] = (self.rush_plan_score * health_difference) / pos_distance
    #
    #

    #
    #     for strategy in self.current_info["available_strategy"]:
    #         if strategy in self.own_strategy_type["enemy"]:
    #             strategy_stat = self.strategy_list[strategy]
    #             if "enemy_ground_density" in self.current_info:
    #                 self.current_info["enemy_ground_density"]
    #                 strategy_at_ground_enemy strategy_at_air_enemy self.current_info["enemy_air_density"]
    #
    #                 grid_range = find_grid_range(self.base_pos[0], strategy_stat["Activate Range"] +
    #                                              strategy_stat["Range"], self.last_grid)
    #                 if "air" in strategy_stat["AI condition"]:
    #                     enemy_in_range = [enemy for grid in grid_range for enemy in
    #                                       self.ground_enemy_collision_grids[grid] if
    #                                       not enemy.invisible and not enemy.no_target]
    #                     strategy_at_air_enemy += (len(enemy_in_range) / self.current_info["total_enemy"]) * 100
    #                 else:
    #                     enemy_in_range = [enemy for grid in grid_range for enemy in
    #                                       self.ground_enemy_collision_grids[grid] if
    #                                       not enemy.invisible and not enemy.no_target]
    #                     strategy_at_ground_enemy += (len(enemy_in_range) /
    #                                                                       self.current_info["total_enemy"]) * 100
    #             else:  # use the closest enemy for strategy consideration
    #                 if closest_enemy_distant <= strategy_stat["Activate Range"]:
    #                     if ("air" in strategy_stat["AI Condition"] and self.commander.closest_enemy.alive and
    #                             self.commander.closest_enemy.character_type == "air"):
    #                         strategy_at_air_enemy += 10
    #                     else:
    #                         recommended_troop_call_plan_score["strategy at ground enemy"] += 10
    #         if strategy in self.own_strategy_type["ally"]:
    #             if "own_density" in self.current_info:
    #                 strategy_stat = self.strategy_list[strategy]
    #                 grid_range = find_grid_range(self.base_pos[0], strategy_stat["Activate Range"] +
    #                                              strategy_stat["Range"], self.last_grid)
    #                 strategy_at_ally = self.current_info["own_density"]
    #                 strategy_at_ally = self.current_info["both_density"]
    #             else:
    #                 strategy_at_ally += len(self.commander.near_ally)
    #
    #     victory_chance *= recommended_commander_plan_score["danger"]
    #     # self.current_info["own_air_group"]
    #     #
    #     # self.current_info["closest_enemy_distance"]
    #     # self.current_info["closest_enemy_pos"]
    # recommended_troop_call_plan_score = {key: value for key, value in sorted(recommended_troop_call_plan_score.items(),
    #                                                               key=lambda item: item[1])}
    # recommended_troop_call_plan_score = dict(list(recommended_troop_call_plan_score.items())[:2])  # keep only most important plan
    #
    # recommended_troop_call_plan_score["strategy_at_ally"] = strategy_at_ally
    # recommended_troop_call_plan_score["strategy_at_ground_enemy"] = strategy_at_ground_enemy
    # recommended_troop_call_plan_score["strategy_at_air_enemy"] = strategy_at_air_enemy

    return dict(sorted(recommended_troop_call_plan_score.items(), key=lambda item: item[1]))
