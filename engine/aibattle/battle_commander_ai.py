from multiprocessing import Process
from time import sleep
from types import MethodType
from random import uniform
from engine.aibattle.gather_info import clever_gather_info_level
from engine.aibattle.analyse_info import analyse_info
from engine.aibattle.conduct_plan import conduct_plan
from engine.utils.common import clean_object

# TODO add condition for ai command retreat or go to specific pos when added
# how to move attack strategy air unit retreat, strategy to change weather, protect commander, consider enemy strategy


class BattleCommanderAI:
    """Battle commander AI act depend on their personality stat where aggressiveness determine their combat tactic,
    cleverness determine what and how they think on gathered information,
    swiftness determine how fast they can act on the given information
    """
    battle = None

    analyse_info = analyse_info
    conduct_plan = conduct_plan

    def __init__(self, team, can_retreat=True):
        self.team = team
        self.enemy_team = 1
        if self.team == 1:
            self.enemy_team = 2
        self.can_retreat = can_retreat
        self.commander = self.battle.team_commander[team]
        self.enemy_commander = self.battle.team_commander[self.enemy_team]
        self.team_stat = self.battle.team_stat[team]
        self.enemy_team_stat = self.battle.team_stat[self.enemy_team]
        self.strategy_list = self.battle.strategy_list
        self.last_grid = self.battle.last_grid
        self.air_group = self.team_stat["air_group"]
        self.own_strategy = self.team_stat["strategy"]
        self.own_strategy_type = {"attack": set(), "buff": set(), "debuff": set(),
                                  "weather": set(), "ally": set(), "enemy": set()}
        for strategy in self.team_stat["strategy"]:
            stat = self.strategy_list[strategy]
            if stat["Power"] or stat["Summon"]:  # attack/summon strategy to use at enemy
                self.own_strategy_type["attack"].add(strategy)
                self.own_strategy_type["enemy"].add(strategy)
            if stat["Status"]:
                self.own_strategy_type["buff"].add(strategy)
                if stat["Enemy Status"]:
                    self.own_strategy_type["enemy"].add(strategy)
            if stat["Enemy Status"]:
                self.own_strategy_type["debuff"].add(strategy)
                self.own_strategy_type["enemy"].add(strategy)
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

        self.reinforcement = self.battle.later_reinforcement["team"][team]
        self.enemy_reinforcement = self.battle.later_reinforcement["team"][self.enemy_team]

        self.aggressive = 0  # determine how aggressive the AI is
        self.defensive = 0
        self.clever = 0  # determine how precise AI act
        self.swift = 0  # determine how often and many actions AI can take
        if self.commander:
            commander_stat = self.battle.character_data.character_list[self.commander.char_id]
            self.aggressive = commander_stat["Commander AI Aggressiveness"]
            self.defensive = 10 - self.aggressive
            self.clever = commander_stat["Commander AI Cleverness"]
            self.swift = commander_stat["Commander AI Swiftness"]

        self.priority_modifier = {"attack": self.aggressive, "skirmish": self.aggressive / 2,
                                  "defend": self.defensive, "flank": self.aggressive / 4,
                                  "commander_danger": self.defensive, "strategy at ally": self.clever + self.defensive,
                                  "strategy at ground enemy": self.clever + self.aggressive,
                                  "strategy at air enemy": self.clever + self.aggressive,
                                  "retreat": self.defensive / 2}
        self.act_timer = 0
        self.act_cooldown_timer = 0
        self.think_time = 0
        self.think_timer = 0
        self.current_info = {}
        self.recommended_plan_score = {}

        self.gather_info = MethodType(clever_gather_info_level[self.clever], self)

        if self.clever:
            self.lower_think_time = 5 / self.swift
            self.higher_think_time = 10 / self.swift
            self.think_time = uniform(self.lower_think_time, self.higher_think_time)
        if self.swift:  # 0 swiftness will do nothing
            self.lower_act_time = 5 / self.swift
            self.higher_act_time = 10 / self.swift
            self.act_time = uniform(self.lower_act_time, self.higher_act_time)
        self.start_pos = self.battle.team_stat[self.team]["start_pos"]

    def update(self, dt):
        self.think_timer += dt
        if self.think_timer >= self.think_time:
            self.think_timer -= self.think_time
            self.current_info = self.gather_info()
            self.recommended_plan_score = self.analyse_info()
            self.think_time = uniform(self.lower_think_time, self.higher_think_time)

        self.act_timer += dt
        if self.act_timer >= self.act_timer:
            self.act_timer -= self.act_timer
            self.conduct_plan()

    def kill(self):
        pass

    def clear(self):
        clean_object(self)


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
