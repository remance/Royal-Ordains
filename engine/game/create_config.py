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
                         "fps": 0, "master_volume": 100.0, "music_volume": 100.0, "easy_text": 0, "show_dmg_number": 1,
                         "voice_volume": 100.0, "effect_volume": 50.0, "max_fps": 60,
                         "language": "en",
                         "keybind": {"Confirm": pygame.K_RETURN,
                                     "Left": pygame.K_a, "Right": pygame.K_d,
                                     "Up": pygame.K_w, "Down": pygame.K_s,
                                     "Select 1": pygame.K_1,
                                     "Select 2": pygame.K_2,
                                     "Select 3": pygame.K_3,
                                     "Select 4": pygame.K_4,
                                     "Select 5": pygame.K_5,
                                     "Menu/Cancel": pygame.K_ESCAPE,
                                     "Retreat": pygame.K_l,
                                     "Strategy 1": pygame.K_q,
                                     "Strategy 2": pygame.K_e,
                                     "Strategy 3": pygame.K_r,
                                     "Strategy 4": pygame.K_t,
                                     "Strategy 5": pygame.K_y,
                                     }
                         }

    config["USER"] = {key: value for key, value in config["DEFAULT"].items()}
    with open(self.config_path, "w") as cf:
        config.write(cf)
    config.read_file(open(self.config_path))
    return config
