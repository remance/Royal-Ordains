from PIL import Image, ImageOps, ImageFilter, ImageEnhance
from pygame import image, Surface, SRCALPHA


def crop_sprite(sprite_pic, custom_base_point=None):
    low_x0 = float("inf")  # lowest x0
    low_y0 = float("inf")  # lowest y0
    high_x1 = 0  # highest x1
    high_y1 = 0  # highest y1

    # Find optimal cropped sprite size and center offset
    size = sprite_pic.get_size()
    data = image.tobytes(sprite_pic, "RGBA")  # convert image to string data for filtering effect
    data = Image.frombytes("RGBA", size, data)  # use PIL to get image data
    bbox = data.getbbox()
    if low_x0 > bbox[0]:
        low_x0 = bbox[0]
    if low_y0 > bbox[1]:
        low_y0 = bbox[1]
    if high_x1 < bbox[2]:
        high_x1 = bbox[2]
    if high_y1 < bbox[3]:
        high_y1 = bbox[3]

    center = ((sprite_pic.get_width() / 2), (sprite_pic.get_height() / 2))

    # Crop transparent area only of surface
    old_size = sprite_pic.get_size()
    sprite_pic = image.tobytes(sprite_pic,
                               "RGBA")  # convert image to string data for filtering effect
    sprite_pic = Image.frombytes("RGBA", old_size, sprite_pic)  # use PIL to get image data
    sprite_pic = sprite_pic.crop((low_x0, low_y0, high_x1, high_y1))
    size = sprite_pic.size
    sprite_pic = sprite_pic.tobytes()
    sprite_pic = image.frombytes(sprite_pic, size,
                                 "RGBA")  # convert image back to a pygame surface

    # Find center offset after crop by finding width and height difference of longer side

    # center_x_offset = ((low_x0 + high_x1) / 2)
    center_x_offset = ((low_x0 + high_x1) / 2) + (((100 - low_x0) - (high_x1 - 100)) / 10)
    if custom_base_point:
        # Different y offset from center
        y_offset = old_size[1] - high_y1
    else:
        y_offset = center[1] - ((low_y0 + high_y1) / 2)
    true_offset = (center[0] - center_x_offset, y_offset)

    return sprite_pic, true_offset


def apply_sprite_colour(surface, colour=None, white_colour=True):
    """Colorise body part sprite"""
    if surface is not None:
        size = surface.get_size()
        data = image.tobytes(surface, "RGBA")  # convert image to string data for filtering effect
        surface = Image.frombytes("RGBA", size, data)  # use PIL to get image data
        alpha = surface.split()[-1]  # save alpha
        surface = surface.convert("L")  # convert to grey scale for colourise
        if colour is not None:
            mid_colour = "white"
            if white_colour is False:
                max_colour = 255  # - (colour[0] + colour[1] + colour[2])
                mid_colour = [int(c - ((max_colour - c) / 2)) for c in colour]

            surface = ImageOps.colorize(surface, black="black", mid=colour, white=mid_colour).convert("RGB")
        surface.putalpha(alpha)  # put back alpha
        surface = surface.tobytes()
        surface = image.frombytes(surface, size, "RGBA")  # convert image back to a pygame surface
    return surface


def apply_sprite_effect(surface, properties):
    for prop in properties:
        if "effect" in prop:
            if "colour" in prop:
                colour = prop[prop.rfind("_") + 1:]
                colour = [int(this_colour) for this_colour in colour.split(".")]
                surface = apply_sprite_colour(surface, colour)
            else:
                size = surface.get_size()
                data = image.tobytes(surface, "RGBA")  # convert image to string data for filtering effect
                surface = Image.frombytes("RGBA", size, data)  # use PIL to get image data
                alpha = surface.split()[-1]  # save alpha
                if "grey" in prop:  # not work with just convert L for some reason
                    surface = surface.convert("L")
                    surface = ImageOps.colorize(surface, black="black", white="white").convert("RGB")
                elif "blur" in prop:
                    surface = surface.filter(
                        ImageFilter.GaussianBlur(
                            radius=float(
                                prop[prop.rfind("_") + 1:])))  # blur Image (or apply other filter in future)
                elif "contrast" in prop:
                    enhancer = ImageEnhance.Contrast(surface)
                    surface = enhancer.enhance(float(prop[prop.rfind("_") + 1:]))
                elif "brightness" in prop:
                    enhancer = ImageEnhance.Brightness(surface)
                    surface = enhancer.enhance(float(prop[prop.rfind("_") + 1:]))
                elif "fade" in prop:
                    empty = Surface(size, SRCALPHA)
                    empty.fill((255, 255, 255, 255))
                    empty = image.tobytes(empty, "RGBA")  # convert image to string data for filtering effect
                    empty = Image.frombytes("RGBA", size,
                                            empty)  # use PIL to get image data
                    surface = Image.blend(surface, empty, alpha=float(prop[prop.rfind("_") + 1:]) / 10)
                surface.putalpha(alpha)  # put back alpha
                surface = surface.tobytes()
                surface = image.frombytes(surface, size, "RGBA")  # convert image back to a pygame surface
    return surface


def sprite_rotate(surface, angle):
    size = surface.get_size()
    data = image.tobytes(surface, "RGBA")  # convert image to string data for filtering effect
    surface = Image.frombytes("RGBA", size, data)  # use PIL to get image data
    surface = surface.rotate(angle, expand=True, resample=Image.BICUBIC)
    size = surface.size
    surface = surface.tobytes()
    surface = image.frombytes(surface, size, "RGBA").convert_alpha()  # convert image back to a pygame surface
    return surface
