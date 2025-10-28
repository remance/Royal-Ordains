import sys

from pygame import quit as pg_quit


def state_menu_process(self):
    # update battle scene first here
    self.scene.update()
    self.camera.update(self.battle_camera_object_drawer)

    self.camera.update(self.battle_camera_ui_drawer)
    self.camera.out_update(self.battle_outer_ui_updater)
    self.ui_drawer.draw(self.screen)  # draw the UI

    if self.input_popup:  # currently, have input pop up on screen, stop everything else until done
        if self.input_ok_button.event_press:
            self.change_pause_update(False)
            self.input_box.render_text("")
            input_popup = self.input_popup[1]
            self.input_popup = None
            self.remove_ui_updater(self.input_popup_uis, self.confirm_popup_uis)

            if input_popup == "quit":  # quit game
                pg_quit()
                sys.exit()
            elif input_popup == "end_battle":
                self.back_to_battle_state()
                if self.end_delay:  # quit battle during already victory screen
                    return True
                return False

        elif self.input_cancel_button.event_press or self.esc_press:
            self.change_pause_update(False)
            self.input_box.render_text("")
            self.input_popup = None
            self.remove_ui_updater(self.input_popup_uis, self.confirm_popup_uis)

    else:
        self.escmenu_process()
