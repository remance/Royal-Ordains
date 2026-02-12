import csv
import os
import random
import re
import sys
import time
from math import atan2, degrees, radians
from os import sep
from os.path import join, split, normpath, abspath
from pathlib import Path

import pygame
from pygame.transform import smoothscale, rotate, flip as pyflip
from pygame.mixer import Channel
from engine.battle.battle import Battle
from engine.data.datalocalisation import Localisation
from engine.data.datasound import SoundData
from engine.game.game import Game
from engine.uibattle.uibattle import UIBattle, UIScroll
from engine.uimenu.uimenu import MenuCursor, NameList, MenuButton, TextPopup, InputUI, InputBox, ListBox
from engine.utils.data_loading import csv_read, load_image, load_images, load_base_button, recursive_image_load, \
    filename_convert_readable as fcv
from engine.utils.rotation import rotation_xy
from engine.utils.sprite_altering import sprite_rotate, apply_sprite_effect, apply_sprite_colour

from engine.utils.data_loading import filename_convert_readable

main_dir = os.path.split(os.path.abspath(__file__))[0]
main_dir = "\\".join(main_dir.split("\\")[:-2])
current_dir = join(main_dir, "animation-maker")  # animation maker folder
current_data_dir = join(main_dir, "animation-maker", "data")  # animation maker folder
sys.path.insert(1, current_dir)
main_data_dir = os.path.join(main_dir, "data")
data_dir = os.path.join(main_dir, "data")

animation_dir = join(current_dir, "data", "animation")

from engine.utils.data_loading import stat_convert


part_column_header = ["head", "neck", "body", "r_arm_up", "r_arm_low", "r_hand", "l_arm_up",
                      "l_arm_low", "l_hand", "r_leg_up", "r_leg_low", "r_foot", "l_leg_up", "l_leg_low", "l_foot",
                      "main_weapon", "sub_weapon", "special_1", "special_2", "special_3", "special_4", "special_5",
                      "special_6", "special_7", "special_8", "special_9", "special_10"]
anim_column_header = ["Name"]
for p in range(1, 5):
    p_name = "p" + str(p) + "_"
    anim_column_header += [p_name + item for item in part_column_header]
anim_column_header += ["effect_1", "effect_2", "effect_3", "effect_4", "effect_5", "effect_6", "effect_7",
                       "effect_8",
                       "frame_property", "animation_property", "sound_effect"]  # For csv saving and accessing
frame_property_list = ["sprite_deal_damage", "hold", "play_time_mod_", "effect_blur_", "effect_fade_",
                       "effect_contrast_", "effect_brightness_", "effect_grey",
                       "effect_colour_", "exclude_p1", "exclude_p2", "exclude_p3",
                       "exclude_p4"]  # starting property list


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
            pool[filename_convert_readable(file)] = animation_pool
            part_name_header = [item for item in part_name_header if item != "sound_effect" and
                                "property" not in item]
            edit_file.close()
    return pool, part_name_header


def effect_check():
    """Check for effect being used as independent effect sprite in all animation exist in effect stat data"""
    effect_list = {}
    with open(os.path.join(data_dir, "character", "effect.csv"),
              encoding="utf-8", mode="r") as edit_file:
        rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
        header = rd[0]
        tuple_column = ("Status Conflict", "Status", "Enemy Status",
                        "Special Effect")  # value in tuple only
        tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
        dict_column = ("Property",)
        dict_column = [index for index, item in enumerate(header) if item in dict_column]
        for index, row in enumerate(rd[1:]):
            for n, i in enumerate(row):
                row = stat_convert(row, n, i, tuple_column=tuple_column, dict_column=dict_column)
            effect_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
    edit_file.close()
    animation_pool_data, part_name_header = read_anim_data(animation_dir, anim_column_header)
    for key, data in animation_pool_data.items():
        for animation_name, animation_frames in data.items():
            for frame_index, frame in enumerate(animation_frames):
                for part, part_data in frame.items():
                    if "effect_" in part and part_data and part_data[-1]:
                        if part_data[0] not in effect_list:
                            print(key, animation_name, frame_index, part, part_data)

effect_check()
