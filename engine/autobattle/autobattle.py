from pygame import sprite

from engine.aibattlecommander.aibattlecommander import AIBattleCommander
from engine.autobattle.activate_strategy import activate_strategy
from engine.autobattle.call_in_air_group import call_in_air_group
from engine.battle.battle import team_list
from engine.battle.call_reinforcement_to_battle import call_reinforcement_to_battle
from engine.character.character import GrandAutoCharacter, CommanderGrandAutoCharacter
from engine.constants import (Phase_To_Round, Phase_To_Battle_Time, Collision_Grid_X_Per_Battle_Scene,
                              Collision_Grid_Y_Per_Battle_Scene,
                              Battle_Supply_Transfer_Rate, Team_Start_x_Distance, Default_Screen_Width,
                              Default_Battle_Ground_Pos)
from engine.utils.common import clean_object
from engine.weather.weather import Weather

Tick_to_Second = Phase_To_Battle_Time / Phase_To_Round


class AutoBattle:
    activate_strategy = activate_strategy
    call_in_air_group = call_in_air_group
    call_reinforcement_to_battle = call_reinforcement_to_battle
    grand = None

    def __init__(self, battle_state):
        grand = self.grand
        self.screen_rect = grand.screen_rect
        self.screen_width = grand.screen_width
        self.screen_height = grand.screen_height
        self.weather_data = grand.weather_data
        self.sprite_data = grand.sprite_data
        self.weather_matters = ()  # empty since not really used in autobattle, just for weather init
        self.weather_ambient_channel = None

        self.animation_load_index = grand.sprite_data.animation_load_index
        self.stat_data = grand.stat_data
        self.character_list = self.stat_data.character_list
        self.strategy_list = self.stat_data.strategy_list
        self.can_cure_status_list = self.stat_data.can_cure_status_list
        self.can_clarity_status_list = self.stat_data.can_clarity_status_list
        self.battle_state = battle_state
        self.team_state = battle_state["team"]
        self.team_commander = {1: None, 2: None}
        self.all_team_ally = {index: sprite.Group() for index in team_list}
        self.all_team_enemy = {index: sprite.Group() for index in team_list}  # for victory check

        self.all_team_ground_enemy_collision_grids = {index: () for index in team_list}
        self.all_team_air_enemy_collision_grids = {index: () for index in team_list}

        stage_len = battle_state["stage_size"]
        self.all_team_ground_enemy_collision_grids = {index: [[
            sprite.Group() for _ in range(int(stage_len * Collision_Grid_X_Per_Battle_Scene))] for
            _ in range(Collision_Grid_Y_Per_Battle_Scene + 1)] for index in team_list}
        self.all_team_air_enemy_collision_grids = {index: [[
            sprite.Group() for _ in range(int(stage_len * Collision_Grid_X_Per_Battle_Scene))] for
            _ in range(Collision_Grid_Y_Per_Battle_Scene + 1)] for index in team_list}

        self.team1_call_leader_cooldown_reinforcement = {}
        self.team1_call_troop_cooldown_reinforcement = {}

        self.team2_call_leader_cooldown_reinforcement = {}
        self.team2_call_troop_cooldown_reinforcement = {}

        self.current_weather = Weather(self, 1, 1, 0)

        self.base_stage_end = stage_len * Default_Screen_Width
        self.last_grid = int(stage_len * Collision_Grid_X_Per_Battle_Scene)
        self.last_game_id = 0

        self.battle_ai_commander1 = AIBattleCommander(self, 1, can_retreat=True)
        self.battle_ai_commander2 = AIBattleCommander(self, 2, can_retreat=True)

        # add commander as character for both team
        for team in (1, 2):
            data = {} | self.character_list[self.team_state[team]["main_army"].commander_id]
            if self.team_state[team]["start_pos"] == 0:
                start_x = Team_Start_x_Distance
            else:
                start_x = self.base_stage_end - Team_Start_x_Distance
            data["Team"] = team
            data["ID"] = self.team_state[team]["main_army"].commander_id
            data["base_pos"] = (start_x, Default_Battle_Ground_Pos)

            self.add_auto_character(team, data, is_commander=True)

    def change_phase(self):
        for tick in range(6):
            all_active_unit = []

            self.team1_call_leader_cooldown_reinforcement = {key: value - Tick_to_Second for key, value in
                                                             self.team1_call_leader_cooldown_reinforcement.items() if
                                                             value > Tick_to_Second}
            self.team1_call_troop_cooldown_reinforcement = {key: value - Tick_to_Second for key, value in
                                                            self.team1_call_troop_cooldown_reinforcement.items() if
                                                            value > Tick_to_Second}
            self.team2_call_leader_cooldown_reinforcement = {key: value - Tick_to_Second for key, value in
                                                             self.team2_call_leader_cooldown_reinforcement.items() if
                                                             value > Tick_to_Second}
            self.team2_call_troop_cooldown_reinforcement = {key: value - Tick_to_Second for key, value in
                                                            self.team2_call_troop_cooldown_reinforcement.items() if
                                                            value > Tick_to_Second}

            for team in (0, 1, 2):
                team_state = self.team_state[team]
                team_state["strategy_cooldown"] = {
                    key: [cooldown - Tick_to_Second if cooldown > Tick_to_Second else 0 for cooldown in value]
                    for key, value in team_state["strategy_cooldown"].items()}
                team_commander = team_state["commander_character"]

                if team_commander and team_commander.alive and team_state["strategy_resource"] < 200:
                    team_state["strategy_resource"] += Tick_to_Second * team_state["strategy_regen"]
                    if team_state["strategy_resource"] > 200:
                        team_state["strategy_resource"] = 200

                if team_state["supply_reserve"]:
                    if team_state["supply_reserve"] > 0:
                        supply_transfer = team_state["supply_reserve"] * Battle_Supply_Transfer_Rate * Tick_to_Second
                    else:
                        supply_transfer = team_state["supply_reserve"]
                    team_state["supply_resource"] += supply_transfer
                    team_state["supply_reserve"] -= supply_transfer

                # commander AI act first

            # call in troop
            self.battle_ai_commander1.conduct_troop_call()
            self.battle_ai_commander2.conduct_troop_call()

            for team in (0, 1, 2):  # update unit
                # get all active units for acting
                team_state = self.team_state[team]
                all_active_unit += team_state["unit"] + team_state["air_unit"]

                # commander act first
                if team:  # skip team 0 since it should not have commander
                    commander_character = team_state["commander_character"]
                    commander_character.status_update(specific_dt=Tick_to_Second)
                    commander_character.ai_logic()

            # for auto battle unit take action queue based on their speed stat
            all_active_unit.sort(key=lambda x: x.speed, reverse=True)
            for unit in all_active_unit:
                # update status first
                unit.status_update(specific_dt=Tick_to_Second)
                # move or take action
                unit.ai_logic()

            if not self.all_team_enemy[1] or not self.all_team_enemy[2]:  # battle end when one team has no unit left
                self.grand.end_battle(self)

    def add_auto_character(self, team, character_data, is_commander: bool = False, is_summon: bool = False):
        if is_commander:
            character = CommanderGrandAutoCharacter(self, self.last_game_id, character_data)
            self.team_state[team]["commander_character"] = character
            if team == 1:
                self.battle_ai_commander1.__init__(self, 1, can_retreat=self.battle_ai_commander1.can_retreat)
            elif team == 2:
                self.battle_ai_commander2.__init__(self, 2, can_retreat=self.battle_ai_commander1.can_retreat)
        else:
            character = GrandAutoCharacter(self, self.last_game_id, character_data,
                                           is_commander=is_commander, is_summon=is_summon, )
            self.team_state[team]["unit"].append(character)
        self.all_team_enemy[team].add(character)
        self.last_game_id += 1

    def end_battle(self):
        for army in self.battle_state["armies"]:
            pass
        clean_object(self)
