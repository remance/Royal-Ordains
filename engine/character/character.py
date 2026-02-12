from __future__ import annotations

from copy import deepcopy
from random import uniform
from types import MethodType

from pygame import sprite, Vector2, Surface
from pygame.mask import from_surface

from engine.character.ai_combat import ai_combat_dict
from engine.character.ai_combat import check_ai_condition
from engine.character.ai_logic import ai_logic
from engine.character.ai_move import ai_move_dict
from engine.character.ai_prepare import (get_near_enemy, ai_prepare, troop_ai_prepare, sub_character_ai_prepare,
                                         interceptor_ai_prepare, bomber_ai_prepare, fighter_ai_prepare)
from engine.character.ai_retreat import ai_retreat_dict
from engine.character.ai_speak import ai_speak
from engine.character.apply_status import apply_status
from engine.character.cal_loss import cal_loss
from engine.character.character_event_process import character_event_process
from engine.character.check_draw import check_draw
from engine.character.die import commander_die, die, air_die
from engine.character.enter_stage import (enter_stage, battle_character_enter_stage, battle_air_character_enter_stage,
                                          delayed_enter_stage, showcase_enter_stage)
from engine.character.erase import erase
from engine.character.finish_animation import finish_animation
from engine.character.get_damage import get_damage
from engine.character.health_resource_logic import health_resource_logic, air_health_resource_logic
from engine.character.issue_commander_order import issue_commander_order
from engine.character.move_logic import move_logic, sub_move_logic, air_move_logic
from engine.character.pick_animation import pick_animation
from engine.character.pick_cutscene_animation import pick_cutscene_animation
from engine.character.play_animation import (next_animation_frame, showcase_next_animation_frame, play_battle_animation,
                                             play_cutscene_animation, play_showcase_animation)
from engine.character.reset_commander_variables import reset_commander_variables
from engine.character.reset_sprite import reset_sprite, battle_reset_sprite
from engine.character.rotate_logic import rotate_logic
from engine.character.status_update import status_update
from engine.constants import *
from engine.effect.cal_damage import cal_damage
from engine.effect.hit_collide_check import hit_collide_check
from engine.effect.hit_register import hit_register
from engine.uibattle.uibattle import DamageNumber
from engine.utils.common import clean_object, empty_method
from engine.utils.rotation import set_rotate

infinity = float("inf")

"""Command action dict Guide
Key:
name = action name that will be used to find animation, name with "Action" will find attack action of weapon for animation name
move attack = indicate using move attack animation
melee attack = indicate animation performing melee attack for spawning damage sprite in frame that can spawn it
range attack = indicate animation performing range attack for spawning bullet sprite when finish
repeat = keep repeating this animation until canceled, should only be used for action that can be controlled like walk
movable = can move during action
controllable = can perform controllable action during action like walk or attack
next action = action that will be performed after the current one finish
uninterruptible = action can not be interrupt with interrupt_animation variable
walk, run = indicate movement type for easy checking, walk and run also use for move_speed
stand, couch, ai = indicate position change after animation finish
land (stand) = indicate position change before animation start
weapon = weapon index of action for easy checking
no combat ai = prevent AI from running combat attack AI method
pos = specific target pos
require input = animation action require input first and will keep holding first frame until this condition is removed 
                or interrupt
x_momentum or y_momentum = assign custom momentum value instead
drop speed = assign value of dropping speed for air animation, higher value mean faster drop
"""


class Character(sprite.Sprite):
    battle = None
    character_data = None
    character_list = None
    effect_list = None
    sound_effect_pool = None

    image = Surface((0, 0))  # start with empty surface
    mask = from_surface(image)
    rect = image.get_rect(topleft=(0, 0))
    collision_grid_width = 0

    ai_speak = ai_speak
    ai_logic = ai_logic
    ai_prepare = ai_prepare
    apply_status = apply_status
    cal_loss = cal_loss
    character_event_process = character_event_process
    check_ai_condition = check_ai_condition
    check_draw = check_draw
    delayed_enter_stage = delayed_enter_stage
    die = die
    enter_stage = enter_stage
    erase = erase
    get_damage = get_damage
    get_near_enemy = get_near_enemy
    finish_animation = finish_animation
    health_resource_logic = health_resource_logic
    issue_commander_order = issue_commander_order
    reset_commander_variables = reset_commander_variables
    move_logic = move_logic
    pick_animation = pick_animation
    pick_cutscene_animation = pick_cutscene_animation
    next_animation_frame = next_animation_frame
    play_battle_animation = play_battle_animation
    play_cutscene = play_cutscene_animation
    reset_sprite = reset_sprite
    rotate_logic = rotate_logic
    status_update = status_update

    cal_damage = cal_damage
    hit_collide_check = hit_collide_check
    hit_register = hit_register

    clean_object = clean_object
    set_rotate = set_rotate

    moveset_command_action = {"moveset": True}

    damaged_command_action = {"name": "Damaged", "damaged": True, "movable": True, "hold": True, "forced move": True}
    standup_command_action = {"name": "Standup"}
    knockdown_command_action = {"name": "Knockdown", "movable": True, "forced move": True,
                                "knockdown": True, "hold": True, "next action": standup_command_action}

    die_command_action = {"name": "Die", "uninterruptible": True,
                          "movable": True, "forced move": True, "hold": True, "die": True}

    spirit_command_action = {"name": "Spirit", "uninterruptible": True,
                             "movable": True, "forced move": True, "hold": True, "spirit": True}

    # static variable
    Base_Animation_Frame_Play_Time = Base_Animation_Frame_Play_Time
    Default_Air_Pos = Default_Air_Pos
    Default_Ground_Pos = Default_Ground_Pos
    Character_Gravity = Character_Gravity

    def __init__(self, game_id: int, stat: dict, additional_layer: (int, str) = 0, is_commander: bool = False) -> None:
        """
        Character object represent a single character in battle
        """
        sprite.Sprite.__init__(self, self.containers)
        # these two commands require replacement of x_momentum and direction, so can not be used as class variable
        self.walk_command_action = {"name": "Walk", "movable": True, "walk": True, "interruptable": True}
        self.run_command_action = {"name": "Run", "movable": True, "run": True, "interruptable": True}

        self.in_drawer = False
        self.blit_culling_check = self.battle.blit_culling_check
        self.screen_scale = self.battle.screen_scale
        self.battle_camera_drawer = self.battle.battle_camera_object_drawer
        self.all_team_enemy_check = self.battle.all_team_enemy_check

        self.char_id = stat["ID"]
        self.race = stat["Race"]
        self.game_id = game_id  # object ID for reference

        self.animation_pool = self.battle.character_animation_data[self.char_id]  # list of animation this character
        self.sprite_height = self.animation_pool["Default"][0]["right"]["sprite"].get_height() * 1.5
        self.sprite_width = self.animation_pool["Default"][0]["right"]["sprite"].get_width() * 0.5

        if additional_layer == "main":
            # use main character layer for sub character
            self._layer = self.main_character._layer - 1
        elif additional_layer == "showcase":
            self._layer = 1
        else:
            self._layer = int((10000 - self.sprite_height) + additional_layer)
        self.name = self.battle.localisation.grab_text(("character", stat["ID"], "Name"))
        self.cutscene_event = None
        self.speech = None
        self.is_commander = is_commander
        self.is_leader = stat["Is Leader"]

        self.current_action = {}  # action being performed
        self.command_action = {}  # next action to be performed
        self.current_animation = {}  # list of animation frames playing
        self.current_animation_frame = {}
        self.current_animation_direction = {}
        self.already_hit = []

        self.timer = 0
        self.frame_timer = 0
        self.hold_timer = 0
        self.hold_too_long_timer = 0
        self.show_frame = 0  # current animation frame
        self.max_show_frame = 0
        self.ai_timer = 0  # for whatever timer require for AI action
        self.ai_movement_timer = 0  # timer daley before can move again for character after performing attack
        self.not_show_delay = 0
        self.replace_idle_animation = None
        self.interrupt_animation = False
        self.animation_name = None

        self.invisible = False  # can not be seen nor detected, will not be drawn on camera
        self.no_move = False
        self.no_run = False
        self.invincible = False  # can not be hurt
        self.no_target = False  # can not be target
        self.broken = False  # broken and no longer fight, will only retreat
        self.alive = True
        self.reach_camera_event = {}

        # self.arrive_condition = stat["Arrive Condition"]

        self.y_momentum = 0
        self.x_momentum = 0
        self.run_speed = 12 * stat["Speed"]
        self.walk_speed = 5 * stat["Speed"]

        self.animation_frame_play_time = self.Base_Animation_Frame_Play_Time
        self.final_animation_frame_play_time = self.animation_frame_play_time

        self.commander_order = ()
        self.true_commander_order = ()
        self.base_pos = Vector2(stat["POS"][0],
                                stat["POS"][1])  # true position of character in battle
        if "direction" in stat:
            self.direction = stat["direction"]
        else:
            self.direction = "right"
            if self.base_pos[0] > self.battle.base_stage_end / 2:
                self.direction = "left"
        self.new_direction = self.direction
        self.target_pos = self.base_pos.copy()
        self.pos = Vector2((self.base_pos[0] * self.screen_scale[0],
                            self.base_pos[1] * self.screen_scale[1]))
        self.offset_pos = self.pos
        self.cutscene_target_pos = None
        self.grid_range = []

        self.update_sprite = False

        # apply property as variable
        char_property = {}
        if "Property" in stat:
            char_property = {key: value for key, value in stat["Property"].items()}
        if "Stage Property" in stat:
            char_property |= stat["Stage Property"]
        for stuff in char_property:  # set attribute from property
            if stuff == "target":
                if type(char_property["target"]) is int:  # target is AI
                    target = char_property["target"]
                else:  # target is player
                    target = char_property["target"][-1]

                for this_char in self.battle.all_battle_characters:
                    if target == this_char.game_id:  # find target char object
                        self.target = this_char
                        break
            elif stuff == "idle":  # replace idle animation
                self.replace_idle_animation = char_property["idle"]
            else:
                self.__setattr__(stuff, char_property[stuff])

        if self.no_run:  # cannot run, reset run variables to walk
            self.run_command_action = self.walk_command_action
            self.run_speed = self.walk_speed

        self.ai_behaviour = stat["AI Behaviour"]

        self.ai_move = MethodType(ai_move_dict["default"], self)
        if self.is_commander:  # leader use behaviour that move based on commander order
            self.ai_move = MethodType(ai_move_dict["leader"], self)
        elif self.ai_behaviour in ai_move_dict:
            self.ai_move = MethodType(ai_move_dict[self.ai_behaviour], self)

        self.ai_combat = MethodType(ai_combat_dict["default"], self)
        if self.is_commander:
            self.ai_combat = MethodType(ai_combat_dict["leader"], self)
        elif self.ai_behaviour in ai_combat_dict:
            self.ai_combat = MethodType(ai_combat_dict[self.ai_behaviour], self)

        self.ai_retreat = MethodType(ai_retreat_dict["default"], self)
        if self.ai_behaviour in ai_retreat_dict:
            self.ai_retreat = MethodType(ai_retreat_dict[self.ai_behaviour], self)

        self.base_ground_pos = self.Default_Ground_Pos
        if "Ground Y POS" in stat and stat["Ground Y POS"]:  # replace ground pos based on data in stage
            self.base_ground_pos = stat["Ground Y POS"]

        self.enter_stage()

    def update(self, dt: float):
        if self.alive:  # only run these when not dead
            self.ai_logic(dt)
            self.rotate_logic()  # Rotate Function

            # Animation and sprite system
            hold_check = False

            if "hold" in self.current_animation_frame["property"] and "hold" in self.current_action:
                # also hold if in freeze timer with frame that can hold
                hold_check = True

            done = self.play_battle_animation(dt, hold_check)
            self.finish_animation(done)

            self.move_logic(dt)  # Move function

            if self.update_sprite:
                self.reset_sprite()
                self.update_sprite = False

            self.check_draw(dt)

    @staticmethod
    def inactive_update(*args):
        pass

    def cutscene_update(self, dt: float):
        """Update for cutscene"""
        if self.cutscene_event:
            if self.cutscene_target_pos and self.cutscene_target_pos != self.base_pos:
                speed = 350
                if "speed" in self.cutscene_event["Property"]:
                    speed = self.cutscene_event["Property"]["speed"]
                # move to target pos based on data if any
                move = self.cutscene_target_pos - self.base_pos
                require_move_length = move.length()  # convert length
                move.normalize_ip()
                move *= speed * dt

                if move.length() <= require_move_length:  # move normally according to move speed
                    self.base_pos += move
                else:  # move length pass the base_target destination
                    self.base_pos = Vector2(self.cutscene_target_pos)  # just change base position to base target

                self.pos = Vector2((self.base_pos[0] * self.screen_scale[0],
                                    self.base_pos[1] * self.screen_scale[1]))

                self.update_sprite = True

        if self.alive or self.cutscene_event:  # only play animation for alive char or have event
            hold_check = False
            if "hold" in self.current_animation_frame["property"] and "hold" in self.current_action:
                hold_check = True
            done = self.play_cutscene_animation(dt, hold_check)
            if done or (self.cutscene_target_pos and self.cutscene_target_pos == self.base_pos):
                if "next action" not in self.current_action:
                    if done:
                        if self.cutscene_event and "die" in self.current_action:  # die animation
                            self.battle.cutscene_playing.remove(self.cutscene_event)
                            self.cutscene_target_pos = None
                            self.current_action = {}
                            self.cutscene_event = None
                            self.show_frame = self.max_show_frame
                            self.max_show_frame = 0  # reset max_show_frame to 0 to prevent restarting animation
                            self.reset_sprite()  # revert previous show_frame 0 animation start
                            return
                    if (self.current_action and
                            ((self.cutscene_target_pos and self.cutscene_target_pos == self.base_pos) or
                             (not self.cutscene_target_pos and "repeat" not in self.current_action and
                              "repeat after" not in self.current_action))):
                        # animation consider finish when reach target or finish animation with no repeat, pick idle animation
                        if "interact" in self.current_action:
                            if "name" in self.current_action:
                                self.current_action.pop("name")
                                self.pick_cutscene_animation(self.current_action)
                        else:
                            self.pick_cutscene_animation({})
                    if (self.cutscene_event and "repeat" not in self.current_action and
                            "interact" not in self.current_action and "select" not in self.current_action and
                            (not self.speech or "wait" not in self.current_action) and
                            (not self.cutscene_target_pos or self.cutscene_target_pos == self.base_pos)):
                        # finish animation, consider event done unless event in timer or
                        # require player interaction first or in repeat
                        self.cutscene_target_pos = None
                        if "repeat after" not in self.current_action:
                            if self.current_action:
                                self.pick_cutscene_animation({})
                            self.command_action = {}
                        else:  # event indicate repeat animation after event end
                            self.current_action["repeat"] = True
                            if not self.alive:
                                self.current_action["die"] = True
                        if self.cutscene_event in self.battle.cutscene_playing:
                            self.battle.cutscene_playing.remove(self.cutscene_event)
                        self.cutscene_event = None
                else:
                    self.cutscene_target_pos = None
                    if self.cutscene_event in self.battle.cutscene_playing:
                        self.battle.cutscene_playing.remove(self.cutscene_event)
                    self.cutscene_event = None
                    self.current_action = self.current_action["next action"]
                    self.pick_cutscene_animation(self.current_action)


class BattleCharacter(Character):
    show_dmg_number = False

    enter_stage = battle_character_enter_stage
    reset_sprite = battle_reset_sprite

    # static variable
    knock_down_sound_distance = 1000
    knock_down_screen_shake = 10
    dmg_screen_shake = 0
    dmg_sound_distance = 500
    is_sub_character = False

    def __init__(self, game_id: int, stat: dict, leader: BattleCharacter = None,
                 additional_layer: (int, str) = 0, is_commander: bool = False, is_summon: bool = False) -> None:
        """
        BattleCharacter object represent a character that take part in the battle in stage
        Character has three different stage of stat;
        first: base stat (e.g., base_offence), this is their stat before applying status effect
        second: stat with all effect (e.g., attack), this is their stat after applying weather, and status effect
        """
        self.ai_speak_list = {}

        if additional_layer != "main":
            self.main_character = None
        self.sub_characters = []
        self.leader = leader

        self.blind = False
        self.false_order = False  # check whether character is given false order by status effect
        self.shield = False  # check whether character is shielded for defence bonus against frontal attack
        self.no_forced_move = False  # check whether character can be forcefully move via knockback/die, will also prevent knockback from occurring
        self.active_without_sub_character = True  # check whether character remain active after all subs die
        self.no_spirit = False
        self.no_weak_side = False
        self.immune_weather = False  # check whether character is immune to weather effect
        self.hit_resource_regen = False
        self.sprite_deal_damage = False
        self.no_clip = False
        self.is_summon = is_summon
        self.indicator = None

        self.current_moveset = None
        self.nearest_enemy = None
        self.nearest_enemy_distance = None
        self.nearest_enemy_pos = None
        self.furthest_enemy = None
        self.furthest_enemy_distance = None
        self.furthest_enemy_pos = None
        self.nearest_ally = None
        self.nearest_ally_pos = None
        self.nearest_ally_distance = None

        self.move_cooldown = {}  # character can attack when cooldown reach attack speed
        self.status_duration = {}  # current status duration

        self.character_type = stat["Type"]
        self.character_class = stat["Class"]
        self.team = stat["Team"]
        self.enemy_team = 1
        if self.team == 1:
            self.enemy_team = 2

        self.total_range_power_score = 0
        self.total_offence_power_score = 0
        self.total_defence_power_score = 0
        self.total_power_score = 0
        self.start_pos = self.battle.team_stat[self.team]["start_pos"]

        # Get char stat
        self.leader = None
        if leader:
            self.leader = leader
            self.ai_prepare = MethodType(troop_ai_prepare, self)
        self.power_score = stat["Power Score"]
        self.original_offence = stat["Offence"]
        self.original_defence = stat["Defence"]
        self.supply = stat["Supply Drop"]

        self.melee_type = "offence"
        if self.original_offence < self.original_defence:
            self.melee_type = "defence"

        self.base_offence = stat["Offence"]
        self.base_defence = stat["Defence"]
        self.base_speed = stat["Speed"]
        self.leadership = stat["Leadership"]
        self.strategy_regen = self.leadership / 100
        self.status_immunity = stat["Status Immunity"]

        self.base_health = stat["Health"]  # max health of character
        self.base_resource = 100

        self.base_element_resistance = {key.split(" ")[0]: stat[key] for key in stat if " Resistance" in key}
        self.base_critical_chance = 0.1
        self.base_health_regen = 0  # health regeneration modifier
        if self.is_summon:
            self.base_health_regen = -1
        self.base_resource_regen = 1  # resource regeneration

        self.status_duration = {}  # current status duration

        self.base_resource_cost_modifier = 1

        self.spawns = stat["Spawns"]
        self.body_mass = stat["Mass"]
        self.knockdown_mass = self.body_mass * 4

        # Final stat after receiving stat effect from various sources, reset every time status is updated
        self.critical_chance = self.base_critical_chance
        self.offence = self.base_offence
        self.low_offence = self.offence * 0.5
        self.defence = self.base_defence
        self.element_resistance = self.base_element_resistance.copy()
        self.speed = self.base_speed
        self.low_speed = self.speed * 0.75
        self.health_regen = self.base_health_regen
        self.resource_regen = self.base_resource_regen
        self.animation_frame_play_time = self.Base_Animation_Frame_Play_Time
        self.final_animation_frame_play_time = self.animation_frame_play_time

        self.resource_cost_modifier = self.base_resource_cost_modifier

        self.health1 = self.base_health * 0.01
        self.health10 = self.base_health * 0.10

        self.health = self.base_health
        self.resource = self.base_resource

        self.run_speed = 7 * self.speed
        self.walk_speed = 3 * self.speed

        # Variables related to sound
        self.knock_down_sound_distance = self.knock_down_sound_distance + self.body_mass
        self.knock_down_screen_shake = self.knock_down_screen_shake + self.body_mass
        self.dmg_sound_distance = self.dmg_sound_distance + self.body_mass
        self.hit_volume_mod = self.body_mass / 10

        self.ai_movement_timer = 0  # timer to move for AI

        self.all_team_enemy_collision_grids = self.battle.all_team_ground_enemy_collision_grids
        self.ground_enemy_collision_grids = self.battle.all_team_ground_enemy_collision_grids[self.team]
        self.air_enemy_collision_grids = self.battle.all_team_air_enemy_collision_grids[self.team]
        self.enemy_collision_grids = self.ground_enemy_collision_grids  # collision grid for self sprite attack
        self.last_grid = self.battle.last_grid
        self.ally_list = self.battle.all_team_ally[self.team]
        self.near_ally = []
        self.near_enemy = []

        ai_speak_data = self.battle.localisation.grab_text(("ai_speak", stat["ID"]))
        if type(ai_speak_data) is dict:
            self.ai_speak_list = ai_speak_data

        # variable for attack cross function check
        self.is_effect_type = False
        self.duration = 0
        self.owner = self
        self.power = 0
        self.penetrate = 0
        self.element = None
        self.impact = None
        self.impact_sum = 0
        self.enemy_status_effect = ()
        self.no_defence = False
        self.no_dodge = False
        Character.__init__(self, game_id, stat, additional_layer=additional_layer, is_commander=is_commander)

        self.movesets = deepcopy(stat["Move"])
        self.ai_range_modifier = 1
        if not self.is_leader:
            self.ai_range_modifier = uniform(0.75, 1)
            for moveset in self.movesets.values():
                moveset["AI Range"] *= self.ai_range_modifier

        self.ai_min_attack_range = stat["ai_min_attack_range"] * self.ai_range_modifier
        self.ai_max_attack_range = stat["ai_max_attack_range"] * self.ai_range_modifier
        self.max_enemy_range_check = stat["max_enemy_range_check"] * self.ai_range_modifier
        self.ai_skirmish_range = stat["ai_skirmish_range"] * self.ai_range_modifier
        self.min_resource_move = stat["min_resource_move"]
        self.ai_min_effect_range = stat["ai_min_effect_range"]
        self.ai_enemy_max_effect_range = stat["ai_enemy_max_effect_range"]
        self.ai_ally_max_effect_range = stat["ai_ally_max_effect_range"]

        self.retreat_stage_end = self.battle.base_stage_end + self.sprite_width
        self.retreat_stage_start = -self.sprite_width
        self.enemy_start_pos = self.battle.team_stat[self.enemy_team]["start_pos"]

        if stat["Sub Characters"]:  # add sub characters
            for character in stat["Sub Characters"]:
                SubBattleCharacter(self.battle.last_char_game_id, self.character_list[character[0]] |
                                   {"ID": character[0], "Team": self.team,
                                    "POS": self.base_pos, "Anchor POS": (character[1], character[2])}, self)
                self.battle.last_char_game_id += 1

        if stat["ID"] in self.battle.character_portraits:
            self.icon = self.battle.character_portraits[stat["ID"]]["tactical"]
            self.command_icon = self.battle.character_portraits[stat["ID"]]["command"]

    def update(self, dt: float):
        """Character battle update, run when cutscene not playing"""
        if self.health:  # only run these when not dead
            self.timer += dt

            if self.timer > 0.1:  # Update status and skill, every 0.1 second
                if self not in self.battle.ai_process_list:
                    self.battle.ai_process_list.append(self)
                self.status_update()
                self.health_resource_logic()
                self.timer -= 0.1

            self.ai_logic(dt)
            self.rotate_logic()

            # Animation and sprite system
            hold_check = False
            if "hold" in self.current_animation_frame["property"] and \
                    "hold" in self.current_action and \
                    ((self.x_momentum or self.y_momentum) or self.current_moveset):
                # keep holding in moving action or moveset that hold when enemy in range
                if self.hold_timer < 3 and self.current_moveset:
                    if not self.nearest_enemy or self.nearest_enemy_distance > self.current_moveset["AI Range"]:
                        # timer proceed when no enemy nearby
                        self.hold_timer += dt
                    else:
                        if self.hold_too_long_timer > 5:  # hold for too long, increase hold timer anyway
                            self.hold_timer += dt
                        else:
                            self.hold_too_long_timer += dt
                    hold_check = True

            if self.sprite_deal_damage and self.penetrate:
                self.hit_collide_check()
                if hold_check and self.already_hit:  # release hold when hit something
                    hold_check = False
                if not self.penetrate and "run" in self.current_action:
                    # remove momentum in running attack animation when penetrate run out
                    self.x_momentum = 0

            if hold_check and not self.x_momentum and not self.y_momentum and self.already_hit:
                # end hold check for standing hold attack when hit enemy
                hold_check = False

            done = self.play_battle_animation(dt, hold_check)
            self.finish_animation(done)

            self.move_logic(dt)  # Movement function, have to be here

            if self.update_sprite:
                self.reset_sprite()
                self.update_sprite = False

            self.check_draw(dt)

            if ((self.broken or "broken" in self.commander_order) and
                    (self.base_pos[0] > self.retreat_stage_end or self.base_pos[0] < self.retreat_stage_start)):
                self.alive = False  # remove character that pass stage border, enter dead state
                self.health = 0
                for sub_character in self.sub_characters:
                    sub_character.die()
                    sub_character.erase()
                self.die()
                self.erase()

        else:  # die
            if self.alive:  # enter dead state
                if not self.in_drawer:  # always add dying character to camera
                    self.battle_camera_drawer.add(self)

                self.alive = False  # enter dead state
                for sub_character in self.sub_characters:
                    sub_character.health = 0
                    # sub_character.erase()

                self.current_action = self.die_command_action
                self.show_frame = 0
                self.frame_timer = 0
                self.pick_animation()
                self.die()

            if "die" in self.current_action:
                # play die animation
                hold_check = False
                if "hold" in self.current_animation_frame["property"] and (self.x_momentum or self.y_momentum):
                    # keep holding while moving
                    hold_check = True
                done = self.play_battle_animation(dt, hold_check)
                self.move_logic(dt)

                if self.update_sprite:
                    self.reset_sprite()
                    self.update_sprite = False

                if done and not self.x_momentum and not self.y_momentum:
                    # finish die animation and no momentum left
                    if not self.is_sub_character:
                        self.battle.scene.full_scene_image.blit(self.image, self.rect)  # blit corpse into main scene
                    if self.is_leader and not self.no_spirit:
                        self.current_action = self.spirit_command_action
                        self.show_frame = 0
                        self.frame_timer = 0
                        self.pick_animation()
                    else:  # non-leader or those with no_spirit property do not play spirit animation
                        if not self.is_summon:  # play float "cross" symbol for non-summon
                            DamageNumber("t", self.rect.midtop, True, self.team)
                        self.erase()  # remove character
            elif "spirit" in self.current_action:
                if self.base_pos[1] > -1500:  # keep floating up
                    self.y_momentum = 500
                    self.move_logic(dt)
                    self.play_battle_animation(dt, True)

                    if self.update_sprite:
                        self.reset_sprite()
                        self.update_sprite = False
                else:
                    self.erase()


class SubBattleCharacter(BattleCharacter):
    is_sub_character = True

    ai_prepare = sub_character_ai_prepare
    move_logic = sub_move_logic

    def __init__(self, game_id: int, stat: dict, main_character: BattleCharacter):
        """
        SubBattleCharacter object represent a battle character that is linked to a main BattleCharacter

        In that when the main character die, the sub character will also die even if they have separate health,
        sub character will also move along with the main character, they can attack while the main character move
        Some examples are archer on tower or big creature
        """
        self.main_character = main_character
        BattleCharacter.__init__(self, game_id, stat, additional_layer="main")
        self.anchor_pos = stat["Anchor POS"]
        if self.main_character.direction == "right":
            self.pos = Vector2(((self.base_pos[0] - self.anchor_pos[0]) * self.screen_scale[0],
                                (self.base_pos[1] + self.anchor_pos[1]) * self.screen_scale[1]))
        else:
            self.pos = Vector2(((self.base_pos[0] + self.anchor_pos[0]) * self.screen_scale[0],
                                (self.base_pos[1] + self.anchor_pos[1]) * self.screen_scale[1]))
        main_character.sub_characters.append(self)
        if main_character.max_enemy_range_check < self.max_enemy_range_check:
            main_character.max_enemy_range_check = self.max_enemy_range_check


class AirBattleCharacter(BattleCharacter):
    enter_stage = battle_air_character_enter_stage
    health_resource_logic = air_health_resource_logic
    move_logic = air_move_logic
    die = air_die

    def __init__(self, game_id: int, stat: dict, leader: Character = None):
        """
        SubBattleCharacter object represent a battle character that is linked to a main BattleCharacter

        In that when the main character die, the sub character will also die even if they have separate health,
        sub character will also move along with the main character, they can attack while the main character move
        Some examples are archer on tower or big creature
        """
        self.active = False
        self.enter_delay = 0
        BattleCharacter.__init__(self, game_id, stat, leader=leader)
        if self.ai_behaviour == "interceptor":
            self.ai_prepare = MethodType(interceptor_ai_prepare, self)
        elif self.ai_behaviour == "bomber":
            self.ai_prepare = MethodType(bomber_ai_prepare, self)
        else:
            self.ai_prepare = MethodType(fighter_ai_prepare, self)

        self.all_team_enemy_collision_grids = self.battle.all_team_air_enemy_collision_grids
        self.enemy_collision_grids = self.air_enemy_collision_grids

    def update(self, dt: float):
        if self.active:
            BattleCharacter.update(self, dt)
        else:
            if not self.broken:
                self.timer += dt

                if self.timer > 0.1:  # Update status and skill, every 0.1 second
                    self.status_update()
                    self.health_resource_logic()
                    self.timer -= 0.1

                if self.enter_delay:
                    self.delayed_enter_stage(dt)
            else:
                # inactive broken air unit from dead commander get erased immediately
                self.alive = False  # remove character that pass stage border, enter dead state
                self.health = 0
                for sub_character in self.sub_characters:
                    sub_character.die()
                    sub_character.erase()
                self.die()
                self.erase()


class CommanderBattleCharacter(BattleCharacter):
    die = commander_die

    def __init__(self, game_id: int, stat: dict):
        """
        CommanderBattleCharacter object represent the team commander

        When the commander character die, every character in that team will enter broken state.
        They will no longer fight and instead retreat from battle.
        """
        self.followers_len_check = [0, 0]
        self.max_followers_len_check = 0
        BattleCharacter.__init__(self, game_id, stat, is_commander=True, additional_layer=100000000)
        # self.max_enemy_range_check = self.last_grid * Default_Screen_Width  # commander check enemy at all range instead
        self.max_ai_commander_range = self.ai_max_attack_range
        for strategy in self.battle.team_stat[self.team]["strategy"]:
            strategy_stat = self.battle.strategy_list[strategy]
            if strategy_stat["Activate Range"] > self.max_ai_commander_range:
                self.max_ai_commander_range = strategy_stat["Activate Range"]


class ShowcaseCharacter(Character):
    ai_logic = empty_method
    enter_stage = showcase_enter_stage
    move_logic = empty_method
    play_battle_animation = play_showcase_animation
    next_animation_frame = showcase_next_animation_frame

    # static variable
    is_sub_character = False

    def __init__(self, game_id: int, stat: dict, leader: BattleCharacter = None,
                 is_commander: bool = False, is_summon: bool = False) -> None:
        """
        BattleCharacter object represent a character that take part in the battle in stage
        Character has three different stage of stat;
        first: base stat (e.g., base_offence), this is their stat before applying status effect
        second: stat with all effect (e.g., attack), this is their stat after applying weather, and status effect
        """
        self.sub_characters = []

        self.current_moveset = None

        self.animation_frame_play_time = self.Base_Animation_Frame_Play_Time
        self.final_animation_frame_play_time = self.animation_frame_play_time

        # variable for attack cross function check
        Character.__init__(self, game_id, stat, additional_layer="showcase", is_commander=is_commander)
        self.movesets = stat["Move"]

        if stat["Sub Characters"]:  # add sub characters
            for character in stat["Sub Characters"]:
                SubShowcaseCharacter(0, self.character_list[character[0]] |
                                     {"ID": character[0], "POS": self.base_pos, "direction": self.direction,
                                      "Anchor POS": (character[1], character[2])}, self)
        self.battle.battle_character_updater.remove(self)
        self.battle.all_battle_characters.remove(self)


class SubShowcaseCharacter(Character):
    is_sub_character = True
    ai_logic = empty_method
    enter_stage = showcase_enter_stage
    move_logic = sub_move_logic
    play_battle_animation = play_showcase_animation
    next_animation_frame = showcase_next_animation_frame

    def __init__(self, game_id: int, stat: dict, main_character: ShowcaseCharacter):
        """
        SubShowcaseCharacter object represent a showcase character that is linked to a main ShowcaseCharacter
        """
        self.main_character = main_character
        Character.__init__(self, game_id, stat, additional_layer="main")
        self.anchor_pos = stat["Anchor POS"]
        if self.main_character.direction == "right":
            self.pos = Vector2(((self.base_pos[0] - self.anchor_pos[0]) * self.screen_scale[0],
                                (self.base_pos[1] + self.anchor_pos[1]) * self.screen_scale[1]))
        else:
            self.pos = Vector2(((self.base_pos[0] + self.anchor_pos[0]) * self.screen_scale[0],
                                (self.base_pos[1] + self.anchor_pos[1]) * self.screen_scale[1]))
        main_character.sub_characters.append(self)
        self.battle.battle_character_updater.remove(self)
        self.battle.all_battle_characters.remove(self)
