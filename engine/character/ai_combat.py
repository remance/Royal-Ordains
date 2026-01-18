from random import choice, uniform


def check_status(who, status):
    if status not in who.status_duration:
        return True


def check_health_lower(who, value):
    if who.health * who.base_health / 100 <= value:
        return True


def check_resource_lower(who, value):
    if who.resource * who.base_resource / 100 <= value:
        return True


def check_health_higher(who, value):
    if who.health * who.base_health / 100 >= value:
        return True


def check_resource_higher(who, value):
    if who.resource * who.base_resource / 100 >= value:
        return True


def check_engage(who, value):
    """Check if who has enemy in provided range"""
    if who.nearest_enemy_distance > value:
        return True


def check_target_type(who, value):
    """Check if who match the target type value"""
    if who.character_type == value:
        return True


def check_no_stay(who, value):
    """Check that commander order is not stay"""
    if "stay" not in who.commander_order is value:
        return True


ai_condition_check_dict = {"health>": check_health_higher, "resource>": check_resource_higher,
                           "health<": check_health_lower, "resource<": check_resource_lower,
                           "no_status": check_status, "no_engage": check_engage,
                           "target_type": check_target_type, "no_stay": check_no_stay}


def leader_condition_check(self, value):
    """Require leader to meet condition"""
    if self.leader:
        for condition2, value2 in value.items():
            if not ai_condition_check_dict[condition2](self.leader, value2):
                return
        return True


def allies_condition_check(self, value):
    """Require all nearby allies to meet condition"""
    for character in self.near_ally:
        for condition2, value2 in value.items():
            if not ai_condition_check_dict[condition2](character[0], value2):
                return
    return True


def ally_condition_check(self, value):
    """Require one nearby ally to meet condition"""
    for character in self.near_ally:
        for condition2, value2 in value.items():
            if ai_condition_check_dict[condition2](character[0], value2):
                return True


def self_condition_check(self, value):
    """Require self to meet condition"""
    for condition2, value2 in value.items():
        if not ai_condition_check_dict[condition2](self, value2):
            return
    return True


def enemy_condition_check(self, value):
    """Require nearest enemy to meet condition"""
    if self.nearest_enemy and self.nearest_enemy.alive:
        for condition2, value2 in value.items():
            if not ai_condition_check_dict[condition2](self.nearest_enemy, value2):
                return
        return True


ai_who_check_dict = {"leader": leader_condition_check, "allies": allies_condition_check,
                     "ally": ally_condition_check, "self": self_condition_check,
                     "enemy": enemy_condition_check}


def check_ai_condition(self, condition_dict):
    for condition, value in condition_dict.items():
        if not ai_who_check_dict[condition](self, value):
            return
    return True


def find_move_to_attack(self):
    # has enemy to attack and within max range attack
    # blind cause random direction melee attack but will not allow ranged attack
    possible_attacks = [value for move, value in self.movesets.items() if
                        move not in self.move_cooldown and value["Resource Cost"] <= self.resource and
                        ((not self.blind and (
                                ("far_target" not in value["Property"] and value[
                                    "AI Range"] >= self.nearest_enemy_distance) or
                                ("far_target" in value["Property"] and self.furthest_enemy_distance and
                                 value["AI Range"] >= self.furthest_enemy_distance))) or
                         (self.blind and not value["Range"])) and
                        (not value["AI Condition"] or self.check_ai_condition(value["AI Condition"]))]
    if possible_attacks:
        self.current_moveset = choice(possible_attacks)  # randomly select move to attack
        if "far_target" not in self.current_moveset["Property"]:
            self.command_action = self.moveset_command_action | {"target": self.nearest_enemy_pos}
        else:
            self.command_action = self.moveset_command_action | {"target": self.furthest_enemy_pos}
        return True


def no_ai(self):
    """No attack at all"""
    pass


def cheer_ai(self):
    """No attack but check for target action for appropriate cheering"""
    if "moveset" in self.target.current_action or "submit" in self.target.current_action or \
            "taunt" in self.target.current_action:
        # Cheer when target attack or spared in decision
        if "cheer" not in self.current_action:  # start cheering
            self.interrupt_animation = True
        if "special" in self.target.current_action or "submit" in self.target.current_action:
            # cheer harder for special occasion
            self.command_action = self.cheer_fast_action
        else:  # normal cheer
            self.command_action = self.cheer_action


def common_ai(self):
    """Common combat AI"""
    if "move" not in self.commander_order:
        if self.nearest_enemy and self.nearest_enemy_distance <= self.ai_max_attack_range:
            if not self.ai_timer and (
                    "interruptable" in self.current_action or (not self.command_action and not self.current_moveset)):
                if find_move_to_attack(self):
                    # stop interruptable action to attack
                    self.ai_movement_timer = uniform(0, 5)
                    self.interrupt_animation = True
                    new_direction = "left"
                    if not self.blind:
                        if self.nearest_enemy_pos[0] >= self.base_pos[0]:
                            new_direction = "right"
                    else:
                        # blind cause random direction attack
                        new_direction = choice(("left", "right"))
                    self.command_action["direction"] = new_direction
                self.ai_timer = 0.2


def air_ai(self):
    """air type combat AI"""
    if (self.nearest_enemy_pos and not self.command_action and
            not self.current_moveset and not self.ai_timer and
            self.nearest_enemy_distance <= self.ai_max_attack_range):
        if find_move_to_attack(self):  # air character will only interrupt movement if can attack
            if "interruptable" in self.current_action:
                # stop interruptable action to attack
                self.interrupt_animation = True
        self.ai_timer = 0.2


ai_combat_dict = {"default": no_ai, "melee": common_ai, "range": common_ai, "flank": common_ai, "nice": no_ai,
                  "curious": common_ai, "territorial": common_ai,
                  "trap": common_ai, "boss_cheer": cheer_ai,
                  "leader": common_ai, "interceptor": air_ai, "fighter": air_ai, "bomber": air_ai}
