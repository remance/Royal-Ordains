def change_phase(self):
    current_campaign_state = self.grand.current_campaign_state
    campaign_battle_dot = current_campaign_state["battle"]["dot"]
    campaign_battle_state = current_campaign_state["battle"]["state"]
    campaign_battle_armies = current_campaign_state["battle"]["armies"]
    campaign_faction_state = current_campaign_state["faction"][self.faction]
    dots_army_occupation = self.grand.dots_army_occupation
    if self.game_id in campaign_battle_armies:  # in battle
        return

    elif self.travelling:
        travelling = self.travelling
        travelling["progress"] += 1
        if travelling["progress"] == travelling["difficulties"][0]:
            # move to next dot in route
            next_dot = travelling["dot_routes"][0][1]
            if self.travelling["type"] == "retreat" or next_dot not in campaign_battle_dot or any([item in campaign_battle_state[next_dot] for item in campaign_faction_state["alliance"]]):
                # can only move to that dots if no battle is taking place between other factions
                travelling["progress"] = 0  # reset progress
                dots_army_occupation[self.base_pos].pop(self.game_id)  # remove army from old occupation
                self.base_pos = travelling["dot_routes"][0][1]
                if self.game_id not in dots_army_occupation[self.base_pos]:
                    dots_army_occupation[self.base_pos][self.game_id] = self
                    dots_army_occupation[self.base_pos] = {k: v for k, v in sorted(dots_army_occupation[self.base_pos].items(), key=lambda item: item[0])}
                    # check if army move to new dot will start battle with enemies in the same dot
                    if self.base_pos not in campaign_battle_dot:
                        enemy_alliance_fight = None
                        battle_army_list = [self]
                        for army in dots_army_occupation[self.base_pos].values():
                            if army.faction in campaign_faction_state["hostile"]:
                                if enemy_alliance_fight and army.faction not in enemy_alliance_fight:
                                    # only 2 factions can fight in a battle, other factions can pass through
                                    # while others in battle
                                    pass
                                else:  # start new battle
                                    if not enemy_alliance_fight:
                                        enemy_alliance_fight = current_campaign_state["faction"][army.faction]["alliance"]
                                    battle_army_list.append(army)
                        if enemy_alliance_fight:
                            self.grand.start_battle_engagement(battle_army_list, self.base_pos,
                                                               campaign_faction_state["alliance"])

                    elif (campaign_battle_state["team"][0] in campaign_faction_state["alliance"] or
                          campaign_battle_state["team"][1] in campaign_faction_state["alliance"]):
                        # ongoing battle belong to this army faction alliance, join in battle
                        campaign_battle_armies.append(self.game_id)
                        campaign_battle_state
                        if self.faction == self.player_faction:
                            self.player_army_list_ui.reset_card(self)

                travelling["dot_routes"][0].pop(0)  # remove passed dot

                if len(travelling["dot_routes"][0]) == 1:  # finish this route
                    travelling["id_routes"].pop(0)
                    travelling["dot_routes"].pop(0)
                    travelling["difficulties"].pop(0)
                    travelling["remain_phase_require"].pop(0)
                else:
                    travelling["remain_phase_require"][0].pop(0)

                self.travel_remain = sum([sum(value) for value in travelling["remain_phase_require"]])
                region_colour = tuple(self.grand.grand_map.true_map_image.get_at((int(self.base_pos[0]),
                                                                                  int(self.base_pos[1]))))[:3]
                self.current_region = self.grand.region_by_colour_index[region_colour]
                if not travelling["dot_routes"]:  # no more route left, finish travel
                    self.travelling = {}
    else:
        if (self.supply < self.max_supply and self.base_pos in self.region_by_pos_index and
                current_campaign_state["region"]["control"][self.region_by_pos_index[self.base_pos]] == self.faction):
            # replenish supply when idle at faction owned settlement
            faction_state = current_campaign_state["faction"][self.faction]
            remain_supply = faction_state["supply"]
            if remain_supply:
                replenish_supply = self.max_supply - self.supply
                if replenish_supply > remain_supply:
                    replenish_supply = remain_supply
                self.supply += replenish_supply
                faction_state["supply"] = remain_supply - replenish_supply

        if self.assembling:
            assembling = self.assembling
            army_change = False
            group = {"leader": self.leader_group, "ground": self.ground_group,
                     "air": self.air_group, "retinue": self.retinue}
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