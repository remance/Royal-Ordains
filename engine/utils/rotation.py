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


def set_rotate(start_pos, target, convert_to_degree=True):
    """
    find angle using starting pos and base_target
    :param start_pos: starting pos
    :param target: pos for target position to rotate to
    :param convert_to_degree: convert degree for sprite rotation
    :param use_pos: use pos instead of base_pos
    :return: new angle
    """
    new_angle = int(degrees(atan2(target[1] - start_pos[1], target[0] - start_pos[0])))
    if convert_to_degree:
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
