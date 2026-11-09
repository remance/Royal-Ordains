def apply_status(self, status):
    # from engine.effect.effect import StatusEffect
    if status not in self.status_immunity:
        status_stat = self.status_list[status]  # get status stat
        status_property = status_stat["Property"]
        if self.race_type in status_stat["Exclude Race Type"]:
            # some status cannot be applied to certain race type
            return

        # if effect not in self.status_duration:
        #     # play status animation
        #     if effect_stat["Status Sprite"]:
        #         StatusEffect(self, (effect_stat["Status Sprite"], "base",
        #                             self.pos[0], self.pos[1], 0, 0, 0, 1, 1))
        if self.status_duration:
            for current_status in tuple(self.status_duration.keys()):  # remove conflicted status
                conflict_check = self.status_list[current_status]["Status Conflict"]
                if conflict_check and status in conflict_check:
                    self.status_duration.pop(current_status)
                    return  # conflicting also prevent the status from being applied

        if "false_order" in status_property and not self.is_commander:  # apply false order
            if status_property["false_order"] == "advance":
                # move command to enemy camp
                self.issue_commander_order(("move", self.battle.team_state[self.enemy_team]["start_pos"]),
                                           false_order=True)
            elif status_property["false_order"] == "idle":
                # attack command to enemy camp
                self.issue_commander_order(("idle", self.base_pos[0]),
                                           false_order=True)
            elif status_property["false_order"] == "retreat":
                # retreat from battle
                if self.no_move:  # character that cannot move go into idle instead
                    self.issue_commander_order(("idle", self.base_pos[0]),
                                               false_order=True)
                else:
                    self.issue_commander_order(("broken",), false_order=True)
        self.status_duration[status] = status_stat["Duration"]
