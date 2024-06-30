from statistics import mean


def camera_process(self):
    # if self.camera_mode == "Free":
    #     if self.player_key_hold[1]["Left"]:
    #         self.camera_pos[0] -= 10
    #         self.fix_camera()
    #
    #     elif self.player_key_hold[1]["Right"]:
    #         self.camera_pos[0] += 10
    #         self.fix_camera()
    #
    # elif self.camera_mode == "Follow":
    if not self.cutscene_playing and not self.cutscene_finish_camera_delay:
        all_alive_player = [player.pos[0] for player in self.player_objects.values()]
        if all_alive_player:
            mean_check = mean(all_alive_player)
            pos_change = (mean_check - self.camera_pos[0]) / 10
            if pos_change != 0:
                if abs(pos_change) < 10:
                    pos_change = (mean_check - self.camera_pos[0])
                self.camera_pos[0] += pos_change
                self.fix_camera()
        # else:
        #     self.camera_mode = "Free"
    else:
        self.fix_camera()
