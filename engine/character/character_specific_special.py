def common_special(self):
    if self.stoppable_frame:
        self.interrupt_animation = True
    self.command_action = self.special_command_action
    self.moveset_command_key_input = tuple(self.command_key_input)


def vraesier_special(self):
    if self.mode != "Demon":
        if self.resource == self.max_resource:
            self.mode = "Demon"
            self.command_action = self.activate_command_action
    else:
        if self.stoppable_frame:
            self.interrupt_animation = True
        self.command_action = self.special_command_action
        self.moveset_command_key_input = tuple(self.command_key_input)


special_dict = {"Vraesier": vraesier_special, "Rodhinbar": common_special}