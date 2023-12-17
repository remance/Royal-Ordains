import csv
import os
from pathlib import Path

from engine.data.datastat import GameData
from engine.utils.data_loading import stat_convert, load_images, csv_read, filename_convert_readable as fcv


class BattleMapData(GameData):
    def __init__(self):
        """
        For keeping all data related to battle map.
        """
        GameData.__init__(self)

        self.weather_data = {}
        with open(os.path.join(self.data_dir, "map", "weather", "weather.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            int_column = ("ID",)  # value int only
            tuple_column = ("Element", "Status", "Spell")
            int_column = [index for index, item in enumerate(header) if item in int_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, tuple_column=tuple_column, int_column=int_column)
                self.weather_data[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        weather_list = [item["Name"] for item in self.weather_data.values()]
        strength_list = ("Light ", "Normal ", "Strong ")
        self.weather_list = []
        for item in weather_list:  # list of weather with different strength
            for strength in strength_list:
                self.weather_list.append(strength + item)
        self.weather_list = tuple(self.weather_list)
        edit_file.close()

        self.weather_matter_images = {}
        for this_weather in weather_list:  # Load weather matter sprite image
            try:
                images = load_images(self.data_dir, screen_scale=self.screen_scale,
                                     subfolder=("map", "weather", "matter", fcv(this_weather, revert=True)))
                self.weather_matter_images[this_weather] = tuple(images.values())
            except FileNotFoundError:
                self.weather_matter_images[this_weather] = ()

        weather_icon_list = load_images(self.data_dir, screen_scale=self.screen_scale,
                                        subfolder=("map", "weather", "icon"))  # Load weather icon
        self.weather_icon = {}
        for weather_icon in weather_list:
            for strength in range(0, 3):
                new_name = weather_icon + "_" + str(strength)
                for item in weather_icon_list:
                    if new_name == fcv(item):
                        self.weather_icon[new_name] = weather_icon_list[item]
                        break

        read_folder = Path(os.path.join(self.data_dir, "map", "preset"))
        sub1_directories = [x for x in read_folder.iterdir() if x.is_dir()]

        self.stage_reward = {}
        self.reward_list = {}
        with open(os.path.join(self.data_dir, "map", "choice.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            dict_column = ("Reward",)
            dict_column = [index for index, item in enumerate(header) if item in dict_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, tuple_column=tuple_column, dict_column=dict_column)
                if row[0] not in self.stage_reward:  # choice
                    self.stage_reward[row[0]] = {}
                if row[1] not in self.stage_reward[row[0]]:  # chapter
                    self.stage_reward[row[0]][row[1]] = {}
                if row[2] not in self.stage_reward[row[0]][row[1]]:  # mission
                    self.stage_reward[row[0]][row[1]][row[2]] = {}
                if row[3] not in self.stage_reward[row[0]][row[1]][row[2]]:  # stage
                    self.stage_reward[row[0]][row[1]][row[2]][row[3]] = {}
                self.stage_reward[row[0]][row[1]][row[2]][row[3]] = {row[4]: row[5]}
                self.reward_list[row[4]] = row[5]
        edit_file.close()

        preset_map_list = []
        self.preset_map_folder = []  # folder for reading later
        self.battle_campaign = {}
        self.preset_map_data = {}

        for file_campaign in sub1_directories:
            read_folder = Path(os.path.join(self.data_dir, "map", "preset", file_campaign))
            campaign_file_name = os.sep.join(os.path.normpath(file_campaign).split(os.sep)[-1:])
            sub2_directories = [x for x in read_folder.iterdir() if x.is_dir()]

            self.preset_map_data[int(campaign_file_name)] = {}
            for file_map in sub2_directories:
                map_file_name = os.sep.join(os.path.normpath(file_map).split(os.sep)[-1:])
                self.preset_map_folder.append(map_file_name)
                map_name = self.localisation.grab_text(key=("preset_map", campaign_file_name,
                                                            "info", map_file_name, "Name"))
                preset_map_list.append(map_name)
                self.battle_campaign[int(map_file_name)] = campaign_file_name
                self.preset_map_data[int(campaign_file_name)][int(map_file_name)] = {}

                read_folder = Path(os.path.join(self.data_dir, "map", "preset", file_campaign, file_map))
                sub3_directories = [x for x in read_folder.iterdir() if x.is_dir()]
                for file_source in sub3_directories:
                    source_file_name = os.sep.join(os.path.normpath(file_source).split(os.sep)[-1:])
                    self.preset_map_data[int(campaign_file_name)][int(map_file_name)][int(source_file_name)] = \
                        {"data": csv_read(file_source, "object_pos.csv", header_key=True),
                         "character": self.load_map_unit_data(campaign_file_name, map_file_name, source_file_name),
                         "stage_event": csv_read(file_source, "event.csv", header_key=True)}

    def load_map_unit_data(self, campaign_id, map_id, map_source):
        try:
            with open(os.path.join(self.data_dir, "map", "preset", campaign_id, map_id, map_source,
                                   "character_pos.csv"), encoding="utf-8", mode="r") as unit_file:
                rd = list(csv.reader(unit_file, quoting=csv.QUOTE_ALL))
                header = rd[0]
                int_column = ("Team",)  # value int only
                list_column = ("POS", "Arrive Condition")  # value in list only
                float_column = ("Angle", "Start Health", "Start Stamina")  # value in float
                int_column = [index for index, item in enumerate(header) if item in int_column]
                list_column = [index for index, item in enumerate(header) if item in list_column]
                float_column = [index for index, item in enumerate(header) if item in float_column]

                for data_index, data in enumerate(rd[1:]):  # skip header
                    for n, i in enumerate(data):
                        data = stat_convert(data, n, i, list_column=list_column, int_column=int_column,
                                            float_column=float_column)
                        for item in data:
                            if type(item) is dict:  # change troop number string to list
                                for key, value in item.items():
                                    if type(value) is str:
                                        item[key] = [int(value2) for value2 in value.split("/")]

                    rd[data_index + 1] = {header[index]: stuff for index, stuff in enumerate(data)}
                char_data = rd[1:]
            unit_file.close()
            return char_data
        except FileNotFoundError as b:
            print(b)
            return {}
