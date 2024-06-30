def cutscene_player_input(self):
    # cutscene that need main player to press button to continue
    for key, pressed in self.player_key_press[self.main_player].items():
        if key == "Weak" and pressed:
            for child_event in self.cutscene_playing.copy():
                if "wait" in child_event["Property"]:  # has event that still requires finishing before events after
                    break
                if "select" in child_event["Property"]:
                    if child_event["Property"]["select"] == "yesno":  # only consider choosing if mouse over choice
                        if self.decision_select.selected:
                            self.end_cutscene_event(child_event)
                            for child_event2 in self.cutscene_playing.copy():
                                if ("yes" in child_event2["Trigger"] or "no" in child_event2["Trigger"]) and \
                                        self.decision_select.selected not in child_event2["Trigger"]:
                                    # remove opposite child event choice
                                    self.cutscene_playing.remove(child_event2)
                            self.decision_select.selected = None
                            self.realtime_ui_updater.remove(self.decision_select)
                    break  # only one select event can be played at a time

                elif "interact" in child_event["Property"]:
                    self.end_cutscene_event(child_event)
                    if "start mission" in child_event["Property"]:  # start new mission after interact
                        if str(child_event["Property"]["start mission"]) in self.game.preset_map_data[self.chapter]:
                            # go to assigned mission
                            return str(child_event["Property"]["start mission"])
                    break  # only one player interact event can be played at a time
