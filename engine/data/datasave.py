import os
import pickle
from pathlib import Path

from engine.data.datastat import GameData

empty_character_save = {"chapter": "1", "mission": "1", "playtime": 0, "total scores": 0, "total kills": 0,
                        "total golds": 500, "boss kills": 0, "total damages": 0, "last save": "Not Saved",
                        "character": {},
                        "equipment": {"head": None, "chest": None, "arm": None, "leg": None,
                                      "weapon 1": None, "weapon 2": None, "accessory 1": None, "accessory 2": None,
                                      "accessory 3": None, "accessory 4": None,
                                      "item": {"Down": None, "Left": None, "Up": None, "Right": "Small Healing Kit"}},
                        "storage": {"Small Healing Kit": 5}, "storage_new": ["Small Healing Kit"], "story event": {},
                        "interface event queue": {"courtbook": {}, "mission": [], "inform": []},
                        "story choice": {}, "selected follower preset": 0,
                        "follower preset": {0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7: {}, 8: {},
                                            9: {}, 10: {}, 11: {}}, "follower list": [], "dialogue log": [],
                        "save state": {"court": {"King": "King", "Queen": None, "Regent": None,
                                                 "Grand Marshal": "Vurus", "Royal Champion": "Vars",
                                                 "King Of Arms": "Vurus", "Provost Marshal": "Picrieas",
                                                 "Vice Marshal": "Knedhel", "Hound Keeper": None,
                                                 "Lord Chamberlain": "Serlon", "Confidant": "Nayedien",
                                                 "Chief Scholar": "Micorte", "Vice Chamberlain": "Luriel",
                                                 "Seneschal": "Serlon", "Flower Keeper": "Rudehst",
                                                 "Court Jester": "Dashisi", "Master Of Ceremony": "Kapuni",
                                                 "Health Keeper": "Peurrus", "Master Of Ride": "Merlaros",
                                                 "Court Herald": "Hermanos", "Faith Keeper": "Monnirl",
                                                 "Lord Chancellor": "Solhatar", "Secret Keeper": "Vurus",
                                                 "Chief Justiciar": "Severn", "Prime Minister": "Solhatar",
                                                 "Chief Architect": "Velmidas", "Lord Judge": "Kervos",
                                                 "Lord Steward": "Elghest", "Chief Verderer": "Merlaros",
                                                 "Court Mage": "Furlest", "Master Of Hunt": "Viskes"}}}

empty_game_save = {"chapter": 1, "mission": 1, "unlock": {"character": []}}


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
            self.make_save_file(os.path.join(self.main_dir, "save", "game.dat"), empty_game_save)

        sub1_directories = [x for x in read_folder.iterdir() if x.is_file()]  # to include new game.dat save
        for save_file in sub1_directories:
            file_name = os.sep.join(os.path.normpath(save_file).split(os.sep)[-1:])
            if file_name != "game.dat":
                self.save_profile["character"][int(file_name.split(".")[0])] = self.load_save_file(save_file)
            else:
                self.save_profile[file_name.split(".")[0]] = self.load_save_file(save_file)

    @staticmethod
    def make_save_file(file_name, profile_data):
        data = profile_data  # remove unrelated stuff
        if "character" in data:
            data["character"] = {key: value for key, value in data["character"].items() if
                                 key not in ("Object", "Team", "Playable")}
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
