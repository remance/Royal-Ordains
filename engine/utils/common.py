from collections.abc import Iterable
from math import radians, sin

import pygame
import pygame.freetype


def empty_method(*args):
    pass


def cutscene_update(self, *args, **kwargs):
    """call cutscene update method of every member sprite instead of update

    Group.update(*args, **kwargs): return None

    Calls the update method of every member sprite. All arguments that
    were passed to this method are passed to the Sprite cutscene_update function.

    """
    for sprite in self.sprites():
        if hasattr(sprite, "cutscene_update"):
            sprite.cutscene_update(*args, **kwargs)
        else:
            sprite.update(*args, **kwargs)


def change_group(item, group, change):
    """Change group of the item, use for multiple change in loop"""
    if change == "add":
        group.add(item)
    elif change == "remove":
        group.remove(item)


def keyboard_mouse_press_check(button_type, button, is_button_just_down, is_button_down, is_button_just_up):
    """
    Check for button just press, holding, and release for keyboard or mouse
    :param button_type: pygame.key, pygame.mouse, or pygame.
    :param button: button index
    :param is_button_just_down: button is just press last update
    :param is_button_down: button is pressing after first update
    :param is_button_just_up: button is just release last update
    :return: new state of is_button_just_down, is_button_down, is_button_just_up
    """
    if button_type.get_pressed()[button]:
        # press button
        if not is_button_just_down:
            if not is_button_down:  # fresh press
                is_button_just_down = True
        else:  # already press in previous frame, now hold until release
            is_button_just_down = False
            is_button_down = True
    else:  # no longer press
        is_button_just_down = False
        if is_button_just_down or is_button_down:
            is_button_just_up = True
            is_button_just_down = False
            is_button_down = False
        elif is_button_just_up:
            is_button_just_up = False

    return is_button_just_down, is_button_down, is_button_just_up


def edit_config(section, option, value, filename, config):
    """
    Edit config file at specific section
    :param section: Section name
    :param option: Part that will be changed
    :param value: Changed value in string text
    :param filename: Config file name
    :param config: Config object
    :return:
    """
    config.set(section, option, str(value))
    with open(filename, "w") as configfile:
        config.write(configfile)


def setup_list(item_class, current_row, show_list, item_group, box, ui_class, layer=15):
    """generate list of subsection buttons"""
    from engine.game.game import Game
    screen_scale = Game.screen_scale
    row = 5 * screen_scale[1]
    column = 5 * screen_scale[0]
    pos = box.rect.topleft
    if current_row > len(show_list) - box.max_row_show:
        current_row = len(show_list) - box.max_row_show

    for stuff in item_group:  # remove previous sprite in the group before generate new one
        stuff.kill()
        del stuff
    item_group.empty()

    for index, item in enumerate(show_list):
        if index >= current_row:
            new_item = item_class(box, (pos[0] + column, pos[1] + row), item, layer=layer)
            item_group.add(new_item)  # add new subsection sprite to group
            row += (new_item.font.get_height() * 1.4 * screen_scale[1])  # next row
            if len(item_group) > box.max_row_show:
                break  # will not generate more than space allowed

        ui_class.add(*item_group)


def list_scroll(screen_scale, mouse_scroll_up, mouse_scroll_down, scroll, box, current_row, name_list, group, ui_class,
                layer=15):
    """
    Process scroll of subsection list
    :param screen_scale:
    :param mouse_scroll_up: Mouse scrolling up input
    :param mouse_scroll_down: Mouse scrolling down input
    :param scroll: Scroll object
    :param box: UI box of the subsection list
    :param current_row: Current showing subsection row (the last one)
    :param name_list:
    :param group: Group of the
    :param ui_class:
    :param layer: Layer of the scroll
    :return: New current_row after scrolling
    """
    from engine.uimenu import uimenu
    if mouse_scroll_up:
        current_row -= 1
        if current_row < 0:
            current_row = 0
        else:
            setup_list(uimenu.NameList, current_row, name_list, group, box, ui_class, layer=layer)
            scroll.change_image(new_row=current_row, row_size=len(name_list))

    elif mouse_scroll_down:
        current_row += 1
        if current_row + box.max_row_show - 1 < len(name_list):
            setup_list(uimenu.NameList, current_row, name_list, group, box, ui_class, layer=layer)
            scroll.change_image(new_row=current_row, row_size=len(name_list))
        else:
            current_row -= 1
    return current_row


def calculate_projectile_target(velocity, angle):
    angle = radians(angle)
    return velocity ** 2 * sin(2 * angle)


def calculate_projectile_velocity(angle, distance):
    """Velocity required for object to reach give distance and angle"""
    angle = radians(angle)
    if angle:
        return (distance / (sin(2 * angle))) ** 0.5
    else:
        return distance ** 0.5


def float_check(value):
    try:
        float(value)
        return True
    except ValueError:
        return


def clean_group_object(groups):
    """Clean all attributes of every object in group in list"""
    for group in groups:
        if len(group) > 0:
            if type(group) is pygame.sprite.Group or type(group) is list or type(group) is tuple:
                for stuff in group:
                    clean_object(stuff)
                group.empty()
            elif type(group) is dict:
                for stuff in group.values():
                    if isinstance(stuff, Iterable):
                        for item in stuff:
                            clean_object(item)
                    else:
                        clean_object(stuff)
            else:
                group.kill()
                group.delete()
                del group


def clean_object(this_object):
    """Clean all attributes of the object and delete it"""
    this_object.kill()
    for attribute in tuple(this_object.__dict__.keys()):
        this_object.__delattr__(attribute)
    del this_object
