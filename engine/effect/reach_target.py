from random import uniform

import engine.character.character
import engine.effect.effect
from engine.constants import Default_Battle_Ground_Pos, Default_Showcase_Character_POS


def reach_target(self, how=None):
    effect_stat_property = self.effect_stat["Property"]
    if self.after_reach_effect:
        after_reach_effect = self.after_reach_effect

        spawn_number = 1
        if "spawn_number" in effect_stat_property:
            spawn_number = effect_stat_property["spawn_number"]
        for _ in range(spawn_number):
            new_pos = self.pos
            stat = [after_reach_effect, "base", new_pos[0], new_pos[1], 0, 0, 0, self.width_scale, self.height_scale]
            if "reach_effect_spawn_ground" in effect_stat_property:  # reach effect spawn with rect bottom on ground
                stat[3] = Default_Battle_Ground_Pos * self.screen_scale_height
                base_image = self.effect_animation_pool[after_reach_effect]["base"][0][1][1][0]
                if effect_stat_property["reach_effect_spawn_ground"] == "bottom":
                    # spawn position at the bottom of sprite
                    stat[3] -= (base_image["sprite"][0].get_height() / 2) - base_image["offset"][1]
                elif effect_stat_property["reach_effect_spawn_ground"] == "top":
                    # spawn position at the top of sprite
                    stat[3] += (base_image["sprite"][0].get_height() / 2) - base_image["offset"][1]
            if "spawn_all_angle" in effect_stat_property:
                stat[4] = uniform(0, 359)
            if "spawn_same_angle" in effect_stat_property:
                stat[4] = self.angle + uniform(-10, 10)
            if "no_damage" in effect_stat_property or not self.effect_list[after_reach_effect]["Damage"]:
                engine.effect.effect.Effect(self.owner_data, stat, moveset=self.current_moveset,
                                            from_owner=False)
            else:
                engine.effect.effect.DamageEffect(self.owner_data, stat, moveset=self.current_moveset,
                                                  from_owner=False)

    if (self.current_moveset and "summon" in self.current_moveset_property) or "summon" in effect_stat_property:
        # summon battle character, at where effect reach
        if "summon" in self.current_moveset_property:
            summon = self.current_moveset_property["summon"]
        else:
            summon = effect_stat_property["summon"]
        char_stat = {"ID": summon, "direction": self.direction, "Team": self.team, "POS": self.base_pos}
        if "summon_spawn_ground" in effect_stat_property:
            char_stat["spawn_at_ground"] = effect_stat_property["summon_spawn_ground"]
        add_battle_character = engine.character.character.BattleCharacter(
            self.battle.last_char_game_id, self.character_list[summon] | char_stat, is_summon=True)
        add_battle_character.enter_stage()
        self.battle.last_char_game_id += 1

    if self.after_reach and how == "ground":
        # effect reach ground and has after reach property, blit sprite to scene for stuck effect
        self.battle.scene.full_scene_image.blit(self.image, self.rect)

    self.clean_object()


def showcase_reach_target(self, how=None):
    if self.after_reach_effect:
        after_reach_effect = self.after_reach_effect
        effect_stat_property = self.effect_stat["Property"]

        spawn_number = 1
        if "spawn_number" in effect_stat_property:
            spawn_number = effect_stat_property["spawn_number"]
        for _ in range(spawn_number):
            new_pos = self.pos
            stat = [after_reach_effect, "base", new_pos[0], new_pos[1], 0, 0, 0, self.width_scale, self.height_scale]
            if "reach_effect_spawn_ground" in effect_stat_property:  # reach effect spawn with rect bottom on ground
                stat[3] = Default_Showcase_Character_POS[1] * self.screen_scale_height
                base_image = self.effect_animation_pool[after_reach_effect]["base"][0][1][1][0]
                if effect_stat_property["reach_effect_spawn_ground"] == "bottom":
                    # spawn position at the bottom of sprite
                    stat[3] -= (base_image["sprite"][0].get_height() / 2) - base_image["offset"][1]
                elif effect_stat_property["reach_effect_spawn_ground"] == "top":
                    # spawn position at the top of sprite
                    stat[3] += (base_image["sprite"][0].get_height() / 2) - base_image["offset"][1]
            if "spawn_all_angle" in effect_stat_property:
                stat[4] = uniform(0, 359)
            if "spawn_same_angle" in effect_stat_property:
                stat[4] = self.angle + uniform(-10, 10)
            if "no_damage" in effect_stat_property or not self.effect_list[after_reach_effect]["Damage"]:
                engine.effect.effect.ShowcaseEffect(self.owner_data, stat, from_owner=False)
            else:
                engine.effect.effect.ShowcaseEffect(self.owner_data, stat, from_owner=False)
    self.clean_object()
