def change_phase(self):
    current_campaign_state = self.grand.current_campaign_state
    campaign_battle_dot = current_campaign_state["battle"]["dot"]
    campaign_battle_factions = current_campaign_state["battle"]["factions"]
    campaign_battle_armies = current_campaign_state["battle"]["armies"]
    campaign_faction_state = current_campaign_state["faction"][self.faction]
    dots_army_occupation = self.grand.dots_army_occupation
    activity = self.activity
    if self.game_id in campaign_battle_armies:  # in battle
        return

    elif activity:
        if "travel" in activity:
            activity["progress"] += 1
            if activity["progress"] == activity["difficulties"][0]:
                # move to next dot in route
                next_dot = activity["dot_routes"][0][1]
                if (self.travelling["type"] == "retreat" or next_dot not in campaign_battle_dot or
                        self.faction in campaign_battle_factions[next_dot]):
                    # can only move to that dots if no battle is taking place between other unrelated factions
                    activity["progress"] = 0  # reset progress
                    dots_army_occupation[self.base_pos].remove(self)  # remove army from old occupation
                    self.base_pos = activity["dot_routes"][0][1]
                    if self.game_id not in dots_army_occupation[self.base_pos]:
                        dots_army_occupation[self.base_pos].append(self)
                        # sort army dot position by power
                        dots_army_occupation[self.base_pos].sort(key=lambda item: item.power)
                        if self.base_pos not in campaign_battle_dot:  # no ongoing battle on this dot, check if enemy exist
                            # check if army move to new dot will start battle with enemies in the same dot
                            enemy_faction_alliance = []
                            battle_army_list = {1: self, 2: []}
                            alliance = current_campaign_state["faction"][self.faction]["alliance"]
                            faction_alliance = (self.faction,)
                            if alliance:
                                faction_alliance = current_campaign_state["alliance"][alliance]

                            for army in dots_army_occupation[self.base_pos]:
                                if army.faction not in faction_alliance:  # enemy faction
                                    # get enemy alliance
                                    if not enemy_faction_alliance:
                                        enemy_alliance = current_campaign_state["faction"][self.faction]["alliance"]
                                        enemy_faction_alliance = (self.faction,)
                                        if enemy_alliance:
                                            enemy_faction_alliance = current_campaign_state["alliance"][enemy_alliance]
                                    elif army.faction not in enemy_faction_alliance:
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
                                self.player_army_list_ui.reset_card(self)

                    activity["dot_routes"][0].pop(0)  # remove passed dot

                    if len(activity["dot_routes"][0]) == 1:  # finish this route
                        activity["id_routes"].pop(0)
                        activity["dot_routes"].pop(0)
                        activity["difficulties"].pop(0)
                        activity["remain_phase_require"].pop(0)
                    else:
                        activity["remain_phase_require"][0].pop(0)

                    region_colour = tuple(self.base_world_map.get_at((int(self.base_pos[0]),
                                                                      int(self.base_pos[1]))))[:3]
                    self.current_region = self.grand.region_by_colour_index[region_colour]
                    if not activity["dot_routes"]:  # no more route left, finish travel
                        self.travelling = {}
    else:
        if (self.base_pos in self.region_by_pos_index and
                current_campaign_state["region"]["control"][self.region_by_pos_index[self.base_pos]] == self.faction):
            # idle at faction owned settlement
            if self.supply < self.max_supply:
                # replenish supply
                faction_state = current_campaign_state["faction"][self.faction]
                remain_supply = faction_state["supply"]
                if remain_supply:
                    replenish_supply = self.max_supply - self.supply
                    if replenish_supply > remain_supply:
                        replenish_supply = remain_supply
                    self.supply += replenish_supply
                    faction_state["supply"] = remain_supply - replenish_supply

            if "assemble" in self.activity:
                assembling = self.assembling_followers
                army_change = False
                for character, value in assembling:
                    value["time"] -= 1
                    if not value["time"]:  # finish assembling for this character, add to group
                        if value["index"] == "new":
                            group[value["type"]].append(value["character"])
                        else:
                            group[value["type"]][value["index"]] = value["character"]

                        assembling.pop(character)
                        army_change = True

                if army_change:
                    self.reset_stat()
