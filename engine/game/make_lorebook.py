import pygame

from engine.lorebook.lorebook import Lorebook, SubsectionList
from engine.uibattle.uibattle import UIScroll
from engine.uimenu.uimenu import MenuImageButton
from engine.utils.data_loading import load_images


def make_lorebook(self):
    """Create Encyclopedia related objects"""
    encyclopedia_images = load_images(self.data_dir, screen_scale=self.screen_scale, subfolder=("ui", "lorebook_ui"))
    encyclopedia = Lorebook(self, encyclopedia_images["lorebook"])  # lorebook sprite
    lore_name_list = SubsectionList(encyclopedia.rect.topleft, encyclopedia_images["section_list"])
    filter_tag_list = SubsectionList(
        (encyclopedia.rect.topright[0] + encyclopedia_images["section_list"].get_width(),
         encyclopedia.rect.topright[1]),
        pygame.transform.flip(encyclopedia_images["section_list"], True, False))
    lore_name_list.max_row_show = encyclopedia.max_row_show

    button_images = load_images(self.data_dir, screen_scale=self.screen_scale,
                                subfolder=("ui", "lorebook_ui", "button"))

    lore_buttons = {0: MenuImageButton((encyclopedia.rect.topleft[0] + (button_images["history"].get_width() / 2),
                                        encyclopedia.rect.topleft[1] - (button_images["history"].get_height() / 2)),
                                       button_images["history"], layer=13),
                    1: MenuImageButton((encyclopedia.rect.topleft[0] + (button_images["history"].get_width() * 1.6),
                                        encyclopedia.rect.topleft[1] - (button_images["character"].get_height() / 2)),
                                       button_images["character"], layer=13),
                    2: MenuImageButton((encyclopedia.rect.topleft[0] + (button_images["history"].get_width() * 2.7),
                                        encyclopedia.rect.topleft[1] - (button_images["enemy"].get_height() / 2)),
                                       button_images["item"], layer=13),
                    3: MenuImageButton((encyclopedia.rect.topleft[0] + (button_images["history"].get_width() * 3.8),
                                        encyclopedia.rect.topleft[1] - (button_images["item"].get_height() / 2)),
                                       button_images["status"], layer=13),
                    "close": MenuImageButton(
                        (encyclopedia.rect.topright[0] - (button_images["history"].get_width() / 2),
                         encyclopedia.rect.topleft[1] - (button_images["close"].get_height() / 2)),
                        button_images["close"], layer=13)}  # next page button

    UIScroll(lore_name_list, lore_name_list.rect.topright)  # add subsection list scroll
    UIScroll(filter_tag_list, filter_tag_list.rect.topright)  # add filter list scroll

    return encyclopedia, lore_name_list, filter_tag_list, lore_buttons
