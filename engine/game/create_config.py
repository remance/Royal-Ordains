from configparser import ConfigParser

import pygame
import screeninfo


def create_config(self):
    config = ConfigParser()

    screen = screeninfo.get_monitors()[0]
    screen_width = int(screen.width)
    screen_height = int(screen.height)
    config["VERSION"] = {"ver": self.game_version}

    config["DEFAULT"] = {"screen_width": screen_width, "screen_height": screen_height, "full_screen": 0,
                         "fps": 0, "master_volume": 100.0, "music_volume": 100.0, "easy_text": 0,
                         "voice_volume": 100.0, "effect_volume": 50.0, "max_fps": 60,
                         "language": "en", "control player 1": "keyboard", "control player 2": "keyboard",
                         "control player 3": "keyboard", "control player 4": "keyboard",
                         "keybind player 1": {"keyboard": {"Weak": pygame.K_g,
                                                           "Strong": pygame.K_h,
                                                           "Guard": pygame.K_j,
                                                           "Special": pygame.K_y,
                                                           "Left": pygame.K_a, "Right": pygame.K_d,
                                                           "Up": pygame.K_w, "Down": pygame.K_s,
                                                           "Menu/Cancel": pygame.K_ESCAPE,
                                                           "Order Menu": pygame.K_q,
                                                           "Inventory Menu": pygame.K_e},
                                              "joystick": {"Weak": 4,
                                                           "Strong": 5,
                                                           "Guard": 6,
                                                           "Special": 7,
                                                           "Left": "axis-0", "Right": "axis+0",
                                                           "Up": "axis-1", "Down": "axis+1",
                                                           "Menu/Cancel": 9,
                                                           "Order Menu": 8,
                                                           "Inventory Menu": 10}},
                         "keybind player 2": {"keyboard": {"Weak": pygame.K_KP1,
                                                           "Strong": pygame.K_KP2,
                                                           "Guard": pygame.K_KP3,
                                                           "Special": pygame.K_KP5,
                                                           "Left": pygame.K_LEFT, "Right": pygame.K_RIGHT,
                                                           "Up": pygame.K_UP, "Down": pygame.K_DOWN,
                                                           "Menu/Cancel": pygame.K_KP_MINUS,
                                                           "Order Menu": pygame.K_KP7,
                                                           "Inventory Menu": pygame.K_KP9},
                                              "joystick": {"Weak": 4,
                                                           "Strong": 5,
                                                           "Guard": 6,
                                                           "Special": 7,
                                                           "Left": "axis-0", "Right": "axis+0",
                                                           "Up": "axis-1", "Down": "axis+1",
                                                           "Menu/Cancel": 9,
                                                           "Order Menu": 8,
                                                           "Inventory Menu": 10}},
                         "keybind player 3": {"keyboard": {"Weak": pygame.K_p,
                                                           "Strong": pygame.K_p,
                                                           "Guard": pygame.K_p,
                                                           "Special": pygame.K_p,
                                                           "Left": pygame.K_p, "Right": pygame.K_p,
                                                           "Up": pygame.K_p, "Down": pygame.K_p,
                                                           "Menu/Cancel": pygame.K_p,
                                                           "Order Menu": pygame.K_p,
                                                           "Inventory Menu": pygame.K_p},
                                              "joystick": {"Weak": 4,
                                                           "Strong": 5,
                                                           "Guard": 6,
                                                           "Special": 7,
                                                           "Left": "axis-0", "Right": "axis+0",
                                                           "Up": "axis-1", "Down": "axis+1",
                                                           "Menu/Cancel": 9,
                                                           "Order Menu": 8,
                                                           "Inventory Menu": 10}},
                         "keybind player 4": {"keyboard": {"Weak": pygame.K_o,
                                                           "Strong": pygame.K_o,
                                                           "Guard": pygame.K_o,
                                                           "Special": pygame.K_o,
                                                           "Left": pygame.K_o, "Right": pygame.K_o,
                                                           "Up": pygame.K_o, "Down": pygame.K_o,
                                                           "Menu/Cancel": pygame.K_o,
                                                           "Order Menu": pygame.K_o,
                                                           "Inventory Menu": pygame.K_o},
                                              "joystick": {"Weak": 4,
                                                           "Strong": 5,
                                                           "Guard": 6,
                                                           "Special": 7,
                                                           "Left": "axis-0", "Right": "axis+0",
                                                           "Up": "axis-1", "Down": "axis+1",
                                                           "Menu/Cancel": 9,
                                                           "Order Menu": 8,
                                                           "Inventory Menu": 10}}
                         }

    config["USER"] = {key: value for key, value in config["DEFAULT"].items()}
    with open(self.config_path, "w") as cf:
        config.write(cf)
    config.read_file(open(self.config_path))
    return config
