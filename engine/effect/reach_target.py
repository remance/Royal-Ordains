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
            layer = 0
            if "no dmg" in self.effect_stat["Property"]:
                engine.effect.effect.Effect(self.owner, stat, layer, moveset=self.current_moveset,
                                            from_owner=False)
            else:
                engine.effect.effect.DamageEffect(self.owner, stat, layer, moveset=self.current_moveset,
                                                  from_owner=False)
    elif how == "ground":
        self.battle.scene.full_scene_image.blit(self.image, self.rect)

    if self.other_property:
        if "spawn" in self.other_property and "spawn after" in self.other_property and how == "border":
            effect_stat = None
            if "spawn same" in self.other_property:  # spawn same effect
                effect_stat = list(self.part_stat)
            elif "spawn other" in self.other_property:
                effect_stat = [self.other_property["spawn other"][0], self.other_property["spawn other"][1],
                               self.part_stat[2], self.part_stat[3],
                               self.part_stat[4], self.part_stat[5], self.part_stat[6], self.part_stat[7],
                               self.part_stat[8]]
            if effect_stat:
                spawn_number = 1
                if "spawn number" in self.other_property:
                    spawn_number = int(self.other_property["spawn number"])
                for _ in range(spawn_number):
                    stat = effect_stat
                    if "spawn sky" in self.other_property:
                        stat[3] = -100
                    if self.owner.nearest_enemy and "aim" in self.other_property:
                        # find the nearest enemy to target
                        if self.other_property["aim"] == "target":
                            if self.owner.angle == 90:
                                stat[2] = uniform(self.owner.nearest_enemy.pos[0],
                                                  self.owner.nearest_enemy.pos[0] + (200 * self.screen_scale[0]))
                            else:
                                stat[2] = uniform(self.owner.nearest_enemy.pos[0] - (200 * self.screen_scale[0]),
                                                  self.owner.nearest_enemy.pos[0])

                            self.pos = (stat[2], stat[3])
                            stat[4] = self.set_rotate(self.owner.nearest_enemy.pos, use_pos=True)

                        elif self.other_property["aim"] == "near target":
                            if self.owner.nearest_enemy:  # find the nearest enemy to target
                                if self.owner.angle == 90:
                                    stat[2] = uniform(self.owner.nearest_enemy.pos[0],
                                                      self.owner.nearest_enemy.pos[0] + (
                                                              500 * self.screen_scale[0]))
                                else:
                                    stat[2] = uniform(
                                        self.owner.nearest_enemy.pos[0] - (500 * self.screen_scale[0]),
                                        self.owner.nearest_enemy.pos[0])

                                self.pos = (stat[2], stat[3])
                                target_pos = (uniform(self.owner.nearest_enemy.base_pos[0] - 200,
                                                      self.owner.nearest_enemy.base_pos[0] + 200),
                                              uniform(self.owner.nearest_enemy.base_pos[1] - 200,
                                                      self.owner.nearest_enemy.base_pos[1] + 200))
                                stat[4] = self.set_rotate(target_pos, use_pos=True)

                    else:  # random target instead
                        stat[2] = uniform(self.pos[0] - (self.travel_distance * self.screen_scale[0]),
                                          self.pos[0] + (self.travel_distance * self.screen_scale[0]))
                        if self.owner.angle == 90:
                            stat[4] = uniform(160, 180)
                        else:
                            stat[4] = uniform(-180, -160)

                    moveset = self.current_moveset.copy()
                    moveset["Property"] = [item for item in moveset["Property"] if
                                           item != "spawn"]  # remove spawn property so it not loop spawn
                    engine.effect.effect.Effect(self.owner, stat, 0, moveset=moveset, from_owner=False)

    self.clean_object()
