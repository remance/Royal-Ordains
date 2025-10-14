def add_sound_effect_queue(self, sound_object, sound_pos, sound_distance_power, shake_power, volume_mod=1,
                           volume="effect"):
    """Stereo sound effect player based on sound pos distance from center camera pos"""
    use_volume = self.play_effect_volume
    if volume == "voice":
        use_volume = self.play_voice_volume

    if use_volume:
        distance = sound_pos.distance_to(self.camera_pos)
        if distance < 1:
            distance = 1
        if distance < sound_distance_power:
            screen_shake_power = self.cal_shake_value(sound_pos, shake_power)
            self.screen_shake_value += screen_shake_power
            if sound_pos[0] > self.camera_pos[0]:  # sound to the right of center camera
                left_distance = distance + abs(sound_pos[0] - self.camera_pos[0])
                right_distance = distance
            elif sound_pos[0] < self.camera_pos[0]:  # sound to the left of center camera
                left_distance = distance
                right_distance = distance + abs(sound_pos[0] - self.camera_pos[0])
            else:  # sound at the center camera
                left_distance = distance
                right_distance = distance

            left_sound_power = sound_distance_power / left_distance
            if left_sound_power < 0:
                left_sound_power = 0
            elif left_sound_power > 1:
                left_sound_power = 1

            right_sound_power = sound_distance_power / right_distance
            if right_sound_power < 0:
                right_sound_power = 0
            elif right_sound_power > 1:
                right_sound_power = 1

            left_effect_volume = left_sound_power * volume_mod * use_volume
            right_effect_volume = right_sound_power * volume_mod * use_volume
            final_effect_volume = [left_effect_volume, right_effect_volume]  # left right sound volume

            if right_effect_volume or left_effect_volume:
                if sound_object not in self.sound_effect_queue:
                    self.sound_effect_queue[sound_object] = final_effect_volume
                else:
                    self.sound_effect_queue[sound_object][0] += final_effect_volume[0]
                    self.sound_effect_queue[sound_object][1] += final_effect_volume[1]
