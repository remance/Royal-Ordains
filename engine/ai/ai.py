from multiprocessing import Process
from time import sleep

# TODO add condition for ai command retreat or go to specific pos when added
# how to move attack strategy air unit retreat


class EnemyCommanderAI:
    battle = None

    def __init__(self, team):
        self.general_list = self.battle.all_team_general[team]
        self.commander = self.battle.team_commander[team]
        self.air_group = self.battle.team_stat[team]["air_group"]
        self.strategy = self.battle.team_stat[team]["strategy"]

    def order(self):
        for general in self.general_list:
            pass


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
