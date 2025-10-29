from os import listdir
from os.path import join
from pathlib import Path

from pygame.transform import smoothscale, flip

from engine.data.datastat import GameData
from engine.utils.data_loading import load_images, filename_convert_readable as fcv
from engine.utils.sprite_caching import load_pickle_with_surfaces


class SpriteData(GameData):
    def __init__(self):
        """
        Containing data related to sprite and animation
        """
        GameData.__init__(self)
        self.character_animation_data = {}
        self.stage_object_animation_pool = {}
        self.character_portraits = {}
        self.faction_coas = {}
        self.strategy_icons = {}
        self.effect_animation_pool = None
        self.stage_object_animation_pool = None
        self.effect_animation_pool = load_pickle_with_surfaces(
            join(self.data_dir, "animation", "effect_animation.xz"),
            screen_scale=self.screen_scale, battle_only=True, effect_sprite_adjust=True)

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

            mini_portrait = smoothscale(
                self.character_portraits[file]["character_ui"], (100 * self.screen_scale[0],
                                                                 100 * self.screen_scale[1]))
            self.character_portraits[file]["command"] = {"right": mini_portrait,
                                                         "left": flip(mini_portrait, True, False)}

        self.faction_coas = load_images(self.data_dir, screen_scale=self.screen_scale,
                                        subfolder=("ui", "faction_ui"), key_file_name_readable=True)
        for file in self.faction_coas:
            self.faction_coas[file] = {"faction_ui": self.faction_coas[file]}
            self.faction_coas[file]["mini"] = smoothscale(
                self.faction_coas[file]["faction_ui"], (200 * self.screen_scale[0],
                                                        200 * self.screen_scale[1]))

        # self.stage_object_animation_pool = load_pickle_with_surfaces(
        #     join(self.data_dir, "animation", "stage_object.xz"),
        #     screen_scale=self.screen_scale, battle_only=True)

    def load_character_animation(self, character_list, battle_only=False, clear=False):
        if clear:
            self.character_animation_data.clear()
            self.character_portraits.clear()
        else:
            for character in self.character_animation_data:
                if character not in character_list:
                    self.character_animation_data.pop(character)
                    self.character_portraits.pop(character)

        part_folder = Path(join(self.data_dir, "animation"))
        for file in listdir(part_folder):
            file_name = file.split(".")[0]
            file_data_name = fcv(file_name)
            if file_data_name not in self.character_animation_data and file_data_name in character_list:
                # get animation for each character
                self.character_animation_data[file_data_name] = load_pickle_with_surfaces(
                    join(self.data_dir, "animation", file),
                    screen_scale=self.screen_scale, battle_only=battle_only)
