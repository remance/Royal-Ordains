from operator import itemgetter

from random import randint, uniform
from pygame import sprite

from engine.character.character import BattleCharacter
from engine.effect.effect import Effect, DamageEffect

from engine.utils.rotation import find_target_point
from engine.constants import Default_Screen_Width, Collision_Grid_Per_Scene

grid_width = Default_Screen_Width / Collision_Grid_Per_Scene


def activate_strategy(self, team, strategy, base_pos_x):
    stat = self.strategy_list[strategy]
    if (self.team_stat[team]["strategy_resource"] > stat["Resource Cost"] and (not self.team_commander[team] or
            abs(self.team_commander[team].base_pos[0] - base_pos_x) < stat["Activate Range"])):
        print(stat)
        self.team_stat[team]["strategy_resource"] -= stat["Resource Cost"]
        if team == 1:
            self.drama_text.queue.append((self.localisation.grab_text(("strategy", strategy, "Ally")),
                                          None))
        else:
            self.drama_text.queue.append((self.localisation.grab_text(("strategy", strategy, "Enemy")),
                                          None))
        self.battle.team_stat[team]["strategy"][strategy] = stat["Cooldown"]

        if stat["Property"]:
            if "weather" in stat["Property"]:  # strategy that change weather
                self.battle.current_weather.__init__(stat["Property"]["weather"], randint(120, 250),
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
                start_x = (base_pos_x + effect_stat[2]) * self.screen_scale[0]
                start_y = effect_stat[3] * self.screen_scale[1]
                base_target_pos = find_target_point(start_x, start_y, 100000, effect_stat[4])
                DamageEffect(stat["owner data"] | {"team": team},
                             (effect_stat[0], effect_stat[1], start_x, start_y, effect_stat[4],
                              effect_stat[5], effect_stat[6], effect_stat[7], effect_stat[8]),
                             moveset=stat, base_target_pos=base_target_pos, from_owner=False)

        if stat["Summon"]:
            team = self.team
            if "chaos summon" in stat["Property"]:  # chaos summon enemy with neutral team
                team = 0
            for spawn in stat["Summon"]:
                spawn_name = spawn
                if "+" in spawn_name:  # + indicate number of possible summon number
                    spawn_num = int(spawn_name.split("+")[1])
                    spawn_name = spawn_name.split("+")[0]
                    for _ in range(spawn_num):
                        if chance >= uniform(0, 100):
                            if "invasion" in spawn_type:
                                start_pos = (self.base_pos[0] + uniform(-2000, 2000),
                                             self.base_pos[1])
                            else:
                                start_pos = (self.base_pos[0] + uniform(-200, 200),
                                             self.base_pos[1])

                            start_pos = (self.base_pos[0] + (part_data[2]),
                                         self.base_ground_pos)

                            BattleCharacter(self.battle.last_char_game_id,
                                            self.character_data.character_list[spawn_name] |
                                            {"ID": spawn_name,
                                             "Direction": self.direction,
                                             "Team": team, "POS": start_pos, "Start Health": 1,
                                             "Start Resource": 1}, is_summon=True)
                            self.battle.last_char_game_id += 1
                            Effect(None, ("Movement", "Summon", start_pos[0],
                                          start_pos[1], -self.angle, 1, 0, 1, 1), 0)
                else:
                    start_pos = (self.base_pos[0] + uniform(-200, 200),
                                 self.base_pos[1])
                    BattleCharacter(self.battle.last_char_game_id,
                                    self.character_data.character_list[spawn_name] |
                                    {"ID": spawn_name,
                                     "Direction": self.direction,
                                     "Team": team, "POS": start_pos, "Start Health": 1,
                                     "Start Resource": 1}, is_summon=True)

                    self.battle.last_char_game_id += 1

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
