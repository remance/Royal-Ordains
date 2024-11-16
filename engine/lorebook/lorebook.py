import pygame

from engine.uimenu.uimenu import UIMenu
from engine.utils.text_making import make_long_text

subsection_tag_colour = [(128, 255, 128), (237, 128, 128), (255, 255, 128), (128, 255, 255),
                         (128, 128, 255), (255, 128, 255), (220, 158, 233), (191, 191, 191), (255, 140, 85)]

subsection_tag_colour = ([(255, 255, 255)] + subsection_tag_colour +
                         [(item, item2) for item in subsection_tag_colour for item2 in subsection_tag_colour if
                          item != item2] +
                         [(item, item2, item3) for item in subsection_tag_colour for item2 in subsection_tag_colour for
                          item3 in subsection_tag_colour if len(set((item, item2, item3))) > 1])


class Lorebook(UIMenu):
    history_lore = {}
    character_lore = {}
    item_lore = {}
    status_lore = {}

    portrait_data = {}

    history_section = 0
    character_section = 1
    equipment_section = 2
    status_section = 3

    def __init__(self, game, image, text_size=24):
        self._layer = 23
        UIMenu.__init__(self)
        self.game = game
        self.font = pygame.font.Font(self.ui_font["main_button"], int(text_size * self.screen_scale[1]))
        self.font_header = pygame.font.Font(self.ui_font["name_font"], int(52 * self.screen_scale[1]))
        self.image = image
        self.base_image = self.image.copy()
        self.section = 0
        self.subsection = 0  # subsection of that section
        self.stat_data = None  # for getting the section stat data
        self.index_data = None  # for getting old and new subsection index reference
        self.current_subsection = None  # Subsection stat currently viewing
        self.current_subsection2 = None  # Subsection lore currently viewing
        self.subsection_list = None
        self.portrait = None
        self.preview_sprite = None

        self.section_list = ()

        self.current_subsection_row = 0
        self.current_filter_row = 0
        self.max_row_show = 19
        self.row_size = 0
        self.filter_size = 0
        self.page = 0
        self.max_page = 0
        self.rect = self.image.get_rect(center=(self.screen_size[0] / 2, self.screen_size[1] / 2))
        self.tag_list = [{stuff["Tag"]: True for stuff in self.history_lore.values() if "Tag" in stuff and  stuff["Tag"]},
                         {stuff["Tag"]: True for stuff in self.character_lore.values() if "Tag" in stuff and stuff["Tag"]},
                         {stuff["Tag"]: True for stuff in self.item_lore.values() if "Tag" in stuff and stuff["Tag"]},
                         {stuff["Tag"]: True for stuff in self.status_lore.values() if type(stuff) != int and "Tag" in stuff
                          and stuff["Tag"]}]
        for index, tag_list in enumerate(self.tag_list):
            tag_list["No Tag"] = True
            self.tag_list[index] = {"No Tag": self.tag_list[index].pop("No Tag"), **self.tag_list[index]}

        self.section_list = (self.history_lore, self.character_lore, self.item_lore, self.status_lore)

    def change_page(self, page):
        """Change page of the current subsection, either next or previous page"""
        self.page = page
        self.image = self.base_image.copy()  # reset lorebook image
        self.page_design()  # draw new pages

    def change_section(self, section, subsection_list_box, subsection_name_group, tag_filter_group,
                       subsection_list_scroll, filter_list_box, filter_list_scroll):
        """Change to new section either by open lorebook or click section button"""
        self.portrait = None
        self.section = section  # get new section
        self.subsection = 0  # reset subsection to the first one
        self.stat_data = self.section_list[self.section]  # get new stat data of the new section
        self.max_page = 0  # reset max page
        self.current_subsection_row = 0  # reset subsection scroll to the top one
        self.current_filter_row = 0
        this_list = tuple(self.stat_data.values())  # get list of subsection
        self.subsection_list = []  # remove the header from subsection list
        # name[0] if
        # type(name) == list and "Name" != name[0] else name["Name"]
        # for name in
        #     this_list
        for index, name in enumerate(this_list):
            if type(name) is list and "Name" != name[0]:
                self.subsection_list.append(name[0])
            elif type(name) is dict:
                self.subsection_list.append(name["Name"])

        if "Name" in self.subsection_list:
            self.subsection_list.remove("Name")
        self.row_size = len(self.subsection_list)  # get size of subsection list
        self.filter_size = len(self.tag_list[self.section])

        self.change_subsection(self.subsection)
        self.setup_subsection_list(subsection_list_box, subsection_name_group, "subsection")

        subsection_list_scroll.change_image(row_size=self.row_size)
        subsection_list_scroll.change_image(new_row=self.current_subsection_row)

        self.setup_subsection_list(filter_list_box, tag_filter_group, "tag")
        filter_list_scroll.change_image(row_size=self.filter_size)
        filter_list_scroll.change_image(new_row=self.current_filter_row)

    def change_subsection(self, subsection):
        self.subsection = subsection
        if type(subsection) == str and self.subsection in self.index_data:  # use new subsection index instead of old one
            self.subsection = self.index_data[self.subsection]
        self.image = self.base_image.copy()

        self.portrait = None  # reset portrait, possible for subsection to not have portrait

        # self.portrait = self.portrait_data[self.section][self.subsection]
        # self.portrait = pygame.transform.smoothscale(self.portrait,
        #                                              (int(self.portrait.get_width() * self.screen_scale[0]),
        #                                               int(self.portrait.get_height() * self.screen_scale[1])))

        self.page_design()

    def setup_subsection_list(self, list_surface, list_group, list_type):
        """generate list of subsection of the left side of lorebook"""
        row = 0
        pos = list_surface.rect.topleft
        if self.current_subsection_row > self.row_size - self.max_row_show:
            self.current_subsection_row = self.row_size - self.max_row_show

        if len(list_group) > 0:  # remove previous subsection in the group before generate new one
            for stuff in list_group:
                stuff.kill()
                del stuff

        if list_type == "subsection":  # subsection list
            stat_key = tuple(self.stat_data.keys())
            for index, item in enumerate(self.subsection_list):
                if index >= self.current_subsection_row:
                    tag = "No Tag"  # white colour
                    tag_index = 0
                    if self.stat_data[stat_key[index]]["Tag"] != "":
                        tag = self.stat_data[stat_key[index]]["Tag"]
                        tag_index = tuple(self.tag_list[self.section].keys()).index(tag)
                    if self.tag_list[self.section][tag]:  # not creating subsection with disabled tag
                        list_group.add(SubsectionName(self.screen_scale, (pos[0], pos[1] + row), item,
                                                      stat_key[index],
                                                      tag_index))  # add new subsection sprite to group
                        row += (41 * self.screen_scale[1])  # next row
                        if len(list_group) > self.max_row_show:
                            break  # will not generate more than space allowed
        elif list_type == "tag":  # tag filter list
            loop_list = self.tag_list[self.section]
            for index, item in enumerate(loop_list):
                tag = tuple(self.tag_list[self.section].keys()).index(item)
                list_group.add(SubsectionName(self.screen_scale, (pos[0], pos[1] + row), item,
                                              item, tag, selected=True))  # add new subsection sprite to group
                row += (41 * self.screen_scale[1])  # next row
                if len(list_group) > self.max_row_show:
                    break  # will not generate more than space allowed

    def page_design(self):
        """Lore book format position of the text"""
        stat = self.stat_data[tuple(self.stat_data.keys())[self.subsection]]

        name = stat["Name"]
        text_surface = self.font_header.render(str(name), True, (0, 0, 0))
        text_rect = text_surface.get_rect(topleft=(int(28 * self.screen_scale[0]), int(20 * self.screen_scale[1])))
        self.image.blit(text_surface, text_rect)  # add name of item to the top of page

        description = stat["Description"]

        description_pos = (int(20 * self.screen_scale[1]), int(100 * self.screen_scale[0]))

        if self.portrait is not None:
            description_pos = (int(20 * self.screen_scale[1]), int(300 * self.screen_scale[0]))

            portrait_rect = self.portrait.get_rect(
                center=(int(300 * self.screen_scale[0]), int(200 * self.screen_scale[1])))
            self.image.blit(self.portrait, portrait_rect)

        description_surface = pygame.Surface((int(550 * self.screen_scale[0]), int(400 * self.screen_scale[1])),
                                             pygame.SRCALPHA)
        description_rect = description_surface.get_rect(topleft=description_pos)
        make_long_text(description_surface, description,
                       (int(5 * self.screen_scale[1]), int(5 * self.screen_scale[0])),
                       self.font)
        self.image.blit(description_surface, description_rect)

        row = 50 * self.screen_scale[1]
        col = 650 * self.screen_scale[0]
        if self.portrait is not None:
            row = 50 * self.screen_scale[1]
            col = 650 * self.screen_scale[0]


class SubsectionList(UIMenu):
    def __init__(self, pos, image):
        self._layer = 23
        UIMenu.__init__(self)
        self.image = image
        self.rect = self.image.get_rect(topright=pos)
        self.max_row_show = 19


class SubsectionName(UIMenu):
    def __init__(self, screen_scale, pos, name, subsection, tag, selected=False, text_size=28):
        self._layer = 24
        UIMenu.__init__(self, has_containers=True)
        self.font = pygame.font.Font(self.ui_font["main_button"], int(text_size * screen_scale[1]))
        self.selected = False
        self.name = str(name)

        # Border
        self.image = pygame.Surface((int(300 * screen_scale[0]), int(40 * screen_scale[1])))
        self.image.fill((0, 0, 0))  # black corner

        # Body square
        self.small_image = pygame.Surface((int(290 * screen_scale[0]), int(34 * screen_scale[1])))
        colour = subsection_tag_colour[tag]
        if type(colour[0]) == int:
            self.small_image.fill(colour)
        else:  # multiple colour
            starting_pos = 0
            colour_size = self.small_image.get_width() / len(colour)
            for this_colour in colour:
                colour_1_surface = pygame.Surface((colour_size, self.small_image.get_height()))
                rect = colour_1_surface.get_rect(topleft=(starting_pos, 0))
                colour_1_surface.fill(this_colour)
                self.small_image.blit(colour_1_surface, rect)
                starting_pos += colour_size
        self.small_rect = self.small_image.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(self.small_image, self.small_rect)

        # Subsection name text
        self.text_surface = self.font.render(self.name, True, (0, 0, 0))
        self.text_rect = self.text_surface.get_rect(midleft=(int(5 * screen_scale[0]), self.image.get_height() / 2))
        self.image.blit(self.text_surface, self.text_rect)

        self.subsection = subsection
        self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)

        if selected:
            self.selection()

    def selection(self):
        if self.selected:
            self.selected = False
        else:
            self.selected = True
        if self.selected:
            self.image.fill((233, 214, 82))
        else:
            self.image.fill((0, 0, 0))
        self.image.blit(self.small_image, self.small_rect)
        self.image.blit(self.text_surface, self.text_rect)


# class Selectionbox(pygame.sprite.Sprite):
#     def __init__(self, pos, lorebook):
#         self._layer = 13
#         pygame.sprite.Sprite.__init__(self, self.containers)
#         self.image = pygame.Surface(300, lorebook.image.get_height())


# class Searchbox(pygame.sprite.Sprite):
#     def __init__(self, text_size=16):
#         self._layer = 14
#         pygame.sprite.Sprite.__init__(self, self.containers)
#         self.font = pygame.font.SysFont("helvetica", text_size)
#         self.image = pygame.Surface(100, 50)
#         self.text = ""
#         self.text_surface = self.font.render(str(self.text), 1, (0, 0, 0))
#         self.text_rect = self.text_surface.get_rect(centerleft=(3, self.image.get_height() / 2))
#
#     def textchange(self, input):
#         newcharacter = pygame.key.name(input)
#         self.text += newcharacter

def lorebook_process(self, esc_press):
    """Lorebook user interaction"""
    command = None
    close = False
    for button_index, button in self.lore_buttons.items():
        if button in self.ui_updater and button.event_press:  # click button
            if type(button_index) is int:  # section button
                self.lorebook.change_section(button_index, self.lore_name_list, self.subsection_name,
                                             self.tag_filter_name, self.lore_name_list.scroll,
                                             self.filter_tag_list,
                                             self.filter_tag_list.scroll)  # change to section of that button

            elif button_index == "close" or esc_press:  # Close button
                close = True

            break  # found clicked button, break loop

    if self.lore_name_list.scroll.event_press:  # click on subsection list scroll
        self.lorebook.current_subsection_row = self.lore_name_list.scroll.player_input(
            self.cursor.pos)  # update the scroll and get new current subsection
        self.lorebook.setup_subsection_list(self.lore_name_list,
                                            self.subsection_name, "subsection")  # update subsection name list
    elif self.filter_tag_list.scroll.event_press:  # click on filter list scroll
        self.lorebook.current_filter_row = self.filter_tag_list.scroll.player_input(
            self.cursor.pos)  # update the scroll and get new current subsection
        self.lorebook.setup_subsection_list(self.filter_tag_list,
                                            self.tag_filter_name, "tag")  # update subsection name list
    else:
        for index, name in enumerate(self.subsection_name):
            if name.event_press:  # click on subsection name
                self.lorebook.change_subsection(index)  # change subsection
                break  # found clicked subsection, break loop
        for name in self.tag_filter_name:
            if name.event_press:  # click on subsection name
                name.selection()
                self.lorebook.tag_list[self.lorebook.section][name.name] = name.selected
                self.lorebook.setup_subsection_list(self.lore_name_list, self.subsection_name,
                                                    "subsection")  # update subsection name list
                break  # found clicked subsection, break loop

    if self.cursor.scroll_up:
        if self.lore_name_list.mouse_over:  # Scrolling at lore book subsection list
            if self.lorebook.current_subsection_row > 0:
                self.lorebook.current_subsection_row -= 1
                self.lorebook.setup_subsection_list(self.lore_name_list, self.subsection_name, "subsection")
                self.lore_name_list.scroll.change_image(new_row=self.lorebook.current_subsection_row)
        elif self.filter_tag_list.mouse_over:  # Scrolling at lore book subsection list
            if self.lorebook.current_filter_row > 0:
                self.lorebook.current_filter_row -= 1
                self.lorebook.setup_subsection_list(self.filter_tag_list, self.tag_filter_name, "tag")
                self.filter_tag_list.scroll.change_image(new_row=self.lorebook.current_filter_row)

    elif self.cursor.scroll_down:
        if self.lore_name_list.mouse_over:  # Scrolling at lore book subsection list
            if self.lorebook.current_subsection_row + self.lorebook.max_row_show - 1 < self.lorebook.row_size:
                self.lorebook.current_subsection_row += 1
                self.lorebook.setup_subsection_list(self.lore_name_list, self.subsection_name, "subsection")
                self.lore_name_list.scroll.change_image(new_row=self.lorebook.current_subsection_row)

        elif self.filter_tag_list.mouse_over:  # Scrolling at lore book subsection list
            if self.lorebook.current_filter_row + self.lorebook.max_row_show - 1 < self.lorebook.row_size:
                self.lorebook.current_filter_row += 1
                self.lorebook.setup_subsection_list(self.filter_tag_list, self.tag_filter_name, "tag")
                self.filter_tag_list.scroll.change_image(new_row=self.lorebook.current_filter_row)

    if close or esc_press:
        self.portrait = None
        self.remove_ui_updater(self.lorebook_stuff)  # remove lorebook related sprites
        for group in (self.subsection_name, self.tag_filter_name):
            for name in group:  # remove subsection name
                name.kill()
                del name
        command = "exit"

    return command
