# import numpy as np
# from PIL import Image
#
# color_list = []
# im = Image.open("world.png")
# rgb_im = np.array(im)
# for row in rgb_im:
#     for col in row:
#         rgb = col
#         color_list.append((int(rgb[0]), int(rgb[1]), int(rgb[2])))
#
# color_list = list(set(color_list))
# print(color_list[0])
# print(len(color_list))

# from PIL import ImageColor
#
# import os
# import csv
# check = []
# with open("region.csv",
#           encoding="utf-8", mode="r") as edit_file:
#     rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
#     header = rd[0]
#     for index, row in enumerate(rd[1:]):
#         check.append(ImageColor.getrgb("#" + row[1]))
# edit_file.close()
#
# print(len(color_list), len(check), len(set(check)))
#
# from collections import Counter
#
# # Use Counter to count
# #the occurrences of each element in the list
# counts = Counter(check)
# duplicates = [item for item, count in counts.items() if count > 1]
# print(['#%02x%02x%02x' % item for item in duplicates], "asd")
#
# for item in color_list:
#     if item not in check:
#         print(item)
#
# print("hmasd")
# for item in check:
#     if item not in color_list:
#         print('#%02x%02x%02x' % item, item)

import csv
import os

from engine.data.data import GameData
from engine.utils.data_loading import stat_convert

current_dir = os.path.split(os.path.abspath(__file__))[0]

main_dir = current_dir[:current_dir.rfind("\\") + 1].split("\\")
main_dir = ''.join(stuff + "\\" for stuff in main_dir[:-2])  # one folder further back
print(main_dir)
data_dir = os.path.join(main_dir, "data")
character_list = {}

from os.path import join
from pathlib import Path

from engine.data.datastat import stat_convert


def read_anim_data(art_style_dir, anim_column_header):
    pool = {}
    part_folder = Path(os.path.join(art_style_dir))
    files = [os.path.split(x)[-1].replace(".csv", "") for x in part_folder.iterdir() if
             ".csv" in os.path.split(x)[-1] and
             "lock." not in os.path.split(x)[-1]]
    for file in files:
        with open(os.path.join(art_style_dir, file + ".csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_MINIMAL)
            rd = [row for row in rd]
            part_name_header = rd[0]
            list_column = anim_column_header  # value in list only
            list_exclude = ["Name"]
            str_column = [item for item in list_column if
                          item not in list_exclude and any(ext in item for ext in list_exclude)]
            str_column = [index for index, item in enumerate(part_name_header) if item in str_column]
            list_column = [item for item in list_column if
                           item not in list_exclude and any(ext in item for ext in list_exclude) is False]
            list_column = [index for index, item in enumerate(part_name_header) if item in list_column]
            part_name_header = part_name_header[1:]  # keep only part name for list ref later
            animation_pool = {}
            for row_index, row in enumerate(rd):
                if row_index > 0:
                    key = row[0].split("/")[0]
                    for n, i in enumerate(row):
                        row = stat_convert(row, n, i, list_column=list_column, str_column=str_column)
                    row = row[1:]
                    if key in animation_pool:
                        animation_pool[key].append(
                            {part_name_header[item_index]: item for item_index, item in enumerate(row)})
                    else:
                        animation_pool[key] = [
                            {part_name_header[item_index]: item for item_index, item in enumerate(row)}]
            pool[file] = animation_pool
            part_name_header = [item for item in part_name_header if item != "sound_effect" and
                                "property" not in item]
            edit_file.close()
    return pool, part_name_header


def anim_to_pool(animation_name, pool, char, activate_list, new=False, replace=None, duplicate=None):
    """Add animation to animation pool data"""
    if replace is not None:  # rename animation
        pool[animation_name] = pool.pop(replace)
    elif duplicate is not None:
        pool[animation_name] = [
            {key: [small_value for small_value in value] if type(value) == list else value for key, value in
             this_frame.items()} for this_frame in pool[duplicate]]
    else:
        if animation_name not in pool:
            pool[animation_name] = []
        if new:
            pool[animation_name] = [frame for index, frame in enumerate(char.frame_list) if
                                    frame != {} and activate_list[index]]
        else:
            pool[animation_name] = [frame for index, frame in enumerate(char.frame_list) if
                                    frame != {} and activate_list[index]]


animation_dir = join(main_dir, "animation-maker", "data", "animation")
anim_column_header = ["Name"]
max_person = 4
max_frame = 30
p_list = tuple(["p" + str(p) for p in range(1, max_person + 1)])
part_column_header = ["head", "neck", "body", "r_arm_up", "r_arm_low", "r_hand", "l_arm_up",
                      "l_arm_low", "l_hand", "r_leg_up", "r_leg_low", "r_foot", "l_leg_up", "l_leg_low", "l_foot",
                      "main_weapon", "sub_weapon", "special_1", "special_2", "special_3", "special_4", "special_5",
                      "special_6", "special_7", "special_8", "special_9", "special_10"]

for p in range(1, max_person + 1):
    p_name = "p" + str(p) + "_"
    anim_column_header += [p_name + item for item in part_column_header]
anim_column_header += ["effect_1", "effect_2", "effect_3", "effect_4", "effect_5", "effect_6", "effect_7",
                       "effect_8",
                       "frame_property", "animation_property", "sound_effect"]  # For csv saving and accessing

animation_pool_data, part_name_header = read_anim_data(animation_dir, anim_column_header)

with open(os.path.join(data_dir, "character", "character.csv"),
          encoding="utf-8", mode="r") as edit_file:
    rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
    header = rd[0]
    tuple_column = ("Status Immunity", "Sub Characters", "Character Tag")
    tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
    dict_column = ("Spawns", "Items", "Property",)
    dict_column = [index for index, item in enumerate(header) if item in dict_column]
    for index, row in enumerate(rd[1:]):
        for n, i in enumerate(row):
            row = stat_convert(row, n, i, tuple_column=tuple_column, dict_column=dict_column)

        # Add character move data
        if os.path.exists(
                os.path.join(data_dir, "character", "moveset", str(row[0]) + ".csv")):
            with open(os.path.join(data_dir, "character", "moveset", str(row[0]) + ".csv"),
                      encoding="utf-8", mode="r") as edit_file2:
                rd2 = tuple(csv.reader(edit_file2, quoting=csv.QUOTE_ALL))
                header2 = rd2[0]
                tuple_column2 = ("Status", "Enemy Status", "Effect Enemy Status")  # value in tuple only
                tuple_column2 = [index for index, item in enumerate(header2) if item in tuple_column2]
                dict_column2 = ("Prepare Animation", "After Animation", "AI Condition", "Property",)
                dict_column2 = [index for index, item in enumerate(header2) if item in dict_column2]
                moveset_dict = {}
                for row_index2, row2 in enumerate(rd2[1:]):
                    for n2, i2 in enumerate(row2):
                        row2 = stat_convert(row2, n2, i2, tuple_column=tuple_column2,
                                            dict_column=dict_column2)

                    move_data = {header2[index]: stuff for index, stuff in enumerate(row2)}
                    if str(row[0]) in animation_pool_data:
                        if move_data["Move"] not in animation_pool_data[str(row[0])]:
                            print(str(row[0]), move_data["Move"])
                        if move_data["Prepare Animation"] and move_data["Prepare Animation"]["name"] not in animation_pool_data[str(row[0])]:
                            print(str(row[0]), move_data["Prepare Animation"]["name"])

                        if move_data["After Animation"] and move_data["After Animation"]["name"] not in animation_pool_data[str(row[0])]:
                            print(str(row[0]), move_data["After Animation"]["name"])
