from engine.effect.effect import Effect, DamageEffect


def start_animation_body_part(self, new_animation=False):
    current_animation_data = self.current_animation_direction[self.show_frame]
    for key, part_data in current_animation_data.items():
        if part_data:
            if "effect" in key:
                if part_data[8]:  # damage effect
                    DamageEffect(self, part_data, part_data[6], self.current_moveset)
                else:
                    Effect(self, part_data, part_data[6])
            else:
                if key in self.body_parts:
                    # only change part if data not same as previous one
                    self.body_parts[key].get_part(part_data, new_animation)
        elif key in self.body_parts:
            self.body_parts[key].data = []
            self.body_parts[key].re_rect()
            self.body_parts[key].already_hit = []
