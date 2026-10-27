import lzma
import pickle
from os.path import join
from PIL import Image

import pygame
from pygame import Surface, SRCALPHA, Vector2
from pygame.image import tobytes
from pygame.transform import smoothscale, flip
from hashlib import md5

from engine.utils.sprite_altering import sprite_rotate, apply_sprite_effect, crop_sprite
from engine.utils.sprite_caching import save_pickle_with_surfaces, load_pickle_with_surfaces, CompilableSurface


def compile_data(animation_dir, data_dir, animation_pool, default_body_sprite_pool, effect_animation_pool, character_list,
                 effect_list, strategy_list, compile_specific=None):
    part_sprite_adjust = {}
    effect_sprite_adjust = {}

    event_actor_sprite_pool = {}
    try:
        event_actor_sprite_pool = load_pickle_with_surfaces(join(data_dir, "animation", "event_actor.xz"),
                                                            (1, 1), add_mask=False)
    except Exception:
        pass

    animation_load_index = {"effect": {}, "character_load_index": {}}
    try:
        with lzma.open(join(data_dir, "animation", "animation_load_index.xz"), "rb") as read_file:
            animation_load_index = pickle.load(read_file)
        read_file.close()
    except Exception:
        pass

    for character in animation_pool:
        if not compile_specific or character == compile_specific:
            character_animation_pool = {}

            if character not in event_actor_sprite_pool:
                event_actor_sprite_pool[character] = {}
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
                        if "EVENT_" not in animation_name:
                            character_animation_pool[animation_name][frame_index]["right"] = frame_data_r
                            character_animation_pool[animation_name][frame_index]["left"] = frame_data_l
                        elif "EVENT_" in animation_name:  # save to event sprite data instead
                            event_animation_name = animation_name + str(frame_index)
                            if animation_name + str(frame_index) not in effect_sprite_adjust:
                                event_actor_sprite_pool[character][event_animation_name] = {}
                            event_actor_sprite_pool[character][event_animation_name]["right"] = frame_data_r
                            event_actor_sprite_pool[character][event_animation_name]["left"] = frame_data_l

                        min_x = float("infinity")
                        max_x = -float("infinity")
                        min_y = float("infinity")
                        max_y = -float("infinity")
                        # get angle, scale, flip
                        animation_data_str = str(
                            {key: value for key, value in animation_data.items() if
                             ("effect" not in key or
                              (len(value) > 5 and not value[9])) and (
                                     "property" not in key or not any(
                                 [prop for prop in value if "effect_" in prop or "exclude_" in prop]))})
                        if animation_data_str in part_sprite_adjust:
                            # sprite with the exact same data already made. ref that one instead
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
                                # exact sprite already exist, reuse that one instead to reduce memory/storage
                                frame_data_list["right"]["sprite"] = \
                                    part_sprite_adjust[image_array]["sprite"]
                                frame_data_list["right"]["offset"] = Vector2(
                                    base_point[0] + crop_offset[0],
                                    base_point[1] + crop_offset[1])
                            else:
                                # not the same as existing sprite
                                frame_data_list["right"]["sprite"] = CompilableSurface(image)
                                frame_data_list["right"]["offset"] = Vector2(
                                    base_point[0] + crop_offset[0],
                                    base_point[1] + crop_offset[1])

                            part_sprite_adjust[animation_data_str] = {"sprite": frame_data_list["right"]["sprite"],
                                                                      "offset": frame_data_list["right"]["offset"]}
                            part_sprite_adjust[image_array] = part_sprite_adjust[animation_data_str]

                            frame_data_list["left"]["offset"] = Vector2(-frame_data_list["right"]["offset"][0],
                                                                        frame_data_list["right"]["offset"][1])

                        # save ind effect part data for rect check or object related functions
                        for part_header, part in animation_data.items():  # add ind effect to data
                            if "effect" in part_header and len(part) > 5 and part[9] and "property" not in part_header:
                                add_ind_effect_adjust_sprite(effect_sprite_adjust, part)
                                frame_data_list["right"]["effects"][part_header] = \
                                    (part[0], part[1], part[2], part[3], part[4], part[5],
                                     part[6], part[7], part[8], part[9])
                                frame_data_list["left"]["effects"][part_header] = [
                                    -item if index in (2, 4) else item for index, item in enumerate(
                                        frame_data_list["right"]["effects"][part_header])]

                if "EVENT_" in animation_name or "DIPLOMACY_" in animation_name:
                    # remove EVENT and DIPLOMACY from battle animation pool save
                    character_animation_pool.pop(animation_name)

            save_pickle_with_surfaces(join(data_dir, "animation", character + ".xz"),
                                                       character_animation_pool)
            # animation_load_index[character] = character_hash

    save_pickle_with_surfaces(join(data_dir, "animation", "event_actor.xz"), event_actor_sprite_pool)

    for character in character_list:
        # create list of effect that must be loaded along with character
        animation_load_index["character_load_index"][character] = []

    # create effect sprite animation pool
    for character in animation_pool:  # recheck for independent effect
        for animation_name, animation_frame in animation_pool[character].items():
            if "EXCLUDE_" not in animation_name and "EVENT_" not in animation_name:
                for frame_index, animation_data in enumerate(animation_frame):
                    for part_header, part in animation_data.items():  # add ind effect to data
                        if "effect" in part_header and len(part) > 5 and part[
                            9] and "property" not in part_header:
                            add_ind_effect_adjust_sprite(effect_sprite_adjust, part)
                            if part[0] not in animation_load_index["character_load_index"][character]:
                                animation_load_index["character_load_index"][character].append(part[0])
                            if part[0] in effect_list and effect_list[part[0]]["After Reach Effect"]:
                                add_ind_effect_adjust_sprite(effect_sprite_adjust,
                                                             [effect_list[part[0]]["After Reach Effect"],
                                                              "base", 0, 0, 0, 0, 0, part[7], part[8]])
                                if effect_list[part[0]]["After Reach Effect"] not in animation_load_index["character_load_index"][character]:
                                    animation_load_index["character_load_index"][character].append(effect_list[part[0]]["After Reach Effect"])

    for strategy, strategy_data in strategy_list.items():
        # add from strategy with effects
        for effect_list in ("Effects", "Damage Effects"):
            for effect in strategy_data[effect_list]:
                add_ind_effect_adjust_sprite(effect_sprite_adjust, effect)
                for character, character_data in character_list.items():
                    if character_data["Strategy"] == strategy and effect not in animation_load_index["character_load_index"][character]:
                        animation_load_index["character_load_index"][character].append(effect[0])

    print("effect")
    for effect_name, data in effect_animation_pool.items():
        effect_animation_pool_save = {}
        effect_raw_data_hash = md5()
        if effect_name not in effect_animation_pool_save:
            effect_animation_pool_save[effect_name] = {}
        if effect_name in effect_sprite_adjust:
            effect_raw_data_hash.update(str(effect_sprite_adjust[effect_name]).encode())
        for effect_part, frame_list in data.items():
            for surface in frame_list:
                effect_raw_data_hash.update(image_avg_hashing(surface))
        effect_raw_data_hash = effect_raw_data_hash.hexdigest()
        if effect_name not in animation_load_index["effect"] or effect_raw_data_hash != animation_load_index["effect"][effect_name]:
            for effect_part, frame_list in data.items():
                if effect_part not in effect_animation_pool_save[effect_name]:
                    effect_animation_pool_save[effect_name][effect_part] = {0: {1: {1: {}}}}
                    for frame_index, surface in enumerate(frame_list):
                        image, crop_offset = crop_sprite(surface, character_offset=False)
                        effect_animation_pool_save[effect_name][effect_part][0][1][1][frame_index] = {
                            "sprite": {0: CompilableSurface(image)},
                            "offset": crop_offset}
                if effect_name in effect_sprite_adjust:
                    for flip_value in effect_sprite_adjust[effect_name]:
                        if flip_value not in effect_animation_pool_save[effect_name][effect_part]:
                            effect_animation_pool_save[effect_name][effect_part][flip_value] = {}
                        for width_scale in effect_sprite_adjust[effect_name][flip_value]:
                            if width_scale not in effect_animation_pool_save[effect_name][effect_part][flip_value]:
                                effect_animation_pool_save[effect_name][effect_part][flip_value][width_scale] = {}
                            for height_scale in effect_sprite_adjust[effect_name][flip_value][width_scale]:
                                if height_scale not in effect_animation_pool_save[effect_name][effect_part][flip_value][
                                    width_scale]:
                                    effect_animation_pool_save[effect_name][effect_part][flip_value][width_scale][
                                        height_scale] = {}
                                for frame_index, frame in enumerate(frame_list):
                                    image, crop_offset = crop_sprite(adjust_effect_sprite(frame_list[frame_index],
                                                                                          flip_value, width_scale,
                                                                                          height_scale),
                                                                     character_offset=False)

                                    effect_animation_pool_save[effect_name][effect_part][flip_value][width_scale][
                                        height_scale][frame_index] = {
                                        "sprite": {0: CompilableSurface(image)},
                                        "offset": crop_offset}
            recursive_remove_mask(effect_animation_pool_save)
            save_pickle_with_surfaces(join(data_dir, "animation", "effect", effect_name + ".xz"),
                                      effect_animation_pool_save)
            animation_load_index["effect"][effect_name] = effect_raw_data_hash

    with lzma.open(join(data_dir, "animation", "animation_load_index.xz"), "wb") as handle:
        pickle.dump(animation_load_index, handle)
    handle.close()
    print("done")


def add_ind_effect_adjust_sprite(effect_sprite_adjust, part):
    """Ignore angle for caching, only save flip and width/height scale"""
    if part[0] not in effect_sprite_adjust:
        effect_sprite_adjust[part[0]] = {}
    adjust_now_at = effect_sprite_adjust[part[0]]

    if part[5] not in adjust_now_at:
        adjust_now_at[part[5]] = {}
    adjust_now_at = adjust_now_at[part[5]]

    if part[7] not in adjust_now_at:
        adjust_now_at[part[7]] = []
    adjust_now_at[part[7]].append(part[8])


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


def image_avg_hashing(surface):
    data = tobytes(surface, "RGBA")
    size = surface.get_size()
    data2 = Image.frombytes("RGBA", size, data).resize((10, 10), Image.Resampling.LANCZOS).convert("L")
    pixel_data = list(data2.getdata())
    avg_pixel = sum(pixel_data) / len(pixel_data)
    bits = "".join(['1' if (px >= avg_pixel) else '0' for px in pixel_data])
    return (str(hex(int(bits, 2)))[2:][::-1].upper()).encode()
