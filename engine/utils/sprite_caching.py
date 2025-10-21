import lzma
import pickle

from pygame import Surface
from pygame.image import tobytes, frombuffer, save
from pygame.mask import from_surface
from pygame.transform import smoothscale, flip, rotate
from PIL import Image


class CompilableSurface:
    def __init__(self, surface):
        self.surface = surface
        self.type = type(self.surface)

    def __getstate__(self):
        if self.type is Surface:
            return tobytes(self.surface, "RGBA"), self.surface.get_size(), self.type
        return self.surface.tobytes(), self.surface.size, self.type, self.surface.getpalette(rawmode="RGBA")

    def __setstate__(self, state):
        if state[2] is Surface:
            self.surface = frombuffer(state[0], state[1], "RGBA").convert_alpha()
        else:
            data2 = Image.frombytes("P", state[1], state[0])  # use PIL to get image data
            data2.putpalette(state[3], rawmode="RGBA")
            data2 = data2.convert("RGBA")  # convert to RGBA first
            data2 = data2.tobytes()
            self.surface = frombuffer(data2, state[1], "RGBA").convert_alpha()


def surface_screen_scale(surface, screen_scale):
    """
    Scale surface with screen scale and usage
    @param surface: surface to scale
    @param screen_scale: scale based on screen resolution
    @return:
    """
    scale = (screen_scale[0], screen_scale[1])
    if scale[0] != 1 or scale[1] != 1:
        return smoothscale(surface, (surface.get_width() * scale[0],
                                     surface.get_height() * scale[1]))
    else:
        return surface


def recursive_dict_creation(data):
    f = recursive_dict_creation
    if type(data) is dict:
        for k, v in data.items():
            if type(v) is dict:
                data[k] = v.copy()
                f(v)


def save_pickle_with_surfaces(file_path, data):
    new_data = data
    if type(data) is dict:  # remake dict to not replace input data
        new_data = data.copy()
        recursive_dict_creation(new_data)

    recursive_cast_surface_to_pickleable_surface(new_data)
    with lzma.open(file_path, "wb") as handle:
        pickle.dump(new_data, handle)


def load_pickle_with_surfaces(file_path, screen_scale, battle_only=False, effect_sprite_adjust=False):
    with lzma.open(file_path, "rb") as handle:
        data = pickle.load(handle)
    if battle_only:
        data = {key: value for key, value in data.items() if key[0:4] != "City"}  # remove "City" animation for battle
    recursive_cast_pickleable_surface_to_surface(data, screen_scale, {}, battle_only, effect_sprite_adjust)
    return data


def recursive_cast_surface_to_pickleable_surface(data):
    f = recursive_cast_surface_to_pickleable_surface
    if data:
        if type(data) is dict:
            for k, v in data.items():
                if type(v) is dict:
                    f(v)
                elif type(v) is Surface:
                    data[k] = CompilableSurface(v)
                elif type(v) is tuple or type(v) is list:
                    data[k] = tuple([c if type(c) is not Surface else CompilableSurface(c) for c in data[k]])
        elif type(data) is tuple or type(data) is list:
            for v in data:
                f(v)


def recursive_cast_pickleable_surface_to_surface(data, screen_scale, already_done, battle_only=False,
                                                 effect_sprite_adjust=False, parent_data=None, parent_key=None):
    f = recursive_cast_pickleable_surface_to_surface
    if type(data) is dict:
        for k in tuple(data.keys()):
            v = data[k]
            if type(v) is dict:
                f(v, screen_scale, already_done, battle_only=battle_only, effect_sprite_adjust=effect_sprite_adjust,
                  parent_data=data, parent_key=k)
            elif type(v) is CompilableSurface:
                if v not in already_done:
                    data[k] = surface_screen_scale(v.surface, screen_scale)
                    if battle_only:
                        if k == "sprite":
                            if effect_sprite_adjust:
                                data["mask"] = {angle: from_surface(rotate(data[k], angle)) for angle in
                                                (90, 120, 45, 0, -90, -45, -120, 180, -180)}
                                data[k] = {0: data[k]}
                            else:
                                data["mask"] = from_surface(data[k])

                        if parent_key == "right":
                            parent_data["left"]["sprite"] = flip(data[k], True, False)
                            parent_data["left"]["mask"] = from_surface(parent_data["left"]["sprite"])
                            already_done[v] = {"right": (data[k], data["mask"]),
                                               "left": (parent_data["left"]["sprite"], parent_data["left"]["mask"])}
                            if effect_sprite_adjust:
                                parent_data["left"]["sprite"] = {0: parent_data["left"]["sprite"]}
                        else:
                            already_done[v] = data[k]
                    else:
                        already_done[v] = data[k]
                else:
                    data[k] = already_done[v]
                    if battle_only:
                        if k == "sprite":
                            data["sprite"] = already_done[v][parent_key][0]
                            data["mask"] = already_done[v][parent_key][1]

                        if parent_key == "right":
                            parent_data["left"]["sprite"] = already_done[v]["left"][0]
                            parent_data["left"]["mask"] = already_done[v]["left"][1]

            elif type(v) is tuple or type(v) is list:

                data[k] = tuple([c if type(c) is not CompilableSurface else
                                 surface_screen_scale(c.surface, screen_scale) for c in data[k]])

            elif "offset" in k:
                data[k] = (v[0] * screen_scale[0], v[1] * screen_scale[1])
