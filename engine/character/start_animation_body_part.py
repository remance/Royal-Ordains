def start_animation_body_part(self, new_animation=False):
    from engine.character.character import BattleAICharacter
    from engine.effect.effect import Effect, DamageEffect, TrapEffect
    current_animation_data = self.current_animation_direction[self.show_frame]
    for key, part_data in current_animation_data.items():
        if part_data:
            if "effect_" in key and not self.battle.cutscene_playing:
                if part_data[8]:  # damage effect
                    if "summon" in self.current_moveset["Property"]:
                        # summon AI character, using effect with damage does not create Effect
                        start_pos = (self.base_pos[0] + (part_data[2]),
                                     self.base_pos[1] + (part_data[3]))
                        BattleAICharacter("summon", -1, self.character_data.character_list[
                            self.current_moveset["Property"]["summon"]] |
                                                   {"ID": self.current_moveset["Property"]["summon"],
                                                    "Sprite Ver": self.sprite_ver, "Angle": self.angle,
                                                    "Team": self.team, "POS": start_pos,
                                                    "Arrive Condition": ()}, leader=self)

                    elif "trap" in self.effect_list[part_data[0]]["Property"]:
                        TrapEffect(self, part_data, part_data[6], self.current_moveset)
                    else:
                        DamageEffect(self, part_data, part_data[6], self.current_moveset)
                else:
                    Effect(self, part_data, part_data[6], moveset=self.current_moveset)
            else:
                if key in self.body_parts:
                    # only change part if data not same as previous one
                    self.body_parts[key].get_part(part_data, new_animation)
        elif key in self.body_parts:  # only reset for body part, not effect part
            self.body_parts[key].data = ()
            self.body_parts[key].re_rect()
            self.body_parts[key].already_hit = []
