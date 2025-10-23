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
    command_target = self.commander_order[1]
    distance_to_target = abs(self.base_pos[0] - command_target)
    if distance_to_target > self.run_speed:
        if not self.command_action:
            self.command_action = self.run_command_action
            self.command_action["x_momentum"] = self.run_speed
            if command_target > self.base_pos[0]:
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


def common_ai(self, attack_range):
    if not self.command_action:
        if self.leader:
            if "attack" not in self.commander_order:
                follow_leader(self)
            else:
                if not self.nearest_enemy or self.nearest_enemy_distance > attack_range:
                    # keep moving to attack target point, stop moving if there are enemy to attack
                    move_to_target_order(self)

        else:  # follower with no leader, attack nearby enemy or walk randomly
            if self.nearest_enemy:
                if self.followers and (not self.commander_order or self.commander_order[1] != self.nearest_enemy_pos[0]):
                    self.issue_commander_order(("attack", self.nearest_enemy_pos[0]))
                if self.nearest_enemy_distance > attack_range:
                    # run to enemy within attack range
                    self.command_action = self.run_command_action
                    self.command_action["x_momentum"] = self.run_speed
                    if self.nearest_enemy_pos[0] > self.base_pos[0]:
                        self.command_action["direction"] = "right"
                    else:
                        self.command_action["direction"] = "left"
            elif not self.ai_movement_timer:
                # walk randomly when no nearby enemy
                random_walk(self)


def melee_ai(self):
    common_ai(self, self.ai_min_attack_range)


def range_ai(self):
    common_ai(self, self.ai_max_attack_range)


def general_common_ai(self, attack_range):
    if not self.command_action:
        if not self.nearest_enemy or self.nearest_enemy_distance > attack_range:
            # keep moving to attack target point, stop moving if there are enemy to attack
            move_to_target_order(self)


def general_melee_ai(self):
    general_common_ai(self, self.ai_min_attack_range)


def general_range_ai(self):
    general_common_ai(self, self.ai_max_attack_range)


def air_ai(self):
    if not self.command_action:
        # air unit keep moving at all time
        if ("back" in self.commander_order or not self.nearest_enemy or
                self.nearest_enemy_distance > self.ai_max_attack_range):
            # move to command point if no nearby enemy or in retreat order
            command_target = self.commander_order[1]
        else:  # move to nearest enemy in attack range instead
            command_target = self.nearest_enemy_pos[0]

        self.command_action = self.run_command_action
        self.command_action["x_momentum"] = self.run_speed
        if command_target > self.base_pos[0]:
            self.command_action["direction"] = "right"
        else:
            self.command_action["direction"] = "left"


def general_ai(self):
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
            else:  # reach move target, remove order
                self.issue_commander_order(())
        elif "attack" in self.commander_order:  # use normal general behaviour to move
            general_inner_move_dict[self.ai_behaviour](self)


ai_move_dict = {"default": stationary_ai, "nice": nice_ai, "curious": curious_ai,
                "territorial": nice_ai, "melee": melee_ai, "range": range_ai,
                "trap": stationary_ai, "boss_cheer": observer_ai, "general": general_ai,
                "interceptor": air_ai, "fighter": air_ai, "bomber": air_ai}


general_inner_move_dict = {"melee": general_melee_ai, "range": general_range_ai}