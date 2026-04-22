import csv
import os

from engine.constants import Turn_To_Phase
from engine.data.data import GameData
from engine.utils.data_loading import stat_convert

infinity = float("infinity")


class DataStat(GameData):
    def __init__(self):
        """
        For keeping all data related to character.
        """
        GameData.__init__(self)
        self.culture_list = {}
        with open(os.path.join(self.data_dir, "character", "culture.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            dict_column = ("Coexistence Modifier", "Property",)
            dict_column = [index for index, item in enumerate(header) if item in dict_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, dict_column=dict_column)
                self.culture_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        # Character status effect dict
        self.status_list = {}
        self.can_cure_status_list = []
        self.can_clarity_status_list = []
        with open(os.path.join(self.data_dir, "character", "status.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            dict_column = ("Property",)
            percent_column = ("Offence Modifier", "Defence Modifier", "Speed Modifier", "Animation Time Modifier",)
            float_column = ("Slash Resistance Bonus", "Crush Resistance Bonus", "Stab Resistance Bonus",
                            "Fire Resistance Bonus", "Water Resistance Bonus", "Air Resistance Bonus",
                            "Earth Resistance Bonus",
                            "Magic Resistance Bonus", "Poison Resistance Bonus", "Magic Resistance Bonus")
            tuple_column = ("Status Conflict",)  # value in tuple only
            dict_column = [index for index, item in enumerate(header) if item in dict_column]
            percent_column = [index for index, item in enumerate(header) if item in percent_column]
            float_column = [index for index, item in enumerate(header) if item in float_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, percent_column=percent_column,
                                       tuple_column=tuple_column, float_column=float_column,
                                       dict_column=dict_column)
                self.status_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
                if "Cure" in self.status_list[row[0]]["Status Conflict"]:
                    self.can_cure_status_list.append(row[0])
                if "Clarity" in self.status_list[row[0]]["Status Conflict"]:
                    self.can_clarity_status_list.append(row[0])
        edit_file.close()

        self.status_apply_funcs = create_status_apply_function_dict(self.status_list)

        self.strategy_list = {}
        with open(os.path.join(self.data_dir, "character", "strategy.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            dict_column = ("Summon", "AI Condition", "Property",)
            tuple_column = (
            "Effects", "Damage Effects", "Status", "Enemy Status", "Effect Enemy Status")  # value in tuple only
            dict_column = [index for index, item in enumerate(header) if item in dict_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, tuple_column=tuple_column, dict_column=dict_column)
                self.strategy_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
                self.strategy_list[row[0]]["owner data"] = {
                    "offence": self.strategy_list[row[0]]["Offence"],
                    "low_offence": self.strategy_list[row[0]]["Offence"] * 0.5,
                    "impact": (self.strategy_list[row[0]]["Impact X"], self.strategy_list[row[0]]["Impact Y"]),
                    "impact_sum": abs(self.strategy_list[row[0]]["Impact X"]) + abs(
                        self.strategy_list[row[0]]["Impact Y"]),
                    "critical_chance": self.strategy_list[row[0]]["Critical Chance"]}
        edit_file.close()

        # Character dict
        self.character_list = {}
        with open(os.path.join(self.data_dir, "character", "character.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            tuple_column = ("Status Immunity", "Sub Characters", "Character Tag")
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            dict_column = ("Spawns", "Items", "Property",)
            dict_column = [index for index, item in enumerate(header) if item in dict_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, tuple_column=tuple_column, dict_column=dict_column)
                self.character_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
                self.character_list[row[0]]["Move"] = {}
                self.character_list[row[0]]["Summon List"] = ()
                self.character_list[row[0]]["ai_min_attack_range"] = infinity
                self.character_list[row[0]]["ai_skirmish_range"] = 0
                self.character_list[row[0]]["ai_max_attack_range"] = 0
                self.character_list[row[0]]["ai_min_effect_range"] = infinity
                self.character_list[row[0]]["ai_enemy_max_effect_range"] = 0
                self.character_list[row[0]]["ai_ally_max_effect_range"] = 0
                self.character_list[row[0]]["max_enemy_range_check"] = 0
                self.character_list[row[0]]["min_resource_move"] = infinity
                if "Spawns" in header:
                    self.character_list[row[0]]["Summon List"] = tuple(row[header.index("Spawns")].keys())
                self.character_list[row[0]]["Supply Drop"] = self.character_list[row[0]]["Supply"]
                if self.character_list[row[0]]["Arrive Per Call"]:
                    self.character_list[row[0]]["Supply Drop"] = self.character_list[row[0]]["Supply"] / \
                                                                 self.character_list[row[0]]["Arrive Per Call"]
                summon_list = []
                self.character_list[row[0]]["Die Move"] = {}
                # Add character move data
                if os.path.exists(
                        os.path.join(self.data_dir, "character", "moveset", str(row[0]) + ".csv")):
                    with open(os.path.join(self.data_dir, "character", "moveset", str(row[0]) + ".csv"),
                              encoding="utf-8", mode="r") as edit_file2:
                        rd2 = tuple(csv.reader(edit_file2, quoting=csv.QUOTE_ALL))
                        header2 = rd2[0]
                        tuple_column2 = ("Status", "Enemy Status", "Effect Enemy Status")  # value in tuple only
                        tuple_column2 = [index for index, item in enumerate(header2) if item in tuple_column2]
                        dict_column2 = ("Prepare Animation", "After Animation", "AI Condition", "Property",)
                        dict_column2 = [index for index, item in enumerate(header2) if item in dict_column2]
                        moveset_dict = {}
                        for row_index2, row2 in enumerate(rd2[1:]):
                            for n2, i2 in enumerate(row2):
                                row2 = stat_convert(row2, n2, i2, tuple_column=tuple_column2,
                                                    dict_column=dict_column2)

                            move_data = {header2[index]: stuff for index, stuff in enumerate(row2)}
                            if "self" in move_data["AI Condition"] and move_data["AI Condition"]["self"] == "die":
                                # add moveset that automatically got used when character die for in battle check
                                self.character_list[row[0]]["Die Move"] = move_data
                            else:
                                moveset_dict[row2[0]] = move_data

                            if "summon" in move_data["Property"]:
                                if type(move_data["Property"]["summon"]) is str:
                                    summon_list.append(move_data["Property"]["summon"])
                                else:
                                    summon_list += move_data["Property"]["summon"]

                        self.character_list[row[0]]["Move"] = moveset_dict

                        # Find max and min range for AI
                        for move in moveset_dict.values():
                            if "no_ai_range_check_setup" not in move["Property"]:
                                if self.character_list[row[0]]["ai_min_attack_range"] > move["AI Range"]:
                                    self.character_list[row[0]]["ai_min_attack_range"] = move["AI Range"]
                                if self.character_list[row[0]]["ai_max_attack_range"] < move["AI Range"]:
                                    self.character_list[row[0]]["ai_max_attack_range"] = move["AI Range"]
                                if self.character_list[row[0]]["ai_min_effect_range"] > move["Range"] and (
                                        move["Status"] or move["Enemy Status"]):
                                    self.character_list[row[0]]["ai_min_effect_range"] = move["Range"]
                                if self.character_list[row[0]]["ai_ally_max_effect_range"] < move["Range"] and move[
                                    "Status"]:
                                    self.character_list[row[0]]["ai_ally_max_effect_range"] = move["Range"]
                                if self.character_list[row[0]]["ai_enemy_max_effect_range"] < move["Range"] and move[
                                    "Enemy Status"]:
                                    self.character_list[row[0]]["ai_enemy_max_effect_range"] = move["Range"]
                            if self.character_list[row[0]]["min_resource_move"] > move["Resource Cost"]:
                                self.character_list[row[0]]["min_resource_move"] = move["Resource Cost"]
                        self.character_list[row[0]]["max_enemy_range_check"] = self.character_list[row[0]][
                            "ai_enemy_max_effect_range"]
                        if self.character_list[row[0]]["ai_max_attack_range"] > self.character_list[row[0]][
                            "max_enemy_range_check"]:
                            self.character_list[row[0]]["max_enemy_range_check"] = self.character_list[row[0]][
                                "ai_max_attack_range"]

                        self.character_list[row[0]]["ai_skirmish_range"] = self.character_list[row[0]][
                                                                               "ai_min_attack_range"] * 0.75
                    self.character_list[row[0]]["Summon List"] = tuple(summon_list)
                    edit_file2.close()
        edit_file.close()

        self.custom_character_setup = {}
        self.all_main_exist_characters = {}
        for character, character_data in self.character_list.items():
            if character_data["Culture"]:
                if character_data["Culture"] not in self.custom_character_setup:
                    self.all_main_exist_characters[character_data["Culture"]] = []
                    self.custom_character_setup[character_data["Culture"]] = {
                        "air": [], "ground": {"leader": {"unique": [], "generic": []}, "troop": []}}
                if character_data["Class"] != "sub" and os.path.exists(
                        os.path.join(self.data_dir, "ui", "character_ui", character + ".png")):
                    self.all_main_exist_characters[character_data["Culture"]].append(character)
                if character_data["Can Custom"]:
                    if character_data["Type"] == "ground":
                        if character_data["Is Leader"]:
                            if character_data["Is Unique"]:
                                self.custom_character_setup[character_data["Culture"]][character_data["Type"]][
                                    "leader"]["unique"].append(character)
                            else:
                                self.custom_character_setup[character_data["Culture"]][character_data["Type"]][
                                    "leader"]["generic"].append(character)
                        else:
                            self.custom_character_setup[character_data["Culture"]][character_data["Type"]][
                                "troop"].append(character)
                    else:
                        self.custom_character_setup[character_data["Culture"]][character_data["Type"]].append(character)

        # Effect that can exist as its own sprite in battle
        self.effect_list = {}
        with open(os.path.join(self.data_dir, "character", "effect.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            dict_column = ("Property",)
            dict_column = [index for index, item in enumerate(header) if item in dict_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, dict_column=dict_column)
                self.effect_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        self.preset_list = {}
        with open(os.path.join(self.data_dir, "character", "preset.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i)
                if row[0]:  # keep preset using culture as dict key
                    if row[header.index("Culture")] not in self.preset_list:
                        self.preset_list[row[header.index("Culture")]] = {}
                    self.preset_list[row[header.index("Culture")]][row[0]] = {
                        header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        self.building_list = {}
        with open(os.path.join(self.data_dir, "character", "building.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            tuple_column = ("Garrison Strategy", "Leader Reinforcement", "Troop Reinforcement",
                            "Air Reinforcement", "Leader Recruit", "Unit Recruit", "Technology")
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, tuple_column=tuple_column)
                self.building_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
                self.building_list[row[0]]["Build Time"] *= Turn_To_Phase  # convert build time to phase
                # add repair time, which is half the build time, minimum is 1 phase
                self.building_list[row[0]]["Repair Time"] = int(self.building_list[row[0]]["Build Time"] / 2)
                if not self.building_list[row[0]]["Repair Time"]:
                    self.building_list[row[0]]["Repair Time"] = 1
        edit_file.close()


def create_status_apply_function_dict(status_list):
    status_apply_funcs = {}
    for status_name, data in status_list.items():
        k = status_name
        func_code = f'''
def {status_name}(self):'''

        if data["Offence Modifier"] != 1:
            func_code += f'''
    self.offence *= {data["Offence Modifier"]}'''

        if data["Defence Modifier"] != 1:
            func_code += f'''
    self.defence *= {data["Defence Modifier"]}'''

        if data["Speed Modifier"] != 1:
            func_code += f'''
    self.speed *= {data["Speed Modifier"]}'''

        if data["HP Regeneration Bonus"]:
            func_code += f'''
    self.health_regen += {data["HP Regeneration Bonus"]}'''

        if data["Resource Regeneration Bonus"]:
            func_code += f'''
    self.resource_regen += {data["Resource Regeneration Bonus"]}'''

        if data["Animation Time Modifier"] != 1:
            func_code += f'''
    self.animation_frame_play_time *= {data["Animation Time Modifier"]}'''

        # element resistant
        if data["Slash Resistance Bonus"]:
            func_code += f'''
    self.element_resistance["slash"] += {data["Slash Resistance Bonus"]}'''

        if data["Crush Resistance Bonus"]:
            func_code += f'''
    self.element_resistance["crush"] += {data["Crush Resistance Bonus"]}'''

        if data["Stab Resistance Bonus"]:
            func_code += f'''
    self.element_resistance["stab"] += {data["Stab Resistance Bonus"]}'''

        if data["Fire Resistance Bonus"]:
            func_code += f'''
    self.element_resistance["fire"] += {data["Fire Resistance Bonus"]}'''

        if data["Water Resistance Bonus"]:
            func_code += f'''
    self.element_resistance["water"] += {data["Water Resistance Bonus"]}'''

        if data["Air Resistance Bonus"]:
            func_code += f'''
    self.element_resistance["air"] += {data["Air Resistance Bonus"]}'''

        if data["Earth Resistance Bonus"]:
            func_code += f'''
    self.element_resistance["earth"] += {data["Earth Resistance Bonus"]}'''

        if data["Magic Resistance Bonus"]:
            func_code += f'''
    self.element_resistance["magic"] += {data["Magic Resistance Bonus"]}'''

        if data["Poison Resistance Bonus"]:
            func_code += f'''
    self.element_resistance["poison"] += {data["Poison Resistance Bonus"]}'''

        for status_property, value in data["Property"].items():
            if type(value) is str:
                value = "'" + value + "'"
            func_code += f'''
    self.{status_property} = {value}'''

        func_code += f'''
    return'''
        func_code += f'''
status_apply_funcs["{k}"] = {status_name}'''
        exec(func_code)
    return status_apply_funcs
