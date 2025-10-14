from random import randint, uniform
from pygame import sprite


def activate_strategy(self, stat):
    if stat["Property"]:
        if "weather" in stat["Property"]:  # item that change weather
            self.battle.current_weather.__init__(stat["Property"]["weather"], randint(0, 359),
                                                 randint(0, 3))
        for spawn_type in ("chaos summon", "chaos invasion", "summon"):
            if spawn_type in stat["Property"]:
                team = self.team
                if "chaos" in spawn_type:  # chaos summon enemy with neutral team
                    team = 0
                for spawn, chance in stat["Property"][spawn_type].items():
                    spawn_name = spawn
                    if "+" in spawn_name:  # + indicate number of possible drop
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
                                BattleCharacter(None,
                                                self.character_data.character_list[spawn_name] |
                                                {"ID": spawn_name,
                                                 "Angle": self.angle,
                                                 "Team": team, "POS": start_pos,
                                                 "Arrive Condition": ()})
                                Effect(None, ("Movement", "Summon", start_pos[0],
                                              start_pos[1], -self.angle, 1, 0, 1, 1), 0)
                    else:
                        if chance >= uniform(0, 100):
                            if "invasion" in spawn_type:
                                start_pos = (self.base_pos[0] + uniform(-2000, 2000),
                                             self.base_pos[1])
                            else:
                                start_pos = (self.base_pos[0] + uniform(-200, 200),
                                             self.base_pos[1])
                            BattleCharacter(None,
                                            self.character_data.character_list[spawn_name] |
                                            {"ID": spawn_name, "Angle": self.angle,
                                             "Team": team, "POS": start_pos,
                                             "Arrive Condition": ()})

    for ally in self.near_ally:
        if ally[1] <= stat["Range"]:  # apply status based on range
            if stat["Status"]:
                for effect in stat["Status"]:
                    ally[0].apply_status(effect)

    for enemy in self.near_enemy:
        if enemy[1] <= stat["Range"]:  # apply status based on range
            if stat["Enemy Status"]:
                for effect in stat["Enemy Status"]:
                    enemy[0].apply_status(effect)
