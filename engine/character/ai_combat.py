def find_move_to_attack(self):
    if self.nearest_enemy[1] <= self.ai_max_attack_range:
        # has enemy to attack and within max range attack
        for move, value in self.moveset[self.position].items():
            if value["AI Range"] >= self.nearest_enemy[1] and value["Move"] not in self.attack_cooldown:
                # blind (7) cause random attack
                self.engage_combat()
                self.moveset_command_key_input = move
                self.check_move_existence()
                self.command_action = self.attack_command_actions[move[-1]]
                break


def training_ai(self):
    pass


def cheer_ai(self):
    """No attack but check for target action for appropriate cheering"""
    if "moveset" in self.target.current_action or "submit" in self.target.current_action or \
            "taunt" in self.target.current_action:
        # Cheer when target attack or spared in decision
        if "cheer" not in self.current_action:
            self.interrupt_animation = True
        if "special" in self.target.current_action:  # cheer harder for special move
            self.command_action = self.cheer_fast_action
        else:
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
            if not self.guarding and self.guard == self.max_guard:
                # always guard first when enemy near
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
    """Common combat AI will use only stand position move and skill but not use combo"""
    if not self.current_action and not self.command_action and self.nearest_enemy:
        if self.nearest_enemy[1] <= self.ai_max_attack_range:
            if self.position in self.moveset:
                find_move_to_attack(self)
                if 7 not in self.status_effect:
                    # blind cause ai to attack in already facing direction and not specifically at enemy
                    if self.nearest_enemy[0].base_pos[0] >= self.base_pos[0]:
                        self.new_angle = -90
                    else:
                        self.new_angle = 90


def complex_ai(self):
    """More complex combat AI will use all position move and skill and combo"""
    if self.stoppable_frame:
        self.interrupt_animation = True


ai_combat_dict = {"default": training_ai, "common": common_ai, "sentry": common_ai,
                  "trap": common_ai, "bigta": common_ai, "guard_melee": guard_ai, "pursue": common_ai,
                  "boss_cheer": cheer_ai}
