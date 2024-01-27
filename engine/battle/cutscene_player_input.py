def cutscene_player_input(self):
    # cutscene that need main player to press button to continue
    for key, pressed in self.player_key_press[self.main_player].items():
        if key == "Weak" and pressed:
            for child_event in self.cutscene_playing.copy():
                if "select" in child_event["Property"]:
                    if child_event["Property"]["select"] == "yesno":  # only consider choosing if mouse over choice
                        if self.decision_select.selected:
                            end_event(self, child_event)
                            for child_event2 in self.cutscene_playing.copy():
                                if ("yes" in child_event2["Trigger"] or "no" in child_event2["Trigger"]) and \
                                        self.decision_select.selected not in child_event2["Trigger"]:
                                    # remove opposite child event choice
                                    self.cutscene_playing.remove(child_event2)
                            self.decision_select.selected = None
                            self.realtime_ui_updater.remove(self.decision_select)
                    break  # only one select event can be played at a time

                elif "player_interact" in child_event["Property"]:
                    end_event(self, child_event)
                    if "start mission" in child_event["Property"]:  # start new mission after interact
                        if child_event["Property"]["start mission"] in self.game.preset_map_data[self.chapter]:
                            # go to assigned mission
                            return child_event["Property"]["start mission"]
                    break  # only one player interact event can be played at a time


def end_event(self, child_event):
    for char in self.all_chars:
        if char.game_id == child_event["Object"] or \
                (child_event["Object"] == "pm" and char == self.main_player_object):
            if char.cutscene_event in self.battle.cutscene_playing:
                # end any player_interact events currently awaiting
                self.battle.cutscene_playing.remove(char.cutscene_event)
            char.cutscene_event = None
            char.pick_cutscene_animation({})
            break

    for box in self.speech_boxes:
        if box.cutscene_event == child_event:  # end speech box related to the event
            box.timer = 0
