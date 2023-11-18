from pygame import Vector2


def vraesier_update(self, dt):
    if self.mode == "Demon":
        self.resource -= dt * 3
        if self.resource <= 0:
            self.resource = 0
            if "uninterruptible" not in self.command_action:  # revert to normal
                self.interrupt_animation = True
                self.command_action = self.deactivate_command_action
                self.mode = "Normal"
    else:
        if self.resource >= self.resource50:
            self.mode = "Bloody"
            if self.resource >= self.max_resource:
                self.mode = "Ready"


def common_update(self, dt):
    # Changes mode depends on percentage of resource left
    if self.resource <= self.resource50:
        self.mode = "Half"
        if self.resource <= self.resource25:
            self.mode = "Near"
            if self.resource == 0:
                self.mode = "Empty"
    else:
        self.mode = "Normal"


def dashisi_update(self, dt):
    """Stereo music player based on dashisi pos distance from center camera pos,
    similar function as in battle.add_sound_effect_queue"""
    if self.pos != self.last_pos:
        self.last_pos = Vector2(self.pos)
        distance = self.pos.distance_to(self.battle.camera_pos)
        if distance < 1:
            distance = 1
        if self.pos[0] > self.battle.camera_pos[0]:  # sound to the right of center camera
            left_distance = distance + abs(self.pos[0] - self.battle.camera_pos[0])
            right_distance = distance
        elif self.pos[0] < self.battle.camera_pos[0]:  # sound to the left of center camera
            left_distance = distance
            right_distance = distance + abs(self.pos[0] - self.battle.camera_pos[0])
        else:  # sound at the center camera
            left_distance = distance
            right_distance = distance

        left_sound_power = 960 / left_distance
        if left_sound_power < 0:
            left_sound_power = 0
        elif left_sound_power > 1:
            left_sound_power = 1

        right_sound_power = 960 / right_distance
        if right_sound_power < 0:
            right_sound_power = 0
        elif right_sound_power > 1:
            right_sound_power = 1
        left_music_volume = left_sound_power * self.battle.play_music_volume
        right_music_volume = right_sound_power * self.battle.play_music_volume

        self.battle.music_left.set_volume(left_music_volume, 0.0)
        self.battle.music_right.set_volume(0.0, right_music_volume)


update_dict = {"Vraesier": vraesier_update, "Rodhinbar": common_update, "Iri":common_update,
               "Dashisi": dashisi_update}
