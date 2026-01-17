from random import randint, uniform

from engine.character.character import BattleCharacter
from engine.constants import Default_Screen_Width, Collision_Grid_Per_Scene, Default_Ground_Pos
from engine.effect.effect import Effect, DamageEffect
from engine.utils.rotation import find_target_point

grid_width = Default_Screen_Width / Collision_Grid_Per_Scene


def activate_strategy(self, team, strategy, strategy_index, base_pos_x):
    stat = self.strategy_list[strategy]
    if (self.team_stat[team]["strategy_resource"] > stat["Resource Cost"] and (
            not self.team_commander[team] or not stat["Activate Range"] or
            abs(self.team_commander[team].base_pos[0] - base_pos_x) < stat["Activate Range"])):
        self.team_stat[team]["strategy_resource"] -= stat["Resource Cost"]

        if team == self.player_team:
            self.drama_text.queue.append((self.localisation.grab_text(("strategy", strategy, "Ally")),
                                          None))
        else:
            self.drama_text.queue.append((self.localisation.grab_text(("strategy", strategy, "Enemy")),
                                          None))
            self.tactical_map_ui.warn_strategy(base_pos_x)

        self.team_stat[team]["strategy_cooldown"][strategy_index] = stat["Cooldown"]
        if stat["Property"]:
            if "weather" in stat["Property"]:  # strategy that change weather
                self.current_weather.__init__(stat["Property"]["weather"], randint(120, 250),
                                              randint(0, 2))

        if stat["Effects"]:
            for effect_stat in stat["Effects"]:
                start_x = (base_pos_x + effect_stat[2]) * self.screen_scale[0]
                start_y = effect_stat[3] * self.screen_scale[1]
                base_target_pos = find_target_point(start_x, start_y, 100000, effect_stat[4])

                Effect(stat["owner data"] | {"team": team},
                       (effect_stat[0], effect_stat[1],
                        start_x, start_y, effect_stat[4],
                        effect_stat[5], effect_stat[6], effect_stat[7],
                        effect_stat[8]), moveset=stat, base_target_pos=base_target_pos, from_owner=False)

        if stat["Damage Effects"]:
            for effect_stat in stat["Damage Effects"]:
                if not self.team_stat[team]["start_pos"]:  # assume that the data is based on right side origin
                    # effect come from left side
                    angle = 180 - effect_stat[4]
                    start_x = (base_pos_x - effect_stat[2]) * self.screen_scale[0]
                else:
                    # effect come from right side
                    angle = effect_stat[4]
                    start_x = (base_pos_x + effect_stat[2]) * self.screen_scale[0]
                start_y = effect_stat[3] * self.screen_scale[1]
                base_target_pos = find_target_point(start_x, start_y, 100000, angle)
                DamageEffect(stat["owner data"] | {"team": team},
                             (effect_stat[0], effect_stat[1], start_x, start_y, angle,
                              effect_stat[5], effect_stat[6], effect_stat[7], effect_stat[8]),
                             moveset=stat, base_target_pos=base_target_pos, from_owner=False)

        if stat["Summon"]:
            if "chaos summon" in stat["Property"]:  # chaos summon enemy with neutral team
                team = 0
            for spawn in stat["Summon"]:
                spawn_name = spawn
                spawn_num = 1
                if "+" in spawn_name:  # + indicate number of possible summon number
                    spawn_num = int(spawn_name.split("+")[1])
                    spawn_name = spawn_name.split("+")[0]
                for _ in range(spawn_num):
                    start_x = base_pos_x
                    if start_x < 0:
                        start_x = 0
                    elif start_x > self.base_stage_end:
                        start_x = self.base_stage_end
                    start_pos = (start_x, Default_Ground_Pos)

                    BattleCharacter(self.last_char_game_id,
                                    self.character_data.character_list[spawn_name] |
                                    {"ID": spawn_name, "Team": team, "POS": start_pos}, is_summon=True)
                    self.last_char_game_id += 1
                    Effect(None, ("Movement", "Summon", start_pos[0],
                                  start_pos[1], 0, 0, 0, 1, 1), from_owner=False)

        range_check = stat["Range"]
        if stat["Enemy Status"]:
            grid_left = int((base_pos_x - range_check) / grid_width)
            if grid_left < 0:
                grid_left = 0
            grid_right = int((base_pos_x + range_check) / grid_width) + 1
            if grid_right > self.last_grid:
                grid_right = self.last_grid
            grid_range = range(grid_left, grid_right)
            for grid in grid_range:
                for enemy in self.all_team_ground_enemy_collision_grids[team][grid]:
                    if abs(enemy.base_pos[0] - base_pos_x) < range_check:
                        for effect in stat["Enemy Status"]:
                            enemy.apply_status(effect)
                for enemy in self.all_team_air_enemy_collision_grids[team][grid]:
                    if abs(enemy.base_pos[0] - base_pos_x) < range_check:
                        for effect in stat["Enemy Status"]:
                            enemy.apply_status(effect)

        if stat["Status"]:
            for ally in [key for key in self.all_team_ally[team] if abs(key.base_pos[0] - base_pos_x) < range_check]:
                for effect in stat["Status"]:
                    ally.apply_status(effect)
        return True
