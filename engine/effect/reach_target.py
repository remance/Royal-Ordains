from random import uniform

import engine.effect.effect
from engine.constants import Default_Ground_Pos


def reach_target(self, how=None):
    if self.after_reach_effect:
        after_reach_effect = self.after_reach_effect
        effect_stat = self.effect_stat

        spawn_number = 1
        if "spawn_number" in effect_stat["Property"]:
            spawn_number = effect_stat["Property"]["spawn_number"]
        for _ in range(spawn_number):
            new_pos = self.pos
            stat = [after_reach_effect, "Base", new_pos[0], new_pos[1], 0, 0, 0, 1, 1]
            if "reach_effect_spawn_ground" in effect_stat["Property"]:  # reach effect spawn with rect bottom on ground
                stat[3] = Default_Ground_Pos * self.screen_scale[1]
                if effect_stat["Property"]["reach_effect_spawn_ground"] == "bottom":
                    # spawn position at the bottom of sprite
                    stat[3] -= (self.effect_animation_pool[after_reach_effect]["Base"][0][1][1][0]["sprite"][
                                    0].get_height() / 2)
                elif effect_stat["Property"]["reach_effect_spawn_ground"] == "top":
                    # spawn position at the top of sprite
                    stat[3] += (self.effect_animation_pool[after_reach_effect]["Base"][0][1][1][0]["sprite"][
                                    0].get_height() / 2)
            if "spawn_all_angle" in effect_stat["Property"]:
                stat[4] = uniform(0, 359)
            if "spawn_same_angle" in effect_stat["Property"]:
                stat[4] = self.angle + uniform(-10, 10)
            if "no_damage" in effect_stat["Property"] or not self.effect_list[after_reach_effect]["Damage"]:
                engine.effect.effect.Effect(self.owner_data, stat, moveset=self.current_moveset,
                                            from_owner=False)
            else:
                engine.effect.effect.DamageEffect(self.owner_data, stat, moveset=self.current_moveset,
                                                  from_owner=False)

    if self.after_reach and how == "ground":
        # effect reach ground and does not have reach effect, blit sprite to scene for stuck effect
        self.battle.scene.full_scene_image.blit(self.image, self.rect)

    self.clean_object()
