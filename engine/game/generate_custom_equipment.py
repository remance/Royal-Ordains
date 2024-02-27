from datetime import datetime
from random import randint, choices, uniform, choice

rarity_mod_number = {"Standard": 1, "Quality": 2, "Master Work": 3, "Enchanted": 4, "Legendary": 5}


def generate_custom_equipment(self, equip_type, rarity):
    mod_list = self.character_data.gear_mod_list[equip_type.split(" ")[0]]
    modifier = {}
    weight = 0
    for _ in range(rarity_mod_number[rarity]):
        new_mod = choices(tuple(mod_list.keys()), [value["Appear Chance"] for value in mod_list.values()])[0]
        while new_mod in modifier:  # keep finding mod not in modifier
            new_mod = choices(tuple(mod_list.keys()), [value["Appear Chance"] for value in mod_list.values()])[0]
        modifier[new_mod] = True
        if True not in mod_list[new_mod][rarity]:
            modifier[new_mod] = uniform(mod_list[new_mod][rarity][0], mod_list[new_mod][rarity][1])
    pick_suffix = tuple(modifier.keys())[choice(range(rarity_mod_number[rarity]))]
    pick_prefix = randint(0, 9)
    return {"Name": (pick_prefix, pick_suffix), "Rarity": rarity, "Modifier": modifier, "Weight": weight,
            "Value": 1000 * (rarity_mod_number[rarity] * rarity_mod_number[rarity]), "Type": equip_type,
            "Create Time": datetime.now()}
