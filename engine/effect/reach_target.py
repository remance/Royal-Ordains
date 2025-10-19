from random import uniform

import engine.effect.effect


def reach_target(self, how=None):
    if self.reach_effect:
        spawn_number = 1
        if "spawn number" in self.effect_stat["Property"]:
            spawn_number = self.effect_stat["Property"]["spawn number"]
        for _ in range(spawn_number):
            new_pos = self.pos
            stat = [self.reach_effect, "Base", new_pos[0], new_pos[1], 0, 0, 0, 1, 1]
            if "reach spawn ground" in self.effect_stat[
                "Property"]:  # reach effect spawn with rect bottom on ground
                height = \
                    self.effect_animation_pool[self.reach_effect]["Base"][self.width_scale][self.height_scale][0][
                        self.sprite_flip].get_height() / 4
                stat[3] = self.pos[1] - height
            if "spawn all angle" in self.effect_stat["Property"]:
                stat[4] = uniform(0, 359)
            if "spawn same angle" in self.effect_stat["Property"]:
                stat[4] = self.angle + uniform(-10, 10)
            if "no damage" in self.effect_stat["Property"]:
                engine.effect.effect.Effect(self.owner_data, stat, moveset=self.current_moveset,
                                            from_owner=False)
            else:
                engine.effect.effect.DamageEffect(self.owner_data, stat, moveset=self.current_moveset,
                                                  from_owner=False)
    elif how == "ground":  # effect reach ground and does not have reach effect, blit sprite to scene for stuck effect
        self.battle.scene.full_scene_image.blit(self.image, self.rect)

    self.clean_object()
