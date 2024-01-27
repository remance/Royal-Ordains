import os
import pickle

from pathlib import Path

from engine.data.datastat import GameData


class SaveData(GameData):
    def __init__(self):
        """
        For keeping all data related to player character save.
        """
        GameData.__init__(self)

        self.save_profile = {"character": {}}
        save_folder_path = os.path.join(self.main_dir, "save")
        if not os.path.isdir(save_folder_path):  # no save data folder inside game folder
            os.mkdir(save_folder_path)  # create save folder

        # Read save file
        read_folder = Path(save_folder_path)
        sub1_directories = [x for x in read_folder.iterdir() if x.is_file()]
        if "game.dat" not in [os.sep.join(os.path.normpath(item).split(os.sep)[-1:]) for
                              item in sub1_directories]:  # make common game save data
            self.make_save_file(os.path.join(self.main_dir, "save", "game.dat"), {"last chapter": 1, "last mission": 1})
        for save_file in sub1_directories:
            file_name = os.sep.join(os.path.normpath(save_file).split(os.sep)[-1:])
            if file_name != "game.dat":
                self.save_profile["character"][int(file_name.split(".")[0])] = self.load_save_file(save_file)
            else:
                self.save_profile[file_name.split(".")[0]] = self.load_save_file(save_file)

    @staticmethod
    def make_save_file(file_name, profile_data):
        data = profile_data  # remove unrelated stuff
        data["character"] = {key: value for key, value in data["character"].items() if key not in ("Object", "Team", "Playable")}
        with open(file_name, "wb") as f:
            pickle.dump(data, f, protocol=2)

    @staticmethod
    def load_save_file(file_name):
        with open(file_name, "rb") as f:
            return pickle.load(f)

    @staticmethod
    def remove_save_file(file_name):
        if os.path.isfile(file_name):
            os.remove(file_name)
