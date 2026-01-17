from random import uniform

from engine.character.ai_prepare import find_grid_range


def conduct_commander(self):
    commander = self.commander
    commander_base_posx = commander.base_pos[0]
    enemy_commander = self.enemy_commander
    current_info = self.current_info

    # plan for commander, overall, strategy related
    victory_chance = self.team_stat["supply_resource"]
    if current_info and current_info["available_strategy"] and self.clever > uniform(0, 120 - self.team_stat[
        "strategy_resource"]):
        for strategy_index, strategy in current_info["available_strategy"]:
            # shuffle strategy list so that
            strategy_stat = self.strategy_list[strategy]
            character_in_range = []
            strategy_range = strategy_stat["Range"]
            if strategy in self.own_strategy_type["enemy"] or strategy in self.own_strategy_type["summon"]:
                if "enemy_ground_density" in current_info:  # use density information
                    grid_range = find_grid_range(commander_base_posx, strategy_stat["Activate Range"] +
                                                 strategy_range, self.last_grid)
                    if "air" in strategy_stat["AI Condition"]:
                        character_in_range = [enemy.base_pos[0] for grid in grid_range for enemy in
                                              self.ground_enemy_collision_grids[grid] if
                                              not enemy.invisible and not enemy.no_target]
                    else:
                        character_in_range = [enemy.base_pos[0] for grid in grid_range for enemy in
                                              self.ground_enemy_collision_grids[grid] if
                                              not enemy.invisible and not enemy.no_target]
                        if "enemy_commander_pos" in current_info:
                            # add more weight for enemy commander position into this list based on their health
                            weight = int((1 - current_info["enemy_commander_health"]) * 20)
                            character_in_range += [current_info["enemy_commander_pos"]] * weight
                else:  # use the closest enemy for strategy consideration
                    if commander.nearest_enemy:
                        if commander.nearest_enemy_distance <= strategy_stat["Activate Range"]:
                            character_in_range = [commander.nearest_enemy_pos]

            if strategy in self.own_strategy_type["ally"]:
                if "own_density" in current_info:
                    grid_range = find_grid_range(commander_base_posx, strategy_stat["Activate Range"] +
                                                 strategy_stat["Range"], self.last_grid)
                    character_in_range += [ally.base_pos[0] for grid in grid_range for ally in
                                           self.ground_ally_collision_grids[grid]]
                elif commander.nearest_ally:
                    character_in_range += [commander.nearest_ally_pos[0]]

            if "can_cure" in current_info and strategy in self.own_strategy_type["cure"]:
                # should already have own_density info with this info
                grid_range = find_grid_range(commander_base_posx, strategy_stat["Activate Range"] +
                                             strategy_stat["Range"], self.last_grid)
                character_in_range += [ally.base_pos[0] for grid in grid_range for ally in
                                       self.ground_ally_collision_grids[grid] if ally in current_info["can_cure"]]

            if "can_clear" in current_info and strategy in self.own_strategy_type["clear"]:
                # should already have own_density info with this info
                grid_range = find_grid_range(commander_base_posx, strategy_stat["Activate Range"] +
                                             strategy_stat["Range"], self.last_grid)
                character_in_range += [ally.base_pos[0] for grid in grid_range for ally in
                                       self.ground_ally_collision_grids[grid] if ally in current_info["can_clear"]]

            if len(character_in_range) >= strategy_range / uniform(50, 200):
                # consider using strategy if possible number of characters is worth using based on range
                if strategy in self.own_strategy_type["summon"]:
                    self.activate_strategy(self.team, strategy, strategy_index, commander_base_posx)
                else:
                    character_in_range = sorted(character_in_range)
                    activate_range = strategy_stat["Activate Range"]
                    radius = strategy_stat["Range"]
                    best_pos = None
                    best_number = 0
                    for i, this_target in enumerate(character_in_range[:-1]):
                        if abs(this_target - commander_base_posx) < activate_range:
                            cover_number = 0
                            for x in character_in_range:
                                if abs(this_target - x) < radius:
                                    cover_number += 1
                            if cover_number > best_number:
                                best_number = cover_number
                                best_pos = this_target

                        if character_in_range[i + 1] != this_target:
                            if abs(this_target - commander_base_posx) < activate_range:
                                cover_number = 0
                                this_target = (this_target + character_in_range[i + 1]) / 2
                                for x in character_in_range:
                                    if abs(this_target - x) < radius:
                                        cover_number += 1
                                if cover_number > best_number:
                                    best_number = cover_number
                                    best_pos = this_target
                    if best_pos:
                        self.activate_strategy(self.team, strategy, strategy_index, best_pos)
                        break

            if "weather" in strategy_stat["Property"]:  # weather changing strategy
                if "weather" in current_info:
                    if (strategy_stat["Property"]["weather"] != self.current_weather.weather_type and
                            uniform(0, 100) > 80):
                        # no waste using strategy for weather that already the same
                        self.activate_strategy(self.team, strategy, strategy_index, commander_base_posx)
                        break
                else:
                    if uniform(0, 100) > 98:
                        # randomly use weather strategy
                        self.activate_strategy(self.team, strategy, strategy_index, commander_base_posx)
                        break

    safety_first = 10
    if current_info:  # clever 1
        safety_first = current_info["commander_health"] * 10

        if "total_power_comparison" in current_info:  # clever 2
            own_power_scale = current_info["total_power_comparison"]
            victory_chance += safety_first / own_power_scale + (self.battle.battle_time / 10)
            if "enemy_commander_health" in current_info:
                victory_chance += current_info["enemy_commander_health"]
                if "future_supply" in current_info:
                    ((self.team_stat["supply_resource"] + self.current_info["future_supply"]) / sum(
                        self.current_info["enemy_supply"]))

            if "available_enemy_strategy" in current_info:
                for strategy in current_info["available_enemy_strategy"]:
                    strategy_stat = self.strategy_list[strategy]
                    if (strategy_stat["Damage Effects"] or strategy_stat["Enemy Status"]) and abs(
                            commander_base_posx - current_info["enemy_commander_pos"]) <= strategy_stat[
                        "Activate Range"] + strategy_stat["Range"]:
                        safety_first -= uniform(1, 2)
                        break

    commander_what_to_do = "aggressive"
    if self.defensive >= safety_first * 0.7:
        commander_what_to_do = "support"
        if self.defensive >= safety_first * 0.4:
            commander_what_to_do = "far_support"
            if self.defensive >= safety_first:
                commander_what_to_do = "observe"

    if commander_what_to_do == "observe":
        start_pos = commander.start_pos
        if abs(commander_base_posx - start_pos) > 200:
            commander.issue_commander_order(("move", commander.start_pos))
    elif commander_what_to_do == "aggressive":
        if enemy_commander and enemy_commander.alive:  # put attack on enemy commander
            commander.issue_commander_order(("attack", enemy_commander.base_pos[0]))
        else:  # put attack on enemy spawn point
            commander.issue_commander_order(("attack", self.enemy_team_stat["start_pos"]))
    elif "support" in commander_what_to_do:
        # move to support from distance
        start_pos = commander.start_pos
        closest_enemy_pos_to_camp = start_pos
        if "closest_enemy_pos_to_camp" in current_info:
            closest_enemy_pos_to_camp = current_info["closest_enemy_pos_to_camp"]
        max_ai_commander_range = commander.max_ai_commander_range
        if abs(start_pos - closest_enemy_pos_to_camp) < max_ai_commander_range:
            # enemy closer to camp
            if "far_" in commander_what_to_do:
                if abs(commander_base_posx - start_pos) > 200:
                    commander.issue_commander_order(("move", start_pos))
            else:
                commander.issue_commander_order(("attack", start_pos))
        else:
            # position based on maximum range of commander
            move_type = "attack"
            move_distance = max_ai_commander_range / 2
            if "far_" in commander_what_to_do:
                move_type = "move"
                move_distance = max_ai_commander_range
            if closest_enemy_pos_to_camp > start_pos:
                target = closest_enemy_pos_to_camp + move_distance
            else:
                target = closest_enemy_pos_to_camp - move_distance

            commander.issue_commander_order((move_type, target))
