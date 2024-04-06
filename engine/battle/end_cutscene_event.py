def end_cutscene_event(self, child_event):
    for char in self.all_chars:
        if char.game_id == child_event["Object"] or \
                (child_event["Object"] == "pm" and char == self.main_player_object):
            if char.cutscene_event in self.cutscene_playing:
                # end any player_interact events currently awaiting
                self.cutscene_playing.remove(char.cutscene_event)
            if "repeat after" not in char.cutscene_event["Property"] and char.current_action:
                char.pick_cutscene_animation({})
            char.cutscene_event = None
            break

    for box in self.speech_boxes:
        if box.cutscene_event == child_event:  # end speech box related to the event
            box.timer = 0
