from os import sep
from os.path import join, split, normpath
from pathlib import Path

from engine.utils.data_loading import load_images, filename_convert_readable as fcv
from engine.utils.sprite_caching import save_pickle_with_surfaces


def compile_out_data(data_dir, animation_dir):
    stage_object_animation_pool = {}
    world_object_animation_pool = {}

    # print("stage object")
    # part_folder = Path(join(animation_dir, "sprite", "object"))
    # subdirectories = [split(
    #     sep.join(normpath(x).split(sep)[normpath(x).split(sep).index("animation"):])) for x
    #     in part_folder.iterdir() if x.is_dir()]
    # for folder in subdirectories:
    #     folder_data_name = fcv(folder[-1])
    #     if folder_data_name not in stage_object_animation_pool:
    #         stage_object_animation_pool[folder_data_name] = {}
    #         images = load_images(part_folder, subfolder=(folder[-1],), key_file_name_readable=True)
    #         stage_object_animation_pool[folder_data_name] = \
    #             {int(key): value for key, value in images.items()}

    # save_pickle_with_surfaces(join(data_dir, "animation", "stage_object.xz"), stage_object_animation_pool)

    print("world object")
    part_folder = Path(join(animation_dir, "sprite", "world"))
    subdirectories = [split(
        sep.join(normpath(x).split(sep)[normpath(x).split(sep).index("animation"):])) for x
        in part_folder.iterdir() if x.is_dir()]
    for folder in subdirectories:
        folder_data_name = fcv(folder[-1])
        if folder_data_name not in world_object_animation_pool:
            world_object_animation_pool[folder_data_name] = {}
            images = load_images(part_folder, subfolder=(folder[-1],), key_file_name_readable=True)

            true_name_list = []
            for key, value in images.items():
                if key.split("_")[-1].isdigit():
                    true_name = " ".join([string for string in key.split("_")[:-1]]) + "#"
                else:
                    true_name = key
                if true_name not in true_name_list:
                    true_name_list.append(true_name)

            for true_name in set(true_name_list):  # create animation list
                final_name = true_name
                if "#" in true_name:  # has animation to play
                    final_name = true_name[:-1]
                    sprite_animation_list = [value for key, value in images.items() if final_name ==
                                             " ".join([string for string in key.split("_")[:-1]])]
                else:  # single frame animation
                    sprite_animation_list = [value for key, value in images.items() if
                                             final_name == key]

                world_object_animation_pool[folder_data_name][final_name] = sprite_animation_list

    save_pickle_with_surfaces(join(data_dir, "animation", "world_object.xz"), world_object_animation_pool)
    print(world_object_animation_pool)

# import pygame
# current_dir = Path.cwd().parents[0]
# main_dir = current_dir.parents[0]
# data_dir = join(main_dir, "data")
# animation_dir = join(current_dir, "data", "animation")
# pygame.init()
# pen = pygame.display.set_mode((1, 1))
# compile_out_data(data_dir, animation_dir)
# print(main_dir, current_dir)
