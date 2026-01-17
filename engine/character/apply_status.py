def apply_status(self, effect):
    from engine.effect.effect import StatusEffect

    if effect not in self.status_immunity:
        effect_stat = self.status_list[effect]  # get status stat
        if (self.race == "construct" and not effect_stat["Construct Apply"]) or (
                self.race == "undead" and not effect_stat["Undead Apply"]):
            # some status cannot be applied to construct or undead character
            return

        if effect not in self.status_duration:
            # play status animation
            if effect_stat["Status Sprite"]:
                StatusEffect(self, (effect_stat["Status Sprite"], "Base",
                                    self.pos[0], self.pos[1], 0, 0, 0, 1, 1))
        for current_status in tuple(self.status_duration.keys()):  # remove conflicted status
            conflict_check = self.status_list[current_status]["Status Conflict"]
            if conflict_check and effect in conflict_check:
                self.status_duration.pop(current_status)

        if "false_order" in effect_stat["Property"] and not self.is_commander:  # apply false order
            if effect_stat["Property"]["false_order"] == "advance":
                # move command to enemy camp
                self.issue_commander_order(("move", self.battle.team_stat[self.enemy_team]["start_pos"]),
                                           false_order=True)
            elif effect_stat["Property"]["false_order"] == "idle":
                # attack command to enemy camp
                self.issue_commander_order(("idle", self.base_pos[0]),
                                           false_order=True)
            elif effect_stat["Property"]["false_order"] == "retreat":
                # retreat from battle
                self.issue_commander_order(("broken",), false_order=True)
        self.status_duration[effect] = effect_stat["Duration"]
