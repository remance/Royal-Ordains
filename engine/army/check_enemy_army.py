def check_enemy_army(self):
    grand = self.grand
    current_campaign_state = grand.current_campaign_state
    campaign_battle_dot = current_campaign_state["battle"]["dot"]
    campaign_battle_faction = current_campaign_state["battle"]["faction"]
    campaign_battle_armies = current_campaign_state["battle"]["army"]
    faction_state = current_campaign_state["faction"][self.faction]
    dots_army_occupation = self.dots_army_occupation
    if self.base_pos not in campaign_battle_dot:
        # no ongoing battle on this dot, check if enemy exist
        # check if army move to new dot will start battle with any enemy in the same dot
        enemy_alliance = []
        battle_army_list = {1: [self], 2: []}
        alliance = current_campaign_state["faction"][self.faction]["alliance"]
        region_owner = current_campaign_state["region"][self.current_region]["control"]

        for army in dots_army_occupation[self.base_pos]:
            if army != self and army.faction not in alliance:  # enemy faction
                # get enemy alliance
                if not enemy_alliance:
                    enemy_alliance = current_campaign_state["faction"][self.faction]["alliance"]
                    battle_army_list[2].append(army)
                    campaign_battle_armies.append(army)
                elif army.faction in enemy_alliance:  # enemy army join the battle
                    # only 2 alliances can fight in a battle,
                    # other factions will wait while others in battle
                    battle_army_list[2].append(army)
                    campaign_battle_armies.append(army)

        if self.base_pos in self.region_settlement_pos_index and region_owner != self.faction and region_owner not in alliance:
            # enemy region, add garrison army if exist
            garrison_army = grand.garrison_army_list[self.region_settlement_pos_index[self.base_pos]]

            if garrison_army.commander_id or battle_army_list[2]:
                # either garrison has commander or normal army already exist that they can join
                battle_army_list[2].append(garrison_army)

        if battle_army_list[2]:  # start new battle
            grand.start_battle_engagement(battle_army_list, self.base_pos)
            return True

    else:
        battle_faction = campaign_battle_faction[self.base_pos]
        if (self.faction in campaign_battle_faction[self.base_pos] or
                battle_faction[0] in faction_state["alliance"] or
                battle_faction[1] in faction_state["alliance"]):
            # ongoing battle belong to this army faction alliance, join in battle
            team = 1
            if self.faction == battle_faction[1] or battle_faction[1] in faction_state["alliance"]:
                team = 2
            campaign_battle_armies.append(self.game_id)
            team_state = current_campaign_state["battle"]["battles"][self.base_pos]["team"][team]
            current_campaign_state["battle"]["battles"][self.base_pos]["team"][team]["reinforcement_army"].append(self)
            if self.belong_to_player_faction and self.faction not in battle_faction:
                # replace battle faction as player when player faction join for banner colouring
                battle_faction[team - 1] = self.faction
            self.battle.add_new_army_to_reinforcement(team_state, self)
            if self.belong_to_player_faction:
                grand.army_list_ui.reset_card(self)
            return True
    return None
