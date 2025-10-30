import os
import pickle
from pathlib import Path

from engine.data.datastat import GameData

empty_game_save = {"playtime": 0, "stats": {}, "game state": {}, "map state": {}, "dialogue log": []}

empty_main_save = {"playtime": 0, "unlock": {"character": [], "faction_ui": [], "timeline": []},
                   "new": {"character": [], "faction_ui": [], "timeline": []}}


class SaveData(GameData):
    def __init__(self):
        """
        For keeping all data related to player character save.
        """
        GameData.__init__(self)

        self.save_profile = None
        save_folder_path = os.path.join(self.main_dir, "save")
        if not os.path.isdir(save_folder_path):  # no save data folder inside game folder
            os.mkdir(save_folder_path)  # create save folder

        # Read save file
        read_folder = Path(save_folder_path)
        sub1_directories = [x for x in read_folder.iterdir() if x.is_file()]
        if "game.dat" not in [os.sep.join(os.path.normpath(item).split(os.sep)[-1:]) for
                              item in sub1_directories]:  # make common game save data
            self.make_save_file(os.path.join(self.main_dir, "save", "game.dat"), empty_game_save)
        self.save_profile = self.load_save_file(os.path.join(self.main_dir, "save", "game.dat"))

        if "custom_army.dat" not in [os.sep.join(os.path.normpath(item).split(os.sep)[-1:]) for
                                     item in sub1_directories]:  # make common game save data
            self.make_save_file(os.path.join(self.main_dir, "save", "custom_army.dat"), {})
        self.custom_army_preset_save = self.load_save_file(os.path.join(self.main_dir, "save", "custom_army.dat"))

    @staticmethod
    def make_save_file(file_name, save_data):
        with open(file_name, "wb") as f:
            pickle.dump(save_data, f, protocol=2)

    @staticmethod
    def load_save_file(file_name):
        with open(file_name, "rb") as f:
            return pickle.load(f)

    @staticmethod
    def remove_save_file(file_name):
        if os.path.isfile(file_name):
            os.remove(file_name)
