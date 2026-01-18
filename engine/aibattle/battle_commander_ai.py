from random import uniform
from types import MethodType

from engine.aibattle.conduct_commander import conduct_commander
from engine.aibattle.conduct_troop_call import conduct_troop_call
from engine.aibattle.gather_info import clever_gather_info_level
from engine.utils.common import clean_object


class BattleCommanderAI:
    """AI action depend on their personality stat where:
    aggressiveness determine their combat tactic,
    cleverness determine what and how they think on gathered information,
    swiftness determine how fast they can act on the given information
    """
    battle = None

    conduct_troop_call = conduct_troop_call
    conduct_commander = conduct_commander

    def __init__(self, team, can_retreat=True):
        self.team = team
        self.enemy_team = 1
        if self.team == 1:
            self.enemy_team = 2
        self.can_retreat = can_retreat
        self.call_reinforcement = self.battle.call_reinforcement
        self.call_in_air_group = self.battle.call_in_air_group
        self.current_weather = self.battle.current_weather
        self.activate_strategy = self.battle.activate_strategy
        self.weather_list = self.battle.weather_list
        self.character_list = self.battle.character_list
        self.commander = self.battle.team_commander[team]
        self.enemy_commander = self.battle.team_commander[self.enemy_team]
        self.team_stat = self.battle.team_stat[team]
        self.enemy_team_stat = self.battle.team_stat[self.enemy_team]

        self.ground_enemy_collision_grids = self.battle.all_team_ground_enemy_collision_grids[self.team]
        self.air_enemy_collision_grids = self.battle.all_team_air_enemy_collision_grids[self.team]

        self.ground_ally_collision_grids = self.battle.all_team_ground_enemy_collision_grids[self.enemy_team]
        self.can_cure_status_list = self.battle.can_cure_status_list
        self.can_clarity_status_list = self.battle.can_clarity_status_list
        self.strategy_list = self.battle.strategy_list
        self.last_grid = self.battle.last_grid
        self.air_group = self.team_stat["air_group"]
        self.own_strategy = self.team_stat["strategy"]
        self.own_strategy_type = {"weather": set(), "ally": set(), "enemy": set(), "summon": set(),
                                  "cure": set(), "clarity": set()}
        self.has_cure_strategy = False
        self.has_clarity_strategy = False

        self.reinforcement = self.battle.later_reinforcement["team"][team]
        self.enemy_reinforcement = self.battle.later_reinforcement["team"][self.enemy_team]

        self.aggressive = 0  # determine how aggressive the AI is
        self.defensive = 0
        self.clever = 0  # determine how precise AI act
        self.swift = 0  # determine how often and many actions AI can take
        self.commander_attack_melee_prefer = 1
        self.commander_defence_melee_prefer = 1
        self.commander_cavalry_melee_prefer = 1
        self.commander_cavalry_range_prefer = 1
        self.commander_range_prefer = 1
        self.commander_siege_prefer = 1
        self.commander_air_prefer = 1
        self.commander_leader_prefer = 1
        self.rush_plan_score = 0
        if self.commander:
            commander_stat = self.character_list[self.commander.char_id]
            self.aggressive = commander_stat["Commander AI Aggressiveness"]
            self.defensive = 10 - self.aggressive
            self.clever = commander_stat["Commander AI Cleverness"]
            self.swift = commander_stat["Commander AI Swiftness"]
            self.commander_attack_melee_prefer = commander_stat["Commander Melee Like"] * self.aggressive
            self.commander_defence_melee_prefer = commander_stat["Commander Melee Like"] * self.defensive
            self.commander_cavalry_melee_prefer = commander_stat["Commander Cavalry Like"] * self.aggressive
            self.commander_cavalry_range_prefer = commander_stat["Commander Cavalry Like"] * self.defensive
            self.commander_range_prefer = commander_stat["Commander Range Like"] * self.aggressive
            self.commander_siege_prefer = commander_stat["Commander Range Like"] * self.defensive
            self.commander_air_prefer = commander_stat["Commander Air Like"]
            self.commander_leader_prefer = commander_stat["Commander Leader Like"]

            for strategy in self.team_stat["strategy"]:
                stat = self.strategy_list[strategy]
                if stat["Power"] or stat["Enemy Status"]:  # attack/summon strategy to use at enemy
                    self.own_strategy_type["enemy"].add(strategy)
                if stat["Summon"]:
                    self.own_strategy_type["summon"].add(strategy)
                if stat["Status"]:
                    if ("Cure" in stat["Status"] or "Clarity" in stat["Status"]) and len(stat["Status"]) == 1:
                        # keep cure/clarity only strategy completely separate from buff strategy
                        if "Cure" in stat["Status"]:
                            self.own_strategy_type["cure"].add(strategy)
                            self.has_cure_strategy = True
                        if "Clarity" in stat["Status"]:
                            self.own_strategy_type["clarity"].add(strategy)
                            self.has_clarity_strategy = True
                    else:
                        self.own_strategy_type["ally"].add(strategy)

                if "weather" in stat["Property"]:
                    self.own_strategy_type["weather"].add(strategy)

        self.enemy_strategy = self.battle.team_stat[self.enemy_team]["strategy"]
        self.enemy_strategy_type = {"ally": set(), "enemy": set()}
        for strategy in self.enemy_strategy:
            stat = self.strategy_list[strategy]
            if stat["Power"] or stat["Enemy Status"]:
                self.enemy_strategy_type["enemy"].add(strategy)
            if stat["Status"]:
                self.enemy_strategy_type["ally"].add(strategy)

        self.act_timer = 0
        self.act_time = 0
        self.think_time = 0
        self.think_timer = 0
        self.current_info = {}
        self.recommended_troop_call_plan_score = {}

        self.gather_info = MethodType(clever_gather_info_level[self.clever], self)

        if self.clever:
            self.lower_think_time = 5 / self.clever
            self.higher_think_time = 10 / self.clever
            self.think_time = uniform(self.lower_think_time, self.higher_think_time)
        if self.swift:  # 0 swiftness will do nothing
            self.lower_act_time = 10 / self.swift
            self.higher_act_time = 50 / self.swift
            self.act_time = uniform(self.lower_act_time, self.higher_act_time)
        self.start_pos = self.battle.team_stat[self.team]["start_pos"]

    def update(self, dt):
        if self.commander.alive:
            self.think_timer += dt
            if self.think_timer >= self.think_time:
                self.think_timer -= self.think_time
                self.current_info = self.gather_info()
                self.think_time = uniform(self.lower_think_time, self.higher_think_time)
                self.conduct_troop_call()

            self.act_timer += dt
            if self.act_timer >= self.act_time:
                self.act_timer -= self.act_time
                self.act_time = uniform(self.lower_act_time, self.higher_act_time)
                self.conduct_commander()

    def kill(self):
        # does nothing when kill via end battle
        pass

    def clear(self):
        clean_object(self)
