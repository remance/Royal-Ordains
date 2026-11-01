from engine.constants import Leadership_Add_Modifier


def reset_stat(self, include_culture_influence=True, reset_player_army_card=False, for_reserve_info=False):
    self.leadership = 0
    self.cost = 0
    self.upkeep = 0
    self.power = 0
    self.total_number = 0
    self.total_supply_usage = 0
    to_check = {"commander": ((self.commander_id, True),)} | self.army_followers
    for key, group in to_check.items():
        for character in group:
            if character and character[0]:
                character_data = self.character_list[character[0]]
                character_culture = character_data["Culture"]
                influence_cost_mod = 0
                if include_culture_influence and character_culture != "free":
                    influence_cost_mod = 2
                    faction_culture = self.grand.current_campaign_state["faction"][self.faction]["culture"]
                    if character_culture in faction_culture:
                        # the lower the culture influence, the higher cost and upkeep
                        # e.g., 50% culture influence result in double cost, 0 = triple cost
                        influence_cost_mod = (1 - faction_culture[character_culture]["influence"]) * 2
                self.cost += int(character_data["Cost"] + (character_data["Cost"] * influence_cost_mod))

                if character[1] or for_reserve_info:  # active character or for showing reserve army info
                    self.upkeep -= int(character_data["Upkeep"] + (character_data["Upkeep"] * influence_cost_mod))
                    total_can_call = character_data["Arrive Per Call"] * character_data["Capacity"]

                    self.power += character_data["Power Score"] * total_can_call
                    if key == "commander":
                        self.leadership += character_data["Leadership"]
                        self.total_number += 1  # commander can't be called multiple time so only 1
                    else:
                        if key == "leader":
                            self.leadership += character_data["Leadership"] * Leadership_Add_Modifier
                        self.total_supply_usage += (character_data["Supply"] * character_data["Capacity"])
                        self.total_number += total_can_call

    self.strategy_regen = self.leadership / 100
    if (reset_player_army_card and self.belong_to_player_faction and
            self in self.grand.current_campaign_state["faction"][self.faction]["army"]):
        self.grand.army_list_ui.reset_card(self)
