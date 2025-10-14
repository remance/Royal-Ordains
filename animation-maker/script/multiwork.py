import csv
import os
import sys
from os.path import join, split, normpath, abspath
from pathlib import Path

import pool

current_dir = split(abspath(__file__))[0]
main_dir = current_dir[:current_dir.rfind("\\") + 1].split("\\")
main_dir = ''.join(stuff + "\\" for stuff in main_dir[:-2])  # one folder further back
sys.path.insert(1, main_dir)

data_dir = join(main_dir, "data")
animation_dir = join(main_dir, "animation-maker", "data", "animation")

read_anim_data = pool.read_anim_data

pool = []
file_list = []

for x in Path(join(animation_dir)).iterdir():  # grab char with sprite
    if ".csv" in normpath(x).split(os.sep)[-1]:
        file_list.append(normpath(x).split(os.sep)[-1])

# for file_name in file_list:
file_name = "nice_bear_cub.csv"
with open(join(main_dir, "animation-maker", "data", "animation", file_name), encoding="utf-8",
          mode="r") as edit_file:
    rd = csv.reader(edit_file, quoting=csv.QUOTE_MINIMAL)
    rd = [row for row in rd]
    part_name_header = rd[0]
    final_save = []
    for row_index, row in enumerate(rd):
        if row_index > 0:
            key = row[0]
            for col_index, column in enumerate(row):
                if len(column.split(",")) > 4 and "sound" not in part_name_header[col_index] and column:
                    new_column = column.split(",")
                    # if float(new_column[2]) > 180:
                    new_column[2] = str(round(float(new_column[2]) * 0.5, 1))
                    # if float(new_column[3]) < -180:
                    new_column[3] = str(round(float(new_column[3]) * 0.5, 1))
                    new_column = ",".join(new_column)
                    row[col_index] = new_column
        final_save.append(row)
    print(final_save)
edit_file.close()

with open(os.path.join(main_dir, "animation-maker", "data", "animation", file_name), mode="w",
          encoding='utf-8',
          newline="") as edit_file:
    filewriter = csv.writer(edit_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for row in final_save:
        filewriter.writerow(row)
    edit_file.close()


def frame_scale(rd, final_save, scale):
    """Scale all parts and move position accordingly"""
    for row_index, row in enumerate(rd):
        if row_index > 0:
            key = row[0]
            if "Small" in key:
                for col_index, column in enumerate(row):
                    if "p1" in part_name_header[col_index] and column:
                        new_column = column.split(",")
                        new_column[2] = str(round(float(new_column[2]) * scale, 1))
                        new_column[3] = str(round(float(new_column[3]) * scale, 1))
                        new_column[7] = str(scale)
                        new_column = ",".join(new_column)
                        row[col_index] = new_column
        final_save.append(row)


def frame_adjust(pool, pool_name, header, filter_list, part_anchor, exclude_filter_list=()):
    """Move every parts in animation pool of specific direction based on specific input part and desired new position"""
    for key, value in pool.items():
        match = False
        for this_filter in filter_list:
            if this_filter in key:
                match = True
        for this_filter in exclude_filter_list:
            if this_filter in key:
                match = False
        if match:
            if type(value[part_anchor[0]]) == list and len(value[part_anchor[0]]) > 1:
                if "weapon" in part_anchor:
                    pos = (float(value[part_anchor[0]][2]), float(value[part_anchor[0]][3]))
                else:
                    pos = (float(value[part_anchor[0]][3]), float(value[part_anchor[0]][4]))
                offset = (part_anchor[1][0] - pos[0], part_anchor[1][1] - pos[1])
            for key2, value2 in value.items():
                if "property" not in key2 and type(value[key2]) == list and len(value[key2]) > 1:
                    if "weapon" in key2:
                        pool[key][key2][2] = str(float(pool[key][key2][2]) + offset[0])
                        pool[key][key2][3] = str(float(pool[key][key2][3]) + offset[1])
                    else:
                        pool[key][key2][3] = str(float(pool[key][key2][3]) + offset[0])
                        pool[key][key2][4] = str(float(pool[key][key2][4]) + offset[1])

    for key in pool:
        for key2, value in pool[key].items():
            new_value = str(pool[key][key2])
            for character in "'[]":
                new_value = new_value.replace(character, "")
            new_value = new_value.replace(", ", ",")
            pool[key][key2] = new_value
    for key in pool:
        pool[key] = [value for value in pool[key].values()]
    save_list = pool
    final_save = [[item for item in header]]
    for item in list(save_list.items()):
        final_save.append([item[0]] + item[1])
    with open(os.path.join(main_dir, "data", "animation", pool_name, "side.csv"), mode="w",
              encoding='utf-8',
              newline="") as edit_file:
        filewriter = csv.writer(edit_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in final_save:
            filewriter.writerow(row)
        edit_file.close()

# frame_adjust(pool, "generic", part_name_header, ("Chariot", ), ("p4_body", (201.8, 222)), exclude_filter_list=("Die", ))
