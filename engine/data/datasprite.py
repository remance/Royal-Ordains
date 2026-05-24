from os import listdir, sep
from os.path import join, getsize, split, normpath
from pathlib import Path

import pickle
import ast
import lzma
import psutil
from pygame.transform import smoothscale, flip

from engine.data.data import GameData
from engine.utils.data_loading import load_images
from engine.utils.sprite_caching import load_pickle_with_surfaces, save_pickle_with_surfaces
from engine.utils.text_making import text_render_with_bg
from engine.utils.common import edit_config


class DataSprite(GameData):
    def __init__(self, character_list):
        """
        Containing data related to sprite and animation
        """
        GameData.__init__(self)
        self.number_text_cache = {}
        self.character_animation_data = {}
        self.stage_object_animation_pool = {}
        self.grand_object_animation_pool = {}
        self.grand_actor_animation_pool = {}
        self.character_portraits = {}
        self.strategy_icons = {}
        self.grand_ui_icons = {}
        self.effect_animation_pool = {}
        self.animation_pickle_hash = {}

        try:
            with lzma.open(join(self.data_dir, "animation", "animation_pickle_hash.xz"), "rb") as read_file:
                self.animation_pickle_hash = pickle.load(read_file)
            read_file.close()
        except Exception:
            pass

        config_animation_hash = ast.literal_eval(self.game.config["VERSION"]["hash"])

        # if (self.game.screen_size != (1, 1) and (self.game.screen_size != config_animation_hash["screen_resolution"] or
        #         "effect" not in self.animation_pickle_hash or not config_animation_hash["effect"] or
        #         self.animation_pickle_hash["effect"] != config_animation_hash["effect"])):
        #     # effect sprite or screen resolution got changed, load and scale
        #     self.effect_animation_pool = load_pickle_with_surfaces(
        #         join(self.data_dir, "animation", "effect_animation.xz"),
        #         screen_scale=self.screen_scale, effect_sprite_adjust=True)
        #
        #     # save the above pool to cache for future use
        #     save_pickle_with_surfaces(join(self.data_dir, "animation", "cache_effect_animation.xz"),
        #                               self.effect_animation_pool)
        #     config_animation_hash["effect"] = self.animation_pickle_hash["effect"]
        # else:
        #     self.effect_animation_pool = load_pickle_with_surfaces(
        #         join(self.data_dir, "animation", "cache_effect_animation.xz"),
        #         screen_scale=(1, 1), effect_sprite_adjust=True)

        self.strategy_icons = load_images(self.data_dir, screen_scale=self.screen_scale,
                                          subfolder=("ui", "strategy_ui"))
        self.grand_ui_icons = load_images(self.data_dir, screen_scale=self.screen_scale,
                                          subfolder=("ui", "grand_ui"))
        self.character_portraits = load_images(self.data_dir, screen_scale=self.screen_scale,
                                               subfolder=("ui", "character_ui"))

        for file in self.character_portraits:
            self.character_portraits[file] = {"character_ui": self.character_portraits[file]}
            mini_portrait = smoothscale(
                self.character_portraits[file]["character_ui"], (200 * self.screen_scale[0],
                                                                 200 * self.screen_scale[1]))
            self.character_portraits[file]["small"] = {"right": mini_portrait,
                                                       "left": flip(mini_portrait, True, False)}

            number_font = self.game.character_number_font
            # icon for setup like purchase unit or custom preset army setup
            self.character_portraits[file]["setup_ui"] = mini_portrait.copy()
            if file in character_list:
                add_number = character_list[file]["Capacity"]
                if add_number:
                    if add_number not in self.number_text_cache:
                        number_text = text_render_with_bg(str(add_number), number_font, o_colour=(200, 200, 100))
                        self.number_text_cache[add_number] = number_text
                    else:
                        number_text = self.number_text_cache[add_number]
                    number_rect = number_text.get_rect(bottomright=mini_portrait.get_size())
                    self.character_portraits[file]["setup_ui"].blit(number_text, number_rect)

            mini_portrait = smoothscale(
                self.character_portraits[file]["character_ui"], (150 * self.screen_scale[0],
                                                                 150 * self.screen_scale[1]))

            self.character_portraits[file]["tiny"] = {"right": mini_portrait,
                                                      "left": flip(mini_portrait, True, False)}

            mini_portrait = smoothscale(
                self.character_portraits[file]["character_ui"], (100 * self.screen_scale[0],
                                                                 100 * self.screen_scale[1]))

            self.character_portraits[file]["mini"] = {"right": mini_portrait,
                                                      "left": flip(mini_portrait, True, False)}

        self.culture_coas = load_images(self.data_dir, screen_scale=self.screen_scale,
                                        subfolder=("ui", "culture_ui"))
        for file in self.culture_coas:
            self.culture_coas[file] = {"culture_ui": self.culture_coas[file]}
            self.culture_coas[file]["small"] = smoothscale(
                self.culture_coas[file]["culture_ui"], (200 * self.screen_scale[0],
                                                        200 * self.screen_scale[1]))
            self.culture_coas[file]["tiny"] = smoothscale(
                self.culture_coas[file]["culture_ui"], (150 * self.screen_scale[0],
                                                        150 * self.screen_scale[1]))

        self.weather_matter_images = {}
        part_folder = Path(join(self.data_dir, "map", "weather", "matter"))
        subdirectories = [split(sep.join(normpath(x).split(sep))) for x
                          in part_folder.iterdir() if x.is_dir()]
        for folder in subdirectories:
            folder_data_name = folder[-1]
            self.weather_matter_images[folder_data_name] = tuple(load_images(
                self.data_dir, screen_scale=self.screen_scale,
                subfolder=("map", "weather", "matter", folder_data_name)).values())

        # self.stage_object_animation_pool = load_pickle_with_surfaces(
        #     join(self.data_dir, "animation", "stage_object.xz"),
        #     screen_scale=self.screen_scale, battle_only=True)

        # save screen resolution size in config for later game launch sprite scale check
        config_animation_hash["screen_resolution"] = self.game.screen_size
        edit_config("VERSION", "hash", config_animation_hash,
                    self.game.config_path, self.game.config)

    def setup_campaign(self):
        """Setup animation for campaign, only run once"""
        if not self.grand_object_animation_pool:
            self.grand_object_animation_pool = load_pickle_with_surfaces(
                join(self.data_dir, "animation", "world_object.xz"),
                screen_scale=self.screen_scale, add_mask=False)

            self.grand_actor_animation_pool = load_pickle_with_surfaces(
                join(self.data_dir, "animation", "world_actor.xz"),
                screen_scale=self.screen_scale, add_mask=False)

    def load_character_animation(self, character_list, clear=False):
        if clear:
            self.character_animation_data.clear()
        else:

            """
            Retrieves and prints system RAM information in GB.
            """
            # Get memory statistics
            available_mem = psutil.virtual_memory().available / (1024 ** 3) * 1000

            total_require_mem_to_load = 0
            part_folder = Path(join(self.data_dir, "animation"))
            for file in listdir(part_folder):
                file_name = file.split(".")[0]
                if file_name not in self.character_animation_data and file_name in character_list:
                    # convert to mb, and estimated ram required (around 10x of file size)
                    total_require_mem_to_load += getsize(join(self.data_dir, "animation", file)) * 10 / 1048576
            if total_require_mem_to_load > available_mem:
                # need to free memory, remove previously loaded unused sprite
                for character in tuple(self.character_animation_data.keys()):
                    if character not in character_list:
                        self.character_animation_data.pop(character)

        part_folder = Path(join(self.data_dir, "animation"))
        for file in listdir(part_folder):
            file_name = file.split(".")[0]
            if file_name not in self.character_animation_data and file_name in character_list:
                # get animation for each character
                self.character_animation_data[file_name] = load_pickle_with_surfaces(
                    join(self.data_dir, "animation", file),
                    screen_scale=self.screen_scale)
