def apply_status(self, status):
    # from engine.effect.effect import StatusEffect
    if status not in self.status_immunity:
        status_stat = self.status_list[status]  # get status stat
        if (self.race == "construct" and not status_stat["Construct Apply"]) or (
                self.race == "undead" and not status_stat["Undead Apply"]):
            # some status cannot be applied to construct or undead character
            return

        # if effect not in self.status_duration:
        #     # play status animation
        #     if effect_stat["Status Sprite"]:
        #         StatusEffect(self, (effect_stat["Status Sprite"], "base",
        #                             self.pos[0], self.pos[1], 0, 0, 0, 1, 1))
        if self.status_duration:
            conflict_found = False
            for current_status in tuple(self.status_duration.keys()):  # remove conflicted status
                conflict_check = self.status_list[current_status]["Status Conflict"]
                if conflict_check and status in conflict_check:
                    conflict_found = True
                    self.status_duration.pop(current_status)
            if conflict_found:
                return  # conflicting also prevent the status from being applied

        if "false_order" in status_stat["Property"] and not self.is_commander:  # apply false order
            if status_stat["Property"]["false_order"] == "advance":
                # move command to enemy camp
                self.issue_commander_order(("move", self.battle.team_stat[self.enemy_team]["start_pos"]),
                                           false_order=True)
            elif status_stat["Property"]["false_order"] == "idle":
                # attack command to enemy camp
                self.issue_commander_order(("idle", self.base_pos[0]),
                                           false_order=True)
            elif status_stat["Property"]["false_order"] == "retreat":
                # retreat from battle
                self.issue_commander_order(("broken",), false_order=True)
        self.status_duration[status] = status_stat["Duration"]
