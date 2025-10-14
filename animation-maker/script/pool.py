import csv
import os
from pathlib import Path

from engine.data.datastat import stat_convert
from engine.utils.data_loading import filename_convert_readable


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


def anim_save_pool(main_dir, pool, race_name, anim_column_header):
    """Save animation pool data"""
    with open(os.path.join(main_dir, "data", "animation", filename_convert_readable(race_name, revert=True) + ".csv"),
              mode="w",
              encoding='utf-8', newline="") as edit_file:
        filewriter = csv.writer(edit_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        save_list = pool
        final_save = [[item for item in anim_column_header]]
        for item in list(save_list.items()):
            for frame_num, frame in enumerate(item[1]):
                subitem = [tiny_item for tiny_item in list(frame.values())]
                for item_index, min_item in enumerate(subitem):
                    if type(min_item) == list:
                        min_item = [this_item if type(this_item) != float else round(this_item, 1) for this_item in
                                    min_item]
                        min_item = [int(this_item) if type(this_item) == float and int(this_item) == this_item else
                                    this_item for this_item in min_item]
                        new_item = str(min_item)
                        for character in "'[]":
                            new_item = new_item.replace(character, "")
                        new_item = new_item.replace(", ", ",")
                        subitem[item_index] = new_item
                new_item = [item[0] + "/" + str(frame_num)] + subitem
                final_save.append(new_item)
        for row in final_save:
            filewriter.writerow(row)
        edit_file.close()


def anim_del_pool(pool, animation_name):
    """Delete animation from animation pool data"""
    if animation_name in pool:
        del pool[animation_name]
