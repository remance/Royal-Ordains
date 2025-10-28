from operator import itemgetter
from random import uniform
from kmeans1d import cluster

from engine.character.ai_prepare import find_grid_range


def analyse_info(self):
    """Analyse information to create recommended plan and create task list"""
    recommended_plan_score = {"attack": 1, "skirmish": 1, "defend": 1, "flank": 0,
                              "strategy at ally": 0, "strategy at ground enemy": 0, "strategy at air enemy": 0,
                              "commander_danger": 0, "retreat": 0}

    if self.current_info:
        closest_enemy_distant = self.commander.nearest_enemy_distance
        distant_danger = closest_enemy_distant
        if distant_danger < 1000:
            distant_danger = 1000 - distant_danger
        else:
            distant_danger = 0

        self.current_info["retreat"] = (100 * self.current_info["commander_health"])
        recommended_plan_score["commander_danger"] = (((100 / self.current_info["commander_health"]) - 100) +
                                                      distant_danger)

        for strategy in self.current_info["available_strategy"]:
            if strategy in self.own_strategy_type["enemy"]:
                strategy_stat = self.strategy_list[strategy]
                if "enemy_ground_density" in self.current_info:
                    "enemy_ground_density"
                    "enemy_air_density"
                    "own_density"
                    "both_density"
                    grid_range = find_grid_range(self.base_pos[0], strategy_stat["Activate Range"] +
                                                 strategy_stat["Range"], self.last_grid)
                    if "air" in strategy_stat["AI condition"]:
                        enemy_in_range = [enemy for grid in grid_range for enemy in
                                          self.ground_enemy_collision_grids[grid] if
                                          not enemy.invisible and not enemy.no_target]
                        self.current_info["strategy at air enemy"] += (len(enemy_in_range) /
                                                                       self.current_info["total_enemy"]) * 100
                    else:
                        enemy_in_range = [enemy for grid in grid_range for enemy in
                                          self.ground_enemy_collision_grids[grid] if
                                          not enemy.invisible and not enemy.no_target]
                        self.current_info["strategy at ground enemy"] += (len(enemy_in_range) /
                                                                          self.current_info["total_enemy"]) * 100
                else:  # use the closest enemy for strategy consideration
                    if closest_enemy_distant <= strategy_stat["Activate Range"]:
                        if ("air" in strategy_stat["AI Condition"] and self.commander.closest_enemy.alive and
                                self.commander.closest_enemy.character_type == "air"):
                            recommended_plan_score["strategy at air enemy"] += 10
                        else:
                            recommended_plan_score["strategy at ground enemy"] += 10
            if strategy in self.own_strategy_type["ally"]:
                if "own_density" in self.current_info:
                    strategy_stat = self.strategy_list[strategy]
                    grid_range = find_grid_range(self.base_pos[0], strategy_stat["Activate Range"] +
                                                 strategy_stat["Range"], self.last_grid)
                    "enemy_ground_density"
                    "enemy_air_density"
                    "own_density"
                    "both_density"
                else:
                    recommended_plan_score["strategy at ally"] += len(self.commander.near_ally)

        # if self.

        if "total_power_comparison" in self.current_info:
            own_power_scale = (self.current_info["total_power_comparison"][0] /
                               self.current_info["total_power_comparison"][1])
            enemy_power_scale = (self.current_info["total_power_comparison"][1] /
                                 self.current_info["total_power_comparison"][0])
            self.current_info["retreat"] += enemy_power_scale * 10
            self.current_info["defend"] += enemy_power_scale * 100
            self.current_info["attack"] += own_power_scale * 100
            self.current_info["skirmish"] += (self.current_info["range_power_comparison"] * 100) - self.current_info["defend"]

        # self.current_info["own_air_group"]
        #
        # self.current_info["closest_enemy_distance"]
        # self.current_info["closest_enemy_pos"]

        enemy_commander_danger = 0
        if "enemy_commander_pos" in self.current_info:
            if "own_density" in self.current_info:
                grid_range = find_grid_range(self.current_info["enemy_commander_pos"], 0, self.last_grid)
                enemy_commander_danger = ((100 * self.current_info["enemy_commander_health"]) +
                                          (4000 - (abs(self.commander.base_pos[0] - self.current_info[
                                              "enemy_commander_pos"]) / 10)))
            else:
                enemy_commander_danger = ((100 * self.current_info["enemy_commander_health"]) +
                                          (4000 - (abs(self.commander.base_pos[0] - self.current_info[
                                              "enemy_commander_pos"]) / 10)))
            self.current_info["attack"] += enemy_commander_danger
            self.current_info["retreat"] -= enemy_commander_danger

    for key in recommended_plan_score:
        # add priority modifier and a bit of randomness
        recommended_plan_score[key] *= self.priority_modifier[key] * uniform(0.5, 1)
    recommended_plan_score = {key: value for key, value in recommended_plan_score.items() if value}
    recommended_plan_score = dict(sorted(recommended_plan_score.items(), key=itemgetter(1), reverse=True))
    print(self.priority_modifier)
    print(recommended_plan_score)
    return recommended_plan_score
