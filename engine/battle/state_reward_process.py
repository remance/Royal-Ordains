def state_reward_process(self, esc_press):
    self.battle_stage.update(self.shown_camera_pos)  # update stage first
    self.camera.update(self.shown_camera_pos, self.battle_camera, self.realtime_ui_updater)
    # self.frontground_stage.update(self.shown_camera_pos)  # update frontground stage last
    self.ui_drawer.draw(self.screen)  # draw the UI

    self.common_process()

    if self.input_popup:  # currently, have input text pop up on screen, stop everything else until done
        if self.input_ok_button.event_press:
            for interface in self.player_char_interfaces.values():
                interface.reward_list = {}
                interface.change_mode("stat")
            self.change_game_state("battle")
            self.remove_ui_updater(self.cursor, self.player_char_base_interfaces.values(),
                                   self.player_char_interfaces.values(), self.input_ui_popup,
                                   self.confirm_ui_popup)

            self.input_box.text_start("")
            self.input_popup = None

        elif self.input_cancel_button.event_press or esc_press:
            self.change_pause_update(False)
            self.input_box.text_start("")
            self.input_popup = None
            self.remove_ui_updater(self.cursor, self.input_ui_popup, self.confirm_ui_popup)

    else:
        if esc_press:  # close and accept reward
            self.activate_input_popup(("confirm_input", "reward"), "Confirm Reward?", self.confirm_ui_popup)
            self.add_ui_updater(self.cursor)
        else:
            for key_list in (self.player_key_press, self.player_key_hold):
                # check key holding for stat mode as well
                for player in key_list:
                    if player in self.player_objects:
                        for key, pressed in key_list[player].items():
                            if pressed:
                                self.player_char_interfaces[player].player_input(key)
