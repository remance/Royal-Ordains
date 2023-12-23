def cutscene_player_input(self):
    # cutscene that need player to press button to continue, get input from any player
    for player in self.player_key_press.values():
        for key, pressed in player.items():
            if key == "Weak" and pressed:
                for child_event in self.cutscene_playing.copy():
                    if "player_interact" in child_event["Property"]:
                        for char in self.all_chars:
                            if char.game_id == child_event["Object"]:
                                if char.cutscene_event in self.battle.cutscene_playing:
                                    # end any player_interact events currently awaiting
                                    self.battle.cutscene_playing.remove(char.cutscene_event)
                                char.cutscene_event = None
                                char.pick_cutscene_animation({})
                                break
                        for box in self.speech_boxes:
                            if box.cutscene_event == child_event:  # end speech box related to the event
                                box.timer = 0
