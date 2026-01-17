def activate_input_popup(self, input_popup, instruction, input_ui_list):
    self.remove_from_ui_updater(self.all_input_popup_uis)  # remove any previous input ui first
    self.change_pause_update(True, except_list=self.all_input_popup_uis)

    self.input_popup = input_popup
    self.input_ui.change_instruction(instruction)
    self.add_to_ui_updater(input_ui_list)
