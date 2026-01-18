def convert_army_to_custom_deployable(self, army_dict, faction):
    deployable_army_dict = {"commander": [], "leader": [], "troop": [], "air": [], "retinue": [], "cost": 0, "total": 0}
    if "leader" in army_dict:  # player custom preset army
        for header in ("commander", "leader", "troop", "air"):
            for character in army_dict[header]:
                if character:
                    deployable_army_dict[header].append(character)
                    deployable_army_dict["cost"] += self.character_data.character_list[character]["Cost"]

    else:  # game custom preset army
        character = army_dict["Commander"]
        if character:
            deployable_army_dict["commander"].append(character)
            deployable_army_dict["cost"] += self.character_data.character_list[character]["Cost"]

        for header in ("Leader 1", "Leader 2", "Leader 3", "Troop 1", "Troop 2", "Troop 3", "Troop 4", "Troop 5",
                       "Air 1", "Air 2", "Air 3", "Air 4", "Air 5"):
            character = army_dict[header]
            if character:
                deployable_army_dict[header.split(" ")[0].lower()].append(character)
                deployable_army_dict["cost"] += self.character_data.character_list[character]["Cost"]

    deployable_army_dict["retinue"] = self.character_data.faction_list[faction]["Custom Battle Retinues"]

    return deployable_army_dict
