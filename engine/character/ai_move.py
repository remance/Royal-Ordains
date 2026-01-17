from random import choice, uniform

follow_distance = 100
stay_formation_distance = 1


def random_walk(self):
    self.command_action = self.walk_command_action
    self.ai_movement_timer = uniform(0.1, 10)
    self.command_action["x_momentum"] = uniform(50, 500)
    self.command_action["direction"] = choice(("left", "right"))


def follow_leader(self):
    leader_distance = self.leader.base_pos[0] - self.base_pos[0]
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


def move_to_target_order(self):
    if "move" in self.commander_order:
        command_target = self.commander_order[1]
    else:
        if self.nearest_enemy_pos:  # walk to nearest enemy first
            command_target = self.nearest_enemy_pos[0]
        elif (self.enemy_commander and self.enemy_commander.alive and
              abs(self.base_pos[0] - self.enemy_commander.base_pos[0]) < self.ai_max_attack_range):
            # no nearby enemy but commander within max attack range, target commander first
            command_target = self.enemy_commander.base_pos[0]
        elif self.commander_order:
            # nothing to target, move to attack order point
            command_target = self.commander_order[1]
        else:
            random_walk(self)
            return

    distance_to_target = abs(self.base_pos[0] - command_target)
    if distance_to_target > self.run_speed:
        if not self.command_action:
            self.command_action = self.run_command_action
            self.command_action["x_momentum"] = self.run_speed * uniform(0.5, 1.25)
            if command_target > self.base_pos[0]:
                self.command_action["direction"] = "right"
            else:
                self.command_action["direction"] = "left"


def move_away_from_enemy(self):
    base_pos_x = self.base_pos[0]
    command_target_x = self.nearest_enemy_pos[0]
    distance_to_target = abs(base_pos_x - command_target_x)
    if distance_to_target > self.run_speed and abs(base_pos_x - self.start_pos) > self.run_speed:
        # ignore if already at start point
        if not self.command_action:
            self.command_action = self.run_command_action
            self.command_action["x_momentum"] = self.run_speed
            if command_target_x < base_pos_x:
                self.command_action["direction"] = "right"
            else:
                self.command_action["direction"] = "left"


def stationary_ai(self):
    pass


def nice_ai(self):
    """Just walk around doing nothing"""
    if not self.ai_movement_timer:
        random_walk(self)


def curious_ai(self):
    """Run to nearby enemy within range"""
    if not self.ai_movement_timer:
        if self.nearest_enemy:
            # keep moving to attack target point, stop moving if there are enemy to attack
            command_target = self.nearest_enemy_pos[0]
            distance_to_target = abs(self.base_pos[0] - command_target)
            if 200 < distance_to_target < 1000:
                if not self.command_action:
                    self.command_action = self.run_command_action
                    self.command_action["x_momentum"] = self.run_speed
                    if command_target > self.base_pos[0]:
                        self.command_action["direction"] = "right"
                    else:
                        self.command_action["direction"] = "left"
            else:
                random_walk(self)
        else:
            random_walk(self)


def observer_ai(self):
    """Keep facing target"""
    if self.target.base_pos[0] >= self.base_pos[0]:
        self.new_direction = "right"
    else:
        self.new_direction = "left"


def melee_ai(self):
    if not self.command_action:
        if "idle" not in self.commander_order:
            if not self.all_team_enemy_check[self.team]:
                # walk randomly when no enemy
                random_walk(self)
            elif not self.nearest_enemy or self.nearest_enemy_distance > self.ai_min_attack_range:
                # keep moving to attack target point, stop moving if there are enemy to attack
                move_to_target_order(self)


def range_ai(self):
    if not self.command_action:
        if "idle" not in self.commander_order:
            if not self.all_team_enemy_check[self.team]:
                # walk randomly when no enemy
                random_walk(self)
            elif not self.nearest_enemy or self.nearest_enemy_distance > self.ai_max_attack_range:
                # keep moving to attack target point, stop moving if there are enemy to attack
                move_to_target_order(self)
            elif self.nearest_enemy and self.nearest_enemy_distance < self.ai_skirmish_range:
                # enemy too close, start running away
                move_away_from_enemy(self)


def flank_ai(self):
    if not self.command_action:
        if "idle" not in self.commander_order:
            if self.nearest_enemy and self.nearest_enemy.alive and self.nearest_enemy.character_class not in (
                    "light_melee", "medium_melee", "heavy_melee", "medium_cavalry", "heavy_cavalry"):
                # flanker will focus on light troop to fight, switch command to attack
                self.issue_commander_order(("attack", self.nearest_enemy_pos[0]))
            elif self.enemy_commander and self.enemy_commander.alive:
                if abs(self.base_pos[0] - self.enemy_commander.base_pos[0]) > self.ai_min_attack_range:
                    if self.base_pos[0] > self.enemy_commander.base_pos[0]:
                        target = self.enemy_commander.base_pos[0] - self.ai_min_attack_range
                    else:
                        target = self.enemy_commander.base_pos[0] + self.ai_min_attack_range
                    self.issue_commander_order(("move", target))
            else:
                if abs(self.base_pos[0] - self.enemy_start_pos) > 200:
                    self.issue_commander_order(("move", self.enemy_start_pos))

            if not self.all_team_enemy_check[self.team]:
                # walk randomly when no enemy
                random_walk(self)
            elif "move" in self.commander_order or ("attack" in self.commander_order and (not self.nearest_enemy or
                                                                                          self.nearest_enemy_distance > self.ai_min_attack_range)):
                # keep moving to attack target point, stop moving if there are enemy to attack
                move_to_target_order(self)


def leader_common_ai(self, attack_range):
    if not self.command_action:
        if not self.nearest_enemy or self.nearest_enemy_distance > attack_range:
            # keep moving to attack target point, stop moving if there are enemy to attack
            move_to_target_order(self)


def leader_melee_ai(self):
    leader_common_ai(self, self.ai_min_attack_range)


def leader_range_ai(self):
    leader_common_ai(self, self.ai_max_attack_range)


def air_ai(self):
    if not self.command_action:
        # air unit keep moving at all time
        if "back" in self.commander_order:
            command_target = self.commander_order[1]
        elif not self.nearest_enemy or self.nearest_enemy_distance > self.ai_max_attack_range:
            # move to command point if no nearby enemy or in retreat order
            enemy_commander = self.battle.team_commander[self.enemy_team]
            if enemy_commander and enemy_commander.alive:  # prioritise attack alive enemy commander first
                command_target = enemy_commander.base_pos[0]
            else:  # if not exist then attack enemy respawn point
                command_target = self.commander_order[1]
        else:  # move to nearest enemy in attack range instead
            command_target = self.nearest_enemy_pos[0]

        self.command_action = self.run_command_action
        self.command_action["x_momentum"] = self.run_speed
        if command_target > self.base_pos[0]:
            self.command_action["direction"] = "right"
        else:
            self.command_action["direction"] = "left"


def leader_ai(self):
    if self.commander_order:
        if "move" in self.commander_order:
            command_target = self.commander_order[1]
            distance_to_target = abs(self.base_pos[0] - command_target)
            if distance_to_target > (self.run_speed / 2):
                if not self.command_action:
                    self.command_action = self.run_command_action
                    self.command_action["x_momentum"] = self.run_speed
                    if command_target > self.base_pos[0]:
                        self.command_action["direction"] = "right"
                    else:
                        self.command_action["direction"] = "left"
            else:  # reach move target, issue stay order that will prevent leader from using move with no_stay condition
                self.issue_commander_order(("stay", self.base_pos[0]))
        elif "attack" in self.commander_order:  # use normal leader behaviour to move
            leader_inner_move_dict[self.ai_behaviour](self)


ai_move_dict = {"default": stationary_ai, "nice": nice_ai, "curious": curious_ai,
                "territorial": nice_ai, "melee": melee_ai, "range": range_ai, "flank": flank_ai,
                "trap": stationary_ai, "boss_cheer": observer_ai, "leader": leader_ai,
                "interceptor": air_ai, "fighter": air_ai, "bomber": air_ai}

leader_inner_move_dict = {"melee": leader_melee_ai, "range": leader_range_ai}
