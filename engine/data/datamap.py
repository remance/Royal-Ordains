import csv
import os
from copy import deepcopy
from pathlib import Path

from engine.constants import Route_Travel_Modifier
from engine.data.data import GameData
from engine.utils.data_loading import stat_convert, load_image, csv_read
from engine.utils.rotation import set_rotate


class DataMap(GameData):
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
            percent_column = ("Offence Modifier", "Defence Modifier", "Speed Modifier",
                              "Air Offence Modifier", "Air Defence Modifier", "Air Speed Modifier",)
            tuple_column = ("Status", "Spell")
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

        self.preset_map_data = {}
        self.region_list = {}
        self.route_list = {}
        self.route_dot_draw_array = {}
        self.dot_route_difficulty = {}
        self.route_pathfinding = {}
        self.start_army_list = {}
        self.event_list = {}
        self.faction_list = {}
        self.region_by_colour_index = {}
        self.region_by_pos_index = {}
        self.base_world_map = None
        self.default_grand_faction = None

    def load_campaign_data(self, campaign: str):
        self.region_list = {}
        self.region_by_colour_index = {}
        self.region_by_pos_index = {}
        with open(os.path.join(self.data_dir, "map", "world", campaign, "region.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            list_column = ["Build Slot " + str(index) for index in range(1, 11)]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            tuple_column = ("Region POS", "Settlement POS",)
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            dict_column = ("Object", "Route")
            dict_column = [index for index, item in enumerate(header) if item in dict_column]
            hex2colour_column = ("Colour",)
            hex2colour_column = [index for index, item in enumerate(header) if item in hex2colour_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, list_column=list_column, tuple_column=tuple_column,
                                       dict_column=dict_column, hex2colour_column=hex2colour_column)
                for header_index, value in enumerate(header):
                    if "Build Slot" in value and row[header_index]:
                        # add active building state to non-empty starting region building lists
                        if row[header_index]:
                            row[header_index].append(True)
                self.region_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
                self.region_by_colour_index[row[1]] = row[0]  # assume colour is column B
                self.region_by_pos_index[row[4]] = row[0]  # assume colour is column E
        edit_file.close()

        self.route_list = {}
        self.route_dot_draw_array = {}
        self.dot_route_difficulty = {}
        with open(os.path.join(self.data_dir, "map", "world", campaign, "route.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            list_column = ["Dots"]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            tuple_column = ("Route",)
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, list_column=list_column, tuple_column=tuple_column)
                self.route_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
                route_data = self.route_list[row[0]]
                dot_route = route_data["Dots"]
                for index, route in enumerate(dot_route):
                    if route[0] not in self.route_dot_draw_array:
                        self.route_dot_draw_array[route[0]] = {}
                    if index + 1 != len(dot_route):
                        self.route_dot_draw_array[route[0]][route[1]] = set_rotate(route, dot_route[index + 1])
                    else:  # next destination is settlement use settlement pos to calculate angle instead
                        self.route_dot_draw_array[route[0]][route[1]] = set_rotate(route, self.region_list[row[0][1]][
                            "Settlement POS"])
                    self.route_dot_draw_array[route[0]] = dict(sorted(self.route_dot_draw_array[route[0]].items()))
                    self.dot_route_difficulty[tuple(route)] = Route_Travel_Modifier[route_data["Type"]]

                # add settlement pos to route after dots draw since dots do not include settlement
                route_data["Dots"].insert(0, self.region_list[row[0][0]]["Settlement POS"])
                route_data["Dots"].append(self.region_list[row[0][1]]["Settlement POS"])
                # convert to tuple
                self.route_list[row[0]]["Dots"] = tuple([tuple(item) for item in self.route_list[row[0]]["Dots"]])

                # create reverse route for each one
                self.route_list[row[0][::-1]] = deepcopy(self.route_list[row[0]])
                self.route_list[row[0][::-1]]["Dots"] = self.route_list[row[0]]["Dots"][::-1]

        self.route_dot_draw_array = dict(sorted(self.route_dot_draw_array.items()))
        edit_file.close()

        self.event_list = {}
        with open(os.path.join(self.data_dir, "map", "world", campaign, "event.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            dict_column = ("Condition", "Effect")
            dict_column = [index for index, item in enumerate(header) if item in dict_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, dict_column=dict_column)
                self.event_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        self.base_world_map = load_image(self.data_dir, (1, 1), "world.png",
                                         ("map", "world", campaign), no_alpha=True)  # no scaling for this

        self.faction_list = {}
        with open(os.path.join(self.data_dir, "map", "world", campaign, "faction.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            hex2colour_column = ("Colour",)
            hex2colour_column = [index for index, item in enumerate(header) if item in hex2colour_column]
            dict_column = ("Faction Relation", "Diplomacy State")
            dict_column = [index for index, item in enumerate(header) if item in dict_column]
            tuple_column = ("Showcase Leader", "Showcase Troop")
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, tuple_column=tuple_column, dict_column=dict_column,
                                       hex2colour_column=hex2colour_column)
                self.faction_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        self.default_grand_faction = tuple(self.faction_list.keys())[0]

        self.start_army_list = {}
        with open(os.path.join(self.data_dir, "map", "world", campaign, "army.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i)
                self.start_army_list[row[0]] = {header[index]: stuff for index, stuff in enumerate(row)}
                self.start_army_list[row[0]]["Route"] = []
        edit_file.close()

    def read_map_data(self, campaign: str, map_name: str):
        read_folder = Path(os.path.join(self.data_dir, "map", "world", campaign, "preset"))
        sub1_directories = [x for x in read_folder.iterdir() if x.is_dir()]
        for file_map in sub1_directories:
            map_file_name = os.sep.join(os.path.normpath(file_map).split(os.sep)[-1:])
            if map_name == map_file_name:
                self.preset_map_data[map_name] = {}

                original_event_data, event_data = self.load_map_event_data(campaign, map_file_name)
                self.preset_map_data[map_name] = \
                    {"data": csv_read(file_map, "object_pos.csv", header_key=True),
                     "character": self.load_map_unit_data(campaign, map_file_name),
                     "event_data": original_event_data,
                     "event": event_data}
                break

    def load_map_event_data(self, campaign, map_id, scene_id=""):
        with open(os.path.join(self.data_dir, "map", "world", campaign, "preset", map_id, scene_id,
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
            original_event_data = deepcopy(event_data)
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

    def load_map_unit_data(self, campaign, map_id, scene_id=""):
        try:
            with open(os.path.join(self.data_dir, "map", "world", campaign, "preset", map_id, scene_id,
                                   "character_pos.csv"), encoding="utf-8", mode="r") as unit_file:
                rd = list(csv.reader(unit_file, quoting=csv.QUOTE_ALL))
                header = rd[0]
                int_column = ("Team",)  # value int only
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
