import sys

import pygame
from pygame import quit as pg_quit


def state_grand_process(self):
    if self.input_popup:  # currently, have input text pop up on screen, stop everything else until done.
        self.ui_menu_updater.update(self.true_dt)
        self.camera.update_with_in_camera_check(self.grand_camera_region_drawer)
        # add route after map region draw to blit route dots on the map under other sprites.
        self.draw_route()

        self.camera.update_with_in_camera_check(self.grand_camera_object_drawer)
        self.camera.update(self.grand_camera_ui_drawer)
        self.camera.out_update(self.outer_ui_drawer)
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
            elif self.input_popup[1] == "dismiss":
                character = self.input_popup[2]
                self.dismiss_faction_character(self.player_faction, character)
                self.court_management_ui.court_reset()

            elif self.input_popup[1] == "quit":
                pygame.time.wait(1000)
                pg_quit()
                sys.exit()

            if done:
                self.change_pause_update(False)
                self.input_box.render_text("")
                self.input_popup = None
                self.remove_from_ui_menu_updater(self.all_input_popup_uis)
                self.add_to_outer_ui_menu_updater(self.cursor)
                self.remove_from_ui_menu_updater(self.cursor)

        elif self.input_cancel_button.event_press or self.input_close_button.event_press or self.esc_press:
            self.change_pause_update(False)
            self.input_box.render_text("")
            self.input_popup = None
            self.remove_from_ui_menu_updater(self.all_input_popup_uis)

    else:
        # Update game time
        dt = self.true_dt * self.game_speed
        self.dt = dt  # apply dt with game_speed for calculation

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
        self.grand_object_updater.update(self.true_dt, dt)
        self.grand_effect_updater.update(self.true_dt)

        # if self.current_campaign_state["battle"]["manual"]:
        #     self.battle.grand_event_notification

        # update camera
        self.camera.camera_left_bound = self.camera_topleft_pos[0]
        self.camera.camera_top_bound = self.camera_topleft_pos[1]
        self.camera.camera_right_bound = self.camera.camera_left_bound + self.screen_width
        self.camera.camera_bottom_bound = self.camera.camera_top_bound + self.screen_height

        # draw object to camera
        self.camera.update_with_in_camera_check(self.grand_camera_region_drawer)
        # add route after map region draw to blit route dots on the map under other sprites.
        self.draw_route()

        # update ui
        self.grand_camera_ui_updater.update(self.true_dt)
        self.outer_ui_updater.update(dt)

        # draw ui
        self.camera.update_with_in_camera_check(self.grand_camera_object_drawer)
        self.camera.update(self.grand_camera_ui_drawer)
        self.camera.out_update(self.outer_ui_drawer)
        self.camera.out_update(self.ui_menu_drawer)

        if self.esc_press:  # pause game and open menu
            self.music_channel.set_volume(0)
            self.ambient_channel.set_volume(0)

            for sound_ch in self.effect_sound_channels:
                if sound_ch.get_busy():  # pause all sound playing
                    sound_ch.set_volume(0)

            self.menu_bar_ui.option_selected = None
            self.change_game_state("menu")  # open menu
            self.remove_from_outer_ui_menu_updater(self.cursor)
            self.add_to_ui_menu_updater(self.cursor)
            self.add_to_ui_menu_updater(self.grand_menu_button.values())  # add menu and its buttons to drawer

