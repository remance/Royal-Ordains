def state_battle_process(self):
    self.outer_ui_updater.remove(self.text_popup)
    self.player_input()

    if self.esc_press:  # pause game and open menu
        for sound_ch in self.battle_sound_channel:
            if sound_ch.get_busy():  # pause all sound playing
                sound_ch.pause()

        self.change_game_state("menu")  # open menu
        self.scene_translation_text_popup.popup(
            (self.screen_rect.midleft[0], self.screen_height * 0.82),
            self.game.localisation.grab_text(
                ("scene", self.scene.data[self.current_scene], "Text")),
            width_text_wrapper=self.screen_width)
        self.add_to_ui_updater(self.cursor, self.battle_menu_button.values(),
                               self.scene_translation_text_popup)  # add menu and its buttons to drawer
        self.outer_ui_updater.remove(self.battle_cursor)
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
    new_dt = self.true_dt * self.game_speed

    self.dt = new_dt  # apply dt with game_speed for calculation
    self.shown_camera_pos = self.camera_pos.copy()

    if new_dt:
        if new_dt > 0.016:  # one frame update should not be longer than 0.016 second (60 fps) for calculation
            new_dt = 0.016  # make it so stutter and lag does not cause overtime issue

        ai_process_list = self.ai_process_list
        if ai_process_list:
            limit = int(len(ai_process_list) / 20)
            if limit < 20:
                limit = 20
                if limit > len(ai_process_list):
                    limit = len(ai_process_list)
            for index in range(limit):
                this_character = ai_process_list[index]
                if this_character.alive:
                    this_character.ai_prepare()

            self.ai_process_list = ai_process_list[limit:]

        for battle_ai_commander in self.all_battle_ai_commanders:
            battle_ai_commander.update(new_dt)

        if self.later_reinforcement:
            self.check_reinforcement()

        for team, team_stat in self.team_stat.items():
            team_stat["strategy_cooldown"] = {key: value - new_dt if value > new_dt else 0 for
                                              key, value in team_stat["strategy_cooldown"].items()}
            if self.team_commander[team] and self.team_commander[team].alive and team_stat["strategy_resource"] < 100:
                team_stat["strategy_resource"] += new_dt * self.team_commander[team].strategy_regen
                if team_stat["strategy_resource"] > 100:
                    team_stat["strategy_resource"] = 100

            if team_stat["supply_reserve"]:
                if team_stat["supply_reserve"] > 0.1:
                    supply_transfer = team_stat["supply_reserve"] * 0.004 * new_dt
                else:
                    supply_transfer = team_stat["supply_reserve"]
                team_stat["supply_resource"] += supply_transfer
                team_stat["supply_reserve"] -= supply_transfer

        if self.cutscene_finish_camera_delay and not self.cutscene_playing:
            self.cutscene_finish_camera_delay -= self.true_dt
            if self.cutscene_finish_camera_delay < 0:
                self.cutscene_finish_camera_delay = 0

        self.battle_time += new_dt
        self.ui_timer += self.true_dt  # ui update by real time instead of self time to reduce workload

        if self.ai_battle_speak_timer:
            self.ai_battle_speak_timer -= new_dt
            if self.ai_battle_speak_timer < 0:
                self.ai_battle_speak_timer = 0

        self.team1_call_leader_cooldown_reinforcement = {key: value - new_dt for key, value in
                                                         self.team1_call_leader_cooldown_reinforcement.items() if
                                                         value > new_dt}
        self.team1_call_troop_cooldown_reinforcement = {key: value - new_dt for key, value in
                                                        self.team1_call_troop_cooldown_reinforcement.items() if
                                                        value > new_dt}
        self.team2_call_leader_cooldown_reinforcement = {key: value - new_dt for key, value in
                                                         self.team2_call_leader_cooldown_reinforcement.items() if
                                                         value > new_dt}
        self.team2_call_troop_cooldown_reinforcement = {key: value - new_dt for key, value in
                                                        self.team2_call_troop_cooldown_reinforcement.items() if
                                                        value > new_dt}

        # Weather system
        if self.current_weather.spawn_cooldown:
            self.current_weather.update(new_dt)

        # Screen shaking
        if self.screen_shake_value:
            decrease = 1000
            if self.screen_shake_value > decrease:
                decrease = self.screen_shake_value
            self.screen_shake_value -= (new_dt * decrease)
            if self.screen_shake_value < 0:
                self.screen_shake_value = 0
            else:
                self.shake_camera()

        # Battle related updater
        if not self.cutscene_playing:
            self.battle_character_updater.update(new_dt)
            self.battle_effect_updater.update(new_dt)
        else:
            self.battle_character_updater.cutscene_update(new_dt)
            self.battle_effect_updater.cutscene_update(new_dt)

        if self.sound_effect_queue:
            for key, value in self.sound_effect_queue.items():  # play each sound effect initiate in this loop
                self.play_sound_effect(key, value)
            self.sound_effect_queue = {}

        self.drama_process()

        if self.ui_timer >= 0.1:
            self.battle_scale = ()
            if self.all_battle_characters:
                self.battle_scale = [len(value) / len(self.all_battle_characters) for value in
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
        #                 self.music.stop()
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
        #         self.end_delay += new_dt
        #
        #         if self.end_delay >= 5:  # end battle
        #             self.end_delay = 0
        #             return True

    self.camera_y_shift = self.camera_center_y - self.shown_camera_pos[1]
    self.camera_x_shift = self.shown_camera_pos[0] - self.camera_w_center  # camera topleft x
    # camera_right_x = pos[0] + self.camera_w_center  # camera topleft x
    self.camera_y = self.shown_camera_pos[1] - self.camera_h_center  # camera topleft y
    self.camera.camera_x_shift = self.camera_x_shift
    self.camera.camera_y_shift = self.camera_y_shift
    self.scene.update()
    self.camera.update(self.battle_camera_object_drawer)
    self.outer_ui_updater.update(new_dt)

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

    self.camera.update(self.battle_camera_ui_drawer)
    self.camera.out_update(self.outer_ui_updater)
    self.blit_culling_check.clear()
