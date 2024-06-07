def state_court_process(self, esc_press):
    self.camera.update(self.shown_camera_pos, self.battle_camera, self.realtime_ui_updater)
    self.ui_drawer.draw(self.screen)  # draw the UI

    self.common_process()

    if self.player_key_press[self.main_player]["Inventory Menu"] or esc_press:
        self.remove_ui_updater(self.cursor, self.court_book)
        self.change_game_state("battle")
