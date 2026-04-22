def change_phase(self):
    if self.game_id not in self.grand.current_campaign_state["battle"]["armies"]:  # in battle
        pass

    elif self.assembling:
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

    elif self.travelling:
        travelling = self.travelling
        travelling["progress"] += 1
        if travelling["progress"] == travelling["difficulties"][0]:
            # move to next dot in route
            travelling["progress"] = 0  # reset progress
            self.grand.dots_army_occupation[self.base_pos].remove(self)  # remove army from old occupation
            self.base_pos = travelling[2][0][1]
            self.grand.dots_army_occupation[self.base_pos].add(self)
            travelling["dot_routes"][0] = travelling["dot_routes"][0][1:]  # remove passed dot

            if not travelling["dot_routes"][0]:  # finish this route
                travelling["dot_routes"].pop(0)
                travelling["difficulties"].pop(0)
                travelling["remain_phase_require"].pop(0)
            else:
                travelling["remain_phase_require"][0] -= travelling["difficulties"][0]

            self.travel_remain = sum(travelling["remain_phase_require"])
            region_colour = tuple(self.grand.grand_map.true_map_image.get_at((int(self.base_pos[0]),
                                                                              int(self.base_pos[1]))))[:3]
            self.current_region = self.grand.region_by_colour_list[region_colour]
            if not travelling["dot_routes"]:  # no more route left, finish travel
                self.travelling = {}

            # if not self.travelling or self.travelling["type"] != "retreat":
            #     # check if enemy exist at base_pos when army reach it
            #