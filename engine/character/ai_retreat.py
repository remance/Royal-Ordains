def common_ai(self, *args):
    if not self.command_action:
        self.command_action = self.run_command_action
        self.command_action["x_momentum"] = self.run_speed
        if self.base_pos[0] > self.retreat_pos:
            self.command_action["direction"] = "left"
        else:
            self.command_action["direction"] = "right"


ai_retreat_dict = {"default": common_ai}
