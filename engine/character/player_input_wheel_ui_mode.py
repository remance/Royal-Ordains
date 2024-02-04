from engine.uibattle.uibattle import CharacterSpeechBox


def player_input_wheel_ui_mode(self, player_index, dt):
    for key, pressed in self.battle.player_key_press[player_index].items():
        if pressed:
            if key == "Order Menu" or key == "Inventory Menu" or key == "Guard":
                if key == self.input_mode or key == "Guard":  # close current wheel
                    self.input_mode = None
                    self.player_input = self.player_input_battle_mode
                    self.battle.realtime_ui_updater.remove(self.battle.player_wheel_uis[player_index])
                else:  # change to another wheel ui menu
                    self.input_mode = key
                    if key == "Order Menu":
                        self.battle.player_wheel_uis[player_index].change_text_icon(self.command_name_list)
                    else:
                        self.battle.player_wheel_uis[player_index].change_text_icon(
                            [value for value in
                             self.battle.all_story_profiles[player_index]["equipment"]["inventory"].values()])
            elif key in ("Left", "Right", "Up", "Down"):  # select item in wheel
                self.battle.player_wheel_uis[player_index].selection(key)
            elif key == "Weak":  # select choice
                if self.input_mode == "Order Menu":
                    command = self.command_list[self.battle.player_wheel_uis[player_index].selected]
                    for follower in self.followers:
                        follower.follow_command = command
                    CharacterSpeechBox(self.battle.player_objects[player_index], command)
                else:
                    pass  # TODO add later for item system
                self.input_mode = None
                self.player_input = self.player_input_battle_mode
                self.battle.realtime_ui_updater.remove(self.battle.player_wheel_uis[player_index])
