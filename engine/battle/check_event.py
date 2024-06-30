from random import randint
from copy import deepcopy


def check_event(self):
    if self.next_lock:  # stage has lock, check if player reach next lock or unlock it
        if self.lock_objective:  # player in locked stage, check if pass yet
            pass_objective = False  # check for passing lock objective
            if self.lock_objective == "clear":
                if not len([enemy for enemy in self.all_team_enemy_check[1] if
                            self.base_stage_start <= enemy.base_pos[0] <= self.base_stage_end]):
                    pass_objective = True
            elif self.lock_objective == "survive":
                self.survive_timer -= self.dt
                if self.survive_timer < 0:
                    self.survive_timer = 0
                    pass_objective = True

            if pass_objective:  # can reach next scene, check for possible scene lock
                self.lock_objective = None
                if self.stage_scene_lock:
                    self.next_lock = tuple(self.stage_scene_lock.keys())[0]
                    self.base_stage_end = self.base_stage_end_list[self.next_lock[-1]]
                    self.stage_end = self.stage_end_list[self.next_lock[-1]]
                else:  # no more lock, make the stage_end the final stage position
                    self.next_lock = None  # assign None so no need to do below code in later update
                    self.base_stage_end = self.base_stage_end_list[
                        tuple(self.base_stage_end_list.keys())[-1]]
                    self.stage_end = self.stage_end_list[tuple(self.stage_end_list.keys())[-1]]

        elif self.battle_stage.current_scene >= self.next_lock[0]:
            # player (camera) reach next lock
            self.base_stage_start = self.base_stage_end_list[self.next_lock[0]] - 1920
            self.stage_start = self.stage_end_list[self.next_lock[0]]
            self.base_stage_end = self.base_stage_end_list[self.next_lock[-1]]
            self.stage_end = self.stage_end_list[self.next_lock[-1]]

            self.lock_objective = self.stage_scene_lock[self.next_lock]
            if "survive" in self.lock_objective:
                self.survive_timer = float(self.lock_objective.split("_")[-1])
                self.lock_objective = "survive"

            self.stage_scene_lock.pop(self.next_lock)

    if self.later_enemy[self.battle_stage.spawn_check_scene]:
        # check for enemy arriving based on camera pos
        self.spawn_delay_timer[self.battle_stage.spawn_check_scene] += self.dt
        first_delay = tuple(self.later_enemy[self.battle_stage.spawn_check_scene].keys())[0]
        if self.spawn_delay_timer[self.battle_stage.spawn_check_scene] >= first_delay:
            # spawn based on delay timer
            self.spawn_character((), self.later_enemy[self.battle_stage.spawn_check_scene][
                first_delay], add_helper=False)
            self.later_enemy[self.battle_stage.spawn_check_scene].pop(first_delay)

    for player_index, player_object in self.player_objects.items():
        player_object.player_input(player_index, self.dt)

    if self.reach_scene_event_list:
        # check for event with camera reaching
        if self.battle_stage.reach_scene in self.reach_scene_event_list:
            if "weather" in self.reach_scene_event_list[self.battle_stage.reach_scene]:
                # change weather
                self.current_weather.__init__(
                    self.reach_scene_event_list[self.battle_stage.reach_scene]["weather"][0],
                    self.reach_scene_event_list[self.battle_stage.reach_scene]["weather"][1],
                    self.reach_scene_event_list[self.battle_stage.reach_scene]["weather"][2],
                    self.weather_data)
                self.reach_scene_event_list[self.battle_stage.reach_scene].pop("weather")
            if "music" in self.reach_scene_event_list[self.battle_stage.reach_scene]:  # change music
                self.current_music = self.stage_music_pool[self.reach_scene_event_list[self.battle_stage.reach_scene]["music"]]
                self.music_left.play(self.current_music, fade_ms=100)
                self.music_left.set_volume(self.play_music_volume, 0)
                self.music_right.play(self.current_music, fade_ms=100)
                self.music_right.set_volume(0, self.play_music_volume)
                self.reach_scene_event_list[self.battle_stage.reach_scene].pop("music")
            if "sound" in self.reach_scene_event_list[self.battle_stage.reach_scene]:  # play sound
                for sound_effect in self.reach_scene_event_list[self.battle_stage.reach_scene]["sound"]:
                    self.add_sound_effect_queue(sound_effect[0],
                                                self.camera_pos, sound_effect[1], sound_effect[2])
                self.reach_scene_event_list[self.battle_stage.reach_scene].pop("sound")
            if "cutscene" in self.reach_scene_event_list[self.battle_stage.reach_scene]:  # cutscene
                self.cutscene_finish_camera_delay = 1
                for parent_event in self.reach_scene_event_list[self.battle_stage.reach_scene]["cutscene"]:
                    # play one parent at a time
                    self.cutscene_playing = parent_event
                    self.cutscene_playing_data = deepcopy(parent_event)
                    if "replayable" not in parent_event[0]["Property"]:
                        self.reach_scene_event_list[self.battle_stage.reach_scene].pop("cutscene")
            if not self.reach_scene_event_list[self.battle_stage.reach_scene]:  # no more event left
                self.reach_scene_event_list.pop(self.battle_stage.reach_scene)

    if self.player_interact_event_list:  # event that require player interaction (talk)
        event_list = sorted({key[0]: self.main_player_object.base_pos.distance_to(key[1]) for key in
                             [(item2, item2) if type(item2) is tuple else (item2, item2.base_pos) for
                              item2 in
                              self.player_interact_event_list]}.items(), key=lambda item3: item3[1])
        for item in event_list:
            target_pos = item[0]
            if type(item[0]) is not tuple:
                target_pos = (item[0].base_pos[0], item[0].base_pos[1] - (item[0].sprite_size * 4.5))
            distance = self.main_player_object.base_pos[0] - target_pos[0]
            angle_check = 1
            if distance < 0:  # target at leftside
                angle_check = -1
            if 100 < abs(distance) < 250 and \
                    ((self.main_player_object.angle == 90 and angle_check == 1) or self.main_player_object.angle == -90):
                # use player with the lowest number as interactor
                self.speech_prompt.add_to_screen(self.main_player_object, item[0], target_pos)
                if self.player_key_press[self.main_player]["Weak"]:  # player interact, start event
                    self.speech_prompt.clear()  # remove prompt
                    if (self.main_player_object.base_pos[0] - target_pos[0] < 0 and
                        self.main_player_object.angle != -90) or \
                            (self.main_player_object.base_pos[0] - target_pos[0] >= 0 and
                             self.main_player_object.angle != 90):  # player face target
                        self.main_player_object.new_angle *= -1
                        self.main_player_object.rotate_logic()

                    if type(item[0]) is not tuple:
                        if (item[0].base_pos[0] - self.main_player_object.base_pos[0] < 0 and
                            item[0].angle != -90) or \
                                (item[0].base_pos[0] - self.main_player_object.base_pos[0] >= 0 and
                                 item[0].angle != 90):  # target face player
                            item[0].new_angle *= -1
                            item[0].rotate_logic()

                    if "replayable" not in self.player_interact_event_list[item[0]][0][0]["Property"]:
                        self.cutscene_playing = self.player_interact_event_list[item[0]][0]
                        self.cutscene_playing_data = deepcopy(self.player_interact_event_list[item[0]][0])
                        self.player_interact_event_list[item[0]].remove(self.cutscene_playing)
                        if not self.player_interact_event_list[item[0]]:
                            self.player_interact_event_list.pop(item[0])
                    else:  # event can be replayed while in this mission, use copy to prevent delete
                        self.cutscene_playing = deepcopy(self.player_interact_event_list[item[0]][0])
                        self.cutscene_playing_data = self.player_interact_event_list[item[0]][0]
                break  # found event npc
            elif distance > 250:  # no event npc nearby
                break
