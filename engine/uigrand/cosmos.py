from math import cos, sin, radians

from pygame import Vector2, draw, Surface
from pygame.transform import rotate

from engine.constants import Turn_To_Phase
from engine.uigrand.uigrand import UIGrand
from engine.utils.rotation import set_rotate


def circle_orbit(center, radius, angle, *args):
    """
    Finding the x,y coordinates on circle, based on given angle
    """
    # center of circle, angle in degree and radius of circle
    x = center[0] + (radius * cos(angle))
    y = center[1] + (radius * sin(angle))
    return x, y


def ellipse_orbit(center, radius, angle, orbit_angle):
    """
    Finding the x,y coordinates on ellipse, based on given angle
    """
    # center of circle, angle in degree and radius of circle
    x = radius[0] * cos(angle)
    y = radius[1] * sin(angle)

    radians_angle = radians(orbit_angle)

    x = center[0] + x * cos(radians_angle) - y * sin(radians_angle)
    y = center[1] + x * sin(radians_angle) + y * cos(radians_angle)
    return x, y


class MiniCosmosUI(UIGrand):
    def __init__(self, images, cosmic_ui):
        self._layer = 4
        UIGrand.__init__(self)
        self.line_width = int(4 * self.screen_scale_width)
        if self.line_width < 1:
            self.line_width = 1
        self.image = images["mini_cosmos"]
        self.base_image = self.image.copy()
        self.base_image_event = images["mini_cosmos_event"].copy()
        self.cosmic_ui = cosmic_ui
        self.size_scale_width = self.image.get_width() / self.cosmic_ui.image.get_width()
        self.size_scale_height = self.image.get_height() / self.cosmic_ui.image.get_height()
        self.rect = self.image.get_rect(topright=(self.screen_width, 0))

    def reset(self):
        if self.grand.current_campaign_state["cosmic_event"]:
            self.image = self.base_image_event.copy()
        else:
            self.image = self.base_image.copy()
        image = self.image
        line_width = self.line_width
        # draw line from planet to earth
        terra_scaled_pos_x = self.cosmic_ui.terra.pos[0] * self.size_scale_width
        terra_scaled_pos_y = self.cosmic_ui.terra.pos[1] * self.size_scale_height

        for planet in self.cosmic_ui.planets.values():
            planet_scaled_pos_x = planet.pos[0] * self.size_scale_width
            planet_scaled_pos_y = planet.pos[1] * self.size_scale_height
            if planet.cosmic_id != "earth" and not planet.movement_angle:
                draw.line(image, planet.colour, (terra_scaled_pos_x, terra_scaled_pos_y),
                          (planet_scaled_pos_x, planet_scaled_pos_y), width=line_width)

            draw.circle(image, planet.colour,
                        (planet_scaled_pos_x, planet_scaled_pos_y),
                        planet.dot_size)

    def update(self, dt):
        UIGrand.update(self, dt)
        if self.mouse_over:
            text = [self.localisation.grab_text(("ui", "info_header_current_cosmic_events")), ]
            cosmic_event_list = self.grand.current_campaign_state["cosmic_event"]
            if cosmic_event_list:
                for event in cosmic_event_list:
                    text.append("- " + self.localisation.grab_text(("ui", "cosmos_" + event)))
            else:
                text.append(self.localisation.grab_text(("ui", "info_text_none")))
            self.text_popup.popup(("topright", self.cursor.rect.bottomleft), text)
            self.outer_ui_updater.add(self.text_popup)
            if self.event_press:
                if self.cosmic_ui not in self.outer_ui_updater:
                    self.outer_ui_updater.add(self.cosmic_ui)
                    self.cosmic_ui.update_image()
                else:
                    self.outer_ui_updater.remove(self.cosmic_ui)


class CosmosUI(UIGrand):
    def __init__(self):
        self._layer = 100
        UIGrand.__init__(self)
        self.show_text = False
        self.must_update_image = False
        self.font = self.game.large_generic_ui_font
        self.line_width = int(10 * self.screen_scale_width)
        if self.line_width < 1:
            self.line_width = 1
        self.base_image = self.grand.cosmos_ui_images["cosmos"].copy()
        self.image = self.base_image
        self.original_image = self.grand.cosmos_ui_images["cosmos"].copy()

        self.image_center = (self.image.get_width() / 2, self.image.get_height() / 2)
        self.one_phase_dt = 1 / Turn_To_Phase

        # Create the earth
        self.terra = CosmicEntity(15, 0, (50, 50, 180), "earth",
                                  specific_base_pos=(1250, 1080))  # center of cosmos ui image before scaling

        comet_hidden_planet_center = CosmicEntity(0, 0, (255, 255, 255), "",
                                                  specific_base_pos=(750, 1836))

        # Add planets
        self.planets = {"pale_moon": CosmicEntity(10, 0, (230, 230, 230), "pale_moon",
                                                  orbit={"parent": self.terra, "speed": 1, "radius": 190}),
                        "dark_moon": CosmicEntity(10, 0, (30, 125, 230), "dark_moon",
                                                  orbit={"parent": self.terra, "speed": 0.8, "radius": 260}),
                        "red_planet": CosmicEntity(10, 0, (200, 30, 30), "red_planet",
                                                   orbit={"parent": self.terra, "speed": 0.048, "radius": 288},
                                                   epicycle={"speed": 0.16, "radius": 120}),
                        "sun": CosmicEntity(15, 0, (255, 100, 10), "sun",
                                            orbit={"parent": self.terra, "speed": 0.2, "radius": 480}),
                        "purple_planet": CosmicEntity(10, 0, (160, 70, 160),
                                                      "purple_planet",
                                                      orbit={"parent": self.terra, "speed": 0.006, "radius": 593},
                                                      epicycle={"speed": 0.048, "radius": 120}),
                        "green_planet": CosmicEntity(10, 0, (86, 150, 86), "green_planet",
                                                     orbit={"parent": self.terra, "speed": 0.002, "radius": 779},
                                                     epicycle={"speed": 0.04, "radius": 100}),
                        "comet": CosmicEntity(7, 200, (255, 255, 0), "comet",
                                              orbit={"parent": comet_hidden_planet_center, "angle": 300,
                                                     "speed": 0.01, "radius": (1200, 2200), "radius_scale": 10},
                                              movement_angle=True),
                        "earth": self.terra}

        self.sun = self.planets["sun"]
        self.pale_moon = self.planets["pale_moon"]
        self.dark_moon = self.planets["dark_moon"]
        self.red_planet = self.planets["red_planet"]
        self.purple_planet = self.planets["purple_planet"]
        self.green_planet = self.planets["green_planet"]
        self.comet = self.planets["comet"]
        self.no_earth_planets = {key: value for key, value in self.planets.items() if key != "earth"}

        self.rect = self.image.get_rect(center=(self.half_screen_width, self.half_screen_height))

    def reset(self, cosmos_time):
        self.base_image = self.original_image.copy()
        for planet in self.no_earth_planets.values():
            planet.reset(cosmos_time)

    def update(self, dt):
        if self.must_update_image:
            self.update_image()
        if self.mouse_over:
            inside_mouse_pos = Vector2(
                (self.cursor.pos[0] - self.rect.topleft[0]),
                (self.cursor.pos[1] - self.rect.topleft[1]))
            for planet in self.planets.values():
                if planet.rect.collidepoint(inside_mouse_pos):
                    break

    def update_image(self):
        # Draw, planet, name and additional info when cosmic ui is being shown

        # Draw distance to the sun for planets other than the sun
        # if not self.sun:
        #     distance_text = font.render(f"{round(self.distance_to_sun / 1000, 1)} km", True, WHITE)
        #     win.blit(distance_text, (int(x - distance_text.get_width() / 2), int(y - distance_text.get_height() / 2)))

        line_width = self.line_width
        # draw movement trail lines
        for planet in self.no_earth_planets.values():
            if not planet.movement_angle:
                if planet.last_path:
                    last_path_to_blit = planet.last_path
                    len_to_blit = len(last_path_to_blit) - 1
                    for index, last_path in enumerate(last_path_to_blit):
                        if index < len_to_blit:
                            draw.line(self.base_image, planet.colour,
                                      last_path_to_blit[index + 1], last_path, width=line_width)
                        else:  # the last one use current pos for second point
                            draw.line(self.base_image, planet.colour, planet.pos, last_path, width=line_width)
                    planet.last_path = []

        image = self.base_image.copy()
        # draw line from planet to earth
        for planet in self.no_earth_planets.values():
            if not planet.movement_angle:
                draw.line(image, planet.colour, self.terra.pos, planet.pos, width=line_width)

        # draw all planets
        for planet in self.planets.values():
            if ((planet.base_pos[0] - 1250) ** 2) + ((planet.base_pos[1] - 1080) ** 2) <= 1102500:
                # only draw planet in inner circle
                image.blit(planet.image, planet.rect)
                if self.show_text:
                    info_text = self.font.render(self.localisation.grab_text("cosmos", planet.cosmic_id, "Name"), True,
                                                 (255, 255, 255))
                    image.blit(info_text, (int(planet.pos[0]),
                                           int(planet.pos[1] - planet.image.get_height() * 0.8)))

        self.image = image

    def apply_cosmic_event(self, event):
        if event not in self.grand.current_campaign_state["cosmic_event"]:
            self.grand.current_campaign_state["cosmic_event"].append(event)

    def phase_change(self):
        self.must_update_image = True
        for planet in self.no_earth_planets.values():
            planet.update(self.one_phase_dt)

        # check cosmic event, hardcode check so it is more efficient
        self.grand.current_campaign_state["cosmic_event"] = []  # reset all cosmic events
        pale_moon = self.pale_moon
        sun = self.sun
        red_planet = self.red_planet
        terra_base_pos = self.terra.pos
        moon_alignment = pale_moon.rect.clipline(terra_base_pos, self.dark_moon.pos)
        if moon_alignment:
            eclipse_alignment = all((moon_alignment, pale_moon.rect.clipline(terra_base_pos, sun.pos)))
            red_moon_alignment = all((moon_alignment, pale_moon.rect.clipline(terra_base_pos, red_planet.pos)))
            purple_moon_alignment = all(
                (moon_alignment, pale_moon.rect.clipline(terra_base_pos, self.purple_planet.pos)))
            green_moon_alignment = all(
                (moon_alignment, pale_moon.rect.clipline(terra_base_pos, self.green_planet.pos)))
            trio_alignment = all((red_planet.rect.clipline(terra_base_pos, self.purple_planet.pos),
                                  (red_planet.rect.clipline(terra_base_pos, self.green_planet.pos))))
            diamond_sun_alignment = all((trio_alignment, red_planet.rect.clipline(terra_base_pos, sun.pos)))
            full_alignment = all((moon_alignment, eclipse_alignment, red_moon_alignment, purple_moon_alignment,
                                  green_moon_alignment))

            if full_alignment:
                self.apply_cosmic_event("full_alignment")
            elif eclipse_alignment:
                self.apply_cosmic_event("radiant_eclipse")
            elif diamond_sun_alignment:
                self.apply_cosmic_event("diamond_sun")
            else:
                if red_moon_alignment:
                    self.apply_cosmic_event("blood_moon")
                elif purple_moon_alignment:
                    self.apply_cosmic_event("royal_moon")
                elif green_moon_alignment:
                    self.apply_cosmic_event("vert_moon")
                elif trio_alignment:
                    self.apply_cosmic_event("trio_conjunction")
        if self.red_planet.base_pos.distance_to(self.terra.base_pos) <= 175:
            self.apply_cosmic_event("red_visit")
        if self.comet.base_pos.distance_to(self.terra.base_pos) <= 350:
            self.apply_cosmic_event("great_comet")


class CosmicEntity(UIGrand):
    rotate_cache = {}
    image = Surface((0, 0))

    def __init__(self, dot_size, start_angle, colour, cosmic_id, orbit=None, epicycle=None, specific_base_pos=(),
                 movement_angle=False):
        UIGrand.__init__(self)
        self.cosmic_event_list = self.grand.character_data.cosmic_event_list
        self.cosmos_ui_images = self.grand.cosmos_ui_images
        self.dot_size = dot_size * self.screen_scale_width
        self.colour = colour
        self.cosmic_id = cosmic_id
        if cosmic_id not in self.rotate_cache:
            self.rotate_cache[cosmic_id] = {}

        self.using_event_image = False
        self.last_path = []
        self.base_pos = ()
        self.pos = ()
        if self.cosmic_id:
            self.base_image = self.cosmos_ui_images[self.cosmic_id]
            self.image = self.base_image
        self.start_angle = start_angle
        self.current_orbit_angle = start_angle
        self.movement_angle = movement_angle
        self.parent = None
        self.sprite_angle = 0
        self.orbit_radius = 0
        self.orbit_speed = 0
        self.orbit_angle = 0
        if orbit:
            self.orbit_speed = orbit["speed"]
            self.orbit_radius = orbit["radius"]
            self.parent = orbit["parent"]
            if "angle" in orbit:
                self.orbit_angle = orbit["angle"]
        else:
            self.base_pos = specific_base_pos
        self.orbit_process = circle_orbit
        if type(self.orbit_radius) is tuple:
            self.orbit_process = ellipse_orbit

        self.current_epicycle_angle = 0
        self.epicycle_speed = 0
        self.epicycle_radius = 0
        self.epicycle_angle = 0
        if epicycle:
            self.epicycle_speed = epicycle["speed"]
            self.epicycle_radius = epicycle["radius"]
            if "angle" in orbit:
                self.epicycle_angle = orbit["angle"]

        self.epicycle_process = circle_orbit
        if type(self.epicycle_radius) is tuple:
            self.epicycle_process = ellipse_orbit
        self.update(0)
        self.start_pos = self.base_pos
        self.pos = (self.base_pos[0] * self.screen_scale_width, self.base_pos[1] * self.screen_scale_height)
        self.rect = self.image.get_rect(center=self.pos)

    def reset(self, cosmos_time):
        """Reset planet for new campaign"""
        if self.parent:  # skip those that are static in place for reset
            self.base_pos = ()
            self.pos = ()
            self.current_orbit_angle = self.start_angle
            self.current_epicycle_angle = 0
            self.update(cosmos_time)

    def update(self, dt):
        cosmic_event = self.grand.current_campaign_state["cosmic_event"]
        if cosmic_event:
            if not self.using_event_image:
                for event in cosmic_event:
                    if self.cosmic_id in self.cosmic_event_list[event]["Cosmic Replace"]:
                        self.base_image = self.cosmos_ui_images[
                            self.cosmic_event_list[event]["Cosmic Replace"][self.cosmic_id]]
                        self.image = self.base_image
                        break
                self.using_event_image = True
        elif self.using_event_image:
            self.base_image = self.cosmos_ui_images[self.cosmic_id]
            self.image = self.base_image
            self.using_event_image = False

        if self.pos and self.pos not in self.last_path:
            self.last_path.append(self.pos)
        if self.orbit_speed:
            self.current_orbit_angle += self.orbit_speed * dt
            new_pos = self.orbit_process(self.parent.base_pos, self.orbit_radius, self.current_orbit_angle,
                                         self.orbit_angle)
            if self.movement_angle and self.base_pos:
                sprite_angle = int(set_rotate(self.base_pos, new_pos))
                if sprite_angle not in self.rotate_cache[self.cosmic_id]:
                    self.image = rotate(self.base_image, sprite_angle)
                    self.rotate_cache[self.cosmic_id][sprite_angle] = self.image
                else:
                    self.image = self.rotate_cache[self.cosmic_id][sprite_angle]
            self.base_pos = new_pos

        if self.epicycle_speed:
            self.current_epicycle_angle += self.epicycle_speed * dt
            self.base_pos = self.epicycle_process(self.base_pos, self.epicycle_radius, self.current_epicycle_angle,
                                                  self.epicycle_angle)

        self.base_pos = Vector2(self.base_pos)
        self.pos = (self.base_pos[0] * self.screen_scale_width, self.base_pos[1] * self.screen_scale_height)
        self.rect = self.image.get_rect(center=self.pos)

        if self.current_orbit_angle >= 360:
            if (int(self.base_pos[0]), int(self.base_pos[1])) == (int(self.start_pos[0]), int(self.start_pos[1])):
                self.current_orbit_angle = self.start_angle
                self.current_epicycle_angle = 0
