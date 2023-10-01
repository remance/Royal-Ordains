from statistics import mean


def camera_process(self):
    if self.camera_mode == "Free":
        if self.player_key_hold["Move Left"]:
            self.camera_pos[0] -= 10
            self.camera_fix()

        elif self.player_key_hold["Move Right"]:
            self.camera_pos[0] += 10
            self.camera_fix()

    elif self.camera_mode == "Follow":
        mean_check = mean([player.pos[0] for player in self.player_objects.values() if player.alive])
        pos_change = (mean_check - self.camera_pos[0]) / 10
        if pos_change != 0:
            if abs(pos_change) < 10:
                pos_change = (mean_check - self.camera_pos[0])
            self.camera_pos[0] += pos_change
            self.camera_fix()
