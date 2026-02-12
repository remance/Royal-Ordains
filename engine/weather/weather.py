from math import cos, sin, radians
from random import choice, uniform, randint

from pygame import transform, Vector2
from pygame.mixer import Sound

from engine.uibattle.uibattle import UIBattle
from engine.utils.rotation import set_rotate


class Weather(UIBattle):
    weather_matter_images = None
    weather_data = None

    def __init__(self, weather_type, wind_direction, level):
        self._layer = 99999999999999999999
        UIBattle.__init__(self)
        self.weather_spawn_timer = {}
        self.weather_type = weather_type
        if self.weather_type == 0:
            # only random non-random weather and int type id weather
            self.weather_type = choice([weather for weather in self.weather_data if weather != 0 and weather.isdigit()])
        self.has_stat_effect = False
        self.has_stat_effect = True
        stat = self.weather_data[self.weather_type]
        self.name = stat["Name"]
        self.level = level  # weather level, start from 0
        if self.level < 0:  # can not be negative level
            self.level = 0
        cal_level = self.level + 1
        self.cal_level = cal_level
        self.offence_modifier = stat["Offence Modifier"] ** cal_level
        self.defence_modifier = stat["Defence Modifier"] ** cal_level
        self.speed_modifier = stat["Speed Modifier"] ** cal_level
        self.air_offence_modifier = stat["Air Offence Modifier"] ** cal_level
        self.air_defence_modifier = stat["Air Defence Modifier"] ** cal_level
        self.air_speed_modifier = stat["Air Speed Modifier"] ** cal_level
        self.health_regen_bonus = stat["Health Regeneration Bonus"] * cal_level
        self.resource_regen_bonus = stat["Resource Regeneration Bonus"] * cal_level
        self.element = stat["Element"]
        self.status_effect = stat["Status"]
        self.spawn_cooldown = {key: value / cal_level for key, value in
                               stat["Spawn Cooldown"].items()}  # divide to make spawn increase with strength
        self.weather_spawn_timer = {key: 0 for key in self.spawn_cooldown}
        self.wind_strength = int(stat["Wind Strength"] * cal_level)
        self.speed = stat["Travel Speed"] * self.wind_strength
        self.wind_direction = wind_direction
        self.travel_angle = wind_direction - 90  # convert degree from human-readable (or whatever it is called)
        if self.travel_angle == 0:
            self.spawn_angle = 180
        else:
            if self.travel_angle > 180:
                self.spawn_angle = self.travel_angle - 180
            else:
                self.spawn_angle = self.travel_angle + 180

        self.travel_angle_radians = radians(self.travel_angle)
        self.spawn_angle_radians = radians(self.spawn_angle)

        self.spawn_angle_radians_sin = sin(self.spawn_angle_radians)
        self.spawn_angle_radians_cos = cos(self.spawn_angle_radians)

        self.random_sprite_angle = False
        if "random_sprite_angle" in stat["Property"]:
            self.random_sprite_angle = True

        self.battle.weather_ambient_channel.stop()
        if stat["Ambient"]:
            if stat["Ambient"] in self.battle.weather_ambient_pool:
                self.battle.weather_ambient_channel.play(Sound(self.battle.weather_ambient_pool[stat["Ambient"]]),
                                                         loops=-1, fade_ms=100)
                self.battle.weather_ambient_channel.set_volume(self.battle.play_effect_volume)
        self.weather_now = str(self.weather_type) + "_" + str(self.level)

    def update(self, dt):
        for key in self.weather_spawn_timer:
            self.weather_spawn_timer[key] += dt
            if self.weather_spawn_timer[key] >= self.spawn_cooldown[key]:
                self.weather_spawn_timer[key] = 0
                self.spawn_weather_matter(key)

    def spawn_weather_matter(self, matter_name):
        if self.travel_angle not in (0, 180):  # matter travel not from direct straight top to bottom angle
            random_pos = (uniform(0, self.screen_rect.width), uniform(0, self.screen_rect.height))
            target = travel_to_map_border(random_pos, self.travel_angle_radians, self.screen_rect.size)
            start_pos = travel_to_map_border(random_pos, self.spawn_angle_radians, self.screen_rect.size)
        else:
            target = (uniform(0, self.screen_rect.width), self.screen_rect.height)
            start_pos = Vector2(target[0] + (self.screen_rect.width * self.spawn_angle_radians_sin),
                                target[1] - (self.screen_rect.height * self.spawn_angle_radians_cos))

        random_pic = randint(0, len(self.weather_matter_images[matter_name]) - 1)
        self.battle.weather_matters.add(MatterSprite(start_pos, target, self.speed,
                                                     self.weather_matter_images[matter_name][random_pic],
                                                     self.screen_rect.size, self.random_sprite_angle))


class MatterSprite(UIBattle):
    set_rotate = set_rotate

    def __init__(self, start_pos, target, speed, image, screen_rect_size, random_sprite_angle):
        self._layer = 1
        UIBattle.__init__(self, has_containers=True)
        self.speed = speed
        self.base_pos = Vector2(start_pos)  # should be at the end corner of screen
        self.target = Vector2(target)  # should be at another end corner of screen
        self.move = self.target - self.base_pos
        self.move.normalize_ip()
        if random_sprite_angle:
            self.image = transform.rotate(image, uniform(0, 359))
        else:
            self.image = transform.rotate(image, self.set_rotate(self.target))  # no need to copy since rotate only once
        self.screen_start = -self.image.get_width() * 2
        self.screen_end = ((self.image.get_width() * 1.5) + screen_rect_size[0],
                           (self.image.get_height() * 1.5) + screen_rect_size[1])
        self.rect = self.image.get_rect(center=self.base_pos)

    def update(self, dt):
        """Update sprite position movement"""
        move = self.move * self.speed * self.battle.dt
        self.base_pos += move
        self.rect.center = list(int(v) for v in self.base_pos)
        if self.screen_end[0] < self.base_pos[0] < self.screen_start or self.screen_end[1] < self.base_pos[1]:
            # pass through screen border, kill sprite
            self.kill()


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
