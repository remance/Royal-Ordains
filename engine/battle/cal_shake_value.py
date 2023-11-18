from math import log2


def cal_shake_value(self, start_pos, shake_value):
    distance = log2(start_pos.distance_to(self.camera_pos))
    if distance < 1:
        distance = 1
    return shake_value / distance
