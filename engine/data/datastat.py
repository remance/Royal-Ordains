"""This file contains all class and function that read troop/leader related data
and save them into dict for in game use """

import csv
import os

from engine.utils.data_loading import stat_convert


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
            int_column = ("ID", "Physical Resistance Bonus",
                          "Fire Resistance Bonus", "Water Resistance Bonus",
                          "Air Resistance Bonus", "Earth Resistance Bonus", "Magic Resistance Bonus",
                          "Heat Resistance Bonus", "Cold Resistance Bonus", "Poison Resistance Bonus",
                          "Melee Attack Bonus", "Melee Defence Bonus", "Ranged Defence Bonus", "Speed Bonus",
                          "Accuracy Bonus", "Range Bonus", "Reload Bonus", "Charge Bonus", "Charge Defence Bonus",
                          "Melee Speed Bonus")  # value int only
            tuple_column = ("Special Effect", "Status Conflict")  # value in tuple only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, tuple_column=tuple_column, int_column=int_column)
                self.status_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        self.status_lore = self.localisation.create_lore_data("status")

        self.common_moveset_skill = {}
        with open(os.path.join(self.data_dir, "character", "playable", "skill.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            tuple_column = ("Buttons", "Status", "Enemy Status")  # value in tuple only
            dict_column = ("Prepare Animation", "Property",)
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
                    tuple_column = ("Property",)  # value in tuple only
                    tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
                    dict_column = ("Drops",)
                    dict_column = [index for index, item in enumerate(header) if item in dict_column]
                    for n, i in enumerate(row):
                        row = stat_convert(row, n, i, int_column=int_column, tuple_column=tuple_column,
                                           dict_column=dict_column)
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
                            dict_column = ("Stat Requirement", "Prepare Animation", "Property",)
                            dict_column = [index for index, item in enumerate(header2) if item in dict_column]
                            moveset_dict = {}
                            remain_next_move_loop = []
                            for row_index2, row2 in enumerate(rd2[1:]):
                                for n2, i2 in enumerate(row2):
                                    row2 = stat_convert(row2, n2, i2, tuple_column=tuple_column,
                                                        dict_column=dict_column)
                                # restructure moveset so move that continue from another is in its parent move
                                move_data = {header2[index]: stuff for index, stuff in enumerate(row2)}
                                if row2[header2.index("Position")] not in moveset_dict:
                                    # keep moveset in each position dict for easier access
                                    moveset_dict[row2[header2.index("Position")]] = {}
                                if not row2[header2.index("Requirement Move")]:
                                    # parent move, must also always at row above any child move in csv file
                                    moveset_dict[row2[header2.index("Position")]][row2[0]] = move_data
                                else:
                                    found = None
                                    for parent_move in row2[header2.index("Requirement Move")]:
                                        done_check = [False]
                                        already_check = []
                                        final_recursive_dict(moveset_dict[row2[header2.index("Position")]],
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
                            for item in remain_next_move_loop:  # one last try to find parent
                                done_check = ["test"]
                                already_check = []
                                final_recursive_dict(item[0], item[1], item[2], item[3], done_check, already_check)
                            self.character_list[row[0]]["Move"] = moveset_dict
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
                            tuple_column = ("Buttons", "Status", "Enemy Status")  # value in tuple only
                            dict_column = ("Prepare Animation", "Property",)
                            tuple_column = [index for index, item in enumerate(header2) if item in tuple_column]
                            dict_column = [index for index, item in enumerate(header2) if item in dict_column]
                            moveset_dict = {}
                            for index2, row2 in enumerate(rd[1:]):
                                for n2, i2 in enumerate(row2):
                                    row2 = stat_convert(row2, n2, i2, tuple_column=tuple_column,
                                                        dict_column=dict_column)
                                move_data = {header2[index + 1]: stuff for index, stuff in enumerate(row2[1:])}
                                if row2[header2.index("Position")] not in moveset_dict:
                                    # keep moveset in each position dict for easier access
                                    moveset_dict[row2[header2.index("Position")]] = {}
                                moveset_dict[row2[header2.index("Position")]][row2[0]] = move_data
                            self.character_list[row[0]]["Skill"] = moveset_dict
                        edit_file2.close()

                    # Add character mode data
                    self.character_list[row[0]]["Mode"] = {}
                    if os.path.exists(
                            os.path.join(self.data_dir, "character", folder_list[file_index], row[0], "mode.csv")):
                        with open(os.path.join(self.data_dir, "character", folder_list[file_index], row[0], "mode.csv"),
                                  encoding="utf-8", mode="r") as edit_file2:
                            rd2 = tuple(csv.reader(edit_file2, quoting=csv.QUOTE_ALL))
                            header2 = rd2[0]
                            for row_index2, row2 in enumerate(rd2[1:]):
                                self.character_list[row[0]]["Mode"][row2[0]] = {header2[index + 1]: stuff for
                                                                                index, stuff in enumerate(row2[1:])}
                    else:  # no specific mode list, has only normal mode
                        self.character_list[row[0]]["Mode"]["Normal"] = default_mode["Normal"]
                edit_file.close()

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


def final_recursive_dict(parent_move_data, move_key, move_data, parent_move_name, done_check, already_check):
    try:
        recursive_moveset_dict(parent_move_data, move_key, move_data, parent_move_name, done_check, already_check)
        return
    except ValueError:
        return


def recursive_moveset_dict(parent_move_data, move_key, move_data, parent_move_name, done_check, already_check):
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
                recursive_moveset_dict(v["Next Move"], move_key, move_data, parent_move_name, done_check, already_check)
