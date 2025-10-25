from operator import itemgetter
from random import uniform
from kmeans1d import cluster


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

        self.current_info["retreat"] = 100 / self.current_info["commander_health"]
        recommended_plan_score["commander_danger"] = (((100 / self.current_info["commander_health"]) - 100) +
                                                      distant_danger)

        for strategy in self.current_info["available_strategy"]:
            if strategy in self.own_strategy_type["enemy"]:
                strategy_stat = self.strategy_list[strategy]
                if closest_enemy_distant <= strategy_stat["Activate Range"]:
                    if "air" in strategy_stat["AI Condition"]:
                        recommended_plan_score["strategy at air enemy"] += 10
                    else:
                        recommended_plan_score["strategy at ground enemy"] += 10
            if strategy in self.own_strategy_type["ally"]:
                recommended_plan_score["strategy at ally"] += len(self.commander.near_ally)

        # if self.

        if "total_power_comparison" in self.current_info:
            own_power_scale = (self.current_info["total_power_comparison"][0] /
                               self.current_info["total_power_comparison"][1])
            enemy_power_scale = (self.current_info["total_power_comparison"][1] /
                                 self.current_info["total_power_comparison"][0])
            self.current_info["retreat"] += enemy_power_scale * 10
            "total_power_comparison"
            "battle_scale", "melee_power_comparison",
            "range_power_comparison",
        # self.current_info["own_air_group"]
        #
        # self.current_info["closest_enemy_distance"]
        # self.current_info["closest_enemy_pos"]

    for key in recommended_plan_score:
        # add priority modifier and randomness
        recommended_plan_score[key] *= self.priority_modifier[key] * uniform(0.5, 1)
    recommended_plan_score = {key: value for key, value in recommended_plan_score.items() if value}
    recommended_plan_score = dict(sorted(recommended_plan_score.items(), key=itemgetter(1), reverse=True))
    print(self.priority_modifier)
    print(recommended_plan_score)
    return recommended_plan_score
