from engine.constants import Retinue_Leadership_Add_Modifier


def add_new_army_arrive(self):
    """Check for sprite loading and add reinforcement after finish loading"""
    for thread in tuple(self.load_sprite_background_threads):
        if not thread.is_alive():
            thread.join()
            self.load_sprite_background_threads.remove(thread)
    if not self.load_sprite_background_threads:
        grab_text = self.grab_text
        player_team = self.player_team
        strategy_change = False
        for team, army_list in tuple(self.awaiting_armies.items()):
            for army in army_list:
                team_state = self.team_state[team]
                commander_id = army.commander_id
                if len(team_state["active_retinue"]) < 3:
                    # add retinue until reach 3
                    if army.army_followers["retinue"]:
                        for retinue in [item[0] for item in army.army_followers["retinue"] if item[1]]:
                            strategy_change = True
                            team_state["leadership"] += (self.character_list[retinue]["Leadership"] *
                                                         Retinue_Leadership_Add_Modifier)
                            self.add_strategy_to_team_state(team_state, self.character_list[retinue]["Strategy"])
                            team_state["active_retinue"].append(retinue)
                            if len(team_state["active_retinue"]) == 3:
                                break
                        if team == player_team:
                            self.strategy_select_ui.setup()

                team_state["reinforcement_army"].append(army)

                self.add_new_army_to_reinforcement(team, team_state, army)

                if team == player_team:
                    self.grand_event_notification.add_event(("good", grab_text(("ui", "info_text_your")) +
                                                             grab_text(("character", commander_id, "Name")) +
                                                             grab_text(("ui", "info_text_army_arrive"))))
                else:
                    self.grand_event_notification.add_event(("bad", grab_text(("ui", "info_text_enemy’s")) +
                                                             grab_text(("character", commander_id, "Name")) +
                                                             grab_text(("ui", "info_text_army_arrive"))))
            self.awaiting_armies.pop(team)
        # change strategy list for ai commander in case new army add new strategies
        if strategy_change:
            self.battle_ai_commander1.change_strategy()
            self.battle_ai_commander2.change_strategy()
