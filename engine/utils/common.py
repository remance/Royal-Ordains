from collections.abc import Iterable

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


def stat_allocation_check(stat, point_pool, how):
    up_cost = int(stat / 10) + 1
    if how == "up":
        if up_cost > point_pool:
            return stat, point_pool
        return stat + 1, point_pool - up_cost
    else:
        if stat > 1:
            return stat - 1, point_pool + up_cost
        else:
            return stat, point_pool


def skill_allocation_check(skill, point_pool, how, current_chapter):
    if how == "up":
        max_level = current_chapter + 1  # max level increase every chapter
        if max_level > 5:  # max skill lv in game is 5 so chapter 4 is when skill can be maxed
            max_level = 5
        if point_pool > 0 and skill < max_level:
            return skill + 1, point_pool - 1
        return skill, point_pool
    else:
        if skill > 0:
            return skill - 1, point_pool + 1
        return skill, point_pool


def keyboard_mouse_press_check(button_type, button, is_button_just_down, is_button_down, is_button_just_up,
                               joystick_check=()):
    """
    Check for button just press, holding, and release for keyboard or mouse
    :param button_type: pygame.key, pygame.mouse, or pygame.
    :param button: button index
    :param is_button_just_down: button is just press last update
    :param is_button_down: button is pressing after first update
    :param is_button_just_up: button is just release last update
    :param joystick_check: check for joystick press as well
    :return: new state of is_button_just_down, is_button_down, is_button_just_up
    """
    if joystick_check:
        if type(joystick_check[1]) is str:  # hat and axis input
            if "hat" in joystick_check[1]:
                button_check = joystick_check[0].get_hat(int(joystick_check[1][-2:]))
            if "axis" in joystick_check[1]:
                button_check = joystick_check[0].get_axis(int(joystick_check[1][-2:]))
                if int(joystick_check[1][-2:]) > 0 > button_check:
                    button_check = 0
                if int(joystick_check[1][-2:]) < 1 < button_check:
                    button_check = 0
        else:  # other buttons input
            button_check = joystick_check[0].get_button(joystick_check[1])

    if button_type.get_pressed()[button] or (joystick_check and button_check):
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
    """generate list of subsection buttons like in the lorebook"""
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


def clean_group_object(groups):
    """Clean all attributes of every object in group in list"""
    for group in groups:
        if len(group) > 0:
            if type(group) == pygame.sprite.Group or type(group) == list or type(group) == tuple:
                for stuff in group:
                    clean_object(stuff)
                group.empty()
            elif type(group) == dict:
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
