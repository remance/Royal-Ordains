from types import MethodType

from pygame import Vector2
from pygame.sprite import Sprite

from engine.autounitgroup.ai_combat import auto_ai_combat_dict
from engine.autounitgroup.ai_logic import auto_ai_logic
from engine.autounitgroup.ai_move import auto_move_to_target_order, auto_ai_move_dict
from engine.autounitgroup.ai_retreat import auto_ai_retreat_dict
from engine.character.ai_prepare import get_near_enemy
from engine.autounitgroup.ai_prepare import auto_ai_prepare_dict
from engine.character.character import BaseCharacter
from engine.character.enter_stage import enter_stage, battle_character_enter_stage
from engine.utils.common import empty_method


class AutoUnitGroup(Sprite, BaseCharacter):
    ai_logic = auto_ai_logic
    enter_stage = enter_stage
    pick_animation = empty_method
    move_to_target_order = auto_move_to_target_order
    battle_character_enter_stage = battle_character_enter_stage
    get_near_enemy = get_near_enemy

    def __init__(self, battle, game_id: int, character_data: dict, is_commander: bool = False, is_summon: bool = False,
                 no_combat=False, load_current_state: (None, dict) = None):
        """This represent a group or swarm of one unit call in battle to reduce the workload of individual calculation,
        for example entire group receive status rather than individual and perform action together per round"""
        Sprite.__init__(self)
        BaseCharacter.__init__(self, game_id, character_data, is_commander, is_summon)
        self.battle = battle
        if not is_summon:
            self.group_character = [{"health": self.health, "group_pos": index * 10} for index, unit in
                                    enumerate(range(character_data["Arrive Per Call"]))]
        else:
            self.group_character = [{"health": self.health, "group_pos": 0}]
        self.animation_load_index = self.battle.animation_load_index["character_load_index"][self.char_id]
        self.sub_characters = []

        self.battle = battle

        self.team = character_data["Team"]
        self.enemy_team = 1
        if self.team == 1:
            self.enemy_team = 2

        self.base_pos = Vector2(character_data["base_pos"])
        self.start_pos = self.battle.team_state[self.team]["start_pos"]
        self.retreat_pos = self.start_pos * 2
        if not self.start_pos:
            self.retreat_pos = -10000

        self.base_stage_end = self.battle.base_stage_end
        self.direction = "right"
        if self.base_pos[0] > self.base_stage_end / 2:
            self.direction = "left"

        self.active = False
        self.nearest_enemy = None
        self.nearest_enemy_distance = None
        self.nearest_enemy_pos = None
        self.furthest_enemy = None
        self.furthest_enemy_distance = None
        self.furthest_enemy_pos = None
        self.nearest_ally = None
        self.nearest_ally_pos = None
        self.nearest_ally_distance = None

        if self.ai_behaviour in auto_ai_prepare_dict:
            self.ai_prepare = MethodType(auto_ai_prepare_dict[self.ai_behaviour], self)
        else:
            self.ai_prepare = MethodType(auto_ai_prepare_dict["default"], self)

        self.all_team_enemy = self.battle.all_team_enemy
        self.all_ground_enemy = self.battle.all_team_ground_enemy_collision_grids[self.team][-1]
        self.all_air_enemy = self.battle.all_team_air_enemy_collision_grids[self.team][-1]
        self.ally_list = self.battle.all_team_ally[self.team]
        self.near_ally = []
        self.near_enemy = []

        self.movesets = character_data["Move"]
        self.die_moveset = character_data["Die Move"]
        self.ai_range_modifier = 1

        self.ai_min_attack_range = character_data["ai_min_attack_range"] * self.ai_range_modifier
        self.ai_max_attack_range = character_data["ai_max_attack_range"] * self.ai_range_modifier
        self.max_enemy_range_check = character_data["max_enemy_range_check"] * self.ai_range_modifier
        self.ai_skirmish_range = character_data["ai_skirmish_range"] * self.ai_range_modifier
        self.min_resource_move = character_data["min_resource_move"]
        self.ai_min_effect_range = character_data["ai_min_effect_range"]
        self.ai_enemy_max_effect_range = character_data["ai_enemy_max_effect_range"]
        self.ai_ally_max_effect_range = character_data["ai_ally_max_effect_range"]

        self.ai_move = MethodType(auto_ai_move_dict["default"], self)
        if self.is_commander:  # commander use behaviour that move based on player/ ai commander order
            self.ai_move = MethodType(auto_ai_move_dict["commander"], self)
        elif self.ai_behaviour in auto_ai_move_dict:
            self.ai_move = MethodType(auto_ai_move_dict[self.ai_behaviour], self)

        self.ai_retreat = MethodType(auto_ai_retreat_dict["default"], self)
        if self.ai_behaviour in auto_ai_retreat_dict:
            self.ai_retreat = MethodType(auto_ai_retreat_dict[self.ai_behaviour], self)

        if self.movesets:
            if self.is_commander:
                self.ai_combat = MethodType(auto_ai_combat_dict["leader"], self)
            elif self.ai_behaviour in auto_ai_combat_dict:
                self.ai_combat = MethodType(auto_ai_combat_dict[self.ai_behaviour], self)

        if load_current_state:  # assign value from loaded state to variable
            self.health = load_current_state["health"]
            self.resource = load_current_state["resource"]
            self.status_duration = load_current_state["status_duration"]
            self.moveset_cooldown = load_current_state["moveset_cooldown"]
            self.commander_order = load_current_state["commander_order"]
            self.base_pos = Vector2(load_current_state["base_pos"])
            self.active = load_current_state["active"]
            self.status_update(specific_dt=0)

        self.total_power_score = 0
        self.followers_len_check = [0, 0]
        self.max_followers_len_check = 0
        max_ai_commander_range = self.ai_max_attack_range
        for strategy in self.battle.team_state[self.team]["strategy_cooldown"]:
            strategy_stat = self.battle.strategy_list[strategy]
            if strategy_stat["Activate Range"] > max_ai_commander_range:
                max_ai_commander_range = strategy_stat["Activate Range"]
        self.optimal_ai_commander_range = max_ai_commander_range * 0.75

        if not no_combat:
            self.battle_character_enter_stage()
        else:
            self.enter_stage()

        if character_data["ID"] in self.battle.character_portraits:
            self.icon = self.battle.character_portraits[character_data["ID"]]["small"]
            self.command_icon = self.battle.character_portraits[character_data["ID"]]["mini"]["right"]
