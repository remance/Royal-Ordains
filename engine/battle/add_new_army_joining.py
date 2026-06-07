from engine.constants import Retinue_Leadership_Add_Modifier


def add_new_army_joining(self):
    """Check for sprite loading and add reinforcement after finish loading"""
    for thread in tuple(self.load_sprite_background_threads):
        if not thread.is_alive():
            thread.join()
            self.load_sprite_background_threads.remove(thread)
    if not self.load_sprite_background_threads:
        # add retinue
        for army in self.awaiting_armies:
            team = army.team
            team_stat = self.team_stat[army.team]
            if len(team_stat["active_retinue"]) < 3:
                # add retinue until reach 3
                if army.retinue:
                    for retinue in army.retinue:
                        team_stat["leadership"] += (self.character_list[retinue]["Leadership"] *
                                                    Retinue_Leadership_Add_Modifier)
                        team_stat["strategy_cooldown"][len(team_stat["strategy"])] = 0
                        team_stat["strategy"].append(self.character_list[retinue]["Strategy"])
                        team_stat["active_retinue"].append(retinue)
                        if len(team_stat["active_retinue"]) == 3:
                            break

            # add
            team_stat["leader_call_list"].append([army.commander_id, 1, self.character_list[army.commander_id][
                "Supply"]])  # add reinforcement commander as leader
            team_stat["leader_call_list"] += [
                [item, self.character_list[item]["Capacity"], self.character_list[item]["Supply"]] for item in
                army.leader_group]
            team_stat["troop_call_list"] += [
                [item, self.character_list[item]["Capacity"], self.character_list[item]["Supply"]] for item in
                army.ground_group]

        self.awaiting_armies = []