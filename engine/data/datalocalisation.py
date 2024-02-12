import csv
import os

from engine.utils.data_loading import csv_read, lore_csv_read


class Localisation:
    def __init__(self, debug=False):
        from engine.game.game import Game
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

        self.read_module_lore("history", "history")
        self.read_module_lore("character", "character")
        self.read_module_lore("enemy", "enemy")
        self.read_module_lore("item", "item")
        self.read_module_lore("status", "status")
        self.read_module_lore("event", "event")
        self.read_module_lore("help", "help")

        # Load map description
        self.text["en"]["map"] = {}

        self.load_map_lore("en")
        if self.language != "en":
            self.load_map_lore(self.language)

    def load_map_lore(self, language):
        try:
            with open(os.path.join(self.data_dir, "localisation", language, "stage.csv"),
                      encoding="utf-8", mode="r") as edit_file:  # read map info file
                rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
                rd = [row for row in rd]
                for index, row in enumerate(rd[1:]):
                    row = [int(item) if item.isdigit() else item for item in row]
                    if row[0]:  # chapter, no need for else since must have chapter
                        if row[0] not in self.text[language]["map"]:
                            self.text[language]["map"][row[0]] = {}
                        if row[1]:  # mission
                            if row[1] not in self.text[language]["map"][row[0]]:
                                self.text[language]["map"][row[0]][row[1]] = {}
                            if row[2]:  # stage
                                if row[2] not in self.text[language]["map"][row[0]][row[1]]:
                                    self.text[language]["map"][row[0]][row[1]][row[2]] = {}
                                if row[3]:  # scene
                                    if row[3] not in self.text[language]["map"][row[0]][row[1]][row[2]]:
                                        # last at scene
                                        self.text[language]["map"][row[0]][row[1]][row[2]][row[3]] = {"Text": row[4]}
                                else:
                                    self.text[language]["map"][row[0]][row[1]][row[2]]["Text"] = row[4]
                            else:
                                self.text[language]["map"][row[0]][row[1]]["Text"] = row[4]
                        else:
                            self.text[language]["map"][row[0]]["Text"] = row[4]
            edit_file.close()
        except FileNotFoundError:
            pass

    def read_module_lore(self, lore_type, lore_key):
        """
        Read module lore data
        :param lore_type: File names to read
        :param lore_key: key name
        :return:
        """
        self.text["en"][lore_key] = {}
        if not isinstance(lore_type, (list, tuple)):
            lore_type = [lore_type]
        for lore in lore_type:
            with open(os.path.join(self.data_dir, "localisation", "en",
                                   lore + ".csv"), encoding="utf-8", mode="r") as edit_file:
                lore_csv_read(edit_file, self.text["en"][lore_key])
            edit_file.close()
            if self.language != "en":
                try:
                    self.text[self.language][lore_key] = {}
                    with open(os.path.join(self.data_dir, "localisation", self.language,
                                           lore + ".csv"), encoding="utf-8", mode="r") as edit_file:
                        lore_csv_read(edit_file, self.text[self.language][lore_key])
                    edit_file.close()
                except FileNotFoundError:
                    pass

    def grab_text(self, key=(), alternative_text_data=None):
        """
        Find localisation of provided object key name,
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
            if self.debug:
                raise LookupError(self.language, key, "This key list is not found in " + self.language, " data")
            try:  # key in language not found now search english
                return self.inner_grab_text(key, "en", text_data)
            except KeyError:
                if self.debug:
                    raise LookupError(self.language, key, "This key list is not found anywhere")
                return str(key)

    def create_lore_data(self, key_type):
        lore_data = self.text["en"][key_type]
        if key_type in self.text[self.language]:  # replace english with available localisation of selected language
            for key in self.text[self.language][key_type]:
                lore_data[key] = self.text[self.language][key_type][key]
        return lore_data

    def inner_grab_text(self, key, language, text_data):
        next_level = text_data[language]
        for subkey in key:
            if subkey not in next_level and self.debug:
                raise LookupError(self.language, key, "This key list is not found anywhere")
            next_level = next_level[subkey]
        return next_level
