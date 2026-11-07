from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.grand.grand import Grand

import sys
from random import choice

import pygame
from pygame import Sound, quit as pg_quit


def state_grand_process(self: Grand):
    true_dt = self.true_dt
    camera = self.camera
    if not self.input_popup:
        # Update game time
        dt = true_dt * self.game_speed
        self.dt = dt  # apply dt with game_speed for calculation

        self.player_input()

        if dt:
            if dt > 0.016:  # one frame update should not be longer than 0.016 second (60 fps) for calculation.
                dt = 0.016  # make it so stutter and lag does not cause overtime issue.

            if self.grand_process(dt):  # TRUE if phase changed
                self.mini_cosmic_ui.reset()
                self.sort_player_army_list()

        self.ui_timer += true_dt  # ui update by real time instead of self time to reduce workload.

        if not self.music_channel.get_busy():  # whatever music end, pick random from default battle music
            self.music_channel.set_volume(self.play_music_volume)
            self.music_channel.play(Sound(choice(self.default_grand_music_pool)), fade_ms=100)

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

        self.drama_process(add_battle_log=False)

        if self.diplomacy_head_talk_queue and self.diplomacy_head_ui not in self.outer_ui_updater:
            self.start_diplomacy_talk()

        # Object related updater
        self.grand_object_updater.update(true_dt, dt)
        self.grand_effect_updater.update(true_dt)

        # if self.current_campaign_state["battle"]["manual"]:
        #     self.battle.grand_event_notification

        # update camera
        camera.camera_left_bound = self.camera_topleft_pos[0]
        camera.camera_top_bound = self.camera_topleft_pos[1]
        camera.camera_right_bound = camera.camera_left_bound + self.screen_width
        camera.camera_bottom_bound = camera.camera_top_bound + self.screen_height

        # draw object to camera
        camera.update_with_in_camera_check(self.grand_camera_region_drawer)
        # add route after map region draw to blit route dots on the map under other sprites.
        self.draw_route()

        # update and draw ui within camera
        self.grand_camera_ui_updater.update(true_dt)
        camera.update_with_in_camera_check(self.grand_camera_object_drawer)
        camera.update(self.grand_camera_ui_drawer)

        # update and draw ui outside camera
        self.outer_ui_updater.update(true_dt)
        camera.out_update(self.outer_ui_drawer)
        camera.out_update(self.ui_menu_drawer)

        if self.esc_press:  # pause game and open menu
            self.music_channel.pause()
            self.ambient_channel.pause()

            for sound_ch in self.effect_sound_channels:
                if sound_ch.get_busy():  # pause all sound playing
                    sound_ch.pause()

            self.menu_bar_ui.option_selected = None
            self.change_game_state("menu")  # open menu
            self.remove_from_outer_ui_menu_updater(self.player_collapsable_uis)
            self.remove_from_outer_ui_menu_updater(self.cursor)
            self.add_to_ui_menu_updater(self.cursor)
            self.add_to_ui_menu_updater(self.grand_menu_button.values())  # add menu and its buttons to drawer
    else:  # have input text pop up on screen, stop everything else until done
        self.ui_menu_updater.update(true_dt)
        camera.update_with_in_camera_check(self.grand_camera_region_drawer)
        # add route after map region draw to blit route dots on the map under other sprites.
        self.draw_route()

        # draw ui within camera
        camera.update_with_in_camera_check(self.grand_camera_object_drawer)
        camera.update(self.grand_camera_ui_drawer)

        # draw ui outside camera
        camera.out_update(self.outer_ui_drawer)
        camera.out_update(self.ui_menu_drawer)

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
                    self.add_sound_effect_queue(choice(self.sound_effect_pool["army_march"]),
                                                self.base_camera_center_pos, 9999999999999,
                                                0)
                # for army in self.player_selected_army:

                pass
            elif self.input_popup[1] == "dismiss":
                character = self.input_popup[2]
                self.dismiss_faction_character(self.player_faction, character)
                self.court_management_ui.reset()

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

    # if self.current_campaign_state["cosmic_event"]:  # add colour effect to screen from cosmic
    #     for event in self.cosmic_event_list:
    #         # apply colour effect only for first event in list
    #         colour = self.cosmic_event_list[event]["Colour"]
    #         s = pygame.Surface(self.screen_size, pygame.SRCALPHA)
    #         if colour:
    #             s.fill(colour)
    #             self.camera.image.blit(s)
    #         break
