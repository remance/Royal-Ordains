def check_health_lower(who, value):
    if who.health * who.base_health / 100 <= value:
        return True
    return False


def check_resource_lower(who, value):
    if who.resource * who.base_resource / 100 <= value:
        return True
    return False


def check_health_higher(who, value):
    if who.health * who.base_health / 100 >= value:
        return True
    return False


def check_resource_higher(who, value):
    if who.resource * who.base_resource / 100 >= value:
        return True
    return False


ai_condition_check_dict = {"health>": check_health_higher, "resource>": check_resource_higher,
                           "health<": check_health_lower, "resource<": check_resource_lower}


def check_ai_condition(self, condition_dict):
    can_use = True
    for condition, value in condition_dict.items():
        if condition == "leader" and self.leader:
            for condition2, value2 in value.items():
                if not ai_condition_check_dict[condition2](self.leader, value2):
                    return False
        else:
            if not ai_condition_check_dict[condition](self, value):
                return False

    return can_use


def find_move_to_attack(self):
    # has enemy to attack and within max range attack
    if self.stoppable_frame and self.continue_moveset:  # continue from previous move
        for move, value in self.continue_moveset.items():
            if value["Move"] not in self.attack_cooldown and \
                    (value["AI Range"] >= self.nearest_enemy[1] or self.blind) and \
                    (not value["AI Condition"] or self.check_ai_condition(value["AI Condition"])):
                self.moveset_command_key_input = move
                self.interrupt_animation = True
                self.command_moveset = value
                self.command_action = self.attack_command_actions[move[-1]]
                if "Next Move" in value:
                    self.continue_moveset = value["Next Move"]
                else:
                    self.continue_moveset = None
                return True

    for move, value in self.moveset_view[self.position]:
        if value["Move"] not in self.attack_cooldown and \
            (value["AI Range"] >= self.nearest_enemy[1] or self.blind) and \
                (not value["AI Condition"] or self.check_ai_condition(value["AI Condition"])):
            # blind (7) cause random attack
            self.engage_combat()
            self.moveset_command_key_input = move
            self.command_moveset = value
            self.command_action = self.attack_command_actions[move[-1]]
            break


def training_ai(self):
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
    elif "die" in self.target.current_action or "execute" in self.target.current_action:
        # Play execute animation when target is executed in decision
        if "execute" not in self.current_action:
            self.interrupt_animation = True
        self.command_action = self.execute_action


def guard_ai(self):
    """Common combat AI will use only stand position with guard priority and not use combo"""
    if (not self.current_action or "guard" in self.current_action) and not self.command_action and self.nearest_enemy:
        if self.nearest_enemy[1] <= self.ai_max_attack_range and not self.ai_timer:
            if not self.guarding and self.guard == self.max_guard and not self.blind:
                # always guard first when enemy near and not blind (7)
                self.guarding = 0.1
                self.ai_timer = 0.1
                self.engage_combat()
                self.command_action = self.guard_hold_command_action
            else:  # attack when cannot guard
                find_move_to_attack(self)

            if self.nearest_enemy[0].base_pos[0] >= self.base_pos[0]:
                self.new_angle = -90
            else:
                self.new_angle = 90

    elif self.stoppable_frame and "moveset" not in self.command_action:
        if self.nearest_enemy[1] <= self.ai_max_attack_range:
            find_move_to_attack(self)
            if not self.blind:  # blind (7) cause random attack
                if self.nearest_enemy[0].base_pos[0] >= self.base_pos[0]:
                    self.new_angle = -90
                else:
                    self.new_angle = 90

    if self.guarding and (self.ai_timer > 3 or self.guard < self.guard_meter20):
        # guard only for 3 seconds then attack
        self.ai_timer = 0
        self.interrupt_animation = True
        self.command_action = {}  # consider go to idle first then check for move
        if self.nearest_enemy:
            find_move_to_attack(self)

    elif not self.guarding and self.ai_timer:
        self.ai_timer = 0


def common_ai(self):
    """Common combat AI will use only stand position move, combo and skill"""
    if not self.current_action and not self.command_action and self.nearest_enemy:
        if self.nearest_enemy[1] <= self.ai_max_attack_range:
            if self.position in self.moveset:
                find_move_to_attack(self)
                if not self.blind:
                    # blind cause random attack
                    if self.nearest_enemy[0].base_pos[0] >= self.base_pos[0]:
                        self.new_angle = -90
                    else:
                        self.new_angle = 90
    elif self.stoppable_frame and "moveset" not in self.command_action:
        if self.nearest_enemy[1] <= self.ai_max_attack_range:
            find_move_to_attack(self)
            if not self.blind:  # blind cause random attack
                if self.nearest_enemy[0].base_pos[0] >= self.base_pos[0]:
                    self.new_angle = -90
                else:
                    self.new_angle = 90


ai_combat_dict = {"default": training_ai, "common": common_ai, "sentry": common_ai,
                  "trap": common_ai, "guard_melee": guard_ai, "pursue": common_ai,
                  "boss_cheer": cheer_ai}
