import csv
import os
from pathlib import Path

from pygame.transform import flip, smoothscale

from engine.data.datastat import GameData
from engine.utils.data_loading import load_images, stat_convert, recursive_image_load, filename_convert_readable as fcv

direction_list = ("side",)


class AnimationData(GameData):
    def __init__(self):
        """
        Containing data related to troop animation sprite
        """
        GameData.__init__(self)

        part_sprite_adjust = {}
        self.character_animation_data = {}
        part_folder = Path(os.path.join(self.data_dir, "animation"))
        for file in os.listdir(part_folder):
            file = file.split(".")[0]
            if os.path.exists(os.path.join(self.data_dir, "animation", file + ".csv")):
                with open(os.path.join(self.data_dir, "animation", file + ".csv"), encoding="utf-8",
                          mode="r") as edit_file:
                    rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
                    part_name_header = rd[0]
                    list_column = ["head", "neck", "body", "r_arm_up", "r_arm_low", "r_hand", "l_arm_up",
                                   "l_arm_low", "l_hand", "r_leg_up", "r_leg_low", "r_foot", "l_leg_up", "l_leg_low",
                                   "l_foot", "main_weapon", "sub_weapon",
                                   "special_1", "special_2", "special_3", "special_4", "special_5",
                                   "special_6", "special_7", "special_8", "special_9", "special_10"]
                    for p in range(1, 5):  # up to p4
                        p_name = "p" + str(p) + "_"
                        list_column += [p_name + item for item in list_column]
                    list_column += ["effect_1", "effect_2", "effect_3", "effect_4",
                                    "effect_5", "effect_6", "effect_7", "effect_8", "frame_property",
                                    "animation_property", "sound_effect"]  # value in list only
                    list_column = [index for index, item in enumerate(part_name_header) if item in list_column]
                    part_name_header = part_name_header[1:]  # keep only part name for list ref later
                    animation_pool = {}
                    file_data_name = fcv(file)
                    for row_index, row in enumerate(rd):
                        if row_index > 0:
                            key = row[0].split("/")[0]
                            for n, i in enumerate(row):
                                row = stat_convert(row, n, i, list_column=list_column)
                            row = row[1:]

                            if key in animation_pool:
                                animation_pool[key]["r_side"].append(
                                    {part_name_header[item_index]: item for item_index, item in enumerate(row)})
                            else:
                                animation_pool[key] = {"r_side": [{part_name_header[item_index]: item for
                                                                   item_index, item in enumerate(row)}],
                                                       "l_side": []}
                            flip_row = row.copy()  # flip sprite data for left direction
                            for part_index, part_data in enumerate(flip_row):
                                if part_data and type(part_data) is list and "property" not in part_name_header[
                                    part_index] and "sound_effect" not in part_name_header[part_index]:
                                    flip_row[part_index] = [-item if index in (2, 4) else item for
                                                            index, item in enumerate(part_data)]
                                    if not flip_row[part_index][5]:
                                        flip_row[part_index][5] = 1
                                    else:
                                        flip_row[part_index][5] -= 1

                            animation_pool[key]["l_side"].append(
                                {part_name_header[item_index]: item for item_index, item in enumerate(flip_row)})

                            for side in animation_pool[key].values():  # get angle, scale, flip for both side
                                for row_part in side:
                                    for part_index, part in enumerate(row_part.values()):
                                        if type(part) is list and len(part) > 5:
                                            part_name = part_name_header[part_index]
                                            if "weapon" in part_name:  # for same dict structure
                                                part_name = part[0]
                                                part_type = "weapon"
                                            elif "effect" in part_name:
                                                part_name = part[0]
                                                part_type = "effect"
                                            else:
                                                if "special" in part_name:
                                                    part_name = part_name.split("_")[1]
                                                else:
                                                    for p in range(1, 5):
                                                        if "p" + str(p) in part_name:
                                                            part_name = part_name[3:]
                                                        if part_name[:2] == "l_" or part_name[:2] == "r_":
                                                            part_name = part_name[2:]
                                                part_type = part[0]
                                            if part_type not in part_sprite_adjust:
                                                part_sprite_adjust[part_type] = {}
                                            if part_name not in part_sprite_adjust[part_type]:
                                                part_sprite_adjust[part_type][part_name] = {}
                                            if part[1] not in part_sprite_adjust[part_type][part_name]:
                                                part_sprite_adjust[part_type][part_name][part[1]] = {}
                                                if part_type == "Item":
                                                    # item mush have default sprite for drop
                                                    part_sprite_adjust[part_type][part_name][part[1]][0] = {}
                                                    part_sprite_adjust[part_type][part_name][part[1]][0][0] = [1]
                                            if part[5] not in part_sprite_adjust[part_type][part_name][part[1]]:  # flip
                                                part_sprite_adjust[part_type][part_name][part[1]][part[5]] = {}
                                            if part[7] not in part_sprite_adjust[part_type][part_name][part[1]][
                                                part[5]]:  # scale
                                                part_sprite_adjust[part_type][part_name][part[1]][part[5]][part[7]] = []
                                            if part[4] not in \
                                                    part_sprite_adjust[part_type][part_name][part[1]][part[5]][
                                                        part[7]]:  # angle
                                                part_sprite_adjust[part_type][part_name][part[1]][part[5]][
                                                    part[7]].append(part[4])

                            for side_data in animation_pool[key].values():
                                for item in side_data:
                                    item["property"] = item["animation_property"] + item["frame_property"]
                                    for item2 in item["property"]:
                                        if "play_time_mod" in item2:
                                            item["play_time_mod"] = float(item2.split("_")[-1])
                                    item["property"] = tuple(set(item["property"]))
                                    if item["sound_effect"]:
                                        item["sound_effect"] = (
                                        item["sound_effect"][0], item["sound_effect"][1], item["sound_effect"][2])

                    # since pool data cannot be changed later, use tuple instead
                    for key in animation_pool:
                        for index in range(len(animation_pool[key]["l_side"])):
                            animation_pool[key]["l_side"][index] = {key: tuple(value) if type(value) is list else value
                                                                    for key, value in
                                                                    animation_pool[key]["l_side"][index].items()}
                        for index in range(len(animation_pool[key]["r_side"])):
                            animation_pool[key]["r_side"][index] = {key: tuple(value) if type(value) is list else value
                                                                    for key, value in
                                                                    animation_pool[key]["r_side"][index].items()}

                    self.character_animation_data[file_data_name] = animation_pool
                edit_file.close()

        self.body_sprite_pool = {}
        part_folder = Path(os.path.join(self.data_dir, "animation", "sprite", "character"))
        char_list = [os.path.split(x)[-1] for x in part_folder.iterdir()]
        for char in char_list:
            char_id = fcv(char)
            self.body_sprite_pool[char_id] = {}
            part_folder = Path(os.path.join(self.data_dir, "animation", "sprite", "character", char))
            try:
                subdirectories = [os.path.split(os.sep.join(
                    os.path.normpath(x).split(os.sep)[os.path.normpath(x).split(os.sep).index("animation"):])) for x
                    in part_folder.iterdir() if x.is_dir()]
                self.body_sprite_pool[char_id] = {}

                for folder in subdirectories:
                    self.body_sprite_pool[char_id][folder[-1]] = {}
                    part_subfolder = Path(
                        os.path.join(self.data_dir, "animation", "sprite", "character", char, folder[-1]))
                    recursive_image_load(self.body_sprite_pool[char_id][folder[-1]], self.screen_scale, part_subfolder,
                                         part_sprite_adjust=part_sprite_adjust)
            except FileNotFoundError:
                pass

        part_folder = Path(os.path.join(self.data_dir, "animation", "sprite", "character", "weapon"))
        subdirectories = [os.path.split(
            os.sep.join(os.path.normpath(x).split(os.sep)[os.path.normpath(x).split(os.sep).index("animation"):])) for x
            in part_folder.iterdir() if x.is_dir()]
        for folder in subdirectories:
            folder_data_name = fcv(folder[-1])
            self.body_sprite_pool[folder_data_name] = {}
            part_subfolder = Path(
                os.path.join(self.data_dir, "animation", "sprite", "character", "weapon", folder[-1]))
            recursive_image_load(self.body_sprite_pool[folder_data_name], self.screen_scale, part_subfolder,
                                 part_sprite_adjust=part_sprite_adjust)

        self.effect_animation_pool = {}
        part_folder = Path(os.path.join(self.data_dir, "animation", "sprite", "effect"))
        subdirectories = [os.path.split(
            os.sep.join(os.path.normpath(x).split(os.sep)[os.path.normpath(x).split(os.sep).index("animation"):])) for x
            in part_folder.iterdir() if x.is_dir()]
        for folder in subdirectories:
            folder_data_name = fcv(folder[-1])
            self.effect_animation_pool[folder_data_name] = {}
            part_folder2 = Path(os.path.join(self.data_dir, "animation", "sprite", "effect", folder[-1]))
            sub_directories2 = [os.path.split(os.sep.join(os.path.normpath(x).split(os.sep)[-1:]))[-1] for x
                                in part_folder2.iterdir() if x.is_dir()]
            if sub_directories2:
                for folder2 in sub_directories2:
                    folder_data_name2 = fcv(folder2)
                    images = load_images(part_folder, screen_scale=self.screen_scale,
                                         subfolder=(folder[-1], folder2), key_file_name_readable=True)
                    self.effect_animation_pool[folder_data_name][folder_data_name2] = {}
                    true_name_list = []
                    for key, value in images.items():
                        if key.split(" ")[-1].isdigit():
                            true_name = " ".join([string for string in key.split(" ")[:-1]]) + "#"
                        else:
                            true_name = key
                        if true_name not in true_name_list:
                            true_name_list.append(true_name)

                    for true_name in set(true_name_list):  # create effect animation list
                        final_name = true_name
                        animation_list = {}
                        if "#" in true_name:  # has animation to play
                            final_name = true_name[:-1]
                            sprite_animation_list = [value for key, value in images.items() if final_name ==
                                                     " ".join([string for string in key.split(" ")[:-1]])]
                            final_check_name = final_name + " 0"
                        else:  # single frame animation
                            sprite_animation_list = [value for key, value in images.items() if final_name == key]
                            final_check_name = final_name
                        if not ("effect" in part_sprite_adjust and fcv(folder[-1]) in part_sprite_adjust["effect"] and
                                final_check_name in part_sprite_adjust["effect"][fcv(folder[-1])]):
                            # add effect with no sprite adjust
                            animation_list = sprite_animation_list
                        else:
                            for flip_value in part_sprite_adjust["effect"][fcv(folder[-1])][final_check_name]:
                                animation_list[flip_value] = {}
                                for scale in part_sprite_adjust["effect"][fcv(folder[-1])][final_check_name][
                                    flip_value]:
                                    animation_list[flip_value][scale] = []
                                    for frame_index, _ in enumerate(sprite_animation_list):
                                        flip_image = sprite_animation_list[frame_index]
                                        if flip_value:
                                            flip_image = flip(flip_image, True, False)
                                        animation_list[flip_value][scale].append(flip_image)
                                        if scale != 1:
                                            animation_list[flip_value][scale][frame_index] = smoothscale(flip_image, (
                                                flip_image.get_width() * scale,
                                                flip_image.get_height() * scale))
                        self.effect_animation_pool[folder_data_name][folder_data_name2][final_name] = animation_list

        self.stage_object_sprite_pool = {}
        self.stage_object_animation_pool = {}
        part_folder = Path(os.path.join(self.data_dir, "animation", "sprite", "object"))
        subdirectories = [os.path.split(
            os.sep.join(os.path.normpath(x).split(os.sep)[os.path.normpath(x).split(os.sep).index("animation"):])) for x
            in part_folder.iterdir() if x.is_dir()]
        for folder in subdirectories:
            folder_data_name = fcv(folder[-1])
            self.stage_object_animation_pool[folder_data_name] = {}
            part_folder2 = Path(os.path.join(self.data_dir, "animation", "sprite", "object", folder[-1]))
            sub_directories2 = [os.path.split(os.sep.join(os.path.normpath(x).split(os.sep)[-1:]))[-1] for x
                                in part_folder2.iterdir() if x.is_dir()]
            if sub_directories2:
                for folder2 in sub_directories2:
                    folder_data_name2 = fcv(folder2)
                    images = load_images(part_folder, screen_scale=self.screen_scale,
                                         subfolder=(folder[-1], folder2), key_file_name_readable=True)
                    self.stage_object_animation_pool[folder_data_name][folder_data_name2] = \
                        {int(key): value for key, value in images.items()}
