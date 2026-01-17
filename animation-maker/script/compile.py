from os.path import join

import pygame
from PIL import Image
from pygame import Surface, SRCALPHA, Vector2
from pygame.image import tobytes
from pygame.transform import smoothscale, flip
from script.compile_out import compile_out_data

from engine.utils.data_loading import filename_convert_readable as fcv
from engine.utils.sprite_altering import sprite_rotate, apply_sprite_effect
from engine.utils.sprite_caching import save_pickle_with_surfaces, CompilableSurface, load_pickle_with_surfaces


def crop_sprite(sprite_pic):
    low_x0 = float("inf")  # lowest x0
    low_y0 = float("inf")  # lowest y0
    high_x1 = 0  # highest x1
    high_y1 = 0  # highest y1

    # Find optimal cropped sprite size
    size = sprite_pic.get_size()
    data = tobytes(sprite_pic, "RGBA")  # convert image to string data for filtering effect
    data2 = Image.frombytes("RGBA", size, data)  # use PIL to get image data
    data2 = data2.convert("P")
    bbox = data2.getbbox()
    if bbox:
        if low_x0 > bbox[0]:
            low_x0 = bbox[0]
        if low_y0 > bbox[1]:
            low_y0 = bbox[1]
        if high_x1 < bbox[2]:
            high_x1 = bbox[2]
        if high_y1 < bbox[3]:
            high_y1 = bbox[3]

        # Crop transparent area only of surface
        data2 = data2.crop((low_x0, low_y0, high_x1, high_y1))

        # Find offset after crop
        center_x_offset = ((low_x0 + high_x1) / 2)

        crop_offset = ((data2.size[0] / 2) - center_x_offset, data2.size[1] - high_y1)
    else:
        crop_offset = (0, 0)

    return data2, crop_offset


def compile_data(animation_dir, data_dir, animation_pool, default_body_sprite_pool, effect_animation_pool,
                 compile_specific=None):
    part_sprite_adjust = {}
    effect_sprite_adjust = {}
    # world_actor_animation_pool = {}
    #
    # try:
    #     world_actor_animation_pool = load_pickle_with_surfaces(join(data_dir, "animation", "world_actor.xz"),
    #                                                            (1, 1))
    # except Exception:
    #     pass

    for character in animation_pool:
        if not compile_specific or character == compile_specific:
            print(character)
            character_animation_pool = {}
            # if character not in world_actor_animation_pool:  # create for grand world actor
            #     world_actor_animation_pool[character] = {}

            for animation_name, animation_frame in animation_pool[character].items():
                if "EXCLUDE_" not in animation_name:
                    character_animation_pool[animation_name] = {"max frame": len(animation_frame) - 1}
                    for frame_index, animation_data in enumerate(animation_frame):
                        character_animation_pool[animation_name][frame_index] = {"right": {}, "left": {},
                                                                                 "property": (), "sound_effect": None}
                        frame_data = character_animation_pool[animation_name][frame_index]
                        prop_list = animation_data["animation_property"] + animation_data["frame_property"]
                        for item2 in prop_list:
                            if "play_time_mod" in item2:
                                frame_data["play_time_mod"] = float(item2.split("_")[-1])
                        frame_data["property"] = tuple(
                            set([item for item in prop_list if "play_time_mod" not in prop_list]))

                        if animation_data["sound_effect"]:
                            frame_data["sound_effect"] = tuple(animation_data["sound_effect"])

                        frame_data_r = {"sprite": None, "offset": (), "effects": {}, "head": None}
                        frame_data_l = {"sprite": None, "offset": (), "effects": {}, "head": None}
                        if len(animation_data["p1_head"]) > 5:
                            frame_data_r["head"] = (animation_data["p1_head"][2], animation_data["p1_head"][3])
                            frame_data_l["head"] = (-animation_data["p1_head"][2], animation_data["p1_head"][3])

                        frame_data_list = {"right": frame_data_r, "left": frame_data_l}
                        character_animation_pool[animation_name][frame_index]["right"] = frame_data_r
                        character_animation_pool[animation_name][frame_index]["left"] = frame_data_l

                        min_x = float("infinity")
                        max_x = -float("infinity")
                        min_y = float("infinity")
                        max_y = -float("infinity")
                        # get angle, scale, flip
                        animation_data_str = str(
                            {key: value for key, value in animation_data.items() if
                             ("effect" not in key or
                              (len(value) > 5 and not value[9])) and "propoerty" not in key})
                        if animation_data_str in part_sprite_adjust:
                            # sprite from exact same frame data already made. ref that one instead
                            frame_data_list["right"]["sprite"] = part_sprite_adjust[animation_data_str]["sprite"]
                            frame_data_list["right"]["offset"] = part_sprite_adjust[animation_data_str]["offset"]
                            frame_data_list["left"]["offset"] = Vector2(
                                - part_sprite_adjust[animation_data_str]["offset"][0],
                                part_sprite_adjust[animation_data_str]["offset"][1])
                        else:
                            for part_header, part in animation_data.items():
                                if len(part) > 5:
                                    part_name = part_header

                                    if "effect" in part_name:
                                        part_name = part[0]
                                        part_type = "effect"
                                        part_sprite = effect_animation_pool[part_name][part[1]][0]
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
                                        part_sprite = default_body_sprite_pool[part_type][part_name][part[1]]

                                    if part_type not in part_sprite_adjust:
                                        part_sprite_adjust[part_type] = {}

                                    if part_name not in part_sprite_adjust[
                                        part_type]:
                                        part_sprite_adjust[part_type][
                                            part_name] = {}
                                    if part[1] not in \
                                            part_sprite_adjust[part_type][
                                                part_name]:
                                        part_sprite_adjust[part_type][part_name][
                                            part[1]] = {}
                                    if part[5] not in \
                                            part_sprite_adjust[part_type][
                                                part_name][
                                                part[1]]:  # flip
                                        save = part_sprite
                                        if part[5]:
                                            save = flip(part_sprite, True, False)
                                        part_sprite_adjust[part_type][part_name][
                                            part[1]][
                                            part[5]] = {"save": save}
                                    if part[7] not in \
                                            part_sprite_adjust[part_type][
                                                part_name][
                                                part[1]][part[5]]:  # width scale
                                        part_sprite_adjust[part_type][part_name][
                                            part[1]][
                                            part[5]][part[7]] = {}
                                    if part[8] not in \
                                            part_sprite_adjust[part_type][
                                                part_name][
                                                part[1]][part[5]][part[7]]:  # height scale
                                        save = part_sprite_adjust[part_type][part_name][part[1]][part[5]]["save"]
                                        if part[7] != 1 or part[8] != 1:
                                            save = smoothscale(save, (save.get_width() * part[7],
                                                                      save.get_height() * part[8]))
                                        part_sprite_adjust[part_type][part_name][
                                            part[1]][
                                            part[5]][part[7]][part[8]] = {"save": save}
                                    if part[4] not in \
                                            part_sprite_adjust[part_type][
                                                part_name][
                                                part[1]][part[5]][part[7]][part[8]]:  # angle
                                        part_sprite_adjust[part_type][part_name][part[1]][part[5]][part[7]][
                                            part[8]][part[4]] = (
                                            sprite_rotate(
                                                part_sprite_adjust[part_type][part_name][part[1]][part[5]][part[7]][
                                                    part[8]]["save"], part[4]))
                                    image = \
                                        part_sprite_adjust[part_type][part_name][part[1]][part[5]][part[7]][part[8]][
                                            part[4]]
                                    width_check = image.get_width()
                                    height_check = image.get_height()
                                    if part[2] - width_check < min_x:
                                        min_x = part[2] - width_check
                                    if part[2] + width_check > max_x:
                                        max_x = part[2] + width_check
                                    if part[3] - height_check < min_y:
                                        min_y = part[3] - height_check  # most top y pos
                                    if part[3] + height_check > max_y:
                                        max_y = part[3] + height_check  # lowest bottom y pos

                                    # save effect and template part data for rect check or object related functions
                                    if "effect" in part_type and part[9]:  # independent effect
                                        if part[0] not in effect_sprite_adjust:
                                            effect_sprite_adjust[part[0]] = {}
                                        adjust_now_at = effect_sprite_adjust[part[0]]

                                        if part[5] not in adjust_now_at:
                                            adjust_now_at[part[5]] = {}
                                        adjust_now_at = adjust_now_at[part[5]]

                                        if part[7] not in adjust_now_at:
                                            adjust_now_at[part[7]] = []
                                        adjust_now_at[part[7]].append(part[8])

                                        frame_data_list["right"]["effects"][part_header] = \
                                            (part[0], part[1], part[2], part[3], part[4], part[5],
                                             part[6], part[7], part[8], part[9])

                            image = Surface((abs(min_x) + abs(max_x), abs(min_y) + abs(max_y)), SRCALPHA)
                            pose_layer_list = {k: v[6] for k, v in animation_data.items() if v and len(v) > 5 and
                                               ("effect" not in k or not v[9]) and "Template" not in v[1]}
                            if prop_list:
                                for frame_property in prop_list:
                                    if "exclude_" in frame_property:
                                        exclude = frame_property.split("_")[1] + "_"
                                        pose_layer_list = {k: v for k, v in pose_layer_list.items() if exclude not in k}
                            pose_layer_list = dict(
                                sorted(pose_layer_list.items(), key=lambda item: item[1], reverse=True))
                            base_point = (image.get_width() / 2 - ((min_x + max_x) / 2), image.get_height() - max_y)

                            for index, layer in enumerate(pose_layer_list):
                                part = animation_data[layer]
                                if part is not None and part[0] is not None:
                                    # surface, part_image, part_name, target, angle, flip, scale,
                                    part_name = layer

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
                                    part_sprite = \
                                        part_sprite_adjust[part_type][part_name][part[1]][part[5]][part[7]][part[8]][
                                            part[4]]
                                    new_target = (part[2] + base_point[0], part[3] + base_point[1])
                                    rect = part_sprite.get_rect(center=new_target)
                                    image.blit(part_sprite, rect)
                            image = apply_sprite_effect(image, prop_list)
                            image, crop_offset = crop_sprite(image)
                            image_array = image.tobytes()
                            if image_array in part_sprite_adjust:
                                # exact sprite already exist, reuse that one instead to reduce memory
                                frame_data_list["right"]["sprite"] = \
                                    part_sprite_adjust[image_array]["sprite"]
                                frame_data_list["right"]["offset"] = \
                                    part_sprite_adjust[image_array]["offset"]
                            else:
                                # Completely new sprite
                                frame_data_list["right"]["sprite"] = CompilableSurface(image)
                                frame_data_list["right"]["offset"] = Vector2(
                                    base_point[0] - (image.size[0] / 2) + crop_offset[0],
                                    base_point[1] - image.size[1] + crop_offset[1])

                                part_sprite_adjust[animation_data_str] = {"sprite": frame_data_list["right"]["sprite"],
                                                                          "offset": frame_data_list["right"]["offset"]}
                                part_sprite_adjust[image_array] = part_sprite_adjust[animation_data_str]
                            frame_data_list["left"]["offset"] = Vector2(-frame_data_list["right"]["offset"][0],
                                                                        frame_data_list["right"]["offset"][1])
                            for stuff2 in frame_data_list["right"]["effects"]:
                                frame_data_list["left"]["effects"][stuff2] = [-item if index in (2, 4) else item for
                                                                              index, item in enumerate(
                                        frame_data_list["right"]["effects"][stuff2])]

                    # if animation_name in ("Idle", "Walk", "Die"):
                    #     world_actor_animation_pool[character][animation_name] = []
                    #     already_done_check_actor_anim = {}
                    #     for frame, frame_value in character_animation_pool[animation_name].items():
                    #         if frame != "max frame":
                    #             image = frame_value["right"]["sprite"].surface
                    #             image_array = image.tobytes()
                    #             if image_array in already_done_check_actor_anim:
                    #                 world_actor_animation_pool[character][animation_name].append(already_done_check_actor_anim[image_array])
                    #             else:
                    #                 to_add = {0.2: {}, 0.4: {}}
                    #                 for scale_value in to_add:
                    #                     offset = (frame_value["right"]["offset"][0] * scale_value,
                    #                               frame_value["right"]["offset"][1] * scale_value)
                    #                     to_add[scale_value] = {
                    #                         "right": {"sprite": CompilableSurface(image.resize((int(image.size[0] * scale_value),
                    #                                                                             int(image.size[1] * scale_value)))),
                    #                                   "offset": offset},
                    #                         "left": {"sprite": None, "offset": offset}}
                    #                 world_actor_animation_pool[character][animation_name].append(to_add)
                    #                 already_done_check_actor_anim[image_array] = to_add

            # for key, value in character_animation_pool.items():
            #     print(key, value)
            save_pickle_with_surfaces(join(data_dir, "animation", fcv(character, revert=True) +
                                           ".xz"), character_animation_pool)
            # save_pickle_with_surfaces(join(data_dir, "animation", "world_actor.xz"), world_actor_animation_pool)

    if not compile_specific:
        compile_out_data(data_dir, animation_dir)

    print("effect")
    effect_animation_pool_save = {}
    if compile_specific:
        try:
            effect_animation_pool_save = load_pickle_with_surfaces(join(data_dir, "animation", "effect_animation.xz"),
                                                                   (1, 1))
        except Exception:
            pass

    for effect_type, data in effect_animation_pool.items():
        if effect_type not in effect_animation_pool_save:
            effect_animation_pool_save[effect_type] = {}
        for effect_name, frame_list in data.items():
            if effect_name not in effect_animation_pool_save[effect_type]:
                effect_animation_pool_save[effect_type][effect_name] = {0: {1: {1: {
                    frame_index: {"sprite": surface} for frame_index, surface in enumerate(frame_list)}}}}
            if effect_type in effect_sprite_adjust:
                for flip_value in effect_sprite_adjust[effect_type]:
                    if flip_value not in effect_animation_pool_save[effect_type][effect_name]:
                        effect_animation_pool_save[effect_type][effect_name][flip_value] = {}
                    for width_scale in effect_sprite_adjust[effect_type][flip_value]:
                        if width_scale not in effect_animation_pool_save[effect_type][effect_name][flip_value]:
                            effect_animation_pool_save[effect_type][effect_name][flip_value][width_scale] = {}
                        for height_scale in effect_sprite_adjust[effect_type][flip_value][width_scale]:
                            if height_scale not in effect_animation_pool_save[effect_type][effect_name][flip_value][
                                width_scale]:
                                effect_animation_pool_save[effect_type][effect_name][flip_value][width_scale][
                                    height_scale] = {}
                            for frame_index, frame in enumerate(frame_list):
                                effect_animation_pool_save[effect_type][effect_name][flip_value][width_scale][
                                    height_scale][frame_index] = {
                                    "sprite": adjust_effect_sprite(frame_list[frame_index],
                                                                   flip_value, width_scale,
                                                                   height_scale)}
    recursive_remove_mask(effect_animation_pool_save)
    save_pickle_with_surfaces(join(data_dir, "animation", "effect_animation.xz"), effect_animation_pool_save)

    print("done")


def adjust_effect_sprite(surface, sprite_flip, width_scale, height_scale):
    if sprite_flip:
        surface = flip(surface, True, False)
    if height_scale != 1 or width_scale != 1:
        surface = smoothscale(surface, (int(surface.get_width() * width_scale),
                                        int(surface.get_height() * height_scale)))
    return surface


def recursive_remove_mask(value_item):
    """Remove mask from dict for caching"""
    for key in tuple(value_item.keys()):
        if type(value_item[key]) is dict:
            recursive_remove_mask(value_item[key])
        elif type(value_item[key]) is pygame.Mask:
            value_item.pop(key)
