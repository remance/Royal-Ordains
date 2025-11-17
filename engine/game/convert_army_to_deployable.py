from engine.army.leader import Leader


def convert_army_to_deployable(self, army_dict):
    deployable_army_dict = {"ground": {}, "air": [], "retinue": [], "cost": 0, "total": 0}

    if "ground" in army_dict:  # player custom preset army
        for value in army_dict["ground"].values():
            this_group = [value2 for value2 in value.values() if value2 not in (None, "custom_lock")]
            if this_group:
                make_ground_group(self, deployable_army_dict, this_group)
        for value in army_dict["air"].values():
            if value not in (None, "custom_lock"):
                capacity = self.character_data.character_list[value]["Capacity"]
                if not capacity:
                    capacity = 1
                deployable_army_dict["cost"] += self.character_data.character_list[value]["Cost"]
                deployable_army_dict["total"] += capacity
                deployable_army_dict["air"].append({value: capacity})
    else:  # game custom preset army
        for air_group in ("Air Group 1", "Air Group 2", "Air Group 3", "Air Group 4", "Air Group 5"):
            if army_dict[air_group]:
                capacity = self.character_data.character_list[army_dict[air_group]]["Capacity"]
                if not capacity:
                    capacity = 1
                deployable_army_dict["cost"] += self.character_data.character_list[army_dict[air_group]]["Cost"]
                deployable_army_dict["total"] += capacity
                deployable_army_dict["air"].append({army_dict[air_group]: capacity})

        for header in ("Ground 1", "Ground 2", "Ground 3", "Ground 4", "Ground 5"):
            if army_dict[header]:
                make_ground_group(self, deployable_army_dict, army_dict[header])

    return deployable_army_dict


def make_ground_group(self, deployable_army_dict, this_group):
    follower_list = []
    for index, value in enumerate(this_group):
        capacity = self.character_data.character_list[value]["Capacity"]
        if not capacity:
            capacity = 1
        deployable_army_dict["cost"] += self.character_data.character_list[value]["Cost"]
        deployable_army_dict["total"] += capacity
        if index:  # follower
            follower_list.append({value: capacity})
    deployable_army_dict["ground"][Leader(this_group[0])] = follower_list
