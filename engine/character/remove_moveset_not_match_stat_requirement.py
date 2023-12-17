def remove_moveset_not_match_stat_requirement(self):
    stat_list = {"Strength": self.strength, "Dexterity": self.dexterity, "Agility": self.agility,
                 "Constitution": self.constitution, "Intelligence": self.intelligence, "Wisdom": self.wisdom,
                 "Charisma": self.charisma}

    for position in ("Couch", "Stand", "Air"):  # combine skill into moveset
        # also check for moveset that require stat
        if position in self.moveset:  # check stat requirement for moveset first
            recursive_remove(stat_list, self.moveset[position], [])


def recursive_remove(stat_list, moveset_data, already_check):
    for move_name, move in moveset_data.copy().items():
        if move["Move"] not in already_check:
            already_check.append(move["Move"])
            if "Stat Requirement" in move:
                for stat_name, value in move["Stat Requirement"].items():
                    if stat_list[stat_name] < float(value):  # remove move that not have required stat
                        moveset_data.pop(move_name)
                        break
                if "Next Move" in move and move["Next Move"]:  # check children moves
                    recursive_remove(stat_list, move["Next Move"], already_check)
