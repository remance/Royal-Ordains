def assign_key(self, key_assign):
    if key_assign not in self.player_key_bind.values() or \
            self.player_key_bind[self.input_popup[1]] == key_assign:
        self.player_key_bind[self.input_popup[1]] = key_assign
        self.config["USER"]["keybind"] = str(self.player_key_bind_list)
        self.change_keybind()

        self.change_pause_update(False)
        self.input_box.text_start("")
        self.input_popup = None
        self.remove_ui_updater(*self.input_ui_popup, *self.confirm_ui_popup, *self.inform_ui_popup)

    else:  # key already exist, confirm to swap key between two actions
        old_action = tuple(self.player_key_bind.values()).index(key_assign)
        old_action = tuple(self.player_key_bind.keys())[old_action]
        self.activate_input_popup(("confirm_input", ("replace key", self.input_popup[1], old_action)),
                                  "Swap key with " + old_action + " ?", self.confirm_ui_popup)
