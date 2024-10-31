import csv
from os import sep, listdir
from os.path import join, split, normpath, exists, isfile
from pathlib import Path

from engine.data.datastat import GameData
from engine.utils.data_loading import load_image, load_images, stat_convert, filename_convert_readable as fcv

direction_list = ("side",)


class AnimationData(GameData):
    def __init__(self):
        """
        Containing data related to troop animation sprite
        """
        GameData.__init__(self)
        self.chapter = 0
        self.part_sprite_adjust = {}
        self.character_animation_data = {}
        self.default_body_sprite_pool = {}
        self.default_effect_animation_pool = {}
        self.effect_animation_pool = {}
        self.stage_object_sprite_pool = {}
        self.stage_object_animation_pool = {}
        self.char_sprite_chapter = {}

    def load_data(self, chapter, character_list=None):
        if self.chapter != chapter:  # new chapter load, reload all assets
            self.chapter = chapter
            self.part_sprite_adjust.clear()
            self.character_animation_data.clear()
            self.default_effect_animation_pool.clear()
            self.effect_animation_pool.clear()
            self.stage_object_sprite_pool.clear()
            self.stage_object_animation_pool.clear()

        new_part_sprite_adjust = {}
        subdirectories = [split(sep.join(
            normpath(x).split(sep)[normpath(x).split(sep).index("animation"):]))[-1] for x
                          in Path(join(self.data_dir, "animation")).iterdir() if x.is_dir()]
        # get only chapter lower or equal to current chapter
        subdirectories = reversed([x for x in subdirectories if x.isdigit() and int(x) <= int(self.chapter)])
        for sub_folder in subdirectories:  # get chapter animation file
            part_folder = Path(join(self.data_dir, "animation", sub_folder))
            for file in listdir(part_folder):
                file = file.split(".")[0]
                file_data_name = fcv(file)
                if file_data_name not in self.character_animation_data and (not character_list or file_data_name in character_list):
                    # get only latest and nearest existing chapter animation for each character
                    # update to new chapter
                    self.char_sprite_chapter[file_data_name] = int(sub_folder)
                    with (open(join(self.data_dir, "animation", str(chapter), file + ".csv"), encoding="utf-8",
                               mode="r") as edit_file):
                        rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
                        part_name_header = rd[0]
                        list_column = ["head", "neck", "body", "r_arm_up", "r_arm_low", "r_hand", "l_arm_up",
                                       "l_arm_low", "l_hand", "r_leg_up", "r_leg_low", "r_foot", "l_leg_up",
                                       "l_leg_low",
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

                        for row_index, row in enumerate(rd):
                            if row_index > 0 and "EXCLUDE_" not in row[0]:
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
                                        if not flip_row[part_index][5]:  # revert flip value
                                            flip_row[part_index][5] = 1
                                        else:
                                            flip_row[part_index][5] = 0

                                animation_pool[key]["l_side"].append(
                                    {part_name_header[item_index]: item for item_index, item in
                                     enumerate(flip_row)})

                                for side in animation_pool[key].values():  # get angle, scale, flip for both side
                                    for row_part in side:
                                        for part_index, part in enumerate(row_part.values()):
                                            if type(part) is list and len(part) > 5:
                                                part_name = part_name_header[part_index]
                                                if "effect" in part_name:
                                                    part_name = part[0]
                                                    part_type = "effect"
                                                else:
                                                    if "special" in part_name:
                                                        part_name = part_name.split("_")[1]
                                                    elif "weapon" in part_name:  # for same dict structure
                                                        part_name = "weapon"
                                                    else:
                                                        for p in range(1, 5):
                                                            if "p" + str(p) in part_name:
                                                                part_name = part_name[3:]
                                                            if part_name[:2] == "l_" or part_name[:2] == "r_":
                                                                part_name = part_name[2:]
                                                    part_type = part[0]
                                                if file_data_name not in new_part_sprite_adjust:
                                                    new_part_sprite_adjust[file_data_name] = {}
                                                if part_type not in new_part_sprite_adjust[file_data_name]:
                                                    new_part_sprite_adjust[file_data_name][part_type] = {}
                                                if part_name not in new_part_sprite_adjust[file_data_name][
                                                    part_type]:
                                                    new_part_sprite_adjust[file_data_name][part_type][
                                                        part_name] = {}
                                                if part[1] not in \
                                                        new_part_sprite_adjust[file_data_name][part_type][
                                                            part_name]:
                                                    new_part_sprite_adjust[file_data_name][part_type][part_name][
                                                        part[1]] = {}
                                                if part[5] not in \
                                                        new_part_sprite_adjust[file_data_name][part_type][
                                                            part_name][
                                                            part[1]]:  # flip
                                                    new_part_sprite_adjust[file_data_name][part_type][part_name][
                                                        part[1]][
                                                        part[5]] = {}
                                                if part[7] not in \
                                                        new_part_sprite_adjust[file_data_name][part_type][
                                                            part_name][
                                                            part[1]][part[5]]:  # scale
                                                    new_part_sprite_adjust[file_data_name][part_type][part_name][
                                                        part[1]][
                                                        part[5]][part[7]] = []
                                                if part[4] not in \
                                                        new_part_sprite_adjust[file_data_name][part_type][
                                                            part_name][
                                                            part[1]][part[5]][part[7]]:  # angle
                                                    new_part_sprite_adjust[file_data_name][part_type][part_name][
                                                        part[1]][
                                                        part[5]][part[7]].append(part[4])

                                for side_data in animation_pool[key].values():
                                    for item in side_data:
                                        item["property"] = item["animation_property"] + item["frame_property"]
                                        for item2 in item["property"]:
                                            if "play_time_mod" in item2:
                                                item["play_time_mod"] = float(item2.split("_")[-1])
                                        item["property"] = tuple(set(item["property"]))
                                        if item["sound_effect"]:
                                            item["sound_effect"] = (
                                                item["sound_effect"][0], item["sound_effect"][1],
                                                item["sound_effect"][2])

                        # since pool data cannot be changed later, use tuple instead
                        for key in animation_pool:
                            for index in range(len(animation_pool[key]["l_side"])):
                                animation_pool[key]["l_side"][index] = {
                                    key: tuple(value) if type(value) is list else value
                                    for key, value in
                                    animation_pool[key]["l_side"][index].items()}
                            for index in range(len(animation_pool[key]["r_side"])):
                                animation_pool[key]["r_side"][index] = {
                                    key: tuple(value) if type(value) is list else value
                                    for key, value in
                                    animation_pool[key]["r_side"][index].items()}

                        self.character_animation_data[file_data_name] = animation_pool
                    edit_file.close()

            if "Item" not in self.part_sprite_adjust:
                new_part_sprite_adjust["Item"] = {"Item": {"special": {}}}
                part_folder = Path(join(self.data_dir, "animation", "sprite",
                                        "character", "item", "special", self.chapter, "normal"))
                for item in [f for f in listdir(part_folder) if isfile(join(part_folder, f))]:
                    item = fcv(item.replace(".png", ""))
                    if item not in new_part_sprite_adjust["Item"]["Item"]["special"]:
                        new_part_sprite_adjust["Item"]["Item"]["special"][item] = {}
                    if 0 not in new_part_sprite_adjust["Item"]["Item"]["special"][item]:
                        new_part_sprite_adjust["Item"]["Item"]["special"][item][0] = {}
                    if 0 not in new_part_sprite_adjust["Item"]["Item"]["special"][item][0]:
                        new_part_sprite_adjust["Item"]["Item"]["special"][item][0][0] = [1]
                self.char_sprite_chapter["Item"] = int(self.chapter)

            for key, part_data in new_part_sprite_adjust.items():
                if self.char_sprite_chapter[key] not in self.default_body_sprite_pool:
                    self.default_body_sprite_pool[self.char_sprite_chapter[key]] = {}
                for char_id in part_data:
                    sprite_pool = self.default_body_sprite_pool[self.char_sprite_chapter[key]]
                    if char_id != "effect":
                        if char_id not in sprite_pool:
                            sprite_pool[char_id] = {}
                        sprite_pool = sprite_pool[char_id]
                        for part_type in part_data[char_id]:
                            if part_type not in sprite_pool:
                                sprite_pool[part_type] = {}
                            for part_name in part_data[char_id][part_type]:
                                part_folder = Path(join(self.data_dir, "animation", "sprite",
                                                        "character", fcv(char_id, revert=True), part_type,
                                                        str(self.char_sprite_chapter[key])))
                                subdirectories = [split(sep.join(normpath(x).split(sep)[normpath(x).split(sep).index(
                                    "animation"):])) for x in part_folder.iterdir() if x.is_dir()]

                                for folder in subdirectories:  # loop part mode
                                    folder_data_name = fcv(folder[-1])
                                    if folder_data_name not in sprite_pool[part_type]:
                                        sprite_pool[part_type][folder_data_name] = {}
                                    if part_name not in sprite_pool[part_type][folder_data_name]:
                                        if exists(join(self.data_dir, folder[0], folder[1],
                                                       fcv(part_name + ".png", revert=True))):
                                            sprite_pool[part_type][folder_data_name][part_name] = load_image(
                                                join(self.data_dir, folder[0], folder[1]), self.screen_scale,
                                                fcv(part_name + ".png", revert=True))

            self.part_sprite_adjust |= new_part_sprite_adjust

            part_folder = Path(join(self.data_dir, "animation", "sprite", "effect"))
            subdirectories = [split(
                sep.join(normpath(x).split(sep)[normpath(x).split(sep).index("animation"):])) for x
                in part_folder.iterdir() if x.is_dir()]
            for folder in subdirectories:
                folder_data_name = fcv(folder[-1])
                if folder_data_name not in self.default_effect_animation_pool:
                    self.default_effect_animation_pool[folder_data_name] = {}
                    part_folder2 = Path(join(self.data_dir, "animation", "sprite", "effect", folder[-1]))
                    sub_directories2 = [split(sep.join(normpath(x).split(sep)[-1:]))[-1] for x
                                        in part_folder2.iterdir() if x.is_dir()]
                    if sub_directories2:
                        for folder2 in sub_directories2:
                            if int(folder2[-1]) <= int(chapter):  # use the closest chapter folder that is not higher
                                images = load_images(part_folder, screen_scale=self.screen_scale,
                                                     subfolder=(folder[-1], folder2), key_file_name_readable=True)
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
                                    if "#" in true_name:  # has animation to play
                                        final_name = true_name[:-1]
                                        sprite_animation_list = [value for key, value in images.items() if final_name ==
                                                                 " ".join([string for string in key.split(" ")[:-1]])]
                                    else:  # single frame animation
                                        sprite_animation_list = [value for key, value in images.items() if
                                                                 final_name == key]

                                    self.default_effect_animation_pool[folder_data_name][final_name] = sprite_animation_list

            self.effect_animation_pool |= {key: value.copy() for key, value in
                                           self.default_effect_animation_pool.items()}

            part_folder = Path(join(self.data_dir, "animation", "sprite", "object"))
            subdirectories = [split(
                sep.join(normpath(x).split(sep)[normpath(x).split(sep).index("animation"):])) for x
                in part_folder.iterdir() if x.is_dir()]
            for folder in subdirectories:
                folder_data_name = fcv(folder[-1])
                if folder_data_name not in self.stage_object_animation_pool:
                    self.stage_object_animation_pool[folder_data_name] = {}
                    part_folder2 = Path(join(self.data_dir, "animation", "sprite", "object", folder[-1]))
                    sub_directories2 = [split(sep.join(normpath(x).split(sep)[-1:]))[-1] for x
                                        in part_folder2.iterdir() if x.is_dir()]
                    if sub_directories2:
                        for folder2 in sub_directories2:
                            if int(folder2[-1]) <= int(chapter):
                                folder_data_name2 = fcv(folder2)
                                images = load_images(part_folder, screen_scale=self.screen_scale,
                                                     subfolder=(folder[-1], folder2), key_file_name_readable=True)
                                self.stage_object_animation_pool[folder_data_name][folder_data_name2] = \
                                    {int(key): value for key, value in images.items()}
