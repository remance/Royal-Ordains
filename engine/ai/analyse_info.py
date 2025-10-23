def analyse_info(self):
    recommended_plan_score = {"attack": 0, "skirmish": 0, "defend": 0, "penetrate": 0, "idle": 0,
                              "commander_fall_back": 0, "commander_attack": 0}
    if self.can_retreat:
        recommended_plan_score["retreat"] = 0

    if self.current_info:
        closest_enemy_distant = self.current_info["closest_enemy_distance"]
        distant_danger = closest_enemy_distant
        if distant_danger < 1000:
            distant_danger = 1000 - distant_danger
        else:
            distant_danger = 0
        if "move" in self.team_commander.commander_order and self.team_commander.commander_order[1]:  # already move back commander
            recommended_plan_score["commander_fall_back"] = -1
            recommended_plan_score["commander_attack"] = -1
        else:
            if self.can_retreat:
                self.current_info["retreat"] = 100 / self.current_info["commander_health"]
            recommended_plan_score["commander_fall_back"] = (((100 / self.current_info["commander_health"]) - 100) + distant_danger)

        # for strategy in  self.current_info["available_strategy"]:
        #     if strategy in self.enemy_strategy_type["attack"]:
        #         strategy_stat = self.strategy_list[strategy]
        #         if closest_enemy_distant <= strategy_stat[0]:
        #             score =
        #     recommended_plan_score["strategy"] =
        # self.current_info["own_air_group"]
        #
        # self.current_info["closest_enemy_distance"]
        # self.current_info["closest_enemy_pos"]
