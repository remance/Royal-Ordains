import sys
import pygame
from pygame import quit as pg_quit


def state_grand_process(self):
    if self.input_popup:  # currently, have input text pop up on screen, stop everything else until done.
        self.ui_menu_updater.update(self.true_dt)
        self.grand_map.update()

        self.camera.update(self.grand_camera_object_drawer)
        self.camera.out_update(self.outer_ui_updater)
        self.camera.out_update(self.ui_menu_drawer)

        if self.input_ok_button.event_press:
            done = True

            if self.input_popup[1] in ("retreat", "retreat_assemble"):
                # all army in the same battles retreat and lose battle
                for army in self.player_selected_army:  # TODO finish retreat function here
                    army.issue_move_command(self.input_popup[2][0], direct=self.input_popup[2][1])
                    # if army.base_pos in self.current_campaign_state["battle"]["auto"]:
                    #     self.current_campaign_state["battle"]["auto"].remove(army.base_pos)
                    #
                    # for battle in self.current_campaign_state["battle"]["auto"]:

                    # self.grand.current_campaign_state["battle"]["armies"].remove(self.game_id)
                # for army in self.player_selected_army:

                pass
            elif self.input_popup[1] == "assemble":
                for army in self.player_selected_army:
                    army.issue_move_command(self.input_popup[2][0], direct=self.input_popup[2][1])

            elif self.input_popup[1] == "quit":
                pygame.time.wait(1000)
                pg_quit()
                sys.exit()

            if done:
                self.change_pause_update(False)
                self.input_box.render_text("")
                self.input_popup = None
                self.remove_from_ui_menu_updater(self.all_input_popup_uis)

        elif self.input_cancel_button.event_press or self.input_close_button.event_press or self.esc_press:
            self.change_pause_update(False)
            self.input_box.render_text("")
            self.input_popup = None
            self.remove_from_ui_menu_updater(self.all_input_popup_uis)

        # elif self.input_popup[0] == "text_input":
        #     if not self.text_delay:
        #         if key_press[self.input_box.hold_key]:
        #             self.input_box.player_input(None, key_press)
        #             self.text_delay = 0.15
        #     else:
        #         self.text_delay -= self.dt
        #         if self.text_delay < 0:
        #             self.text_delay = 0.
    else:
        if self.esc_press or self.menu_bar_ui.option_selected == "menu":  # pause game and open menu
            for sound_ch in self.effect_sound_channels:
                if sound_ch.get_busy():  # pause all sound playing
                    sound_ch.pause()

            self.menu_bar_ui.option_selected = None
            self.change_game_state("menu")  # open menu
            self.add_to_ui_menu_updater(self.grand_menu_button.values())  # add menu and its buttons to drawer

        # Update game time
        dt = self.true_dt * self.game_speed
        self.dt = dt  # apply dt with game_speed for calculation
        self.shown_camera_topleft_pos = self.camera_pos.copy()

        self.player_input()

        if dt:
            if dt > 0.016:  # one frame update should not be longer than 0.016 second (60 fps) for calculation.
                dt = 0.016  # make it so stutter and lag does not cause overtime issue.

            if self.grand_process(dt):  # TRUE if phase changed
                self.mini_cosmic_ui.reset()
                self.sort_player_army_list()

            self.ui_timer += self.true_dt  # ui update by real time instead of self time to reduce workload.

            # Screen shaking
            if self.screen_shake_value:
                decrease = 1000
                if self.screen_shake_value > decrease:
                    decrease = self.screen_shake_value
                self.screen_shake_value -= (dt * decrease)
                if self.screen_shake_value < 0:
                    self.screen_shake_value = 0
                else:
                    self.shake_camera()

            if self.sound_effect_queue:
                for key, value in self.sound_effect_queue.items():  # play each sound effect initiate in this loop
                    self.play_sound_effect(key, value)
                self.sound_effect_queue = {}

            self.drama_process()

        # Object related updater
        self.grand_actor_updater.update(self.true_dt, dt)
        self.grand_effect_updater.update(self.true_dt)

        # if self.current_campaign_state["battle"]["manual"]:
        #     self.battle.grand_event_notification

        # update camera
        self.camera.camera_left_bound = self.shown_camera_topleft_pos[0]
        self.camera.camera_top_bound = self.shown_camera_topleft_pos[1]
        self.camera.camera_right_bound = self.camera.camera_left_bound + self.screen_width
        self.camera.camera_bottom_bound = self.camera.camera_top_bound + self.screen_height
        self.grand_map.update()

        # update ui and add object to camera
        self.grand_camera_ui_updater.update(self.true_dt)
        self.camera.update(self.grand_camera_object_drawer)
        self.outer_ui_updater.update(dt)
        self.camera.update(self.ui_menu_drawer)
        self.camera.out_update(self.outer_ui_updater)

