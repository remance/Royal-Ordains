from math import log2


def add_sound_effect_queue(self, sound_object, sound_pos, sound_distance_power, shake_power, volume_mod=1,
                           volume="effect"):
    """Stereo sound effect player based on sound pos distance from center camera pos"""
    use_volume = self.play_effect_volume
    if volume == "voice":
        use_volume = self.play_voice_volume

    distance = sound_pos.distance_to(self.base_camera_pos)
    screen_shake_power = cal_shake_value(distance, shake_power)
    self.screen_shake_value += screen_shake_power
    if use_volume:
        if sound_distance_power > distance:
            if sound_pos[0] > self.base_camera_pos[0]:  # sound to the right of center camera
                left_distance = distance + abs(sound_pos[0] - self.base_camera_pos[0])
                right_distance = distance
            elif sound_pos[0] < self.base_camera_pos[0]:  # sound to the left of center camera
                left_distance = distance
                right_distance = distance + abs(sound_pos[0] - self.base_camera_pos[0])
            else:  # sound at the center camera
                left_distance = distance
                right_distance = distance

            left_sound_power = 1
            if left_distance:
                left_sound_power -= left_distance / sound_distance_power
                if left_sound_power < 0.01:
                    left_sound_power = 0
                elif left_sound_power > 1:
                    left_sound_power = 1

            right_sound_power = 1
            if right_distance:
                right_sound_power -= right_distance / sound_distance_power
                if right_sound_power < 0.01:
                    right_sound_power = 0
                elif right_sound_power > 1:
                    right_sound_power = 1

            left_effect_volume = left_sound_power * volume_mod * use_volume
            right_effect_volume = right_sound_power * volume_mod * use_volume

            if right_effect_volume or left_effect_volume:
                if sound_object not in self.sound_effect_queue:
                    self.sound_effect_queue[sound_object] = [left_effect_volume, right_effect_volume]
                else:
                    self.sound_effect_queue[sound_object][0] += left_effect_volume
                    self.sound_effect_queue[sound_object][1] += right_effect_volume


def cal_shake_value(distance, shake_value):
    distance = log2(distance + 0.1)
    if distance < 1:
        distance = 1
    return shake_value / distance
