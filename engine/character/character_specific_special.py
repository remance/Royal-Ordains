def common_special(self):
    if self.check_move_existence():
        self.engage_combat()
        self.command_action = self.special_command_action


def vraesier_special(self):
    if self.mode != "Demon":
        if self.resource == self.base_resource:
            self.mode = "Demon"
            self.just_change_mode = True
            self.engage_combat()
            self.command_action = self.activate_command_action
    else:
        if self.check_move_existence():
            self.engage_combat()
            self.command_action = self.special_command_action


special_dict = {"Vraesier": vraesier_special, "Rodhinbar": common_special, "Duskuksa": common_special,
                "Iri": common_special, "Nayedien": common_special, }
