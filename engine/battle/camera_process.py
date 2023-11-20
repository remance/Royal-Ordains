from statistics import mean


def camera_process(self):
    if self.camera_mode == "Free":
        if self.player_key_hold["Move Left"]:
            self.camera_pos[0] -= 10
            self.fix_camera()

        elif self.player_key_hold["Move Right"]:
            self.camera_pos[0] += 10
            self.fix_camera()

    elif self.camera_mode == "Follow":
        all_alive = [player.pos[0] for player in self.player_objects.values()]
        if all_alive:
            mean_check = mean(all_alive)
            pos_change = (mean_check - self.camera_pos[0]) / 10
            if pos_change != 0:
                if abs(pos_change) < 10:
                    pos_change = (mean_check - self.camera_pos[0])
                self.camera_pos[0] += pos_change
                self.fix_camera()
        else:
            self.camera_mode = "Free"
