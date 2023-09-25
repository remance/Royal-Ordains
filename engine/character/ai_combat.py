from random import getrandbits


def training_ai(self):
    pass


def guard_ai(self):
    """Common combat AI will use only stand position with guard priority and not use combo"""
    if (not self.current_action or "guard" in self.current_action) and \
            not self.command_action and not self.attack_cooldown and self.nearest_enemy:
        if self.nearest_enemy[1] <= self.max_attack_range:
            if not self.guarding and not self.ai_timer:  # always guard first when enemy near
                self.ai_timer = 0.1
                self.engage_combat()
                self.command_action = self.guard_hold_command_action

            elif self.guarding and self.ai_timer > 5:  # guard only for 5 seconds then attack
                self.ai_timer = 0
                self.interrupt_animation = True
                self.command_action = {}  # consider go to idle first then check for move
                for move, value in self.moveset[self.position].items():
                    if value["Range"] >= self.nearest_enemy[1]:
                        self.engage_combat()
                        if "Prepare Animation" in value:  # skill
                            self.command_action = self.use_skill(value)
                        elif "Weak" in move:
                            self.command_action = self.weak_attack_command_action
                        elif "Strong" in move:
                            self.command_action = self.strong_attack_command_action
                        elif "Special" in move:
                            self.command_action = self.special_command_action
                        self.moveset_command_key_input = move
                        break
            if self.nearest_enemy[0].base_pos[0] >= self.base_pos[0]:
                self.new_angle = -90
            else:
                self.new_angle = 90


def common_ai(self):
    """Common combat AI will use only stand position move and skill but not use combo"""
    if not self.current_action and not self.command_action and self.nearest_enemy:
        if self.nearest_enemy[1] <= self.max_attack_range:
            if self.position in self.moveset:
                for move, value in self.moveset[self.position].items():
                    if value["Range"] >= self.nearest_enemy[1] and value["Move"] not in self.attack_cooldown:
                        self.engage_combat()
                        if "Prepare Animation" in value:  # skill
                            self.command_action = self.use_skill(value)
                        elif "Weak" in move:
                            self.command_action = self.weak_attack_command_action
                        elif "Strong" in move:
                            self.command_action = self.strong_attack_command_action
                        elif "Special" in move:
                            self.command_action = self.special_command_action
                        self.moveset_command_key_input = move
                        break
                if self.nearest_enemy[0].base_pos[0] >= self.base_pos[0]:
                    self.new_angle = -90
                else:
                    self.new_angle = 90


ai_combat_dict = {"default": training_ai, "common_melee": common_ai, "common_range": common_ai, "sentry": common_ai,
                  "trap": common_ai, "bigta": common_ai, "guard_melee": guard_ai, "pursue_melee": common_ai}
