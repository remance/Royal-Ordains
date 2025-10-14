import csv
import os
from pathlib import Path

import pygame

from engine.data.datalocalisation import Localisation
from engine.data.datamap import BattleMapData
from engine.game.game import Game
from engine.utils.data_loading import csv_read

main_dir = os.path.split(os.path.abspath(__file__))[0]
main_dir = "\\".join(main_dir.split("\\")[:-2])
main_data_dir = os.path.join(main_dir, "data")

print(main_dir)

screen_size = (1300, 900)
screen_scale = (1, 1)

pygame.init()
pen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Animation Maker")  # set the self name on program border/tab
pygame.mouse.set_visible(False)  # set mouse as invisible, use cursor object instead

data_dir = os.path.join(main_dir, "data")
animation_dir = os.path.join(data_dir, "animation")
language = "en"

default_sprite_size = (600, 600)

ui = pygame.sprite.LayeredUpdates()
fake_group = pygame.sprite.LayeredUpdates()  # just fake group to add for container and not get auto update

Game.main_dir = main_dir
Game.data_dir = data_dir
Game.screen_size = screen_size
Game.screen_scale = screen_scale
Game.language = language
Game.ui_font = csv_read(data_dir, "ui_font.csv", ("ui",), header_key=True)
Game.font_dir = os.path.join(data_dir, "font")
Game.ui_updater = ui

localisation = Localisation()
Game.localisation = localisation
battle_map_data = BattleMapData()


def event_translation_check(language):
    """Check for existence of both event data and its localisation data for the input language"""
    read_folder = Path(os.path.join(data_dir, "map", "preset"))
    sub1_directories = [x for x in read_folder.iterdir() if x.is_dir()]
    for file_chapter in sub1_directories:
        read_folder = Path(os.path.join(data_dir, "map", "preset", file_chapter))
        chapter_file_name = os.sep.join(os.path.normpath(file_chapter).split(os.sep)[-1:])
        sub2_directories = [x for x in read_folder.iterdir() if x.is_dir()]
        for file_map in sub2_directories:
            map_file_name = os.sep.join(os.path.normpath(file_map).split(os.sep)[-1:])
            read_folder = Path(os.path.join(data_dir, "map", "preset", file_chapter, file_map))
            sub3_directories = [x for x in read_folder.iterdir() if x.is_dir()]
            for file_stage in sub3_directories:
                stage_file_name = os.sep.join(os.path.normpath(file_stage).split(os.sep)[-1:])
                if stage_file_name != "0":  # city scene use different reading
                    with open(os.path.join(data_dir, "map", "preset", chapter_file_name, map_file_name, stage_file_name,
                                           "event.csv"), encoding="utf-8", mode="r") as unit_file:
                        rd = list(csv.reader(unit_file, quoting=csv.QUOTE_ALL))
                        for item4 in rd:
                            if item4[1] and item4[1] != "Text ID" and item4[1] not in localisation.text[language][
                                "event"]:
                                print(chapter_file_name, map_file_name, stage_file_name, item4[1])
                else:  # city scene, read each scene
                    read_folder = Path(os.path.join(data_dir, "map", "preset", file_chapter, file_map, "0"))
                    sub4_directories = [x for x in read_folder.iterdir() if x.is_dir()]
                    for file_scene in sub4_directories:
                        scene_file_name = os.sep.join(os.path.normpath(file_scene).split(os.sep)[-1:])
                        with open(os.path.join(data_dir, "map", "preset", chapter_file_name, map_file_name,
                                               stage_file_name, scene_file_name,
                                               "event.csv"), encoding="utf-8", mode="r") as unit_file:
                            rd = list(csv.reader(unit_file, quoting=csv.QUOTE_ALL))
                            for item4 in rd:
                                if item4[1] and item4[1] != "Text ID" and item4[1] not in localisation.text[language][
                                    "event"]:
                                    print(chapter_file_name, map_file_name, stage_file_name, scene_file_name, item4[1])


event_translation_check("en")
