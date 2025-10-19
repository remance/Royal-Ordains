import csv
import os
import re
from pathlib import Path

from PIL import Image
from pygame import image
from pygame.mixer import Sound
from pygame.transform import smoothscale, flip

from engine.utils.sprite_altering import sprite_rotate

accept_image_types = ("png", "jpg", "jpeg", "svg", "gif", "bmp")


def load_image(directory, screen_scale, file, subfolder="", no_alpha=False, as_pillow_image=False):
    """
    loads an image and prepares it for game
    :param directory: Directory folder path
    :param screen_scale: Resolution scale of game
    :param file: File name
    :param subfolder: List of sub1_folder path
    :param no_alpha: Indicate if surface require alpha or not
    :param as_pillow_image: return surface as Pillow image instead of pygame surface
    :return: Pygame.Surface
    """
    new_subfolder = subfolder
    if isinstance(new_subfolder, list) or isinstance(new_subfolder, tuple):
        new_subfolder = ""
        for folder in subfolder:
            new_subfolder = os.path.join(new_subfolder, folder)
    this_file = os.path.join(directory, new_subfolder, file)
    if not no_alpha:
        surface = image.load(this_file).convert_alpha()
    else:
        surface = image.load(this_file).convert()
    if screen_scale[0] != 1 and screen_scale[1] != 1:  # scale to screen scale
        surface = smoothscale(surface, (surface.get_width() * screen_scale[0],
                                        surface.get_height() * screen_scale[1]))
    if as_pillow_image:
        size = surface.get_size()
        data = image.tobytes(surface, "RGBA")  # convert image to string data for filtering effect
        surface = Image.frombytes("RGBA", size, data)  # use PIL to get image data

    return surface


def load_images(directory, screen_scale=(1, 1), subfolder=(), key_file_name_readable=False, no_alpha=False,
                as_pillow_image=False):
    """
    loads all images(only png files) in folder
    :param directory: Directory folder path
    :param screen_scale: Resolution scale of game
    :param subfolder: List of sub1_folder path
    :param key_file_name_readable: Convert key name from file name into data readable
    :param no_alpha: Indicate if all loaded surfaces require alpha or not
    :param as_pillow_image: return surfaces as Pillow image instead of pygame surface
    :return: Dict of loaded and scaled images as Pygame Surface
    """
    images = {}
    dir_path = directory
    for folder in subfolder:
        dir_path = os.path.join(dir_path, folder)

    try:
        load_order_file = [f for f in os.listdir(dir_path) if
                           any(f.endswith(item) for item in accept_image_types)]  # read all image file
        try:  # sort file name if all in number only
            load_order_file.sort(
                key=lambda var: [int(x) if x.lstrip("-").isdigit() else x for x in re.findall(r"[^0-9]|[0-9]+", var)])
        except TypeError:  # has character in file name
            pass
        for file in load_order_file:
            file_name = file
            if "." in file_name:  # remove extension from name
                file_name = file.split(".")[:-1]
                file_name = "".join(file_name)
            if key_file_name_readable:
                file_name = filename_convert_readable(file_name)
            images[file_name] = load_image(directory, screen_scale, file, subfolder=dir_path, no_alpha=no_alpha,
                                           as_pillow_image=as_pillow_image)

        return images

    except FileNotFoundError as b:
        print(b)
        return images


def recursive_image_load(save_dict, screen_scale, part_folder, key_file_name_readable=True,
                         part_sprite_adjust=None):
    next_level = save_dict
    sub_directories = [os.path.split(os.sep.join(os.path.normpath(x).split(os.sep)[-1:]))[-1] for x
                       in part_folder.iterdir() if x.is_dir()]
    if sub_directories:
        for folder in sub_directories:
            folder_name = filename_convert_readable(folder)
            next_level[folder_name] = {}
            part_subfolder = Path(os.path.join(part_folder, folder))
            recursive_image_load(next_level[folder_name], screen_scale, part_subfolder,
                                 key_file_name_readable=key_file_name_readable, part_sprite_adjust=part_sprite_adjust)

    else:
        imgs = load_images(part_folder, screen_scale=screen_scale,
                           key_file_name_readable=key_file_name_readable)
        if part_sprite_adjust:
            part_type = os.path.normpath(part_folder).split(os.sep)[-4]
            part_name = os.path.normpath(part_folder).split(os.sep)[-3]

            if part_type != "weapon":
                part_type = filename_convert_readable(part_type)
            else:
                part_name = filename_convert_readable(part_name)
            for key, value in imgs.items():
                if part_type in part_sprite_adjust:
                    if part_name in part_sprite_adjust[part_type]:
                        if key in part_sprite_adjust[part_type][part_name]:
                            imgs[key] = {}
                            for flip_value in part_sprite_adjust[part_type][part_name][key]:
                                imgs[key][flip_value] = {}
                                flip_image = value
                                if flip_value:
                                    flip_image = flip(flip_image, True, False)
                                for scale in part_sprite_adjust[part_type][part_name][key][flip_value]:
                                    imgs[key][flip_value][scale] = {}
                                    scale_image = flip_image
                                    if scale != 1:
                                        scale_image = smoothscale(scale_image, (scale_image.get_width() * scale,
                                                                                scale_image.get_height() * scale))
                                    for angle in part_sprite_adjust[part_type][part_name][key][flip_value][scale]:
                                        imgs[key][flip_value][scale][angle] = scale_image
                                        if angle:
                                            imgs[key][flip_value][scale][angle] = sprite_rotate(scale_image, angle)
        save_dict |= imgs


def filename_convert_readable(filename: str, revert=False) -> str:
    if revert:
        new_filename = filename.replace(" ", "-").lower()  # replace space with - and make name lowercase
    else:
        if "-" in filename or " " in filename:
            new_filename = filename.replace(" ", "-").split("-")
        else:
            new_filename = [filename]

        for index, item in enumerate(new_filename):
            new_filename[index] = item.capitalize()  # capitalise each word divided by -

        new_filename = " ".join(new_filename)  # replace - with space

    return new_filename


def csv_read(main_dir, file, subfolder=(), output_type="dict", header_key=False, dict_value_return_as_str=None):
    """
    Read csv file
    :param main_dir: Game directory folder path
    :param file: File name
    :param subfolder: Array of sub1_folder path
    :param output_type: Type of returned object, either dict or list
    :param header_key: Use header as dict key or not
    :param dict_value_return_as_str: Returned dict value is stored as string instead of list
    :return:
    """
    return_output = {}
    if output_type == "list":
        return_output = []

    folder_dir = ""
    for folder in subfolder:
        folder_dir = os.path.join(folder_dir, folder)
    folder_dir = os.path.join(folder_dir, file)
    folder_dir = os.path.join(main_dir, folder_dir)
    try:
        with open(folder_dir, encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            for row_index, row in enumerate(rd):
                for n, i in enumerate(row):
                    if i.lstrip("-").isdigit():
                        row[n] = int(i)
                    elif re.search("[a-zA-Z]", i) is None and "." in i and "," not in i:
                        row[n] = float(i)
                if output_type == "dict":  # return as dict
                    if header_key:
                        if row_index > 0:  # skip header row
                            return_output[row[0]] = {header[index + 1]: item for index, item in enumerate(row[1:])}
                    else:
                        if dict_value_return_as_str:
                            return_output[row[0]] = ",".join(row[1:])
                        else:
                            return_output[row[0]] = row[1:]
                elif output_type == "list":  # return as list
                    return_output.append(row)
            edit_file.close()
    except FileNotFoundError as b:
        print(b)
    return return_output


def lore_csv_read(edit_file, input_dict):
    rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
    rd = [row for row in rd]
    for index, row in enumerate(rd[1:]):
        for n, i in enumerate(row):
            if i.lstrip("-").isdigit():
                row[n] = int(i)
        input_dict[row[0]] = [stuff for index, stuff in enumerate(row[1:])]
        while len(input_dict[row[0]]) > 2 and input_dict[row[0]][-1] == "":  # keep remove last empty text
            input_dict[row[0]] = input_dict[row[0]][:-1]
        input_dict[row[0]] = {rd[0][index + 1]: value for index, value in enumerate(input_dict[row[0]])}


def load_sound(main_dir, file):
    """
    Load sound file
    :param main_dir: Game directory folder path
    :param file: File name
    :return: Pygame Sound
    """
    file = os.path.join(main_dir, "data", "sound", file)
    sound = Sound(file)
    return sound


def load_base_button(data_dir, screen_scale):
    return (load_image(data_dir, screen_scale, "idle_button.png", ("ui", "mainmenu_ui")),
            load_image(data_dir, screen_scale, "mouse_button.png", ("ui", "mainmenu_ui")),
            load_image(data_dir, screen_scale, "click_button.png", ("ui", "mainmenu_ui")))


def stat_convert(row, n, i, percent_column=(), list_column=(), tuple_column=(), int_column=(),
                 float_column=(), dict_column=(), str_column=()):
    """
    Convert string value to another type
    :param row: row that contains value
    :param n: index of value
    :param i: value
    :param percent_column: list of value header that should be in percentage as decimal value
    :param list_column: list of value header that should be in list type, in case it needs to be modified later
    :param tuple_column: list of value header that should be in tuple type, for value that is static
    :param int_column: list of value header that should be in int number type
    :param float_column: list of value header that should be in float number type
    :param dict_column: list of value header that should be in dict type
    :param str_column: list of value header that should be in str type
    :return: converted row
    """
    if n in percent_column:
        if not i:
            row[n] = 1
        else:
            row[n] = float(i) + 1

    elif n in list_column or n in tuple_column:
        if "," not in i:  # single item
            if i == "":
                row[n] = []
            else:
                row[n] = [i, ]
        else:
            row[n] = [item for item in i.split(",")]
        row[n] = [item_conversion(k) for k in row[n]]
        if n in tuple_column:
            row[n] = tuple(row[n])

    elif n in int_column:
        if i:
            row[n] = int(i)
        else:
            row[n] = 0

    elif n in float_column:
        if i:
            row[n] = float(i)
        else:
            row[n] = 0

    elif n in dict_column:
        # dict column value can be in key:value format or just key, if contains only key it will be assigned TRUE value
        # if it has / and character after the value after / will be the item value
        row[n] = {}
        if i:
            new_i = i.split(",")
            result_i = {}
            for item in new_i:
                if ":" in item:
                    new_i2 = item.split(":")
                    result_i[new_i2[0]] = new_i2[1]
                    if "(" in new_i2[1]:  # tuple value
                        new_i2[1] = new_i2[1].split("(")
                        new_i2[1] = [item.replace(")", "") for item in new_i2[1] if item]
                        new_i2[1] = [item.strip(";").split(";") for item in new_i2[1]]
                        for k_index, k in enumerate(new_i2[1]):
                            new_i2[1][k_index] = tuple([item_conversion(item2) for item2 in k])
                        result_i[new_i2[0]] = tuple(tuple(new_i2[1]))
                    elif "{" in new_i2[1]:  # dict value with key=value instead of key:value
                        new_i2[1] = new_i2[1].replace("{", "").replace("}", "")
                        item_list = tuple([item_conversion(item2) for item2 in new_i2[1].split(";")])
                        result_i[new_i2[0]] = {
                            i3.split("=")[0]: item_conversion(i3.split("=")[1]) if "=" in i3 else True for i3 in
                            item_list}
                    else:
                        result_i[new_i2[0]] = item_conversion(result_i[new_i2[0]])
                else:
                    if "/" not in item:
                        result_i[item] = True
                    else:
                        value = item.split("/")[1]
                        if value.isdigit():
                            value = int(value)
                        elif "." in value and re.search("[a-zA-Z]", i) is None:
                            value = float(value)
                        result_i[item.split("/")[0]] = value
            row[n] = result_i

    elif n in str_column:
        row[n] = str(i)

    else:
        row[n] = item_conversion(i)

    return row


def item_conversion(i):
    if type(i) is str:
        if i == "":
            return 0
        elif i[0] == "(" and i[-1] == ")":
            i = i[1:-1]
            i = i.split(";")  # item with item1;item2 instead of ","
            for index_c, c in enumerate(i):
                i[index_c] = item_conversion(c)
            return i
        elif i.lower() == "none":
            return None
        elif i.lower() == "true":
            return True
        elif i.lower() == "false":
            return False
        elif ("." in i and re.search("[a-zA-Z]", i) is None) or i == "inf":
            return float(i)
        elif "," in i:
            return tuple([item_conversion(k) for k in i.split(",")])
        elif i.isdigit() or i.lstrip("-").isdigit():
            return int(i)
        else:
            return i
    elif type(i) is tuple or type(i) is list:  # tuple/list item
        i = [item.strip(";").split(";") for item in i]  # item with item1;item2 instead of ","
        for index_c, c in enumerate(i):
            i[index_c] = item_conversion(c)
        return i
    else:
        return i
