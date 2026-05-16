import csv
import os
from engine.game.game import Game

from engine.data.datastat import stat_convert, DataStat
current_dir = os.path.split(os.path.abspath(__file__))[0]

main_dir = current_dir[:current_dir.rfind("\\") + 1].split("\\")
main_dir = ''.join(stuff + "\\" for stuff in main_dir[:-2])  # one folder further back
print(main_dir)
data_dir = os.path.join(main_dir, "data")

Game.main_dir = main_dir
Game.data_dir = data_dir

character_data = DataStat()


# check status existence
for char_id, character in character_data.character_list.items():
    for move_id, move in character["Move"].items():
        if move["Power"] and (not move["Element"] or move["Element"] not in ("slash", "crush", "stab", "fire", "water",
                                                          "air", "earth", "magic", "poison")):
            print("Element need to check", move["Element"], char_id, move_id)
        for status in move["Status"]:
            if status not in character_data.status_list:
                print("status not found", status, char_id, move_id)
        for status in move["Enemy Status"]:
            if status not in character_data.status_list:
                print("enemy status not found", status, char_id, move_id)
        for status in move["Effect Enemy Status"]:
            if status not in character_data.status_list:
                print("effect enemy status not found", status, char_id, move_id)