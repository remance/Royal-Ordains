def common_special(self):
    if self.stoppable_frame:
        self.interrupt_animation = True
    self.command_action = self.special_command_action


def vraesier_special(self):
    if self.mode != "Demon":
        if self.resource == self.max_resource:
            self.mode = "Demon"
            self.command_action = self.activate_command_action
    else:
        if self.stoppable_frame:
            self.interrupt_animation = True
        self.command_action = self.special_command_action


special_dict = {"Vraesier": vraesier_special, "Rodhinbar": common_special, "Duskuksa": common_special, "Iri": common_special}
