import sys

from pygame import quit as pg_quit


def state_menu_process(self, esc_press):
    self.back_stage.update(self.shown_camera_pos, self.camera_pos)  # update backstage first
    self.battle_stage.update(self.shown_camera_pos, self.camera_pos)
    # self.realtime_ui_updater.update()  # update UI
    self.camera.update(self.shown_camera_pos, self.battle_camera)
    self.front_stage.update(self.shown_camera_pos, self.camera_pos)  # update front stage last
    self.camera.out_update(self.realtime_ui_updater)
    self.ui_drawer.draw(self.screen)  # draw the UI

    if self.input_popup:  # currently, have input pop up on screen, stop everything else until done
        if self.input_ok_button.event_press:
            self.change_pause_update(False)
            self.input_box.text_start("")
            input_popup = self.input_popup[1]
            self.input_popup = None
            self.remove_ui_updater(self.input_ui_popup, self.confirm_ui_popup)

            if input_popup == "quit":  # quit game
                pg_quit()
                sys.exit()
            elif input_popup == "main_menu":
                self.back_to_battle_state()
                return False
            elif input_popup == "end_battle":
                self.back_to_battle_state()
                return "Throne"

        elif self.input_cancel_button.event_press or esc_press:
            self.change_pause_update(False)
            self.input_box.text_start("")
            self.input_popup = None
            self.remove_ui_updater(self.input_ui_popup, self.confirm_ui_popup)

    else:
        self.escmenu_process(esc_press)
