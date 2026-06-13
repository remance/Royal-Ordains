from engine.constants import Retinue_Leadership_Add_Modifier


def add_new_army_joining(self):
    """Check for sprite loading and add reinforcement after finish loading"""
    for thread in tuple(self.load_sprite_background_threads):
        if not thread.is_alive():
            thread.join()
            self.load_sprite_background_threads.remove(thread)
    if not self.load_sprite_background_threads:
        # add retinue
        for team, army_list in tuple(self.awaiting_armies.items()):
            for army in army_list:
                team_state = self.team_state[team]
                commander_id = army.commander_id
                if len(team_state["active_retinue"]) < 3:
                    # add retinue until reach 3
                    if army.retinue:
                        for retinue in army.retinue:
                            team_state["leadership"] += (self.character_list[retinue]["Leadership"] *
                                                         Retinue_Leadership_Add_Modifier)
                            team_state["strategy_cooldown"][len(team_state["strategy"])] = 0
                            team_state["strategy"].append(self.character_list[retinue]["Strategy"])
                            team_state["active_retinue"].append(retinue)
                            if len(team_state["active_retinue"]) == 3:
                                break
                        if team == self.player_team:
                            self.strategy_select_ui.setup()

                team_state["supply_reserve"] += army.supply
                team_state["total_supply"] += army.supply
                team_state["reinforcement_army"].append(army)

                team_state["leader_call_list"].append([commander_id, 1, self.character_list[commander_id][
                    "Supply"]])  # add reinforcement commander as leader
                team_state["leader_call_list"] += [
                    [item, self.character_list[item]["Capacity"], self.character_list[item]["Supply"]] for item in
                    army.leader_group]
                team_state["troop_call_list"] += [
                    [item, self.character_list[item]["Capacity"], self.character_list[item]["Supply"]] for item in
                    army.ground_group]

                if team == self.player_team:
                    self.grand_event_notification.add_event(("good", self.grab_text(("ui", "info_text_your")) +
                                                             self.grab_text(("character", commander_id, "Name")) +
                                                             self.grab_text(("ui", "info_text_army_arrive"))))
                else:
                    self.grand_event_notification.add_event(("bad", self.grab_text(("ui", "info_text_enemy’s")) +
                                                             self.grab_text(("character", commander_id, "Name")) +
                                                             self.grab_text(("ui", "info_text_army_arrive"))))
            self.awaiting_armies.pop(team)
