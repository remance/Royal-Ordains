from engine.constants import Opposite_Team, Phase_To_Battle_Time


def state_battle_process(self):
    self.outer_ui_updater.remove(self.text_popup)
    self.player_input()

    if self.esc_press:  # pause game and open menu
        for sound_ch in self.battle_sound_channels:
            if sound_ch.get_busy():  # pause all sound playing
                sound_ch.pause()

        self.change_game_state("menu")  # open menu
        self.scene_translation_text_popup.popup(
            (self.screen_rect.midleft[0], self.screen_height * 0.82),
            self.localisation.grab_text(
                ("scene", self.scene.data[self.current_scene], "Text")),
            width_text_wrapper=self.screen_width)
        self.add_to_ui_menu_updater(self.cursor, self.battle_menu_button.values(),
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
    dt = self.true_dt * self.game_speed
    if dt > 0.016:  # one frame update should not be longer than 0.016 second (60 fps) for calculation
        dt = 0.016  # make it so stutter and lag does not cause overtime issue

    self.dt = dt  # apply dt with game_speed for calculation
    self.shown_camera_center_pos = self.camera_pos.copy()

    current_frame = self.camera_pos[0] / self.screen_width
    if current_frame == 0.5:  # at center of first scene
        self.current_scene = 1
        self.reach_scene = 1
    elif abs(current_frame - int(current_frame)) >= 0.5:  # at right half of scene
        self.current_scene = int(current_frame) + 1
        self.reach_scene = self.current_scene + 1
    else:
        self.current_scene = int(current_frame)  # at left half of scene
        self.reach_scene = self.current_scene

    if dt:
        # Screen shaking
        if self.screen_shake_value:
            decrease = 1000
            if self.screen_shake_value > decrease:
                decrease = self.screen_shake_value
            self.screen_shake_value -= (dt * decrease)
            if self.screen_shake_value <= 0:
                self.screen_shake_value = 0
            else:
                self.shake_camera()

        ai_process_list = self.ai_process_list  # process ai prepare
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
            battle_ai_commander.update(dt)

        if self.later_reinforcement:
            self.check_reinforcement()

        for team, team_stat in self.team_stat.items():
            team_stat["strategy_cooldown"] = {key: value - dt if value > dt else 0 for
                                              key, value in team_stat["strategy_cooldown"].items()}
            team_commander = self.team_commander[team]
            if team_commander and team_commander.alive and team_stat["strategy_resource"] < 200:
                team_stat["strategy_resource"] += dt * team_stat["strategy_regen"]
                if team_stat["strategy_resource"] > 100:
                    team_stat["strategy_resource"] = 100

            if team_stat["supply_reserve"]:
                if team_stat["supply_reserve"] > 0.1:
                    supply_transfer = team_stat["supply_reserve"] * 0.004 * dt
                else:
                    supply_transfer = team_stat["supply_reserve"]
                team_stat["supply_resource"] += supply_transfer
                team_stat["supply_reserve"] -= supply_transfer

        if self.cutscene_finish_camera_delay and not self.cutscene_playing:
            self.cutscene_finish_camera_delay -= self.true_dt
            if self.cutscene_finish_camera_delay < 0:
                self.cutscene_finish_camera_delay = 0

        self.battle_time += dt
        self.ui_timer += self.true_dt  # ui update by real time instead of self time to reduce workload

        if self.ai_battle_speak_timer:
            self.ai_battle_speak_timer -= dt
            if self.ai_battle_speak_timer < 0:
                self.ai_battle_speak_timer = 0

        self.team1_call_leader_cooldown_reinforcement = {key: value - dt for key, value in
                                                         self.team1_call_leader_cooldown_reinforcement.items() if
                                                         value > dt}
        self.team1_call_troop_cooldown_reinforcement = {key: value - dt for key, value in
                                                        self.team1_call_troop_cooldown_reinforcement.items() if
                                                        value > dt}
        self.team2_call_leader_cooldown_reinforcement = {key: value - dt for key, value in
                                                         self.team2_call_leader_cooldown_reinforcement.items() if
                                                         value > dt}
        self.team2_call_troop_cooldown_reinforcement = {key: value - dt for key, value in
                                                        self.team2_call_troop_cooldown_reinforcement.items() if
                                                        value > dt}

        # Weather system
        if self.current_weather.spawn_cooldown:
            self.current_weather.update(dt)

        # Battle related updater
        if not self.cutscene_playing:
            self.battle_character_updater.update(dt)
            self.battle_effect_updater.update(dt)
        else:
            self.battle_character_updater.cutscene_update(dt)
            self.battle_effect_updater.cutscene_update(dt)

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

        if not self.all_team_ally[1] or not self.all_team_ally[2]:  # no character exist in either team
            if not self.end_delay:
                # not ending scene yet, due to decision waiting or playing cutscene
                if self.drama_timer:
                    self.drama_timer = self.drama_text.timer
                win_team = " 1 "
                if not self.team_commander[1]:  # prioritise team 2 (defender) winning if both commander die
                    win_team = " 2 "
                result = "defeat"
                self.winner_team = int(win_team)

                # give upto 15% of loser's max supply to winning team
                loser_team = Opposite_Team[self.winner_team]

                gain_supply = 0
                transfer_supply = self.team_stat[loser_team]["total_supply"] * 0.15
                remain_supply = self.team_stat[loser_team]["supply_resource"] + self.team_stat[loser_team][
                    "supply_reserve"] * 0.15
                if transfer_supply < remain_supply:  # max supply is less than remain supply, use remain instead
                    transfer_supply = remain_supply
                if transfer_supply > self.team_stat[loser_team]["supply_resource"]:
                    # transfer from remaining active supply
                    gain_supply += self.team_stat[loser_team]["supply_resource"]
                    transfer_supply -= self.team_stat[loser_team]["supply_resource"]
                    self.team_stat[loser_team]["supply_resource"] = 0
                    # transfer the rest from reserve
                    if self.team_stat[loser_team]["supply_reserve"] < transfer_supply:
                        # not enough in reserve give whatever remain left
                        gain_supply += self.team_stat[loser_team]["supply_reserve"]
                        self.team_stat[loser_team]["supply_reserve"] = 0
                    else:
                        gain_supply += transfer_supply
                        self.team_stat[loser_team]["supply_reserve"] -= transfer_supply
                else:
                    gain_supply += transfer_supply
                    self.team_stat[loser_team]["supply_resource"] -= transfer_supply

                self.team_stat[self.winner_team]["supply_resource"] += gain_supply

                bad_drama = True
                if self.winner_team == self.player_team:
                    bad_drama = False
                    result = "victory"
                self.battle_helper_ui.battle_end(result)
                victory_drama = (bad_drama,
                                 self.localisation.grab_text(("ui", "result_text_team")) + win_team +
                                 self.localisation.grab_text(("ui", "result_text_win")), None)

                # redistribute remaining supply to army
                for team in self.team_stat:
                    army = [self.team_stat[team]["main_army"]] + self.team_stat[team]["reinforcement_army"]
                    army = [this_army for this_army in army if this_army and this_army.commander_id]
                    if army:
                        equal_distribute_supply = self.team_stat[team]["supply_resource"] + self.team_stat[team][
                            "supply_reserve"] / len(army)
                        for this_army in army:
                            this_army.supply = equal_distribute_supply

                self.end_delay = 0.1
                self.drama_text.queue = []  # clear all drama text queue
                self.drama_text.queue.append(victory_drama)
            else:
                self.end_delay += dt
                if self.end_delay >= 5:  # show result
                    self.outer_ui_updater.remove(self.command_ui, self.strategy_select_ui, self.player_interact,
                                                 self.battle_scale_ui, self.tactical_map_ui,
                                                 self.battle_helper_ui, self.battle_cursor)
                    self.outer_ui_updater.add(self.battle_result_ui, self.out_of_battle_result_button)

                    self.add_to_ui_menu_updater(self.cursor)

                    self.battle_result_ui.show_result()
                    self.change_game_state("result")
                    self.end_delay = 0

        elif self.grand:  # update grand campaign during battle still ongoing
            # time in battle is slower than time in grand campaign where 1 battle minute is equal to 1 phase instead of 1 second in campaign at normal game speed
            self.grandgrand_process(dt / Phase_To_Battle_Time)

    # update camera
    self.camera.camera_left_bound = self.camera_left_bound
    self.camera.camera_top_bound = self.shown_camera_center_pos[1] - self.camera_center_y
    self.camera.camera_right_bound = self.shown_camera_center_pos[0] + self.camera_w_center
    self.camera.camera_bottom_bound = self.shown_camera_center_pos[0] + self.camera_center_y
    self.scene.update()
    self.camera.update(self.battle_camera_object_drawer)
    self.outer_ui_updater.update(dt)
    self.camera.update(self.battle_camera_ui_drawer)
    self.camera.out_update(self.outer_ui_updater)
    self.blit_culling_check.clear()
