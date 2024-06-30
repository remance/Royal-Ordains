from math import cos, sin, radians
from random import uniform, randint

from pygame import Vector2

from engine.weather.weather import MatterSprite


def travel_to_map_border(pos, angle, screen_size):
    """
    Find target at border of screen based on angle
    :param pos: Starting pos
    :param angle: Angle in radians
    :param screen_size: Size of screen (width, height)
    :return: target pos on border
    """
    dx = cos(angle)
    dy = sin(angle)

    if dx < 1.0e-16:  # left border
        y = (-pos[0]) * dy / dx + pos[1]

        if 0 <= y <= screen_size[1]:
            return Vector2((0, y))

    if dx > 1.0e-16:  # right border
        y = (screen_size[0] - pos[0]) * dy / dx + pos[1]
        if 0 <= y <= screen_size[1]:
            return Vector2((screen_size[0], y))

    if dy < 1.0e-16:  # top border
        x = (-pos[1]) * dx / dy + pos[0]
        if 0 <= x <= screen_size[0]:
            return Vector2((x, 0))

    if dy > 1.0e-16:  # bottom border
        x = (screen_size[1] - pos[1]) * dx / dy + pos[0]
        if 0 <= x <= screen_size[0]:
            return Vector2((x, screen_size[1]))


def spawn_weather_matter(self):
    travel_angle = self.current_weather.travel_angle
    spawn_angle = self.current_weather.spawn_angle

    if travel_angle not in (0, 180):  # matter travel not from direct straight top to bottom angle
        random_pos = (uniform(0, self.screen_rect.width), uniform(0, self.screen_rect.height))
        target = travel_to_map_border(random_pos, radians(travel_angle), self.screen_rect.size)
        start_pos = travel_to_map_border(random_pos, radians(spawn_angle), self.screen_rect.size)
    else:
        target = (uniform(0, self.screen_rect.width), self.screen_rect.height)
        start_pos = Vector2(target[0] + (self.screen_rect.width * sin(radians(spawn_angle))),
                            target[1] - (self.screen_rect.height * cos(radians(spawn_angle))))

    random_pic = randint(0, len(self.weather_matter_images[self.current_weather.name]) - 1)
    self.weather_matters.add(MatterSprite(start_pos, target, self.current_weather.speed,
                                          self.weather_matter_images[self.current_weather.name][random_pic],
                                          self.screen_rect.size, self.current_weather.random_sprite_angle))
