from multiprocessing import Process
from time import sleep
from types import MethodType
from random import uniform
from engine.ai.gather_info import clever_gather_info_level

# TODO add condition for ai command retreat or go to specific pos when added
# how to move attack strategy air unit retreat, stratety to change weather, protect commander, consider enemy strategy


class BattleCommanderAI:
    """Battle commander AI act depend on their personality stat where aggressiveness determine their combat tactic,
    cleverness determine what and how they think on gathered information,
    swiftness determine how fast they can act on the given information
    """
    battle = None

    def __init__(self, team, aggressive, clever, swift, can_retreat=True):
        self.team = team
        self.enemy_team = 1
        if self.team == 1:
            self.enemy_team = 2
        self.can_retreat = can_retreat
        self.commander = self.battle.team_commander[team]
        self.team_stat = self.battle.team_stat[team]
        self.strategy_list = self.battle.strategy_list
        self.air_group = self.team_stat["air_group"]
        self.own_strategy = self.team_stat["strategy"]
        self.own_strategy_type = {"attack": [], "buff": [], "debuff": [], "buff and debuff": [], "weather": []}
        for strategy in self.team_stat["strategy"]:
            stat = self.strategy_list[strategy]
            if stat["Power"]:
                self.own_strategy_type["attack"].append(strategy)
            if stat["Status"]:
                self.own_strategy_type["buff"].append(strategy)
                if stat["Enemy Status"]:
                    self.own_strategy_type["buff and debuff"].append(strategy)
            if stat["Enemy Status"]:
                self.own_strategy_type["debuff"].append(strategy)
            if "weather" in stat["Property"]:
                self.own_strategy_type["weather"].append(strategy)

        self.enemy_strategy = self.battle.team_stat[self.enemy_team]["strategy"]
        self.enemy_strategy_type = {"attack": [], "buff": [], "debuff": [], "buff and debuff": [], "weather": []}
        for strategy in self.enemy_strategy:
            stat = self.strategy_list[strategy]
            if stat["Power"]:
                self.enemy_strategy_type["attack"].append(strategy)
            if stat["Status"]:
                self.enemy_strategy_type["buff"].append(strategy)
                if stat["Enemy Status"]:
                    self.enemy_strategy_type["buff and debuff"].append(strategy)
            if stat["Enemy Status"]:
                self.enemy_strategy_type["debuff"].append(strategy)

        self.reinforcement = self.battle.later_reinforcement["team"][team]
        self.enemy_reinforcement = self.battle.later_reinforcement["team"][self.enemy_team]
        self.aggressive = aggressive  # determine how aggressive the AI is
        self.clever = clever  # determine how precise AI act
        self.swift = swift  # determine how often and many actions AI can take
        self.priority_modifier = {"attack": self.aggressive, "skirmish": self.aggressive / 2,
                                  "defend": 10 - self.aggressive, "move": 0,
                                  "commander_danger": 10 - self.aggressive, "command_combat": self.aggressive,
                                  "retreat": (10 - self.aggressive) / 2}
        self.act_timer = 0
        self.act_cooldown_timer = 0
        self.think_time = 0
        self.think_timer = 0
        self.current_info = {}

        self.gather_info = MethodType(clever_gather_info_level[self.clever], self)
        if self.clever:
            self.lower_think_time = 5 / self.swift
            self.higher_think_time = 10 / self.swift
            self.think_time = uniform(self.lower_think_time, self.higher_think_time)
        if self.swift:  # 0 swiftness will do nothing
            self.lower_act_time = 5 / self.swift
            self.higher_act_time = 10 / self.swift
            self.act_time = uniform(self.lower_act_time, self.higher_act_time)
        self.start_point = self.battle.team_stat[self.team]["start_pos"]

    def update(self, dt):
        self.think_timer += dt
        if self.think_timer >= self.think_time:
            self.think_timer -= self.think_time
            self.current_info = self.gather_info()
            self.think_time = uniform(self.lower_think_time, self.higher_think_time)
            action_can_do = self.clever

        self.act_timer += dt
        if self.act_timer >= self.act_timer:
            self.act_timer -= self.act_timer


class EnemyCommanderAIHelp:
    def __init__(self):
        self.input_list = []

        Process(target=self._loop, daemon=True).start()

    def analyse_battle(self):
        pass

    def _loop(self):
        while True:
            # Check for commands
            if self.input_list:
                unit = self.input_list[0].ai_logic()
                self.input_list = self.input_list[1:]
