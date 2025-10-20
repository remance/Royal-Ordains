import copy
import csv
import os

from engine.utils.data_loading import stat_convert

infinity = float("infinity")


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
            dict_column = ("Property",)
            percent_column = ("Offence Modifier", "Defence Modifier", "Speed Modifier", "Animation Time Modifier",)
            float_column = ("Slash Resistance Bonus", "Crush Resistance Bonus", "Stab Resistance Bonus",
                            "Fire Resistance Bonus", "Water Resistance Bonus", "Air Resistance Bonus",
                            "Earth Resistance Bonus",
                            "Magic Resistance Bonus", "Poison Resistance Bonus", "Magic Resistance Bonus")
            tuple_column = ("Special Effect", "Status Conflict")  # value in tuple only
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
        edit_file.close()

        self.status_apply_funcs = create_status_apply_function_dict(self.status_list)

        self.strategy_list = {}
        with open(os.path.join(self.data_dir, "character", "strategy.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            dict_column = ("AI Condition", "Property",)
            tuple_column = ("Effects", "Damage Effects", "Status", "Enemy Status")  # value in tuple only
            dict_column = [index for index, item in enumerate(header) if item in dict_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, tuple_column=tuple_column, dict_column=dict_column)
                self.strategy_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
                self.strategy_list[row[0]]["owner data"] = {
                    "offence": self.strategy_list[row[0]]["Offence"],
                    "power": self.strategy_list[row[0]]["Power"], "element": self.strategy_list[row[0]]["Element"],
                    "impact": (self.strategy_list[row[0]]["Impact X"], self.strategy_list[row[0]]["Impact Y"]),
                    "impact_sum": abs(self.strategy_list[row[0]]["Impact X"]) + abs(self.strategy_list[row[0]]["Impact Y"]),
                    "critical_chance": self.strategy_list[row[0]]["Critical Chance"],
                    "enemy_status_effect": self.strategy_list[row[0]]["Enemy Status"],
                    "no_defence": True if "no_defence" in self.strategy_list[row[0]]["Property"] else False,
                    "no_dodge": True if "no_dodge" in self.strategy_list[row[0]]["Property"] else False,
                    "penetrate": self.strategy_list[row[0]]["Penetrate"]}
        edit_file.close()

        # Character dict
        self.character_list = {}
        with open(os.path.join(self.data_dir, "character", "character.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            tuple_column = ("Status Immunity", )
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            dict_column = ("Followers", "Spawns", "Items", "Property", "Sub Characters",)
            dict_column = [index for index, item in enumerate(header) if item in dict_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, tuple_column=tuple_column, dict_column=dict_column)
                self.character_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
                self.character_list[row[0]]["Move"] = {}
                self.character_list[row[0]]["Summon List"] = ()
                self.character_list[row[0]]["ai_min_attack_range"] = infinity
                self.character_list[row[0]]["ai_max_attack_range"] = 0
                self.character_list[row[0]]["ai_min_effect_range"] = infinity
                self.character_list[row[0]]["ai_max_effect_range"] = 0
                self.character_list[row[0]]["max_enemy_range_check"] = 0
                if "Spawns" in header:
                    self.character_list[row[0]]["Summon List"] = tuple(row[header.index("Spawns")].keys())

                summon_list = []
                # Add character move data
                if os.path.exists(
                        os.path.join(self.data_dir, "character", "moveset", str(row[0]) + ".csv")):
                    with open(os.path.join(self.data_dir, "character", "moveset", str(row[0]) + ".csv"),
                              encoding="utf-8", mode="r") as edit_file2:
                        rd2 = tuple(csv.reader(edit_file2, quoting=csv.QUOTE_ALL))
                        header2 = rd2[0]
                        tuple_column2 = ("Status", "Enemy Status")  # value in tuple only
                        tuple_column2 = [index for index, item in enumerate(header2) if item in tuple_column2]
                        dict_column2 = ("Prepare Animation", "After Animation", "AI Condition", "Property",)
                        dict_column2 = [index for index, item in enumerate(header2) if item in dict_column2]
                        moveset_dict = {}
                        for row_index2, row2 in enumerate(rd2[1:]):
                            for n2, i2 in enumerate(row2):
                                row2 = stat_convert(row2, n2, i2, tuple_column=tuple_column2,
                                                    dict_column=dict_column2)

                            move_data = {header2[index]: stuff for index, stuff in enumerate(row2)}

                            moveset_dict[row2[0]] = move_data

                            if "summon" in move_data["Property"]:
                                if type(move_data["Property"]["summon"]) is str:
                                    summon_list.append(move_data["Property"]["summon"])
                                else:
                                    summon_list += move_data["Property"]["summon"]

                        self.character_list[row[0]]["Move"] = moveset_dict

                        # Find max and min range for AI
                        for move in moveset_dict.values():
                            if "no max ai range" not in move["Property"] and self.character_list[row[0]][
                                "ai_min_attack_range"] > move["AI Range"]:
                                self.character_list[row[0]]["ai_min_attack_range"] = move["AI Range"]
                            if "no max ai range" not in move["Property"] and self.character_list[row[0]][
                                "ai_max_attack_range"] < move["AI Range"]:
                                self.character_list[row[0]]["ai_max_attack_range"] = move["AI Range"]
                            if self.character_list[row[0]]["ai_min_effect_range"] > move["Range"] and (
                                    move["Status"] or move["Enemy Status"]):
                                self.character_list[row[0]]["ai_min_effect_range"] = move["Range"]
                            if self.character_list[row[0]]["ai_max_effect_range"] < move["Range"] and (
                                    move["Status"] or move["Enemy Status"]):
                                self.character_list[row[0]]["ai_max_effect_range"] = move["Range"]
                        self.character_list[row[0]]["max_enemy_range_check"] = self.character_list[row[0]][
                            "ai_max_effect_range"]
                        if self.character_list[row[0]]["ai_max_attack_range"] > self.character_list[row[0]][
                            "max_enemy_range_check"]:
                            self.character_list[row[0]]["max_enemy_range_check"] = self.character_list[row[0]][
                                "ai_max_attack_range"]

                    self.character_list[row[0]]["Summon List"] = tuple(summon_list)
                    edit_file2.close()
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
    self.animation_play_time *= {data["Animation Time Modifier"]}'''

        # element resistant
        if data["Slash Resistance Bonus"]:
            func_code += f'''
    self.element_resistance["Slash"] += {data["Slash Resistance Bonus"]}'''

        if data["Crush Resistance Bonus"]:
            func_code += f'''
    self.element_resistance["Crush"] += {data["Crush Resistance Bonus"]}'''

        if data["Stab Resistance Bonus"]:
            func_code += f'''
    self.element_resistance["Stab"] += {data["Stab Resistance Bonus"]}'''

        if data["Fire Resistance Bonus"]:
            func_code += f'''
    self.element_resistance["Fire"] += {data["Fire Resistance Bonus"]}'''

        if data["Water Resistance Bonus"]:
            func_code += f'''
    self.element_resistance["Water"] += {data["Water Resistance Bonus"]}'''

        if data["Air Resistance Bonus"]:
            func_code += f'''
    self.element_resistance["Air"] += {data["Air Resistance Bonus"]}'''

        if data["Earth Resistance Bonus"]:
            func_code += f'''
    self.element_resistance["Earth"] += {data["Earth Resistance Bonus"]}'''

        if data["Magic Resistance Bonus"]:
            func_code += f'''
    self.element_resistance["Magic"] += {data["Magic Resistance Bonus"]}'''

        if data["Poison Resistance Bonus"]:
            func_code += f'''
    self.element_resistance["Poison"] += {data["Poison Resistance Bonus"]}'''

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
