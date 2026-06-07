def check_battle_character_to_load(self, battle_character_list):
    already_check_char = set()
    battle_character_list = [item for item in battle_character_list if item]
    battle_character_list = list(set([char_id if "+" not in char_id else char_id.split("+")[0] for char_id in
                                      battle_character_list]))
    while battle_character_list:
        char_id = battle_character_list[0]
        battle_character_list.remove(char_id)
        if char_id not in already_check_char:
            already_check_char.add(char_id)
            if self.character_list[char_id]["Summon List"]:
                battle_character_list += (self.character_list[char_id]["Summon List"])
            if self.character_list[char_id]["Sub Characters"]:
                battle_character_list += set(
                    [item[0] for item in self.character_list[char_id]["Sub Characters"]])
            battle_character_list = list(
                set([char_id if "+" not in char_id else char_id.split("+")[0] for char_id in
                     battle_character_list]))

    return already_check_char
