import csv
import os

from engine.utils.data_loading import csv_read, lore_csv_read


class Localisation:
    def __init__(self, debug=False):
        from engine.game.game import Game
        self.game = Game.game
        self.main_dir = Game.main_dir
        self.data_dir = Game.data_dir
        self.language = Game.language
        self.debug = debug
        # start with the creation of common UI localisation
        self.text = {"en": {"ui": csv_read(self.data_dir, "ui.csv", ("localisation", "en"),
                                           dict_value_return_as_str=True)},
                     self.language: {}}
        try:
            ui_language_file = csv_read(self.data_dir, "ui.csv", ("localisation", self.language),
                                        dict_value_return_as_str=True)
            self.text[self.language]["ui"] = ui_language_file
        except FileNotFoundError:
            pass

        self.read_localisation("building")
        self.read_localisation("character")
        self.read_localisation("faction")
        self.read_localisation("status")
        self.read_localisation("mission")
        self.read_localisation("scene")
        self.read_localisation("strategy")
        self.read_localisation("event")
        self.read_localisation("load")

        self.text["en"]["ai_speak"] = {}
        self.load_follower_talk_localisation("en")
        if self.language != "en":
            self.text[self.language]["ai_speak"] = {}
            self.text[self.language]["scene"] = {}
            self.load_follower_talk_localisation(self.language)

    def load_follower_talk_localisation(self, language):
        try:
            with open(os.path.join(self.data_dir, "localisation", language,
                                   "ai_speak" + ".csv"), encoding="utf-8", mode="r") as edit_file:
                rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
                rd = [row for row in rd]
                for index, row in enumerate(rd[1:]):
                    if row[0] not in self.text[language]["ai_speak"]:
                        self.text[language]["ai_speak"][row[0]] = {}
                    if row[1].split("_")[0] not in self.text[language]["ai_speak"][row[0]]:
                        self.text[language]["ai_speak"][row[0]][row[1].split("_")[0]] = []
                    self.text[language]["ai_speak"][row[0]][row[1].split("_")[0]].append(row[2])
            edit_file.close()
            for key, value in self.text[language]["ai_speak"].items():
                for key2, value2 in value.items():
                    self.text[language]["ai_speak"][key][key2] = tuple(value2)

        except FileNotFoundError:
            pass

    def read_localisation(self, file_name: str, subfolders=()):
        """
        Read localisation data
        :param file_name: File name to read
        :param subfolders: Subfolder list
        :return:
        """
        self.text["en"][file_name] = {}
        new_subfolder = ""
        if subfolders:
            for subfolder in subfolders:
                new_subfolder = os.path.join(new_subfolder, subfolder)
        with open(os.path.join(self.data_dir, "localisation", "en", new_subfolder,
                               file_name + ".csv"), encoding="utf-8", mode="r") as edit_file:
            lore_csv_read(edit_file, self.text["en"][file_name])
        edit_file.close()
        if self.language != "en":
            try:
                self.text[self.language][file_name] = {}
                with open(os.path.join(self.data_dir, "localisation", self.language, new_subfolder,
                                       file_name + ".csv"), encoding="utf-8", mode="r") as edit_file:
                    lore_csv_read(edit_file, self.text[self.language][file_name])
                edit_file.close()
            except FileNotFoundError:
                pass

    def grab_text(self, key, alternative_text_data=None):
        """
        Find localisation of provided object key name list,
        Return: Translated text if found in provided language, if not then English text, if not found anywhere then return key
        """
        text_data = self.text
        if alternative_text_data:
            text_data = alternative_text_data

        try:
            if self.language in text_data:  # in case config use language that not exist in data
                return self.inner_grab_text(key, self.language, text_data)
            else:
                return self.inner_grab_text(key, "en", text_data)
        except KeyError:  # no translation found
            # print(str(key) + " This key list is not found in " + self.language + " data")
            # self.game.error_log.write(str(key) + " This key list is not found in " + self.language + " data")
            return str(key)
            # try:  # key in language not found now search english
            #     return self.inner_grab_text(key, "en", text_data)
            # except KeyError:
            #     return str(key)

    def inner_grab_text(self, key, language, text_data):
        next_level = text_data[language]
        for subkey in key:
            if subkey not in next_level and self.debug:
                raise LookupError(self.language, key, "This key list is not found anywhere")
            next_level = next_level[subkey]
        return next_level
