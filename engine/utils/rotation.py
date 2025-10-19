from math import cos, sin, atan2, degrees, radians

from pygame import Vector2


def find_target_point(start_x, start_y, distance, angle_degrees):
    """
    Find target point from start by a given distance at a specified angle.
    """
    # Convert angle from degrees to radians
    angle_radians = radians(convert_projectile_degree_angle(angle_degrees))

    return start_x + (distance * cos(angle_radians)), start_y + (distance * sin(angle_radians))


def rotation_xy(origin, point, angle):
    """
    Rotate point to the new pos
    :param origin: origin pos
    :param point: target point pos
    :param angle: angle of rotation in radians
    :return: Rotated point pos
    """
    ox, oy = origin
    px, py = point
    x = ox + cos(angle) * (px - ox) - sin(angle) * (py - oy)
    y = oy + sin(angle) * (px - ox) + cos(angle) * (py - oy)
    return Vector2(x, y)


def set_rotate(self, base_target, convert=True, use_pos=False):
    """
    find angle using starting pos and base_target
    :param self: any object with base_pos or pos as position attribute
    :param base_target: pos for target position to rotate to
    :param convert: convert degree for rotation
    :param use_pos: use pos instead of base_pos
    :return: new angle
    """
    if not use_pos:
        my_radians = atan2(base_target[1] - self.base_pos[1], base_target[0] - self.base_pos[0])
    else:
        my_radians = atan2(base_target[1] - self.pos[1], base_target[0] - self.pos[0])
    new_angle = int(degrees(my_radians))
    if convert:
        new_angle = convert_degree_angle(new_angle)
    return new_angle


def convert_degree_angle(angle):
    # """upper left and upper right"""
    if -180 <= angle < 0:
        return -angle - 90

    # """lower right -"""
    elif 0 <= angle <= 90:
        return -(angle + 90)

    # """lower left +"""
    elif 90 < angle <= 180:
        return 270 - angle


def convert_projectile_degree_angle(angle):
    # """upper left"""
    if -90 <= angle < 0:
        return 90 + angle

    # """upper right"""
    elif 0 <= angle < 90:
        return angle - 90

    # """lower right"""
    elif -180 <= angle < -90:
        return angle + 270

    # """lower left"""
    else:
        return angle - 270


def convert_degree_to_360(angle):
    """Convert math.degrees to 360 degree with 0 at the top"""
    return 360 - (angle % 360)
