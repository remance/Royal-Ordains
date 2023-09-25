def no_retreat_ai(self):
    pass


def common_ai(self):
    if not self.current_action and not self.command_action:
        if self.battle.base_stage_end - self.base_pos[0] < self.battle.base_stage_end / 2:  # near start of stage
            self.x_momentum = self.battle.base_stage_end
        else:  # near right of end stage
            self.x_momentum = -self.battle.base_stage_end
        self.command_action = self.run_command_action | {"x_momentum": self.x_momentum}


ai_retreat_dict = {"default": common_ai, "training": no_retreat_ai}
