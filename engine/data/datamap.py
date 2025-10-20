import copy
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
        with open(os.path.join(self.data_dir, "map", "stage", "weather", "weather.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            percent_column = ("Offence Modifier", "Defence Modifier", "Speed Modifier",
                              "Air Offence Modifier", "Air Defence Modifier", "Air Speed Modifier",)
            tuple_column = ("Element", "Status", "Spell")
            dict_column = ("Spawn Cooldown", "Property",)
            percent_column = [index for index, item in enumerate(header) if item in percent_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            dict_column = [index for index, item in enumerate(header) if item in dict_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, percent_column=percent_column,
                                       tuple_column=tuple_column, dict_column=dict_column)
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
                                     subfolder=("map", "stage", "weather", "matter", fcv(this_weather, revert=True)))
                self.weather_matter_images[this_weather] = tuple(images.values())
            except FileNotFoundError:
                self.weather_matter_images[this_weather] = ()

        read_folder = Path(os.path.join(self.data_dir, "map", "stage", "preset"))
        sub1_directories = [x for x in read_folder.iterdir() if x.is_dir()]

        self.preset_map_data = {}
        for file_map in sub1_directories:
            map_file_name = os.sep.join(os.path.normpath(file_map).split(os.sep)[-1:])
            self.preset_map_data[map_file_name] = {}

            if map_file_name != "event":  # city scene use different reading
                original_event_data, event_data = self.load_map_event_data(map_file_name)
                self.preset_map_data[map_file_name] = \
                    {"data": csv_read(file_map, "object_pos.csv", header_key=True),
                     "character": self.load_map_unit_data(map_file_name),
                     "event_data": original_event_data,
                     "event": event_data}
            else:  # events, read each scene
                read_folder = Path(os.path.join(self.data_dir, "map", "stage", "preset", "event"))
                sub4_directories = [x for x in read_folder.iterdir() if x.is_dir()]
                for file_scene in sub4_directories:
                    scene_file_name = fcv(os.sep.join(os.path.normpath(file_scene).split(os.sep)[-1:]))
                    original_event_data, event_data = self.load_map_event_data(map_file_name.lower(),
                                                                               scene_id=scene_file_name.lower())
                    self.preset_map_data[map_file_name][
                        scene_file_name] = \
                        {"data": csv_read(file_scene, "object_pos.csv", header_key=True),
                         "character": self.load_map_unit_data(map_file_name.lower(),
                                                              scene_id=scene_file_name.lower()),
                         "event_data": original_event_data,
                         "event": event_data}

    def load_map_event_data(self, map_id, scene_id=""):
        with open(os.path.join(self.data_dir, "map", "stage", "preset", map_id, scene_id,
                               "event.csv"), encoding="utf-8", mode="r") as unit_file:
            rd = list(csv.reader(unit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            tuple_column = ("Trigger",)
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            dict_column = ("Property",)
            dict_column = [index for index, item in enumerate(header) if item in dict_column]
            for data_index, data in enumerate(rd[1:]):  # skip header
                for n, i in enumerate(data):
                    data = stat_convert(data, n, i, tuple_column=tuple_column, dict_column=dict_column)
                rd[data_index + 1] = {header[index]: stuff for index, stuff in enumerate(data)}
            event_data = rd[1:]
            # keep event data in trigger structure for easier check
            original_event_data = copy.deepcopy(event_data)
            if event_data:
                final_event_data = {"music": []}
                for item in event_data:
                    if item["ID"]:  # item with no parent ID mean it is child of previous found parent
                        next_level = final_event_data
                        for trigger in item["Trigger"]:
                            if trigger not in next_level:
                                next_level[trigger] = {}
                            next_level = next_level[trigger]
                        parent_id = item["ID"]
                        if parent_id not in next_level:
                            next_level[parent_id] = []
                    if item["Type"] == "music":  # add music to list for loading
                        final_event_data["music"].append(str(item["Object"]))
                    next_level[parent_id].append(item)
                unit_file.close()
                return original_event_data, final_event_data

            unit_file.close()
            return original_event_data, event_data

    def load_map_unit_data(self, map_id, scene_id=""):
        try:
            with open(os.path.join(self.data_dir, "map", "stage", "preset", map_id, scene_id,
                                   "character_pos.csv"), encoding="utf-8", mode="r") as unit_file:
                rd = list(csv.reader(unit_file, quoting=csv.QUOTE_ALL))
                header = rd[0]
                int_column = ("Team", )  # value int only
                dict_column = ("Followers", "Behaviour", "Stage Property", "Arrive Condition")
                int_column = [index for index, item in enumerate(header) if item in int_column]
                dict_column = [index for index, item in enumerate(header) if item in dict_column]

                for data_index, data in enumerate(rd[1:]):  # skip header
                    for n, i in enumerate(data):
                        data = stat_convert(data, n, i, int_column=int_column, dict_column=dict_column)
                    rd[data_index + 1] = {header[index]: stuff for index, stuff in enumerate(data)}
                char_data = rd[1:]
            unit_file.close()
            return char_data
        except FileNotFoundError as b:
            print(b)
            return {}
