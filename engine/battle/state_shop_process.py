def state_shop_process(self, esc_press):
    self.back_stage.update(self.shown_camera_pos, self.camera_pos)  # update backstage first
    self.battle_stage.update(self.shown_camera_pos, self.camera_pos)
    self.camera.update(self.shown_camera_pos, self.battle_camera)
    self.front_stage.update(self.shown_camera_pos, self.camera_pos)  # update front stage last
    self.camera.out_update(self.realtime_ui_updater)
    self.ui_drawer.draw(self.screen)  # draw the UI

    self.common_process()

    if esc_press:  # close shop
        for interface in self.player_char_interfaces.values():
            interface.shop_list = []
            interface.purchase_list = {}
            interface.change_mode("stat")
        self.remove_ui_updater(self.cursor, self.player_char_base_interfaces.values(),
                               self.player_char_interfaces.values())
        self.change_game_state("battle")
    else:
        for key_list in (self.player_key_press, self.player_key_hold):
            # check key holding for stat mode as well
            for player in key_list:
                if player in self.player_objects:
                    for key, pressed in key_list[player].items():
                        if pressed:
                            self.player_char_interfaces[player].player_input(key)
