def no_retreat_ai(self, *args):
    pass


def common_ai(self, *args):
    if not self.current_action and not self.command_action:
        if self.battle.base_stage_end - self.base_pos[0] > self.base_pos[0] - self.battle.base_stage_start:
            # near start of stage
            self.x_momentum = -1000000
        else:  # near right of end stage
            self.x_momentum = 1000000
        if self.special_combat_state and self.special_walk_command:
            self.command_action = self.special_walk_command[self.special_combat_state]
        else:
            self.command_action = self.walk_command_action


ai_retreat_dict = {"default": common_ai, "training": no_retreat_ai}
