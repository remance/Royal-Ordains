def state_battle_process(self):
    self.player_input()

    if self.esc_press:  # pause game and open menu
        for sound_ch in self.battle_sound_channel:
            if sound_ch.get_busy():  # pause all sound playing
                sound_ch.pause()

        self.change_game_state("menu")  # open menu
        self.scene_translation_text_popup.popup(
            (self.screen_rect.midleft[0], self.screen_height * 0.88),
            self.game.localisation.grab_text(
                ("scene", self.mission, str(self.current_scene), "Text")),
            width_text_wrapper=self.screen_width)
        self.add_ui_updater(self.cursor, self.battle_menu_button.values(),
                            self.scene_translation_text_popup)  # add menu and its buttons to drawer
        self.battle_outer_ui_updater.remove(self.battle_cursor)
    # elif not self.cutscene_playing:
    #     if self.player_key_press["Inventory Menu"]:
    #         # open court book
    #         self.court_book.add_portraits(self.main_story_profile["interface event queue"]["courtbook"])
    #         self.add_ui_updater(self.cursor, self.court_book)
    #         self.change_game_state("court")
    #     elif self.player_key_press["Special"]:
    #         # open city map
    #         self.add_ui_updater(self.cursor, self.city_map)
    #         self.change_game_state("map")

    # Update game time
    self.dt = self.true_dt * self.game_speed  # apply dt with game_speed for calculation
    self.shown_camera_pos = self.camera_pos.copy()

    if self.dt:
        if self.dt > 0.016:  # one frame update should not be longer than 0.016 second (60 fps) for calculation
            self.dt = 0.016  # make it so stutter and lag does not cause overtime issue

        if self.ai_process_list:
            limit = int(len(self.ai_process_list) / 20)
            if limit < 20:
                limit = 20
                if limit > len(self.ai_process_list):
                    limit = len(self.ai_process_list)
            for index in range(limit):
                this_character = self.ai_process_list[index]
                if this_character.alive:
                    this_character.ai_prepare()

            self.ai_process_list = self.ai_process_list[limit:]

        if self.cutscene_finish_camera_delay and not self.cutscene_playing:
            self.cutscene_finish_camera_delay -= self.true_dt
            if self.cutscene_finish_camera_delay < 0:
                self.cutscene_finish_camera_delay = 0

        self.battle_time += self.dt
        self.ui_timer += self.true_dt  # ui update by real time instead of self time to reduce workload

        if self.ai_battle_speak_timer:
            self.ai_battle_speak_timer -= self.dt
            if self.ai_battle_speak_timer < 0:
                self.ai_battle_speak_timer = 0

        # Weather system
        if self.current_weather.spawn_cooldown:
            self.current_weather.update(self.dt)

        # Screen shaking
        if self.screen_shake_value:
            decrease = 1000
            if self.screen_shake_value > decrease:
                decrease = self.screen_shake_value
            self.screen_shake_value -= (self.dt * decrease)
            if self.screen_shake_value < 0:
                self.screen_shake_value = 0
            else:
                self.shake_camera()

        # Battle related updater
        if not self.cutscene_playing:
            self.character_updater.update(self.dt)
            self.effect_updater.update(self.dt)
        else:
            self.character_updater.cutscene_update(self.dt)
            self.effect_updater.cutscene_update(self.dt)

        if self.sound_effect_queue:
            for key, value in self.sound_effect_queue.items():  # play each sound effect initiate in this loop
                self.play_sound_effect(key, value)
            self.sound_effect_queue = {}

        self.drama_process()

        if self.ui_timer >= 0.1:
            self.battle_scale = ()
            if self.all_characters:
                self.battle_scale = [len(value) / len(self.all_characters) for value in
                                     self.all_team_ally.values()]
            self.ui_drawer.draw(self.screen)  # draw the UI
            self.ui_timer -= 0.1

        if not self.cutscene_playing:  # no current cutscene check for event
            self.check_event()
        # else:  # currently in cutscene mode
        #     end_battle_specific_mission = self.event_process()
        #     if end_battle_specific_mission is not None:  # event cause the end of mission, go to the output mission next
        #         return end_battle_specific_mission
        #
        #     if not self.cutscene_playing:  # finish with current parent cutscene
        #         for char in self.character_updater:  # add back hidden characters
        #             if char.indicator:
        #                 self.battle_camera.add(char.indicator)
        #             char.cutscene_update = MethodType(Character.cutscene_update, char)
        #         if "once" in self.cutscene_playing_data[0]["Trigger"]:
        #             self.main_story_profile["story event"][self.cutscene_playing_data[0]["ID"] +
        #                                                    self.mission] = True

        # if not self.all_team_enemy_check[1] and not self.later_enemy[
        #     self.spawn_check_scene]:  # all enemies dead, end scene process
        #     if not self.end_delay and not self.cutscene_playing:
        #         mission_str = + self.mission
        #         # not ending scene yet, due to decision waiting or playing cutscene
        #         victory_drama = ("Victory", None)
        #         if self.decision_select not in self.realtime_ui_updater and self.stage_end_choice:
        #             if mission_str not in self.main_story_profile["story choice"]:
        #                 self.current_music = None  # stop music during end decision
        #                 self.music_left.stop()
        #                 self.music_right.stop()
        #
        #                 if victory_drama not in self.drama_text.queue:
        #                     self.drama_text.queue.append(victory_drama)
        #                 self.realtime_ui_updater.add(self.decision_select)
        #         elif not self.stage_end_choice:  # no choice in this scene, just show victory banner and count to end
        #             if victory_drama not in self.drama_text.queue:
        #                 self.end_delay = 0.1
        #                 self.drama_text.queue.append(victory_drama)
        #
        #         if self.decision_select.selected or mission_str in self.main_story_profile["story choice"]:
        #             self.end_delay = 0.1
        #             choice = self.decision_select.selected
        #             if mission_str in self.main_story_profile["story choice"]:
        #                 choice = self.main_story_profile["story choice"][mission_str]
        #
        #             self.realtime_ui_updater.remove(self.decision_select)
        #
        #     if not self.cutscene_playing and self.end_delay:
        #         #  player select decision or mission has no decision, count end delay
        #         self.end_delay += self.dt
        #
        #         if self.end_delay >= 5:  # end battle
        #             self.end_delay = 0
        #             return True

    self.camera_y_shift = self.camera_center_y - self.shown_camera_pos[1]
    self.scene.update(self.camera_left, self.camera_y_shift)
    self.camera.update(self.shown_camera_pos, self.battle_cameras["battle"])
    self.battle_outer_ui_updater.update()

    current_frame = self.camera_pos[0] / self.screen_width
    if current_frame == 0.5:  # at center of first scene
        self.current_scene = 1
        self.spawn_check_scene = 1
        self.reach_scene = 1
    elif abs(current_frame - int(current_frame)) >= 0.5:  # at right half of scene
        self.current_scene = int(current_frame) + 1
        self.spawn_check_scene = self.current_scene
        self.reach_scene = self.current_scene + 1
    else:
        self.current_scene = int(current_frame)  # at left half of scene
        self.spawn_check_scene = self.current_scene + 1
        self.reach_scene = self.current_scene

    self.camera.update(self.shown_camera_pos, self.battle_cameras["ui"])
    self.camera.out_update(self.battle_outer_ui_updater)
