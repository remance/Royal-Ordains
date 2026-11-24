from pygame import sprite

from engine.aibattlecommander.aibattlecommander import AIBattleCommander
from engine.autobattle.activate_strategy import activate_strategy
from engine.autobattle.call_in_air_group import call_in_air_group
from engine.autobattle.check_reinforcement import check_reinforcement
from engine.autobattle.add_auto_character import add_auto_character
from engine.battle.battle import team_list
from engine.battle.call_reinforcement_to_battle import call_reinforcement_to_battle
from engine.battle.create_air_group import create_air_group
from engine.constants import (Round_To_Battle_Time, Collision_Grid_X_Per_Battle_Scene,
                              Collision_Grid_Y_Per_Battle_Scene,
                              Battle_Supply_Transfer_Rate, Team_Start_x_Distance, Default_Screen_Width,
                              Default_Battle_Ground_Pos)
from engine.utils.common import clean_object
from engine.weather.weather import Weather


class AutoBattle:
    activate_strategy = activate_strategy
    add_auto_character = add_auto_character
    call_in_air_group = call_in_air_group
    call_reinforcement_to_battle = call_reinforcement_to_battle
    check_reinforcement = check_reinforcement
    create_air_group = create_air_group
    grand = None

    def __init__(self, battle_state):
        grand = self.grand
        self.character_portraits = grand.character_portraits
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
        self.player_team = None
        self.player_selected_strategy = None
        self.true_dt = 0
        self.battle_time = 0
        self.team_commander = {1: None, 2: None}
        self.team_deployed = {1: 0, 2: 0}
        self.team_loss = {team: 0 for team in team_list}
        self.all_team_ally = {index: sprite.Group() for index in team_list}
        self.all_team_enemy = {index: sprite.Group() for index in team_list}  # for victory check

        self.all_team_ground_enemy_collision_grids = {team: [[]] for team in team_list}
        self.all_team_air_enemy_collision_grids = {team: [[]] for team in team_list}

        stage_len = battle_state["stage_size"]

        self.team1_call_leader_cooldown_reinforcement = {}
        self.team1_call_troop_cooldown_reinforcement = {}

        self.team2_call_leader_cooldown_reinforcement = {}
        self.team2_call_troop_cooldown_reinforcement = {}

        self.current_weather = Weather(self, 1, 1, 0)

        self.base_stage_end = stage_len * Default_Screen_Width
        self.last_grid = 0  # auto battle use only 1 grid
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

        self.battle_ai_commander1.__init__(self, 1, can_retreat=self.battle_ai_commander1.can_retreat)
        self.battle_ai_commander2.__init__(self, 2, can_retreat=self.battle_ai_commander1.can_retreat)

    def change_round(self):
        all_active_unit = []

        self.team1_call_leader_cooldown_reinforcement = {key: value - Round_To_Battle_Time for key, value in
                                                         self.team1_call_leader_cooldown_reinforcement.items() if
                                                         value > Round_To_Battle_Time}
        self.team1_call_troop_cooldown_reinforcement = {key: value - Round_To_Battle_Time for key, value in
                                                        self.team1_call_troop_cooldown_reinforcement.items() if
                                                        value > Round_To_Battle_Time}
        self.team2_call_leader_cooldown_reinforcement = {key: value - Round_To_Battle_Time for key, value in
                                                         self.team2_call_leader_cooldown_reinforcement.items() if
                                                         value > Round_To_Battle_Time}
        self.team2_call_troop_cooldown_reinforcement = {key: value - Round_To_Battle_Time for key, value in
                                                        self.team2_call_troop_cooldown_reinforcement.items() if
                                                        value > Round_To_Battle_Time}

        for team in (0, 1, 2):
            team_state = self.team_state[team]
            team_state["strategy_cooldown"] = {
                key: [cooldown - Round_To_Battle_Time if cooldown > Round_To_Battle_Time else 0 for cooldown in value]
                for key, value in team_state["strategy_cooldown"].items()}
            team_commander = team_state["commander_character"]

            if team_commander and team_commander.alive and team_state["strategy_resource"] < 200:
                team_state["strategy_resource"] += Round_To_Battle_Time * team_state["strategy_regen"]
                if team_state["strategy_resource"] > 200:
                    team_state["strategy_resource"] = 200

            if team_state["supply_reserve"]:
                if team_state["supply_reserve"] > 0:
                    supply_transfer = team_state["supply_reserve"] * Battle_Supply_Transfer_Rate * Round_To_Battle_Time
                else:
                    supply_transfer = team_state["supply_reserve"]
                team_state["supply_resource"] += supply_transfer
                team_state["supply_reserve"] -= supply_transfer

            # commander AI act first

        # call in troop
        self.battle_ai_commander1.update(Round_To_Battle_Time)
        self.battle_ai_commander2.update(Round_To_Battle_Time)

        self.check_reinforcement()

        for team in (0, 1, 2):  # update unit
            # get all active units for acting
            team_state = self.team_state[team]
            all_active_unit += team_state["unit"]

            # commander act first
            if team:  # skip team 0 since it should not have commander
                commander_character = team_state["commander_character"]
                commander_character.status_update(specific_dt=Round_To_Battle_Time)
                commander_character.ai_logic()

        # for auto battle unit take action queue based on their speed stat
        all_active_unit.sort(key=lambda x: x.speed, reverse=True)
        for unit in all_active_unit:
            # update status first
            unit.status_update(specific_dt=Round_To_Battle_Time)
            # move or take action
            unit.ai_logic()

        self.battle_time += Round_To_Battle_Time

        if not self.all_team_enemy[1] or not self.all_team_enemy[2]:  # battle end when one team has no unit left
            self.grand.end_battle(self)

    def end_battle(self):
        for army in self.battle_state["armies"]:
            pass
        clean_object(self)
