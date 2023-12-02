def apply_status(self, effect):
    from engine.effect.effect import StatusEffect

    effect_stat = self.status_list[effect]  # get status stat
    if effect not in self.status_duration:
        self.status_effect[effect] = effect_stat  # add status effect
        # play status animation
        if effect_stat["Status Sprite"]:
            StatusEffect(self, (effect_stat["Status Sprite"], effect_stat["Status Sprite"],
                                self.pos[0], self.pos[1], 0, 1, 0, 1), 0)

    self.status_duration[effect] = effect_stat["Duration"]
