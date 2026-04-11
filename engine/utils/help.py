# import numpy as np
# from PIL import Image
from os.path import join, split, abspath

import pygame

from engine.data.datamap import DataMap
from engine.data.datasprite import DataSprite
from engine.game.game import Game
from engine.utils.data_loading import load_images


class FakeGame:
    def __init__(self, sound_effect_pool):
        self.play_effect_volume = 0
        self.dt = 0.01
        self.sound_effect_pool = sound_effect_pool
        self.add_to_ui_menu_updater = None
        self.remove_from_ui_menu_updater = None
        self.button_sound_channel = None
        self.font_text_cache = {}
        self.config = {"VERSION": {
            "hash": "{'screen_resolution': (1360, 768), 'character': {}, 'effect': 'f14932053866e17234c8c76bbf184e1495ce5ddf8907bea346ed47a10d48fa4f'}"}}


pygame.init()
pen = pygame.display.set_mode((1, 1))
Game.game = FakeGame({})
current_dir = split(abspath(__file__))[0]
main_dir = current_dir[:current_dir.rfind("\\") + 1].split("\\")
main_dir = ''.join(stuff + "\\" for stuff in main_dir[:-2])  # one folder further back
data_dir = join(main_dir, "data")
Game.main_dir = main_dir
Game.data_dir = data_dir

campaign = "rabbit"
map_data = DataMap()
map_data.load_campaign_data(campaign)
sprite_data = DataSprite({}, initial_load_data=False)
building_portraits = load_images(data_dir, subfolder=("ui", "building_ui"))

grand_ui_images = load_images(data_dir, subfolder=("ui", "grand_ui"))

map_shown_to_base_scale_width = 5
map_shown_to_base_scale_height = 5
sprite_data.load_region_sprite(map_data, grand_ui_images, map_shown_to_base_scale_width,
                               map_shown_to_base_scale_height, campaign)


def make_image(specific=()):
    for region, image in sprite_data.region_sprites.items():
        if not specific or region in specific:
            region_data = map_data.region_list[region]
            region_rect = image.get_rect(center=((region_data["Region POS"][0] * map_shown_to_base_scale_width,
                                                  region_data["Region POS"][1] * map_shown_to_base_scale_height)))
            settlement_pos = region_data["Settlement POS"]

            settle_icon = pygame.Surface((200, 200))
            dot_rect = settle_icon.get_rect(center=(settlement_pos[0] * map_shown_to_base_scale_width,
                                                    settlement_pos[1] * map_shown_to_base_scale_height))
            blit_dot_rect = settle_icon.get_rect(topleft=(dot_rect.x - region_rect.x,
                                                          dot_rect.y - region_rect.y))
            image.blit(settle_icon, blit_dot_rect)

            for region_object in region_data["Object"].values():
                pos = (region_object[1], region_object[2])

                settle_icon = building_portraits["unique_rabbit_first_warren"]
                dot_rect = settle_icon.get_rect(center=(pos[0] * map_shown_to_base_scale_width,
                                                        pos[1] * map_shown_to_base_scale_height))

                blit_dot_rect = settle_icon.get_rect(topleft=(dot_rect.x - region_rect.x,
                                                              dot_rect.y - region_rect.y))
                image.blit(settle_icon, blit_dot_rect)

            pygame.image.save(image, region + ".png")


make_image(specific=("center9",))

#
# color_list = []
# im = Image.open("world.png")
# rgb_im = np.array(im)
# for row in rgb_im:
#     for col in row:
#         rgb = col
#         color_list.append((int(rgb[0]), int(rgb[1]), int(rgb[2])))
#
# color_list = list(set(color_list))
# print(color_list[0])
# print(len(color_list))

# from PIL import ImageColor
#
# import os
# import csv
# check = []
# with open("region.csv",
#           encoding="utf-8", mode="r") as edit_file:
#     rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
#     header = rd[0]
#     for index, row in enumerate(rd[1:]):
#         check.append(ImageColor.getrgb("#" + row[1]))
# edit_file.close()
#
# print(len(color_list), len(check), len(set(check)))
#
# from collections import Counter
#
# # Use Counter to count
# #the occurrences of each element in the list
# counts = Counter(check)
# duplicates = [item for item, count in counts.items() if count > 1]
# print(['#%02x%02x%02x' % item for item in duplicates], "asd")
#
# for item in color_list:
#     if item not in check:
#         print(item)
#
# print("hmasd")
# for item in check:
#     if item not in color_list:
#         print('#%02x%02x%02x' % item, item)
