def call_reinforcement(self, team, call_type, character_index):
    if check_if_can_call_reinforcement(self, team, call_type, character_index):
        if call_type == "leader":
            call_pool = self.team_stat[team]["leader_call_list"]
            if team == 1:
                cooldown_check = self.team1_call_leader_cooldown_reinforcement
            else:
                cooldown_check = self.team2_call_leader_cooldown_reinforcement
        else:
            call_pool = self.team_stat[team]["troop_call_list"]
            if team == 1:
                cooldown_check = self.team1_call_troop_cooldown_reinforcement
            else:
                cooldown_check = self.team2_call_troop_cooldown_reinforcement

        character_to_call = call_pool[character_index]

        if "team" not in self.later_reinforcement:
            self.later_reinforcement["team"] = {team: {}}
        elif team not in self.later_reinforcement["team"]:
            self.later_reinforcement["team"][team] = {}
        if "ground" not in self.later_reinforcement["team"][team]:
            self.later_reinforcement["team"][team]["ground"] = []
        character_stat = self.character_list[character_to_call[0]]
        self.later_reinforcement["team"][team]["ground"].append([character_to_call[0], character_stat["Respond Time"],
                                                                 0, character_stat["Arrive Per Call"]])
        character_to_call[1] -= 1
        self.team_stat[team]["supply_resource"] -= call_pool[character_index][2]
        if not character_to_call[1]:
            call_pool.remove(character_to_call)
        else:
            cooldown_check[character_index] = character_stat["Reinforce Time"]


def check_if_can_call_reinforcement(self, team, call_type, character_index):
    if call_type == "leader":
        call_pool = self.team_stat[team]["leader_call_list"]
        if team == 1:
            cooldown_check = self.team1_call_leader_cooldown_reinforcement
        else:
            cooldown_check = self.team2_call_leader_cooldown_reinforcement
    else:
        call_pool = self.team_stat[team]["troop_call_list"]
        if team == 1:
            cooldown_check = self.team1_call_troop_cooldown_reinforcement
        else:
            cooldown_check = self.team2_call_troop_cooldown_reinforcement
    if (self.team_commander[team] and self.team_commander[team].alive and
            character_index not in cooldown_check and character_index < len(call_pool) and
            call_pool[character_index] and call_pool[character_index][2] <= self.team_stat[team]["supply_resource"]):
        return True
