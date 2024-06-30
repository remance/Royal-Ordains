from random import choice, uniform

from pygame import transform, Vector2

from engine.uibattle.uibattle import UIBattle
from engine.utils.rotation import set_rotate


class Weather(UIBattle):
    def __init__(self, weather_type, wind_direction, level, weather_data):
        self._layer = 99999999999999999999
        UIBattle.__init__(self)
        self.weather_type = weather_type
        if self.weather_type == 0:
            # only random non-random weather and int type id weather
            self.weather_type = choice([weather for weather in weather_data if weather != 0 and weather.isdigit()])
        self.has_stat_effect = False
        if weather_data:
            self.has_stat_effect = True
            stat = weather_data[self.weather_type]
            self.name = stat["Name"]
            self.level = level  # weather level, start from 0
            if self.level < 0:  # can not be negative level
                self.level = 0
            cal_level = self.level + 1

            self.atk_buff = stat["Power Bonus"] * cal_level
            self.def_buff = stat["Defence Bonus"] * cal_level
            self.speed_buff = stat["Speed Bonus"] * cal_level
            self.hp_regen_buff = stat["HP Regeneration Bonus"] * cal_level
            self.element = tuple([(element, cal_level) for element in stat["Element"] if element != ""])
            self.status_effect = stat["Status"]
            self.spawn_rate = stat["Spawn Rate"] / cal_level  # divide to make spawn increase with strength
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

            self.random_sprite_angle = False
            if "random sprite angle" in stat["Property"]:
                self.random_sprite_angle = True


class MatterSprite(UIBattle):
    set_rotate = set_rotate

    def __init__(self, start_pos, target, speed, image, screen_rect_size, random_sprite_angle):
        self._layer = 8
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

    def update(self):
        """Update sprite position movement"""
        move = self.move * self.speed * self.battle.dt
        self.base_pos += move
        self.rect.center = list(int(v) for v in self.base_pos)
        if self.screen_end[0] < self.base_pos[0] < self.screen_start or self.screen_end[1] < self.base_pos[1]:
            # pass through screen border, kill sprite
            self.kill()


class SpecialWeatherEffect(UIBattle):
    """Super effect that affect whole screen"""

    def __init__(self, pos, target, speed, image, end_time):
        self._layer = 8
        UIBattle.__init__(self, has_containers=True)
        self.pos = Vector2(pos)
        self.target = Vector2(target)
        self.speed = speed
        self.image = image
        self.rect = self.image.get_rect(center=self.pos)
        self.end_time = end_time

    def update(self):
        """TODO later when weather has extreme effect """
        pass
