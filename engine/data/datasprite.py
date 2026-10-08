import ast
import lzma
import pickle
from math import ceil
from multiprocessing import cpu_count
from os import sep, listdir
from os.path import join, split, normpath, getsize
from pathlib import Path
from threading import Thread

import psutil
from pygame.mask import from_surface
from pygame.transform import smoothscale, flip, rotate, scale

from engine.data.data import GameData
from engine.utils.common import edit_config
from engine.utils.data_loading import load_image, load_images
from engine.utils.sprite_caching import load_pickle_with_surfaces, save_pickle_with_surfaces
from engine.utils.text_making import text_render_with_bg


class DataSprite(GameData):
    def __init__(self, character_list, initial_load_data=True):
        """
        Containing data related to sprite and animation
        """
        GameData.__init__(self)
        self.load_threads = cpu_count()
        if self.load_threads > 10:
            self.load_threads = 10

        self.number_text_cache = {}
        self.character_animation_data = {}
        self.region_sprites = {}
        self.stage_object_animation_pool = {}
        self.grand_object_animation_pool = {}
        self.grand_actor_animation_pool = {}
        self.character_portraits = {}
        self.strategy_icons = {}
        self.grand_ui_images = {}
        self.effect_animation_pool = {}
        self.animation_pickle_hash = {}

        if initial_load_data:
            try:
                with lzma.open(join(self.data_dir, "animation", "animation_pickle_hash.xz"), "rb") as read_file:
                    self.animation_pickle_hash = pickle.load(read_file)
                read_file.close()
            except Exception:
                pass

            image = load_image(self.data_dir, "drop_normal.png", self.screen_scale, ("ui", "mainmenu_ui"))
            image2 = load_image(self.data_dir, "drop_hover.png", self.screen_scale, ("ui", "mainmenu_ui"))
            image3 = load_image(self.data_dir, "drop_click.png", self.screen_scale, ("ui", "mainmenu_ui"))
            self.drop_button_list = (image, image2, image3)

            image = scale(image, (image.get_width() * 1.15, image.get_height() * 1.25))
            image2 = scale(image2, (image2.get_width() * 1.15, image2.get_height() * 1.25))
            image3 = scale(image3, (image3.get_width() * 1.15, image3.get_height() * 1.25))
            self.drop_big_button_list = (image, image2, image3)

            text_button_image = load_image(self.data_dir, "text_normal.png", self.screen_scale, ("ui", "mainmenu_ui"))
            text_button_image2 = load_image(self.data_dir, "text_hover.png", self.screen_scale, ("ui", "mainmenu_ui"))
            text_button_image3 = load_image(self.data_dir, "text_click.png", self.screen_scale, ("ui", "mainmenu_ui"))
            self.text_button_image_list = (text_button_image, text_button_image2, text_button_image3)

            self.config_animation_hash = ast.literal_eval(self.game.config["VERSION"]["hash"])

            self.strategy_icons = load_images(self.data_dir, screen_scale=self.screen_scale,
                                              subfolder=("ui", "strategy_ui"))
            self.grand_ui_images = load_images(self.data_dir, screen_scale=self.screen_scale,
                                               subfolder=("ui", "grand_ui"))
            self.battle_ui_images = load_images(self.data_dir, screen_scale=self.screen_scale,
                                                subfolder=("ui", "battle_ui"))
            self.cosmos_ui_images = load_images(self.data_dir, screen_scale=self.screen_scale,
                                                subfolder=("ui", "cosmos_ui"))
            self.weather_icon_images = load_images(self.data_dir, screen_scale=self.screen_scale,
                                                   subfolder=("ui", "weather_ui"))
            self.option_menu_images = load_images(self.data_dir, screen_scale=self.screen_scale,
                                                  subfolder=("ui", "option_ui"))

            self.battle_helper_images = {}
            part_folder = Path(join(self.data_dir, "ui", "battle_ui", "helper"))
            subdirectories = [split(sep.join(normpath(x).split(sep))) for x
                              in part_folder.iterdir() if x.is_dir()]
            for folder in subdirectories:
                folder_data_name = folder[-1]
                self.battle_helper_images[folder_data_name] = load_images(self.data_dir, screen_scale=self.screen_scale,
                                                                          subfolder=(
                                                                              "ui", "battle_ui", "helper",
                                                                              folder_data_name))

            building_portraits = load_images(self.data_dir, subfolder=("ui", "building_ui"))
            self.building_portraits = {}
            for file, image in building_portraits.items():
                self.building_portraits[file] = {"building_ui": smoothscale(image, (
                    image.get_width() * self.screen_scale_width, image.get_height() * self.screen_scale_height))}
                self.building_portraits[file]["big"] = smoothscale(image,
                                                                   (300 * self.screen_scale_width,
                                                                    300 * self.screen_scale_height))

            character_portraits = load_images(self.data_dir, subfolder=("ui", "character_ui"))
            self.character_portraits = {}
            for file, image in character_portraits.items():
                self.character_portraits[file] = {"character_ui": smoothscale(image, (
                    image.get_width() * self.screen_scale_width, image.get_height() * self.screen_scale_height))}
                mini_portrait = smoothscale(image, (200 * self.screen_scale_width, 200 * self.screen_scale_height))
                self.character_portraits[file]["small"] = {"right": mini_portrait,
                                                           "left": flip(mini_portrait, True, False)}

                number_font = self.game.character_number_font
                # icon for setup like purchase unit or custom preset army setup
                self.character_portraits[file]["setup_ui"] = mini_portrait.copy()
                if file in character_list:
                    icon = self.character_portraits[file]["setup_ui"]
                    add_number = character_list[file]["Capacity"]
                    if add_number:
                        if add_number not in self.number_text_cache:
                            number_text = text_render_with_bg(str(add_number), number_font, o_colour=(200, 200, 100))
                            self.number_text_cache[add_number] = number_text
                        else:
                            number_text = self.number_text_cache[add_number]
                        number_rect = number_text.get_rect(bottomright=mini_portrait.get_size())
                        icon.blit(number_text, number_rect)
                    icon.blit(self.battle_ui_images["class_" + self.game.character_list[file]["Class"]], (0, 0))

                mini_portrait = smoothscale(image, (150 * self.screen_scale_width, 150 * self.screen_scale_height))
                self.character_portraits[file]["tiny"] = {"right": mini_portrait,
                                                          "left": flip(mini_portrait, True, False)}

                mini_portrait = smoothscale(image, (100 * self.screen_scale_width, 100 * self.screen_scale_height))
                self.character_portraits[file]["mini"] = {"right": mini_portrait,
                                                          "left": flip(mini_portrait, True, False)}

            culture_coas = load_images(self.data_dir, subfolder=("ui", "culture_ui"))
            self.culture_coas = {}
            for file, image in culture_coas.items():
                self.culture_coas[file] = {"culture_ui": smoothscale(image, (
                    image.get_width() * self.screen_scale_width, image.get_height() * self.screen_scale_height))}
                self.culture_coas[file]["small"] = smoothscale(
                    image, (200 * self.screen_scale_width, 200 * self.screen_scale_height))
                self.culture_coas[file]["tiny"] = smoothscale(
                    image, (150 * self.screen_scale_width, 150 * self.screen_scale_height))
                self.culture_coas[file]["mini"] = smoothscale(
                    image, (100 * self.screen_scale_width, 100 * self.screen_scale_height))
                self.culture_coas[file]["text"] = smoothscale(
                    image, (70 * self.screen_scale_width, 70 * self.screen_scale_height))

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
            #     screen_scale=self.screen_scale)

    def load_region_sprite(self, map_data, grand_ui_images, map_shown_to_base_scale_width,
                           map_shown_to_base_scale_height, campaign: str):
        self.region_sprites = load_images(self.data_dir, screen_scale=self.screen_scale,
                                          subfolder=("map", "world", campaign, "region"))

        # draw route dot on region sprite
        map_data_route_dot_draw_array = map_data.route_dot_draw_array
        route_list = map_data.route_list
        dot_route_difficulty = map_data.dot_route_difficulty
        region_list = map_data.region_list
        already_done_dot = []
        already_cache_region = {}
        for route, route_data in route_list.items():
            region_1 = route[0]
            region_2 = route[1]
            for region in (region_1, region_2):
                if region not in already_cache_region:
                    region_data = region_list[region]
                    image = self.region_sprites[region]
                    rect = image.get_rect(center=((region_data["Region POS"][0] * map_shown_to_base_scale_width,
                                                   region_data["Region POS"][1] * map_shown_to_base_scale_height)))
                    mask = from_surface(image)
                    already_cache_region[region] = {"mask": mask, "rect": rect}

            for dot in route_data["Dots"]:
                if dot not in already_done_dot:
                    already_done_dot.append(dot)
                    if dot in dot_route_difficulty:  # skip settlement dot with no difficulty for draw
                        dot_image = rotate(grand_ui_images["route_dot_" + str(dot_route_difficulty[dot])],
                                           map_data_route_dot_draw_array[dot])
                        dot_rect = dot_image.get_rect(center=(dot[0] * map_shown_to_base_scale_width,
                                                              dot[1] * map_shown_to_base_scale_height))
                        dot_mask = from_surface(dot_image)
                        for region in (region_1, region_2):
                            region_rect = already_cache_region[region]["rect"]
                            if collide_mask(already_cache_region[region]["mask"], dot_mask,
                                            region_rect, dot_rect):
                                blit_dot_rect = dot_image.get_rect(topleft=(dot_rect.x - region_rect.x,
                                                                            dot_rect.y - region_rect.y))
                                self.region_sprites[region].blit(dot_image, blit_dot_rect)
                                break

    def load_character_animation(self, character_list):
        # only load those not already loaded
        character_list = [item for item in character_list if item not in self.character_animation_data]

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

        self.inner_load_character_animation(character_list, wait_to_finish=True)

    def inner_load_character_animation(self, character_list, wait_to_finish=False):
        if len(character_list) > 1 and self.load_threads > 1:
            chunk = ceil(len(character_list) / self.load_threads)
            chunks = [tuple(character_list)[i:i + chunk] for i in range(0, len(character_list), chunk)]
            threads = []
            for index, character_todo in enumerate(chunks):
                thread = Thread(target=load_character_sprite, args=(self.data_dir, self.screen_scale,
                                                                    self.character_animation_data, character_todo),
                                daemon=True)
                threads.append(thread)
                thread.start()
            if wait_to_finish:
                for thread in threads:
                    thread.join()
            else:  # add to load sprite background threads
                self.game.load_sprite_background_threads += threads
        else:
            load_character_sprite(self.data_dir, self.screen_scale, self.character_animation_data, character_list)

    def load_effect_sprites(self, game):
        config_animation_hash = game.sprite_data.config_animation_hash
        data_dir = game.data_dir
        effect_animation_pool = game.effect_animation_pool
        animation_pickle_hash = game.sprite_data.animation_pickle_hash
        screen_size = game.screen_size
        screen_scale = game.screen_scale
        if (not Path(join(data_dir, "animation", "cache_effect_animation.xz")).exists() or
                (screen_scale != (1, 1) and (screen_size != config_animation_hash["screen_resolution"] or
                                             "effect" not in animation_pickle_hash or not config_animation_hash[
                            "effect"] or animation_pickle_hash["effect"] != config_animation_hash["effect"]))):
            # effect sprite or screen resolution got changed, load and scale

            new_effect_animation_pool = load_pickle_with_surfaces(
                join(data_dir, "animation", "effect_animation.xz"),
                screen_scale=screen_scale, effect_sprite_adjust=True)

            # below need to be redone if character sprite need caching as well
            # save the above pool to cache for future use
            save_pickle_with_surfaces(join(data_dir, "animation", "cache_effect_animation.xz"),
                                      new_effect_animation_pool)

            # save screen resolution size in config for later game launch sprite scale check
            config_animation_hash["effect"] = animation_pickle_hash["effect"]
            config_animation_hash["screen_resolution"] = game.screen_size
            edit_config("VERSION", "hash", config_animation_hash,
                        game.config_path, game.config)
        else:
            # use (1, 1) scaling since the cached already got scaled
            try:
                new_effect_animation_pool = load_pickle_with_surfaces(
                    join(data_dir, "animation", "cache_effect_animation.xz"),
                    screen_scale=(1, 1), effect_sprite_adjust=True)
            except lzma.LZMAError:
                # file corrupt, recreate the cache
                config_animation_hash["effect"] = ""
                edit_config("VERSION", "hash", config_animation_hash,
                            game.config_path, game.config)
                self.load_effect_sprites(game)
                return

        for key, value in new_effect_animation_pool.items():
            effect_animation_pool[key] = value


def load_character_sprite(data_dir, screen_scale, character_animation_data, character_list):
    for file_name in character_list:
        if file_name not in character_animation_data:
            # get animation for each character that is not yet loaded
            character_animation_data[file_name] = load_pickle_with_surfaces(
                join(data_dir, "animation", file_name + ".xz"),
                screen_scale=screen_scale)


def collide_mask(left_mask, right_mask, left_rect, right_rect):
    """from pygame collide mask but use mask instead"""
    return left_mask.overlap(right_mask, (right_rect[0] - left_rect[0], right_rect[1] - left_rect[1]))
