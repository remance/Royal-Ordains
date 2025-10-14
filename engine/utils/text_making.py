import datetime
import os
from random import randint

import pygame
from PIL import Image
from pygame import Color, Surface, image, SRCALPHA


def change_number(number):
    """Change number more than a thousand to K digit e.g. 1k = 1000"""
    if number >= 1000000:
        return str(round(number / 1000000, 1)) + "m"
    elif number >= 1000:
        return str(round(number / 1000, 1)) + "k"


def number_to_minus_or_plus(number):
    """Number should not be 0"""
    if number > 0:
        return "+"
    else:  # assuming number is not 0
        return "-"


def sort_list_dir_with_str(dir_list, str_list):
    sorted_dir = []
    for index in range(len(str_list)):
        for x in dir_list:
            if os.path.normpath(x).split(os.sep)[-1:][0] == str_list[index]:
                sorted_dir.append(x)
    for item in dir_list:  # add item not in already sorted to the end of list
        if item not in sorted_dir:
            sorted_dir.append(item)
    return sorted_dir


def make_long_text(surface, text, pos, font, color=Color("black"), with_texture=(), specific_width=None,
                   alignment="left"):
    """
    Blit long text into separate row of text by blitting text word by word
    :param surface: Input Pygame Surface
    :param text: Text in either list or string format
    :param pos: Starting position
    :param font: Pygame Font
    :param color: Text colour
    :param with_texture: List array with value for argument of text_render_with_texture (texture, (gf_colour, o_colour, opx))
    :param specific_width: Specific width size of text
    :param alignment: text alignment "left", "right", "center"
    """
    # TODO Add sizing and colouring for highlight and maybe URL system
    if type(text) not in (list, tuple):
        text = [text]
    x, y = [0, 0]
    true_x = pos[0]
    word_height = font.size(" ")[1]
    max_width = surface.get_width()
    if specific_width:
        max_width = specific_width
    space = font.size(" ")[0]  # the width of a space

    for this_text in text:
        words = [word.split(" ") for word in str(this_text).splitlines()]  # 2D array where each row is a list of words
        for line in words:
            this_subsurface_list = {}
            for word in line:
                if not with_texture:
                    word_surface = font.render(word, True, color)
                else:
                    word_surface = text_render_with_texture(word, font, with_texture[0], with_bg=with_texture[1])

                word_width = word_surface.get_width()
                if true_x + word_width >= max_width or word == "\\n":  # new line
                    subsurface = Surface((x, word_height), SRCALPHA)
                    for w_x, w_surface in this_subsurface_list.items():
                        subsurface.blit(w_surface, (w_x, 0))
                    if alignment == "left":
                        surface.blit(subsurface, (pos[0], y))
                    elif alignment == "right":
                        surface.blit(subsurface, subsurface.get_rect(topright=(surface.get_rect().topright[0], y)))
                    else:
                        surface.blit(subsurface, subsurface.get_rect(center=(surface.get_rect().center[0],
                                                                             y + (word_height / 2))))
                    x = 0  # reset x
                    true_x = pos[0]
                    y += word_height  # start on new line.
                    this_subsurface_list = {}

                if word != "\\n":
                    this_subsurface_list[x] = word_surface
                    x += word_width + space
                    true_x += word_width + space

            subsurface = Surface((x, word_height), SRCALPHA)
            for w_x, w_surface in this_subsurface_list.items():
                subsurface.blit(w_surface, (w_x, 0))

            if alignment == "left":
                surface.blit(subsurface, (pos[0], y))
            elif alignment == "right":
                surface.blit(subsurface, subsurface.get_rect(topright=(surface.get_rect().topright[0], y)))
            else:
                surface.blit(subsurface, subsurface.get_rect(center=(surface.get_rect().center[0],
                                                                     y + (word_height / 2))))
            x = 0  # reset x
            true_x = pos[0]
        y += word_height  # start on new line


def text_render_with_texture(text, font, texture, with_bg=None):
    """
    Render text with custom texture
    :param text: Text strings
    :param font: Pygame font
    :param texture: Texture for font
    :param with_bg: array value for bg argument (gf_colour, o_colour, opx)
    :return: Text surface
    """
    if not with_bg:
        text_surface = font.render(text, True, (0, 0, 0))
    else:
        text_surface = text_render_with_bg(text, font, gf_colour=with_bg[0], o_colour=with_bg[1], opx=with_bg[2])
    size = text_surface.get_size()
    data = image.tobytes(text_surface, "RGBA")  # convert image to string data for filtering effect
    text_surface = Image.frombytes("RGBA", size, data)  # use PIL to get image data

    if texture:
        surface = Image.new("RGBA", size, (0, 0, 0, 0))
        texture_size = texture.size
        pos = (randint(0, texture_size[0] - size[0]), randint(0, texture_size[1] - size[1]))
        new_texture = texture.crop((pos[0], pos[1], pos[0] + size[0], pos[1] + size[1]))
        surface.paste(new_texture, box=(0, 0), mask=text_surface)
        size = surface.size
        surface = surface.tobytes()
        surface = image.frombytes(surface, size, "RGBA")  # convert image back to a pygame surface
    else:  # no assigned texture
        surface = text_surface

    return surface


def text_render_with_bg(text, font, gf_colour=Color("black"), o_colour=(255, 255, 255), opx=2):
    """
    Render text with background border
    :param text: Text strings
    :param font: Pygame font
    :param gf_colour: Text colour
    :param o_colour: Background colour
    :param opx: Background colour thickness
    :return: Text surface
    """
    text_surface = font.render(text, True, gf_colour)
    w = text_surface.get_width() + 2 * opx
    h = font.get_height()

    osurf = Surface((w, h + 2 * opx), pygame.SRCALPHA)
    osurf.fill((0, 0, 0, 0))

    surface = osurf.copy()

    osurf.blit(font.render(text, True, o_colour), (0, 0))

    for dx, dy in circle_points(opx):
        surface.blit(osurf, (dx + opx, dy + opx))

    surface.blit(text_surface, (opx, opx))

    return surface


def circle_points(r):
    """Calculate text point to add background"""
    circle_cache = {}
    r = int(round(r))
    if r in circle_cache:
        return circle_cache[r]
    x, y, e = r, 0, 1 - r
    circle_cache[r] = points = []
    while x >= y:
        points.append((x, y))
        y += 1
        if e < 0:
            e += 2 * y - 1
        else:
            x -= 1
            e += 2 * (y - x) - 1
    points += [(y, x) for x, y in points if x > y]
    points += [(-x, y) for x, y in points if x]
    points += [(x, -y) for x, y in points if y]
    points.sort()
    return points


def convert_str_time(event):
    """
    Convert text string of time to datetime
    :param event: Event must be in string format
    """
    for index, item in enumerate(event):
        new_time = datetime.datetime.strptime(item[1], "%H:%M:%S").time()
        new_time = datetime.timedelta(hours=new_time.hour, minutes=new_time.minute, seconds=new_time.second)
        event[index][1] = new_time
        event[index] = tuple(event[index])


def minimise_number_text(text: str):
    num_text = int(text)
    if num_text >= 1000000000000000:
        return str(round(num_text / 1000000000000000, 1)) + "Q"
    elif num_text >= 1000000000000:
        return str(round(num_text / 1000000000000, 1)) + "T"
    elif num_text >= 1000000000:
        return str(round(num_text / 1000000000, 1)) + "B"
    elif num_text >= 1000000:
        return str(round(num_text / 1000000, 1)) + "M"
    elif num_text >= 1000:
        return str(round(num_text / 1000, 1)) + "K"
    return str(num_text)
