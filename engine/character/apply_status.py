def apply_status(self, effect):
    from engine.effect.effect import StatusEffect

    effect_stat = self.status_list[effect]  # get status stat
    if effect not in self.status_duration:
        # play status animation
        if effect_stat["Status Sprite"]:
            StatusEffect(self, (effect_stat["Status Sprite"], "Base",
                                self.pos[0], self.pos[1], 0, 1, 0, 1), 0)
    for current_status in self.status_duration:  # remove conflicted status
        conflict_check = self.status_list[current_status]["Status Conflict"]
        if conflict_check and effect in conflict_check:
            self.status_duration.remove(current_status)

    self.status_duration[effect] = effect_stat["Duration"]
