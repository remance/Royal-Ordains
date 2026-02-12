import psutil

from os import listdir
from os.path import join, getsize
from pathlib import Path

from pygame.transform import smoothscale, flip

from engine.data.datastat import GameData
from engine.utils.data_loading import load_images, filename_convert_readable as fcv
from engine.utils.sprite_caching import load_pickle_with_surfaces
from engine.utils.text_making import text_render_with_bg


class SpriteData(GameData):
    def __init__(self, character_list, number_font):
        """
        Containing data related to sprite and animation
        """
        GameData.__init__(self)
        self.number_text_cache = {}
        self.character_animation_data = {}
        self.stage_object_animation_pool = {}
        self.grand_object_animation_pool = {}
        self.character_portraits = {}
        self.faction_coas = {}
        self.strategy_icons = {}
        self.effect_animation_pool = load_pickle_with_surfaces(
            join(self.data_dir, "animation", "effect_animation.xz"),
            screen_scale=self.screen_scale, effect_sprite_adjust=True)

        self.strategy_icons = load_images(self.data_dir, screen_scale=self.screen_scale,
                                          subfolder=("ui", "strategy_ui"),
                                          key_file_name_readable=True)
        self.character_portraits = load_images(self.data_dir, screen_scale=self.screen_scale,
                                               subfolder=("ui", "character_ui"),
                                               key_file_name_readable=True)
        for file in self.character_portraits:
            self.character_portraits[file] = {"character_ui": self.character_portraits[file]}
            mini_portrait = smoothscale(
                self.character_portraits[file]["character_ui"], (170 * self.screen_scale[0],
                                                                 170 * self.screen_scale[1]))

            self.character_portraits[file]["tactical"] = {"right": mini_portrait,
                                                          "left": flip(mini_portrait, True, False)}

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
                self.character_portraits[file]["character_ui"], (100 * self.screen_scale[0],
                                                                 100 * self.screen_scale[1]))
            self.character_portraits[file]["command"] = mini_portrait

        self.faction_coas = load_images(self.data_dir, screen_scale=self.screen_scale,
                                        subfolder=("ui", "faction_ui"), key_file_name_readable=True)
        for file in self.faction_coas:
            self.faction_coas[file] = {"faction_ui": self.faction_coas[file]}
            self.faction_coas[file]["mini"] = smoothscale(
                self.faction_coas[file]["faction_ui"], (170 * self.screen_scale[0],
                                                        170 * self.screen_scale[1]))
            self.faction_coas[file]["small"] = smoothscale(
                self.faction_coas[file]["faction_ui"], (200 * self.screen_scale[0],
                                                        200 * self.screen_scale[1]))

        # self.stage_object_animation_pool = load_pickle_with_surfaces(
        #     join(self.data_dir, "animation", "stage_object.xz"),
        #     screen_scale=self.screen_scale, battle_only=True)

        self.grand_object_animation_pool = load_pickle_with_surfaces(
            join(self.data_dir, "animation", "world_object.xz"),
            screen_scale=self.screen_scale)

    def load_character_animation(self, character_list, battle_only=False, clear=False):
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
                file_data_name = fcv(file_name)
                if file_data_name not in self.character_animation_data and file_data_name in character_list:
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
            file_data_name = fcv(file_name)
            if file_data_name not in self.character_animation_data and file_data_name in character_list:
                # get animation for each character
                self.character_animation_data[file_data_name] = load_pickle_with_surfaces(
                    join(self.data_dir, "animation", file),
                    screen_scale=self.screen_scale)
