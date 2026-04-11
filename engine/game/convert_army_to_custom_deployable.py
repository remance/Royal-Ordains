from engine.constants import Retinue_Leadership_Add_Modifier


def convert_army_to_custom_deployable(self, army_dict, culture):
    deployable_army_dict = {"culture": culture, "commander": [], "leader": [], "troop": [], "air": [],
                            "retinue": [], "cost": 0, "leadership": 0}
    if "leader" in army_dict:  # player custom preset army
        for header in ("commander", "leader", "troop", "air"):
            for character in army_dict[header]:
                if character:
                    deployable_army_dict[header].append(character)
                    deployable_army_dict["cost"] += self.character_list[character]["Cost"]
        deployable_army_dict["retinue"] = [item for item in army_dict["retinue"] if item]
    else:  # game custom preset army
        character = army_dict["Commander"]
        if character:
            deployable_army_dict["commander"].append(character)
            deployable_army_dict["cost"] += self.character_list[character]["Cost"]
            deployable_army_dict["leadership"] += self.character_list[character]["Leadership"]

        for header in ("Leader 1", "Leader 2", "Leader 3", "Troop 1", "Troop 2", "Troop 3", "Troop 4", "Troop 5",
                       "Air 1", "Air 2", "Air 3", "Air 4", "Air 5"):
            character = army_dict[header]
            if character:
                deployable_army_dict[header.split(" ")[0].lower()].append(character)
                deployable_army_dict["cost"] += self.character_list[character]["Cost"]
        deployable_army_dict["retinue"] = [army_dict["Retinue 1"], army_dict["Retinue 2"], army_dict["Retinue 3"]]
        deployable_army_dict["retinue"] = [item for item in deployable_army_dict["retinue"] if item]

    for item in deployable_army_dict["retinue"]:
        if item:
            deployable_army_dict["cost"] += self.character_list[item]["Cost"]
            deployable_army_dict["leadership"] += self.character_list[item]["Leadership"] * Retinue_Leadership_Add_Modifier

    return deployable_army_dict
