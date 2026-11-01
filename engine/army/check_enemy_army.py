def check_enemy_army(self):
    current_campaign_state = self.grand.current_campaign_state
    campaign_battle_dot = current_campaign_state["battle"]["dot"]
    campaign_battle_factions = current_campaign_state["battle"]["factions"]
    campaign_battle_armies = current_campaign_state["battle"]["armies"]
    campaign_faction_state = current_campaign_state["faction"][self.faction]
    dots_army_occupation = self.dots_army_occupation
    if self.base_pos not in campaign_battle_dot:  # no ongoing battle on this dot, check if enemy exist
        # check if army move to new dot will start battle with enemies in the same dot
        enemy_alliance = []
        battle_army_list = {1: self, 2: []}
        alliance = current_campaign_state["faction"][self.faction]["alliance"]

        for army in dots_army_occupation[self.base_pos]:
            if army.faction not in alliance:  # enemy faction
                # get enemy alliance
                if not enemy_alliance:
                    enemy_alliance = current_campaign_state["faction"][self.faction]["alliance"]
                elif army.faction not in enemy_alliance:
                    # only 2 alliances can fight in a battle,
                    # other factions will wait while others in battle
                    pass
                else:  # enemy army join the battle
                    battle_army_list[2].append(army)

        if battle_army_list[2]:  # start new battle
            self.grand.start_battle_engagement(battle_army_list, self.base_pos)

    elif (campaign_battle_factions["team"][0] in campaign_faction_state["alliance"] or
          campaign_battle_factions["team"][1] in campaign_faction_state["alliance"]):
        # ongoing battle belong to this army faction alliance, join in battle
        campaign_battle_armies.append(self.game_id)
        campaign_battle_factions
        if self.faction == self.player_faction:
            self.grand_army_list_ui.reset_card(self)