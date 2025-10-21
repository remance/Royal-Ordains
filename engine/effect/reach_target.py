from random import uniform

import engine.effect.effect
from engine.constants import Default_Ground_Pos


def reach_target(self, how=None):
    if self.after_reach_effect:
        spawn_number = 1
        if "spawn_number" in self.effect_stat["Property"]:
            spawn_number = self.effect_stat["Property"]["spawn_number"]
        for _ in range(spawn_number):
            new_pos = self.pos
            stat = [self.after_reach_effect, "Base", new_pos[0], new_pos[1], 0, 0, 0, 1, 1]
            if "reach_spawn_ground" in self.effect_stat["Property"]:  # reach effect spawn with rect bottom on ground
                stat[3] = Default_Ground_Pos * self.screen_scale[1]
            if "spawn_all_angle" in self.effect_stat["Property"]:
                stat[4] = uniform(0, 359)
            if "spawn_same_angle" in self.effect_stat["Property"]:
                stat[4] = self.angle + uniform(-10, 10)
            if "no damage" in self.effect_stat["Property"] or not self.effect_list[self.after_reach_effect]["Damage"]:
                engine.effect.effect.Effect(self.owner_data, stat, moveset=self.current_moveset,
                                            from_owner=False)
            else:
                engine.effect.effect.DamageEffect(self.owner_data, stat, moveset=self.current_moveset,
                                                  from_owner=False)

    if self.after_reach and how == "ground":  # effect reach ground and does not have reach effect, blit sprite to scene for stuck effect
        self.battle.scene.full_scene_image.blit(self.image, self.rect)

    self.clean_object()
