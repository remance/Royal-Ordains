from datetime import datetime
from random import randint, choices, uniform, choice, getrandbits

rarity_mod_number = {"Standard": 1, "Quality": 2, "Master Work": 3, "Enchanted": 4, "Legendary": 5}
rarity_enchant_cost = {"Standard": 1000, "Quality": 5000, "Master Work": 20000, "Enchanted": 50000, "Legendary": 100000}
enchant_cost_modifier = {"weapon 1": 1.25, "weapon 2": 1.25, "head": 1, "chest": 1, "arm": 1, "leg": 1,
                         "accessory": 0.75}


def generate_custom_equipment(self, equip_type, rarity):
    mod_list = self.character_data.gear_mod_list[equip_type.split(" ")[0]]
    modifier = {}
    weight = 0
    for _ in range(rarity_mod_number[rarity]):
        new_mod = choices(tuple(mod_list.keys()), [value["Appear Chance"] for value in mod_list.values()])[0]
        while new_mod in modifier:  # keep finding mod not in modifier
            new_mod = choices(tuple(mod_list.keys()), [value["Appear Chance"] for value in mod_list.values()])[0]
        modifier[new_mod] = True
        if mod_list[new_mod][rarity][0] is not True:
            modifier[new_mod] = round(uniform(mod_list[new_mod][rarity][0], mod_list[new_mod][rarity][1]), 2)
        weight += mod_list[new_mod]["Weight"]
    if "no_weight" in modifier:
        weight = 0
    pick_suffix = tuple(modifier.keys())[choice(range(rarity_mod_number[rarity]))]
    pick_prefix = randint(0, 9)
    return {"Name": (pick_prefix, pick_suffix), "Rarity": rarity, "Modifier": tuple(modifier.items()), "Weight": weight,
            "Value": 1000 * (rarity_mod_number[rarity] * rarity_mod_number[rarity]), "Type": equip_type,
            "Rework Cost": rarity_enchant_cost[rarity] * enchant_cost_modifier[equip_type],
            "Create Time": datetime.now(), "Hash": getrandbits(128)}
