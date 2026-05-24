def state_result_process(self):
    # update battle scene first here
    self.scene.update()
    self.camera.update(self.battle_camera_object_drawer)

    self.camera.update(self.battle_camera_ui_drawer)
    self.outer_ui_updater.update(self.true_dt)

    self.camera.out_update(self.outer_ui_updater)
    self.ui_menu_drawer.draw(self.screen)  # draw the UI

    if self.out_of_battle_result_button.event_press or self.esc_press:
        self.outer_ui_updater.remove(self.out_of_battle_result_button, self.battle_result_ui)
        self.back_to_battle_state()
        self.battle_helper_ui.battle_end("normal")
        return True
