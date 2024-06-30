"""This file contains all class and function that read troop/leader related data
and save them into dict for in game use """

import copy
import csv
import os

from engine.utils.data_loading import stat_convert, load_images


class GameData:
    def __init__(self):
        from engine.game.game import Game
        self.main_dir = Game.main_dir
        self.data_dir = Game.data_dir
        self.font_dir = Game.font_dir
        self.localisation = Game.localisation
        self.screen_scale = Game.screen_scale


class CharacterData(GameData):
    def __init__(self):
        """
        For keeping all data related to character.
        """
        GameData.__init__(self)

        # Character status effect dict
        self.status_list = {}
        with open(os.path.join(self.data_dir, "character", "status.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            int_column = ("ID", "Power Bonus", "Speed Bonus",)  # value int only
            float_column = ("Animation Time Modifier", "Physical Resistance Bonus", "Fire Resistance Bonus",
                            "Water Resistance Bonus", "Air Resistance Bonus", "Earth Resistance Bonus",
                            "Magic Resistance Bonus", "Poison Resistance Bonus", "Magic Resistance Bonus")
            tuple_column = ("Special Effect", "Status Conflict")  # value in tuple only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            float_column = [index for index, item in enumerate(header) if item in float_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, tuple_column=tuple_column, int_column=int_column,
                                       float_column=float_column)
                self.status_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        self.status_lore = self.localisation.create_lore_data("status")

        self.common_moveset_skill = {}
        with open(os.path.join(self.data_dir, "character", "playable", "skill.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            tuple_column = ("Buttons", "Status", "Enemy Status")  # value in tuple only
            dict_column = ("Prepare Animation", "After Animation", "AI Condition", "Property",)
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            dict_column = [index for index, item in enumerate(header) if item in dict_column]
            moveset_dict = {}
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, tuple_column=tuple_column,
                                       dict_column=dict_column)
                move_data = {header[index]: stuff for index, stuff in enumerate(row)}
                if row[header.index("Position")] not in moveset_dict:
                    # keep moveset in each position dict for easier access
                    moveset_dict[row[header.index("Position")]] = {}
                moveset_dict[row[header.index("Position")]][row[0]] = move_data
            self.common_moveset_skill = moveset_dict
        edit_file.close()

        # Equipment dict
        self.equipment_list = {}
        # with open(os.path.join(self.data_dir, "troop", "troop_armour.csv"),
        #           encoding="utf-8", mode="r") as edit_file:
        #     rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
        #     header = rd[0]
        #     int_column = ("ID", "Cost")  # value int only
        #     list_column = ("Trait",)  # value in list only
        #     tuple_column = ()  # value in tuple only
        #     int_column = [index for index, item in enumerate(header) if item in int_column]
        #     list_column = [index for index, item in enumerate(header) if item in list_column]
        #     tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
        #     for row_index, row in enumerate(rd[1:]):
        #         for n, i in enumerate(row):
        #             row = stat_convert(row, n, i, list_column=list_column, tuple_column=tuple_column,
        #                                int_column=int_column)
        #         self.armour_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        # edit_file.close()
        #

        # Character stat dict
        default_mode = {}
        with open(os.path.join(self.data_dir, "animation", "template.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            for index, stuff in enumerate(rd[0]):
                if "special" in stuff:  # remove number after special
                    rd[0][index] = "_".join(rd[0][index].split("_")[:-1])
            default_mode["Normal"] = {stuff: "Normal" for
                                      index, stuff in enumerate(rd[0]) if stuff[0] == "p"}

        self.character_list = {}
        folder_list = ("playable", "enemy")
        for file_index, char_list in enumerate(("playable.csv", "enemy.csv")):
            with open(os.path.join(self.data_dir, "character", char_list),
                      encoding="utf-8", mode="r") as edit_file:
                rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
                header = rd[0]
                for row_index, row in enumerate(rd[1:]):
                    int_column = ("Only Sprite Version",)  # value in tuple only
                    int_column = [index for index, item in enumerate(header) if item in int_column]
                    dict_column = ("Drops", "Spawns", "Items", "Property")
                    dict_column = [index for index, item in enumerate(header) if item in dict_column]
                    for n, i in enumerate(row):
                        row = stat_convert(row, n, i, int_column=int_column, dict_column=dict_column)
                    self.character_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
                    self.character_list[row[0]]["Move"] = {}

                    # Add character move data
                    if os.path.exists(
                            os.path.join(self.data_dir, "character", folder_list[file_index], row[0], "move.csv")):
                        with open(os.path.join(self.data_dir, "character", folder_list[file_index], row[0], "move.csv"),
                                  encoding="utf-8", mode="r") as edit_file2:
                            rd2 = tuple(csv.reader(edit_file2, quoting=csv.QUOTE_ALL))
                            header2 = rd2[0]
                            tuple_column = (
                                "Buttons", "Requirement Move", "Status", "Enemy Status")  # value in tuple only
                            tuple_column = [index for index, item in enumerate(header2) if item in tuple_column]
                            dict_column = ("Stat Requirement", "Prepare Animation", "After Animation", "AI Condition", "Property",)
                            dict_column = [index for index, item in enumerate(header2) if item in dict_column]
                            moveset_dict = {}
                            remain_next_move_loop = []
                            for row_index2, row2 in enumerate(rd2[1:]):
                                for n2, i2 in enumerate(row2):
                                    row2 = stat_convert(row2, n2, i2, tuple_column=tuple_column,
                                                        dict_column=dict_column)

                                move_data = {header2[index]: stuff for index, stuff in enumerate(row2)}
                                if row2[header2.index("Position")] not in moveset_dict:
                                    # keep moveset in each position dict for easier access
                                    moveset_dict[row2[header2.index("Position")]] = {}

                                if not row2[header2.index("Requirement Move")]:
                                    # parent move
                                    moveset_dict[row2[header2.index("Position")]][row2[0]] = move_data

                                # restructure moveset so move that continue from another is in its parent move
                                parent_move_list = row2[header2.index("Requirement Move")]
                                if "all child moveset" in move_data["Property"]:
                                    parent_move_list = [row3[header2.index("Move")] for row3 in rd2 if
                                                        row3[header2.index("Position")] == move_data["Position"]][1:]
                                if row2[header2.index("Requirement Move")] or "all child moveset" in move_data[
                                    "Property"]:
                                    found = None
                                    for parent_move in parent_move_list:
                                        done_check = [False]
                                        already_check = []
                                        final_parent_moveset(moveset_dict[row2[header2.index("Position")]],
                                                             row2[0], move_data, parent_move, done_check,
                                                             already_check)
                                        if False in done_check:
                                            if found:
                                                remain_next_move_loop.append(
                                                    (moveset_dict[row2[header2.index("Position")]],
                                                     row2[0], found, parent_move))
                                            else:
                                                remain_next_move_loop.append(
                                                    (moveset_dict[row2[header2.index("Position")]],
                                                     row2[0], move_data, parent_move))
                                        else:
                                            found = done_check[0]
                            for item in remain_next_move_loop:
                                # one last try to find parent in case it order in data is lower
                                done_check = ["test"]
                                already_check = []
                                final_parent_moveset(item[0], item[1], item[2], item[3], done_check, already_check)

                            self.character_list[row[0]]["Move"] = moveset_dict
                            self.character_list[row[0]]["Move Original"] = {}

                            for row2 in rd2[1:]:
                                if row2[header2.index("Position")] not in self.character_list[row[0]]["Move Original"]:
                                    self.character_list[row[0]]["Move Original"][row2[header2.index("Position")]] = {}
                                self.character_list[row[0]]["Move Original"][row2[header2.index("Position")]][row2[1]] = \
                                    {header2[index]: stuff for index, stuff in enumerate(row2)}
                            edit_file2.close()

                    self.character_list[row[0]]["Skill"] = {}
                    if os.path.exists(
                            os.path.join(self.data_dir, "character", folder_list[file_index], row[0], "skill.csv")):
                        # Add character skill data
                        with open(
                                os.path.join(self.data_dir, "character", folder_list[file_index], row[0], "skill.csv"),
                                encoding="utf-8", mode="r") as edit_file2:
                            rd = tuple(csv.reader(edit_file2, quoting=csv.QUOTE_ALL))
                            header2 = rd[0]
                            tuple_column = (
                            "Buttons", "Requirement Move", "Status", "Enemy Status")  # value in tuple only
                            dict_column = ("Prepare Animation", "After Animation", "AI Condition", "Property",)
                            tuple_column = [index for index, item in enumerate(header2) if item in tuple_column]
                            dict_column = [index for index, item in enumerate(header2) if item in dict_column]
                            moveset_dict = {}
                            moveset_ui_dict = {}
                            for index2, row2 in enumerate(rd[1:]):
                                for n2, i2 in enumerate(row2):
                                    row2 = stat_convert(row2, n2, i2, tuple_column=tuple_column,
                                                        dict_column=dict_column)
                                move_data = {header2[index + 1]: stuff for index, stuff in enumerate(row2[1:])}
                                if row2[header2.index("Position")] not in moveset_dict:
                                    # keep moveset in each position dict for easier access
                                    moveset_dict[row2[header2.index("Position")]] = {}
                                moveset_dict[row2[header2.index("Position")]][row2[0]] = move_data
                                moveset_ui_dict[row2[0]] = move_data
                            self.character_list[row[0]]["Skill"] = moveset_dict
                            self.character_list[row[0]]["Skill UI"] = moveset_ui_dict
                        edit_file2.close()

                    # Add character mode data
                    self.character_list[row[0]]["Mode"] = {"Normal": default_mode["Normal"],
                                                           "City": default_mode["Normal"]}
                    if os.path.exists(
                            os.path.join(self.data_dir, "character", folder_list[file_index], row[0], "mode.csv")):
                        with open(os.path.join(self.data_dir, "character", folder_list[file_index], row[0], "mode.csv"),
                                  encoding="utf-8", mode="r") as edit_file2:
                            rd2 = tuple(csv.reader(edit_file2, quoting=csv.QUOTE_ALL))
                            header2 = rd2[0]
                            for row_index2, row2 in enumerate(rd2[1:]):
                                self.character_list[row[0]]["Mode"][row2[0]] = {header2[index + 1]: stuff for
                                                                                index, stuff in enumerate(row2[1:])}
                edit_file.close()

        self.character_portraits = load_images(self.data_dir, screen_scale=self.screen_scale,
                                               subfolder=("character", "portrait"),
                                               key_file_name_readable=True)

        # Drop item
        self.drop_item_list = {}
        with open(os.path.join(self.data_dir, "character", "drop.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            tuple_column = ("Status", "Property")  # value in tuple only
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, tuple_column=tuple_column)
                self.drop_item_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        # Equip Item
        self.equip_item_list = {}
        with open(os.path.join(self.data_dir, "character", "item.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            str_column = ("Chapter", "Mission", "Stage")
            str_column = [index for index, item in enumerate(header) if item in str_column]
            tuple_column = ("Status", "Enemy Status", "Property")  # value in tuple only
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, tuple_column=tuple_column, str_column=str_column)
                self.equip_item_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        self.gear_list = {}
        with open(os.path.join(self.data_dir, "character", "gear.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            dict_column = ("Modifier",)  # value in tuple only
            dict_column = [index for index, item in enumerate(header) if item in dict_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, dict_column=dict_column)
                self.gear_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        self.shop_list = self.equip_item_list | self.gear_list

        gear_mod_list = {}
        # use structure as gear type: mod id: "rarity", "weight", "chance"  for easier access
        self.gear_mod_list = {"weapon": {}, "head": {}, "chest": {}, "arm": {}, "leg": {}, "accessory": {}}
        with open(os.path.join(self.data_dir, "character", "gear_mod.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            tuple_column = ("Standard", "Quality", "Master Work", "Enchanted", "Legendary", "Gear Type")
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, tuple_column=tuple_column)
                gear_mod_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
            for gear_type in self.gear_mod_list:
                for mod in gear_mod_list:
                    if gear_type in gear_mod_list[mod]["Gear Type"]:
                        self.gear_mod_list[gear_type][mod] = gear_mod_list[mod]
        edit_file.close()

        # Effect that exist as its own sprite in battle
        self.effect_list = {}
        with open(os.path.join(self.data_dir, "character", "effect.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            tuple_column = ("Status Conflict", "Status", "Enemy Status",
                            "Special Effect")  # value in tuple only
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            dict_column = ("Property",)
            dict_column = [index for index, item in enumerate(header) if item in dict_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, tuple_column=tuple_column, dict_column=dict_column)
                self.effect_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()


def final_parent_moveset(parent_move_data, move_key, move_data, parent_move_name, done_check, already_check):
    try:
        recursive_find_parent_moveset(parent_move_data, move_key, move_data, parent_move_name, done_check,
                                      already_check)
        return
    except ValueError:
        return


def recursive_find_parent_moveset(parent_move_data, move_key, move_data, parent_move_name, done_check, already_check):
    for k, v in parent_move_data.items():
        if v["Move"] == parent_move_name:  # found parent move
            if "Next Move" not in v:
                v["Next Move"] = {}
            # if move_data not in v["Next Move"][move_key]:
            v["Next Move"][move_key] = move_data
            done_check[0] = move_data
            raise ValueError("Found, end recursive")
        else:  # not yet search deeper
            if "Next Move" in v and v["Move"] not in already_check:
                already_check.append(v["Move"])  # add move to already check to prevent unending loop
                recursive_find_parent_moveset(v["Next Move"], move_key, move_data, parent_move_name, done_check,
                                              already_check)


def recursive_rearrange_moveset(move_data, already_check):
    if "Next Move" in move_data and move_data["Next Move"] and move_data["Move"] not in already_check:
        already_check.append(move_data["Move"])
        old_v = copy.deepcopy(move_data["Next Move"])
        for key in move_data["Next Move"].copy():  # remove to keep old dict reference
            move_data["Next Move"].pop(key)
        for key in sorted(old_v, key=lambda key: len(key), reverse=True):
            move_data["Next Move"][key] = old_v[key]
        for move in move_data["Next Move"]:
            if move not in already_check:
                recursive_rearrange_moveset(move_data["Next Move"][move], already_check)
    if move_data["Move"] not in already_check:
        already_check.append(move_data["Move"])
