from types import MethodType
from copy import deepcopy

from pygame.mixer import Channel

from engine.character.character import Character


def state_battle_process(self, esc_press):
    if esc_press:  # pause game and open menu
        for sound_ch in range(0, 1000):
            if Channel(sound_ch).get_busy():  # pause all sound playing
                Channel(sound_ch).pause()
        if self.city_mode:  # add character setup UI for city mode when pause game
            for player in self.player_objects:
                self.add_ui_updater(self.player_char_base_interfaces[player],
                                    self.player_char_interfaces[player])
        self.change_game_state("menu")  # open menu
        scene = self.battle_stage.current_scene
        if self.scene:  # use city scene
            scene = self.scene
        self.stage_translation_text_popup.popup(
            (self.screen_rect.midleft[0], self.screen_height * 0.88),
            self.game.localisation.grab_text(
                ("map", self.chapter, self.mission, self.stage, str(scene), "Text")),
            width_text_wrapper=self.screen_width)
        self.add_ui_updater(self.cursor, self.battle_menu_button,
                            self.stage_translation_text_popup)  # add menu and its buttons to drawer
        self.realtime_ui_updater.remove(self.main_player_battle_cursor)
    elif self.city_mode and not self.cutscene_playing and \
            self.player_key_press[self.main_player]["Inventory Menu"]:
        # open court book
        self.court_book.add_portraits(self.main_story_profile["interface event queue"]["courtbook"])
        self.add_ui_updater(self.cursor, self.court_book)
        self.change_game_state("court")
    elif self.city_mode and not self.cutscene_playing and \
            self.player_key_press[self.main_player]["Special"]:
        # open city map
        self.add_ui_updater(self.cursor, self.city_map)
        self.change_game_state("map")

    self.camera_process()

    # Update game time
    self.dt = self.true_dt * self.game_speed  # apply dt with game_speed for calculation
    if self.dt > 0.1:  # one frame update should not be longer than 0.1 second for calculation
        self.dt = 0.1  # make it so stutter and lag does not cause overtime issue

    if self.cutscene_finish_camera_delay and not self.cutscene_playing:
        self.cutscene_finish_camera_delay -= self.dt
        if self.cutscene_finish_camera_delay < 0:
            self.cutscene_finish_camera_delay = 0
    self.ui_timer += self.dt  # ui update by real time instead of self time to reduce workload
    self.ui_dt = self.dt  # get ui timer before apply

    if self.main_player_battle_cursor.pos_change:  # display cursor when have movement
        self.show_cursor_timer = 0.1
        self.main_player_battle_cursor.shown = True

    if self.show_cursor_timer:
        self.show_cursor_timer += self.dt
        if self.show_cursor_timer > 3:
            self.show_cursor_timer = 0
            self.main_player_battle_cursor.shown = False
            self.main_player_battle_cursor.rect.topleft = (-100, -100)

    # Weather system
    if self.current_weather.spawn_rate:
        self.weather_spawn_timer += self.dt
        if self.weather_spawn_timer >= self.current_weather.spawn_rate:
            self.weather_spawn_timer = 0
            self.spawn_weather_matter()

    # Screen shaking
    self.shown_camera_pos = self.camera_pos.copy()  # reset camera pos first
    if self.screen_shake_value:
        self.screen_shake_value -= (self.dt * 100)
        self.shake_camera()
        if self.screen_shake_value < 0:
            self.screen_shake_value = 0

    # Battle related updater
    self.battle_stage.update(self.shown_camera_pos)  # update stage first
    if not self.cutscene_playing:
        self.character_updater.update(self.dt)
        self.effect_updater.update(self.dt)
    else:
        self.character_updater.cutscene_update(self.dt)
        self.effect_updater.cutscene_update(self.dt)
    self.realtime_ui_updater.update()  # update UI
    self.camera.update(self.shown_camera_pos, self.battle_camera, self.realtime_ui_updater)
    # self.frontground_stage.update(self.shown_camera_pos[0])  # update frontground stage last

    self.common_process()

    if self.ui_timer >= 0.1 and not self.city_mode:
        for key, value in self.player_objects.items():
            self.player_portraits[key].value_input(value)

        self.ui_drawer.draw(self.screen)  # draw the UI
        self.ui_timer -= 0.1

    if not self.cutscene_playing:  # no current cutscene check for event
        self.check_event()
    else:  # currently in cutscene mode
        end_battle_specific_mission = self.event_process()
        if end_battle_specific_mission:  # event cause the end of mission, go to the output mission next
            return end_battle_specific_mission

        if not self.cutscene_playing:  # finish with current parent cutscene
            for char in self.character_updater:  # add back hidden characters
                self.battle_camera.add(char.body_parts.values())
                if char.indicator:
                    self.battle_camera.add(char.indicator)
                char.cutscene_update = MethodType(Character.cutscene_update, char)
            if "once" in self.cutscene_playing_data[0]["Trigger"]:
                self.main_story_profile["story event"][self.cutscene_playing_data[0]["ID"] +
                                                       self.chapter + self.mission + self.stage] = True

    if not self.city_mode and not self.all_team_enemy_check[1] and not self.later_enemy[self.battle_stage.spawn_check_scene]:  # all enemies dead, end stage process TODO rework for pvp mode
        if not self.end_delay and not self.cutscene_playing:
            mission_str = self.chapter + "." + self.mission + "." + self.stage
            # not ending stage yet, due to decision waiting or playing cutscene
            victory_drama = ("Victory", None)
            if self.decision_select not in self.realtime_ui_updater and self.stage_end_choice:
                if mission_str not in self.main_story_profile["story choice"]:
                    if victory_drama not in self.drama_text.queue:
                        self.drama_text.queue.append(victory_drama)
                    self.realtime_ui_updater.add(self.decision_select)
            elif not self.stage_end_choice:
                if victory_drama not in self.drama_text.queue:
                    self.end_delay = 0.1
                    self.drama_text.queue.append(victory_drama)

            if self.decision_select.selected or mission_str in self.main_story_profile["story choice"]:
                self.end_delay = 0.1
                choice = self.decision_select.selected
                if mission_str in self.main_story_profile["story choice"]:
                    choice = self.main_story_profile["story choice"][mission_str]
                if choice == "yes":
                    self.cutscene_playing = self.submit_cutscene
                    self.cutscene_playing_data = deepcopy(self.submit_cutscene)
                else:  # start execution cutscene
                    self.cutscene_playing = self.execute_cutscene
                    self.cutscene_playing_data = deepcopy(self.execute_cutscene)

                self.realtime_ui_updater.remove(self.decision_select)

        if not self.cutscene_playing and self.end_delay:
            #  player select decision or mission has no decision, count end delay
            self.end_delay += self.dt

            if self.end_delay >= 5:  # end battle
                self.end_delay = 0

                if str(int(self.stage) + 1) in self.game.preset_map_data[self.chapter][self.mission] or \
                        str(int(self.mission) + 1) in self.game.preset_map_data[self.chapter]:
                    # has next stage or mission
                    return True
                else:
                    return False
