from operator import itemgetter
from random import uniform

from engine.character.ai_prepare import find_grid_range


def conduct_plan(self):
    task_list = {}
    control_general_list = [general for general in self.battle.all_team_general[self.team] if general.is_controllable]

    already_assigned_general = []
    for plan in self.recommended_plan_score:
        if plan == "commander_danger":
            # if ("move" not in self.commander.commander_order and
            #         abs(self.commander.commander_order[1] - self.start_point) < abs(
            #             self.commander.base_pos[0] - self.start_point)):
            #         # not already moving back commander
            if self.current_info["commander_health"] > 0.5:  # move back a bit if able
                self.commander.issue_commander_order(("move", ))
            elif self.current_info["commander_health"] > 0.3:  # move to back line
                self.commander.issue_commander_order(("move", ))
            else:  # move back to retreat point
                self.commander.issue_commander_order(("move", self.start_pos))
            already_assigned_general.append(self.commander)

        elif plan in ("attack", "defend", "skirmish", "flank"):  # general related plan
            general_plan[plan](self, control_general_list, already_assigned_general)

        # elif plan == "strategy at ally":
        #     if uniform(0, 100) < self.recommended_plan_score[plan]:
        #         strategy_to_use = {strategy: 1 for strategy in self.current_info["available_strategy"] if
        #                            strategy in self.own_strategy_type["buff"]}
        #
        #         if "own_density" in self.current_info:
        #             [enemy for grid in grid_range for enemy in self.air_enemy_collision_grids[grid] if
        #              not enemy.invisible and not enemy.no_target]
        #             strategy_to_use = dict(sorted({strategy: value for strategy, value in strategy_to_use.items()},
        #                                           key=itemgetter(1), reverse=True))
        #         for strategy in strategy_to_use:
        #             strategy_stat = self.strategy_list[strategy]
        #             best_pos_x_to_use = self.commander.base_pos[0] + uniform(-strategy_stat["Activate Range"],
        #                                                                      strategy_stat["Activate Range"])
        #
        #             self.battle.activate_strategy(self.team, strategy, best_pos_x_to_use)
        #             break
        #
        # elif "strategy" in plan == " at enemy":
        #     strategy_to_use = [strategy for strategy in self.current_info["available_strategy"] if
        #                        strategy in self.own_strategy_type["attack"] or
        #                        strategy in self.own_strategy_type["debuff"]]
        #
        #     best_pos_x_to_use = self.commander.nearest_enemy_pos[0]
        #     if self.recommended_plan_score["ground"] > self.recommended_plan_score["air"]:
        #         strategy_to_use = [strategy for strategy in strategy_to_use if
        #                            strategy in self.own_strategy_type["attack"] and
        #                            "air" not in self.strategy_list[strategy]["AI Condition"]]
        #         if "combat_ground_density" in self.current_info:
        #             grid_range = find_grid_range(self.base_pos[0], self.strategy_list[strategy]["Activate Range"] +
        #                                          self.strategy_list[strategy]["Range"], self.last_grid)
        #             pass
        #     else:
        #         strategy_to_use = [strategy for strategy in strategy_to_use if
        #                            strategy in self.own_strategy_type["attack"] and
        #                            "air" in self.strategy_list[strategy]["AI Condition"]]
        #         # best_pos_x_to_use = self.commander.nearest_enemy_pos[0]
        #         if "combat_aird_density" in self.current_info:
        #             pass
        #
        #     for strategy in strategy_to_use:
        #         strategy_stat = self.strategy_list[strategy]
        #         if closest_enemy_distant <= strategy_stat["Activate Range"]:
        #             self.battle.activate_strategy(self.team, strategy, best_pos_x_to_use)


def conduct_attack_plan(self, control_general_list, already_assigned_general):
    attack_point = self.commander.nearest_enemy_pos[0]
    attack_general = dict(sorted({general: general.total_offence_power_score for
                                  general in control_general_list if general not in already_assigned_general}.items(),
                                 key=itemgetter(1), reverse=True))
    for general in attack_general:
        general.issue_commander_order(("attack", attack_point))
        self.recommended_plan_score["attack"] -= general.total_offence_power_score
        already_assigned_general.append(general)
        if self.recommended_plan_score["attack"] <= 0:
            break


def conduct_defend_plan(self, control_general_list, already_assigned_general):
    defend_point = self.commander.base_pos[0]
    defend_general = dict(sorted({general: general.total_defend_power_score for
                                  general in control_general_list if general not in already_assigned_general},
                                 key=itemgetter(1), reverse=True))
    for general in defend_general:
        general.issue_commander_order(("move", defend_point))
        self.recommended_plan_score["defend"] -= general.total_defence_power_score
        already_assigned_general.append(general)
        if self.recommended_plan_score["defend"] <= 0:
            break


def conduct_skirmish_plan(self, control_general_list, already_assigned_general):
    attack_point = self.commander.nearest_enemy_pos[0]
    skirmish_general = dict(sorted({general: general.total_range_power_score for
                                    general in control_general_list if general not in already_assigned_general},
                                   key=itemgetter(1), reverse=True))
    for general in skirmish_general:
        general.issue_commander_order(("attack", attack_point))
        self.recommended_plan_score["flank"] -= general.total_range_power_score
        already_assigned_general.append(general)
        if self.recommended_plan_score["flank"] <= 0:
            break


def conduct_flank_plan(self, control_general_list, already_assigned_general):
    attack_point = self.commander.nearest_enemy_pos[0]
    attack_general = dict(sorted({general: general.total_flank_power_score for
                                  general in control_general_list if general not in already_assigned_general},
                                 key=itemgetter(1), reverse=True))
    for general in attack_general:
        general.issue_commander_order(("attack", attack_point))
        self.recommended_plan_score["attack"] -= general.total_flank_power_score
        already_assigned_general.append(general)
        if self.recommended_plan_score["attack"] <= 0:
            break


general_plan = {"attack": conduct_attack_plan, "skirmish": conduct_defend_plan,
                "defend": conduct_skirmish_plan, "flank": conduct_flank_plan}