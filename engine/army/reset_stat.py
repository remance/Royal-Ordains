from engine.constants import Retinue_Leadership_Add_Modifier


def reset_stat(self, include_culture_influence=True):
    self.leadership = 0
    self.cost = 0
    self.upkeep = 0
    self.power = 0
    self.total_number = 0
    self.total_supply_usage = 0
    to_check = {"commander": [[self.commander_id, True]]} | self.army_followers
    for key, group in to_check.items():
        for character in group:
            if character and character[0] and character[1]:
                character_stat = self.character_list[character[0]]
                character_culture = character_stat["Culture"]
                influence = 0
                if include_culture_influence and character_culture != "free":
                    influence = 2
                    faction_culture = self.grand.current_campaign_state["faction"][self.faction]["culture"]
                    if character_culture in faction_culture:
                        # the lower the culture influence, the higher cost and upkeep
                        # e.g., 50% culture influence result in double cost, 0 = triple cost
                        influence = (1 - faction_culture[character_culture]["influence"]) * 2
                self.cost += character_stat["Cost"] + (character_stat["Cost"] * influence)
                self.upkeep -= character_stat["Upkeep"] + (character_stat["Upkeep"] * influence)
                total_can_call = character_stat["Arrive Per Call"] * character_stat["Capacity"]

                self.power += character_stat["Power Score"] * total_can_call
                if key == "commander":
                    self.leadership += character_stat["Leadership"]
                    self.total_number += 1  # commander can't be called multiple time so only 1
                elif key == "retinue":
                    self.leadership += character_stat["Leadership"] * Retinue_Leadership_Add_Modifier
                else:
                    self.total_supply_usage += (character_stat["Supply"] * character_stat["Capacity"])
                    self.total_number += total_can_call
    self.strategy_regen = self.leadership / 100
