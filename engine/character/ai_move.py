from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.character.character import NonCombatCharacter, CombatCharacter, GrandAutoNonCombatCharacter, \
    AirCombatCharacter

from random import choice, uniform

follow_distance = 100
stay_formation_distance = 1


def random_walk(self: (NonCombatCharacter, CombatCharacter)):
    self.command_action = self.walk_command_action
    self.ai_movement_timer = uniform(0.1, 10)
    self.command_action["x_momentum"] = uniform(50, 500)
    self.command_action["direction"] = choice(("left", "right"))


def follow_leader(self: (NonCombatCharacter, CombatCharacter)):
    leader_distance = self.commander_character.base_pos[0] - self.base_pos[0]
    abs_leader_distance = abs(leader_distance)
    if abs_leader_distance > self.follow_leader_distance:  # follow leader
        self.command_action = self.run_command_action
        move_speed = self.run_speed
        if self.run_speed > abs_leader_distance:
            move_speed = abs_leader_distance
        self.command_action["x_momentum"] = move_speed
        if leader_distance > 0:  # move to right
            self.command_action["direction"] = "right"
        else:
            self.command_action["direction"] = "left"


def move_to_target_order(self: (NonCombatCharacter, CombatCharacter)):
    base_pos_x = self.base_pos[0]
    if "move" in self.commander_order:
        command_target_x = self.commander_order[1]
    else:
        enemy_commander_character = self.enemy_commander_character
        if self.nearest_enemy_pos:  # walk to nearest enemy first
            command_target_x = self.nearest_enemy_pos[0]
        elif (enemy_commander_character and enemy_commander_character.alive and
              abs(base_pos_x - enemy_commander_character.base_pos[0]) < self.ai_max_attack_range):
            # no nearby enemy but commander within max attack range, target commander first
            command_target_x = enemy_commander_character.base_pos[0]
        elif self.commander_order:
            # nothing to target, move to attack order point
            command_target_x = self.commander_order[1]
        else:
            random_walk(self)
            return

    distance_to_target = abs(base_pos_x - command_target_x)
    if distance_to_target > self.run_speed:
        if not self.command_action:
            self.command_action = self.run_command_action
            self.command_action["x_momentum"] = self.run_speed * 2
            if base_pos_x > command_target_x:
                self.command_action["direction"] = "left"
            else:
                self.command_action["direction"] = "right"


def move_away_from_enemy(self: (NonCombatCharacter, CombatCharacter)):
    base_pos_x = self.base_pos[0]

    if abs(base_pos_x - self.start_pos) > self.run_speed:
        # ignore if already at start point
        if not self.command_action:
            self.command_action = self.run_command_action
            self.command_action["x_momentum"] = self.run_speed
            if base_pos_x > self.retreat_pos:  # move back to retreat point
                self.command_action["direction"] = "left"
            else:
                self.command_action["direction"] = "right"


def stationary_ai(self: (NonCombatCharacter, CombatCharacter)):
    pass


def nice_ai(self: (NonCombatCharacter, CombatCharacter)):
    """Just walk around doing nothing"""
    if not self.ai_movement_timer:
        random_walk(self)


def curious_ai(self: (NonCombatCharacter, CombatCharacter)):
    """Run to nearby enemy within range"""
    if not self.ai_movement_timer:
        if self.nearest_enemy:
            # keep moving to attack target point, stop moving if there are enemy to attack
            command_target_x = self.nearest_enemy_pos[0]
            distance_to_target = abs(self.base_pos[0] - command_target_x)
            if 200 < distance_to_target < 1000:
                if not self.command_action:
                    self.command_action = self.run_command_action
                    self.command_action["x_momentum"] = self.run_speed
                    if self.base_pos[0] > command_target_x:
                        self.command_action["direction"] = "left"
                    else:
                        self.command_action["direction"] = "right"
            else:
                random_walk(self)
        else:
            random_walk(self)


def observer_ai(self: (NonCombatCharacter, CombatCharacter)):
    """Keep facing target"""
    if self.target.base_pos[0] >= self.base_pos[0]:
        self.new_direction = "right"
    else:
        self.new_direction = "left"


def melee_ai(self: CombatCharacter):
    if not self.command_action:
        if "idle" not in self.commander_order:
            if ("move" in self.commander_order or not self.nearest_enemy or
                    self.nearest_enemy_distance > self.ai_min_attack_range):
                # keep moving to attack target point, stop moving if there are enemy to attack with min range
                self.move_to_target_order()
            elif not self.all_team_enemy[self.team]:
                # walk randomly when no enemy
                random_walk(self)


def range_ai(self: CombatCharacter):
    if not self.command_action:
        if "idle" not in self.commander_order:
            if self.all_team_enemy[self.team]:
                if self.nearest_enemy and self.nearest_enemy_distance < self.ai_skirmish_range:
                    # enemy too close, start running away
                    self.move_away_from_enemy()
                elif ("move" in self.commander_order or not self.nearest_enemy or
                      self.nearest_enemy_distance > self.ai_max_attack_range):
                    # keep moving to target point, stop moving if there are enemy to attack with max range
                    self.move_to_target_order()
            else:
                # walk randomly when no enemy
                random_walk(self)


def mix_ai(self: CombatCharacter):
    """Mix ai behave like ranged ai but does not run away from enemy, will stand their ground instead"""
    if not self.command_action:
        if "idle" not in self.commander_order:
            if not self.all_team_enemy[self.team]:
                # walk randomly when no enemy
                random_walk(self)
            elif "move" in self.commander_order or not self.nearest_enemy or self.nearest_enemy_distance > self.ai_max_attack_range:
                # keep moving to target point, stop moving if there are enemy to attack with max range
                self.move_to_target_order()


def flank_ai(self: CombatCharacter):
    if not self.command_action:
        if self.all_team_enemy[self.team]:
            nearest_enemy = self.nearest_enemy
            if "idle" not in self.commander_order:
                enemy_commander_character = self.enemy_commander_character
                if nearest_enemy and nearest_enemy.alive and (nearest_enemy.ai_behaviour != "melee" or
                                                              nearest_enemy.character_grade == "common"):
                    # flanker will focus on nearby non-melee or low class melee troop to fight, switch command to attack
                    self.issue_commander_order(("attack", self.nearest_enemy_pos[0]))
                elif enemy_commander_character and enemy_commander_character.alive:
                    # aim at enemy commander
                    if self.base_pos[0] > enemy_commander_character.base_pos[0]:
                        target = enemy_commander_character.base_pos[0] - self.ai_min_attack_range
                    else:
                        target = enemy_commander_character.base_pos[0] + self.ai_min_attack_range
                    if abs(self.base_pos[0] - enemy_commander_character.base_pos[0]) > self.ai_min_attack_range:
                        self.issue_commander_order(("move", target))
                    else:
                        self.issue_commander_order(("attack", target))
                else:
                    if abs(self.base_pos[0] - self.enemy_start_pos) > 500:
                        self.issue_commander_order(("move", self.enemy_start_pos))
                    else:
                        self.issue_commander_order(("attack", self.enemy_start_pos))

            if "move" in self.commander_order or (
                    "attack" in self.commander_order and (
                    not self.nearest_enemy or self.nearest_enemy_distance > self.ai_min_attack_range)):
                # keep moving to attack target point, stop moving if there are enemy to attack
                self.move_to_target_order()
        else:
            # walk randomly when no enemy
            random_walk(self)


def leader_common_ai(self: CombatCharacter, attack_range: (int, float)):
    if not self.command_action:
        if not self.nearest_enemy or self.nearest_enemy_distance > attack_range:
            # keep moving to attack target point, stop moving if there are enemy to attack
            self.move_to_target_order()


def commander_melee_ai(self: CombatCharacter):
    leader_common_ai(self, self.ai_min_attack_range)


def commander_range_ai(self: CombatCharacter):
    leader_common_ai(self, self.ai_max_attack_range)


def air_ai(self: AirCombatCharacter):
    if not self.command_action:
        # air unit keep moving at all time
        if "back" in self.commander_order:
            command_target_x = self.commander_order[1]
        elif not self.nearest_enemy or self.nearest_enemy_distance > self.ai_max_attack_range:
            # move to command point if no nearby enemy
            enemy_commander_character = self.enemy_commander_character
            if enemy_commander_character and enemy_commander_character.alive:
                # prioritise attack alive enemy commander first
                command_target_x = enemy_commander_character.base_pos[0]
            else:  # if enemy commander not exist then attack enemy respawn point
                command_target_x = self.commander_order[1]
        else:  # move to nearest enemy in attack range instead
            command_target_x = self.nearest_enemy_pos[0]

        self.command_action = self.run_command_action
        self.command_action["x_momentum"] = self.run_speed
        if self.base_pos[0] > command_target_x:
            self.command_action["direction"] = "left"
        else:
            self.command_action["direction"] = "right"


def interceptor_ai(self: AirCombatCharacter):
    """interceptor character does not care about enemy commander because they can't attack it anyway"""
    if not self.command_action:
        # air unit keep moving at all time
        if "back" in self.commander_order:
            command_target_x = self.commander_order[1]
        elif not self.nearest_enemy or self.nearest_enemy_distance > self.ai_max_attack_range:
            # move to command point if no nearby enemy
            command_target_x = self.commander_order[1]
        else:  # move to nearest enemy in attack range instead
            command_target_x = self.nearest_enemy_pos[0]

        self.command_action = self.run_command_action
        self.command_action["x_momentum"] = self.run_speed
        if self.base_pos[0] > command_target_x:
            self.command_action["direction"] = "left"
        else:
            self.command_action["direction"] = "right"


def leader_ai(self: CombatCharacter):
    if self.commander_order:
        if "move" in self.commander_order:
            command_target_x = self.commander_order[1]
            distance_to_target = abs(self.base_pos[0] - command_target_x)
            if distance_to_target > (self.run_speed / 2):
                if not self.command_action:
                    self.command_action = self.run_command_action
                    self.command_action["x_momentum"] = self.run_speed
                    if self.base_pos[0] > command_target_x:
                        self.command_action["direction"] = "left"
                    else:
                        self.command_action["direction"] = "right"
            else:  # reach move target, issue stay order that will prevent leader from using move with no_stay condition
                self.issue_commander_order(("stay", self.base_pos[0]))
        elif "attack" in self.commander_order:  # use normal leader behaviour to move
            commander_inner_move_dict[self.ai_behaviour](self)


ai_move_dict = {"default": stationary_ai, "nice": nice_ai, "curious": curious_ai,
                "territorial": nice_ai, "melee": melee_ai, "range": range_ai, "mix": mix_ai, "flank": flank_ai,
                "trap": stationary_ai, "boss_cheer": observer_ai, "commander": leader_ai,
                "interceptor": interceptor_ai, "fighter": air_ai, "bomber": air_ai}

commander_inner_move_dict = {"melee": commander_melee_ai, "range": commander_range_ai, "mix": commander_range_ai}


def auto_random_walk(self: GrandAutoNonCombatCharacter):
    self.base_pos[0] += uniform(-self.walk_speed, self.walk_speed)


def auto_move_to_target_order(self: GrandAutoNonCombatCharacter):
    """Move function for grand auto character, character move to target point right away rather than perform animation"""
    base_pos_x = self.base_pos[0]
    if "move" in self.commander_order:
        command_target_x = self.commander_order[1]
    else:
        enemy_commander_character = self.enemy_commander_character
        if self.nearest_enemy_pos:  # walk to nearest enemy first
            command_target_x = self.nearest_enemy_pos[0]
        elif (enemy_commander_character and enemy_commander_character.alive and
              abs(base_pos_x - enemy_commander_character.base_pos[0]) < self.ai_max_attack_range):
            # no nearby enemy but commander within max attack range, target commander first
            command_target_x = enemy_commander_character.base_pos[0]
        elif self.commander_order:
            # nothing to target, move to attack order point
            command_target_x = self.commander_order[1]
        else:
            return
    base_pos_x = self.base_pos[0]
    distance_to_target = abs(base_pos_x - command_target_x)
    if distance_to_target > self.ai_max_attack_range:
        if base_pos_x > command_target_x:  # left direction
            self.direction = "left"
            self.base_pos[0] -= self.run_speed
            if self.base_pos[0] < 0:
                self.base_pos[0] = 0
        else:
            self.direction = "right"
            self.base_pos[0] += self.run_speed
            if self.base_pos[0] > self.base_stage_end:
                self.base_pos[0] = self.base_stage_end


def auto_move_away_from_enemy(self: GrandAutoNonCombatCharacter):
    base_pos_x = self.base_pos[0]
    command_target_x = self.nearest_enemy_pos[0]
    if base_pos_x > command_target_x:  # run to left direction

        self.direction = "left"
        self.base_pos[0] -= self.run_speed
        if self.base_pos[0] < 0:
            self.base_pos[0] = 0
    else:
        self.direction = "right"
        self.base_pos[0] += self.run_speed
        if self.base_pos[0] > self.base_stage_end:
            self.base_pos[0] = self.base_stage_end


def auto_nice_ai(self: GrandAutoNonCombatCharacter):
    """Just walk around doing nothing"""
    random_walk(self)


def auto_curious_ai(self: GrandAutoNonCombatCharacter):
    """Run to nearby enemy within range"""
    if self.nearest_enemy:
        # keep moving to attack target point, stop moving if there are enemy to attack
        command_target_x = self.nearest_enemy_pos[0]
        distance_to_target = abs(self.base_pos[0] - command_target_x)
        if 200 < distance_to_target < 1000:
            if not self.command_action:
                self.command_action = self.run_command_action
                self.command_action["x_momentum"] = self.run_speed
                if command_target_x > self.base_pos[0]:
                    self.command_action["direction"] = "right"
                else:
                    self.command_action["direction"] = "left"
        else:
            random_walk(self)
    else:
        random_walk(self)


def auto_melee_ai(self: CombatCharacter):
    if "idle" not in self.commander_order:
        if ("move" not in self.commander_order and
                (not self.nearest_enemy or self.nearest_enemy_distance > self.ai_min_attack_range)):
            # keep moving to attack target point, stop moving if there are enemy to attack
            self.move_to_target_order()
        elif not self.all_team_enemy[self.team]:
            # walk randomly when no enemy
            random_walk(self)


def auto_range_ai(self: CombatCharacter):
    if "idle" not in self.commander_order:
        if self.all_team_enemy[self.team]:
            if self.nearest_enemy and self.nearest_enemy_distance < self.ai_skirmish_range:
                # enemy too close, start running away
                self.move_away_from_enemy()
            elif ("move" in self.commander_order or not self.nearest_enemy or
                  self.nearest_enemy_distance > self.ai_max_attack_range):
                # keep moving to target point, stop moving if there are enemy to attack
                self.move_to_target_order()
        else:
            # walk randomly when no enemy
            random_walk(self)


def auto_mix_ai(self: CombatCharacter):
    """Mix ai behave like ranged ai but does not run away from enemy, will stand their ground instead"""
    if "idle" not in self.commander_order:
        if not self.all_team_enemy[self.team]:
            # walk randomly when no enemy
            random_walk(self)
        elif "move" in self.commander_order or not self.nearest_enemy or self.nearest_enemy_distance > self.ai_max_attack_range:
            # keep moving to target point, stop moving if there are enemy to attack
            self.move_to_target_order()


def auto_flank_ai(self: CombatCharacter):
    if self.all_team_enemy[self.team]:
        nearest_enemy = self.nearest_enemy
        if "idle" not in self.commander_order:
            enemy_commander_character = self.enemy_commander_character
            if nearest_enemy and nearest_enemy.alive and (nearest_enemy.ai_behaviour != "melee" or
                                                          nearest_enemy.character_grade == "common"):
                # flanker will focus on nearby non-melee or low class melee troop to fight, switch command to attack
                self.issue_commander_order(("attack", self.nearest_enemy_pos[0]))
            elif enemy_commander_character and enemy_commander_character.alive:
                # aim at enemy commander
                if self.base_pos[0] > enemy_commander_character.base_pos[0]:
                    target = enemy_commander_character.base_pos[0] - self.ai_min_attack_range
                else:
                    target = enemy_commander_character.base_pos[0] + self.ai_min_attack_range
                if abs(self.base_pos[0] - enemy_commander_character.base_pos[0]) > self.ai_min_attack_range:
                    self.issue_commander_order(("move", target))
                else:
                    self.issue_commander_order(("attack", target))
            else:
                if abs(self.base_pos[0] - self.enemy_start_pos) > 500:
                    self.issue_commander_order(("move", self.enemy_start_pos))
                else:
                    self.issue_commander_order(("attack", self.enemy_start_pos))

        if "move" in self.commander_order or (
                "attack" in self.commander_order and (
                not self.nearest_enemy or self.nearest_enemy_distance > self.ai_min_attack_range)):
            # keep moving to attack target point, stop moving if there are enemy to attack
            self.move_to_target_order()
    else:
        # walk randomly when no enemy
        random_walk(self)


def auto_leader_common_ai(self: CombatCharacter, attack_range: (int, float)):
    if not self.nearest_enemy or self.nearest_enemy_distance > attack_range:
        # keep moving to attack target point, stop moving if there are enemy to attack
        self.move_to_target_order()


def auto_commander_melee_ai(self: CombatCharacter):
    auto_leader_common_ai(self, self.ai_min_attack_range)


def auto_commander_range_ai(self: CombatCharacter):
    auto_leader_common_ai(self, self.ai_max_attack_range)


def auto_air_ai(self: CombatCharacter):
    # air unit keep moving at all time
    if "back" in self.commander_order:
        command_target_x = self.commander_order[1]
    elif not self.nearest_enemy or self.nearest_enemy_distance > self.ai_max_attack_range:
        # move to command point if no nearby enemy
        enemy_commander_character = self.enemy_commander_character
        if enemy_commander_character and enemy_commander_character.alive:
            # prioritise attack alive enemy commander first
            command_target_x = enemy_commander_character.base_pos[0]
        else:  # if enemy commander not exist then attack enemy respawn point
            command_target_x = self.commander_order[1]
    else:  # move to nearest enemy in attack range instead
        command_target_x = self.nearest_enemy_pos[0]

    base_pos_x = self.base_pos[0]
    distance_to_target = abs(base_pos_x - command_target_x)
    if distance_to_target > self.ai_max_attack_range:
        if command_target_x > base_pos_x:
            self.direction = "right"
        else:
            self.direction = "left"

        if command_target_x < base_pos_x:  # left direction
            self.base_pos[0] -= self.run_speed
            if self.base_pos[0] < 0:
                self.base_pos[0] = 0
        else:
            self.base_pos[0] += self.run_speed
            if self.base_pos[0] > self.base_stage_end:
                self.base_pos[0] = self.base_stage_end


def auto_leader_ai(self: CombatCharacter):
    if self.commander_order:
        if "move" in self.commander_order:
            command_target_x = self.commander_order[1]
            distance_to_target = abs(self.base_pos[0] - command_target_x)
            if distance_to_target > (self.run_speed / 2):
                if not self.command_action:
                    self.command_action = self.run_command_action
                    self.command_action["x_momentum"] = self.run_speed
                    if command_target_x > self.base_pos[0]:
                        self.direction = "right"
                    else:
                        self.direction = "left"
            else:  # reach move target, issue stay order that will prevent leader from using move with no_stay condition
                self.issue_commander_order(("stay", self.base_pos[0]))
        elif "attack" in self.commander_order:  # use normal leader behaviour to move
            commander_inner_move_dict[self.ai_behaviour](self)


auto_ai_move_dict = {"default": stationary_ai, "nice": auto_nice_ai, "curious": auto_curious_ai,
                     "territorial": auto_nice_ai, "melee": auto_melee_ai, "range": auto_range_ai, "mix": auto_mix_ai,
                     "flank": auto_flank_ai, "trap": stationary_ai, "boss_cheer": observer_ai,
                     "commander": auto_leader_ai, "interceptor": auto_air_ai, "fighter": auto_air_ai,
                     "bomber": auto_air_ai}

auto_commander_inner_move_dict = {"melee": auto_commander_melee_ai, "range": auto_commander_range_ai,
                                  "mix": auto_commander_range_ai}
