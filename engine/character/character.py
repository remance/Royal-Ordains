from __future__ import annotations
from types import MethodType

from pygame import sprite, Vector2, Surface
from pygame.mask import from_surface

from engine.character.ai_combat import ai_combat_dict
from engine.character.ai_move import ai_move_dict
from engine.character.ai_retreat import ai_retreat_dict

from engine.character.ai_prepare import (get_near_enemy, ai_prepare, follower_ai_prepare, sub_character_ai_prepare,
                                         interceptor_ai_prepare, bomber_ai_prepare, fighter_ai_prepare)
from engine.character.ai_combat import check_ai_condition
from engine.character.ai_speak import ai_speak
from engine.character.ai_logic import ai_logic
from engine.character.apply_status import apply_status
from engine.character.cal_loss import cal_loss
from engine.character.character_event_process import character_event_process
from engine.character.die import commander_die, die, air_die
from engine.character.enter_stage import (enter_stage, battle_character_enter_stage, battle_air_character_enter_stage,
                                          delayed_enter_stage)
from engine.character.erase import erase
from engine.character.get_damage import get_damage
from engine.character.finish_animation import finish_animation
from engine.character.health_resource_logic import health_resource_logic, air_health_resource_logic
from engine.character.issue_commander_order import issue_commander_order
from engine.character.issue_general_order import issue_general_order
from engine.character.reset_general_variables import reset_general_variables
from engine.character.move_logic import move_logic, sub_move_logic, air_move_logic
from engine.character.pick_animation import pick_animation
from engine.character.pick_cutscene_animation import pick_cutscene_animation
from engine.character.play_animation import next_animation_frame, play_battle_animation, play_cutscene_animation
from engine.character.reset_sprite import reset_sprite
from engine.character.rotate_logic import rotate_logic
from engine.character.status_update import status_update

from engine.effect.cal_dmg import cal_dmg
from engine.effect.hit_collide_check import hit_collide_check
from engine.effect.hit_register import hit_register

from engine.uibattle.uibattle import DamageNumber, CharacterGeneralIndicator

from engine.utils.text_making import text_render_with_bg
from engine.utils.common import clean_object
from engine.utils.rotation import set_rotate

from engine.constants import *

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
    effect_list = None
    sound_effect_pool = None

    image = Surface((0, 0))  # start with empty surface
    collision_grid_width = 0

    ai_speak = ai_speak
    ai_logic = ai_logic
    ai_prepare = ai_prepare
    apply_status = apply_status
    cal_loss = cal_loss
    character_event_process = character_event_process
    check_ai_condition = check_ai_condition
    delayed_enter_stage = delayed_enter_stage
    die = die
    enter_stage = enter_stage
    erase = erase
    get_damage = get_damage
    get_near_enemy = get_near_enemy
    finish_animation = finish_animation
    health_resource_logic = health_resource_logic
    issue_commander_order = issue_commander_order
    issue_general_order = issue_general_order
    reset_general_variables = reset_general_variables
    move_logic = move_logic
    pick_animation = pick_animation
    pick_cutscene_animation = pick_cutscene_animation
    next_animation_frame = next_animation_frame
    play_battle_animation = play_battle_animation
    play_cutscene = play_cutscene_animation
    reset_sprite = reset_sprite
    rotate_logic = rotate_logic
    status_update = status_update

    cal_dmg = cal_dmg
    hit_collide_check = hit_collide_check
    hit_register = hit_register

    clean_object = clean_object
    set_rotate = set_rotate

    moveset_command_action = {"moveset": True}

    damaged_command_action = {"name": "Damaged", "damaged": True, "movable": True, "hold": True,
                                   "forced move": True}
    standup_command_action = {"name": "Standup"}
    knockdown_command_action = {"name": "Knockdown", "movable": True, "forced move": True,
                                     "knockdown": True, "hold": True, "next action": standup_command_action}

    die_command_action = {"name": "Die", "uninterruptible": True,
                               "movable": True, "forced move": True, "hold": True, "die": True}

    spirit_command_action = {"name": "Spirit", "uninterruptible": True,
                                  "movable": True, "forced move": True, "hold": True, "spirit": True}

    # static variable
    Base_Animation_Play_Time = Base_Animation_Play_Time
    Default_Air_Pos = Default_Air_Pos
    Default_Ground_Pos = Default_Ground_Pos
    Character_Gravity = Character_Gravity

    def __init__(self, game_id: int, stat: dict, additional_layer: int = 0) -> None:
        """
        Character object represent a character that may or may not fight in battle
        """
        sprite.Sprite.__init__(self, self.containers)

        # these two commands require replacement of x_momentum and direction, faster to use it as object variable
        self.walk_command_action = {"name": "Walk", "movable": True, "walk": True, "interruptable": True}
        self.run_command_action = {"name": "Run", "movable": True, "run": True, "interruptable": True}

        self.screen_scale = self.battle.screen_scale
        self.battle_scale = (self.screen_scale[0] * 0.2, self.screen_scale[1] * 0.2)
        self.battle_camera = self.battle.battle_cameras["battle"]
        self.weather = self.battle.current_weather

        # Variable related to sprite
        # use for pseudo sprite size of character for positioning of effect and ui
        self.char_id = stat["ID"]
        self.game_id = game_id  # object ID for reference

        self.animation_pool = self.battle.character_animation_data[self.char_id]  # list of animation this character
        self.sprite_height = self.animation_pool["Default"][0]["right"]["sprite"].get_height() * 1.5
        self.sprite_width = self.animation_pool["Default"][0]["right"]["sprite"].get_width() * 0.5

        self._layer = (10000 - self.sprite_height) + additional_layer
        self.name = self.battle.localisation.grab_text(("character", stat["ID"], "Name"))
        self.cutscene_event = None
        self.speech = None
        self.ai_lock = False

        self.current_action = {}  # action being performed
        self.command_action = {}  # next action to be performed
        self.current_animation = {}  # list of animation frames playing
        self.current_animation_frame = {}
        self.current_animation_direction = {}
        self.already_hit = []

        self.timer = 0
        self.frame_timer = 0
        self.show_frame = 0  # current animation frame
        self.max_show_frame = 0
        self.replace_idle_animation = None
        self.interrupt_animation = False

        self.alive = True
        self.reach_camera_event = {}

        # self.arrive_condition = stat["Arrive Condition"]

        self.y_momentum = 0
        self.x_momentum = 0

        self.animation_play_time = self.Base_Animation_Play_Time
        self.final_animation_play_time = self.animation_play_time

        self.commander_order = ()
        self.false_commander_order = ()
        self.true_commander_order = ()
        self.base_pos = Vector2(stat["POS"][0],
                                stat["POS"][1])  # true position of character in battle
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

        self.rect = self.image.get_rect(topleft=(0, 0))
        self.mask = from_surface(self.image)

        self.update_sprite = False

        self.move_speed = 0  # speed of current movement

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

                for this_char in self.battle.all_characters:
                    if target == this_char.game_id:  # find target char object
                        self.target = this_char
                        break
            elif stuff == "idle":  # replace idle animation
                self.replace_idle_animation = char_property["idle"]
            else:
                self.__setattr__(stuff, char_property[stuff])

        self.base_ground_pos = self.Default_Ground_Pos
        if "Ground Y POS" in stat and stat["Ground Y POS"]:  # replace ground pos based on data in stage
            self.base_ground_pos = stat["Ground Y POS"]

        self.enter_stage()

    def update(self, dt: float):
        if self.alive:  # only run these when not dead
            self.rotate_logic()  # Rotate Function
            self.move_logic(dt)  # Move function

            # Animation and sprite system
            hold_check = False

            if "hold" in self.current_animation_frame["property"] and "hold" in self.current_action:
                # also hold if in freeze timer with frame that can hold
                hold_check = True

            done = self.play_battle_animation(dt, hold_check)
            self.finish_animation(done)

            if self.update_sprite:
                self.reset_sprite()
                self.update_sprite = False

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

    # static variable
    knock_down_sound_distance = 1000
    knock_down_screen_shake = 10
    dmg_screen_shake = 0
    dmg_sound_distance = 500
    is_sub_character = False

    def __init__(self, game_id: int, stat: dict, leader: BattleCharacter = None,
                 additional_layer: int = 0, is_commander: bool = False,
                 is_general: bool = False, is_controllable: bool = False) -> None:
        """
        BattleCharacter object represent a character that take part in the battle in stage
        Character has three different stage of stat;
        first: base stat (e.g., base_offence), this is their stat before applying status effect
        second: stat with all effect (e.g., attack), this is their stat after applying weather, and status effect
        """
        self.ai_speak_list = {}
        self.followers = []
        self.followers_len_check = None
        self.max_followers_len_check = None
        if "Followers" in stat:
            self.follower_form = stat["Followers"]

        self.main_character = None
        self.general = None
        self.sub_characters = []
        self.leader = leader
        self.is_commander = is_commander
        self.is_general = is_general
        self.is_controllable = is_controllable

        self.invisible = False
        self.blind = False
        self.invincible = False
        self.shield = False  # check whether character is shielded for defence bonus against frontal attack
        self.no_forced_move = False  # check whether character can be forcefully move via knockback/die
        self.active_without_sub_character = True  # check whether character remain active after all subs die
        self.no_spirit = False
        self.no_weak_side = False
        self.immune_weather = False  # check whether character is immune to weather effect
        self.hit_resource_regen = False
        self.sprite_deal_damage = False
        self.no_clip = False
        self.is_summon = False
        if stat["Is Summon"]:
            self.is_summon = True
        self.spawns = {}
        self.broken = False
        self.indicator = None

        self.current_moveset = None
        self.nearest_enemy = None
        self.nearest_enemy_distance = None
        self.nearest_enemy_pos = None
        self.nearest_ally = None
        self.nearest_ally_distance = None

        self.move_speed = 0  # speed of current movement

        self.move_cooldown = {}  # character can attack when cooldown reach attack speed
        self.status_duration = {}  # current status duration

        self.character_type = stat["Type"]
        self.team = stat["Team"]
        self.enter_pos = self.battle.team_stat[self.team]["start_pos"]

        # Get char stat
        stat_boost = 0
        leader_charisma = 0
        self.leader = None
        if leader:  # character with leader get stat boost from leader charisma
            self.leader = leader
            if self.character_type != "air":  # air character does not add into followers list
                self.leader.followers.append(self)
            leader_charisma = self.leader.leadership
            stat_boost = int(leader_charisma / 5)
            self.ai_prepare = MethodType(follower_ai_prepare, self)
        self.original_offence = stat["Offence"]
        self.original_defence = stat["Defence"]
        self.original_leadership = stat["Leadership"]

        self.base_offence = stat["Offence"] + (stat["Offence"] * (leader_charisma / 200)) + stat_boost
        self.base_defence = stat["Defence"] + (stat["Defence"] * (leader_charisma / 200)) + stat_boost
        self.base_speed = stat["Speed"]
        self.leadership = stat["Leadership"] + (stat["Leadership"] * (leader_charisma / 200)) + stat_boost

        self.base_health = stat["Health"]  # max health of character
        self.base_resource = 100 + (100 * (leader_charisma / 200))

        self.base_element_resistance = {key.split(" ")[0]: stat[key] for key in stat if " Resistance" in key}
        self.base_critical_chance = 0.1
        self.base_health_regen = 0  # health regeneration modifier
        if self.is_summon:
            self.base_health_regen = -1
        self.base_resource_regen = 1 + (self.leadership * 0.01) + (
                leader_charisma * 0.01)  # resource regeneration

        self.status_duration = {}  # current status duration

        self.base_resource_cost_modifier = 1

        self.movesets = stat["Move"]
        self.spawns = stat["Spawns"]
        self.body_mass = stat["Mass"]
        self.knockdown_mass = self.body_mass * 3

        self.base_impact_modifier = 1  # extra impact for weapon attack

        # Final stat after receiving stat effect from various sources, reset every time status is updated
        self.impact_modifier = self.base_impact_modifier
        self.critical_chance = self.base_critical_chance
        self.offence = self.base_offence
        self.defence = self.base_defence
        self.element_resistance = self.base_element_resistance.copy()
        self.speed = self.base_speed
        self.health_regen = self.base_health_regen
        self.resource_regen = self.base_resource_regen
        self.animation_play_time = self.Base_Animation_Play_Time
        self.final_animation_play_time = self.animation_play_time

        self.resource_cost_modifier = self.base_resource_cost_modifier

        start_health = stat["Start Health"]
        start_resource = stat["Start Resource"]

        self.health1 = self.base_health * 0.01
        self.health10 = self.base_health * 0.10

        self.health = self.base_health * start_health
        self.resource = self.base_resource * start_resource

        self.run_speed = 10 * self.speed
        self.walk_speed = 4 * self.speed

        # Variables related to sound
        self.knock_down_sound_distance = self.knock_down_sound_distance + self.body_mass
        self.knock_down_screen_shake = self.knock_down_screen_shake + self.body_mass
        self.dmg_sound_distance = self.dmg_sound_distance + self.body_mass
        self.hit_volume_mod = self.body_mass / 10

        self.event_ai_lock = False  # lock AI until event unlock it only

        self.ai_timer = 0  # for whatever timer require for AI action
        self.ai_movement_timer = 0  # timer to move for AI

        self.general_order = "follow"

        self.ai_behaviour = stat["AI Behaviour"]

        self.ai_move = MethodType(ai_move_dict["default"], self)
        if self.is_general and self.is_controllable:  # controllable general use behaviour that move based on commander order
            self.ai_move = MethodType(ai_move_dict["general"], self)
        elif self.ai_behaviour in ai_move_dict:
            self.ai_move = MethodType(ai_move_dict[self.ai_behaviour], self)

        self.ai_combat = MethodType(ai_combat_dict["default"], self)
        if self.is_general and self.is_controllable:
            self.ai_combat = MethodType(ai_combat_dict["general"], self)
        elif self.ai_behaviour in ai_combat_dict:
            self.ai_combat = MethodType(ai_combat_dict[self.ai_behaviour], self)

        self.ai_retreat = MethodType(ai_retreat_dict["default"], self)
        if self.ai_behaviour in ai_retreat_dict:
            self.ai_retreat = MethodType(ai_retreat_dict[self.ai_behaviour], self)

        self.ai_min_attack_range = stat["ai_min_attack_range"]
        self.ai_max_attack_range = stat["ai_max_attack_range"]
        self.ai_min_effect_range = stat["ai_min_effect_range"]
        self.ai_max_effect_range = stat["ai_max_effect_range"]
        self.max_enemy_range_check = stat["max_enemy_range_check"]

        self.ai_timer = 0  # for whatever timer require for AI action
        self.ai_movement_timer = 0  # timer to move for AI

        self.all_team_enemy_collision_grids = self.battle.all_team_ground_enemy_collision_grids
        self.ground_enemy_collision_grids = self.battle.all_team_ground_enemy_collision_grids[self.team]
        self.air_enemy_collision_grids = self.battle.all_team_air_enemy_collision_grids[self.team]
        self.enemy_collision_grids = self.ground_enemy_collision_grids  # collision grid for self sprite attack
        self.last_grid = self.battle.last_grid
        self.ally_list = self.battle.all_team_ally[self.team]
        self.near_ally = []
        self.near_enemy = []

        ai_speak = self.battle.localisation.grab_text(("ai_speak", stat["ID"]))
        if type(ai_speak) is dict:
            self.ai_speak_list = ai_speak

        # variable for attack cross function check
        self.remain_reach = None
        self.remain_timer = None
        self.is_effect_type = False
        self.owner = self
        self.dmg = 0
        self.penetrate = 0
        self.element = None
        self.impact = None
        self.impact_sum = 0
        self.enemy_status_effect = ()
        self.no_defence = False
        self.no_dodge = False
        Character.__init__(self, game_id, stat, additional_layer=additional_layer)

        self.retreat_stage_end = self.battle.base_stage_end + self.sprite_width
        self.retreat_stage_start = -self.sprite_width

        if stat["Sub Characters"]:  # add sub characters
            for character, anchor_pos in stat["Sub Characters"].items():
                for sub_character_pos in anchor_pos:
                    SubBattleCharacter(self.battle.last_char_game_id, self.character_data.character_list[character] |
                                       {"ID": character, "Team": self.team,
                                        "Start Health": stat["Start Health"], "Start Resource": stat["Start Resource"],
                                        "POS": self.base_pos, "Anchor POS": sub_character_pos,
                                        "Arrive Condition": ()}, self)
                    self.battle.last_char_game_id += 1

        if stat["ID"] in self.battle.character_portraits:
            self.icon = self.battle.character_portraits[stat["ID"]]["tactical"]
            self.command_icon = self.battle.character_portraits[stat["ID"]]["command"]
            self.command_icon_right = self.battle.character_portraits[stat["ID"]]["command"]["right"]

        if is_controllable and self.team == 1:
            self.battle.player_control_generals.append(self)
            self.indicator = CharacterGeneralIndicator(self)

            index = self.battle.player_control_generals.index(self) + 1
            if "control" not in self.battle.character_portraits[stat["ID"]] or \
                    index not in self.battle.character_portraits[stat["ID"]]["control"]:
                self.icon = {key: value.copy() for key, value in self.icon.items()}
                text = text_render_with_bg(str(self.battle.player_control_generals.index(self) + 1),
                                           self.battle.game.character_indicator_font,
                                           gf_colour=(0, 0, 0),
                                           o_colour=(255, 255, 255))
                for key in self.icon:
                    self.icon[key].blit(text, text.get_rect(midtop=(self.icon[key].get_width() / 2, 0)))
                if "control" not in self.battle.character_portraits[stat["ID"]]:
                    self.battle.character_portraits[stat["ID"]]["control"] = {}
                self.battle.character_portraits[stat["ID"]]["control"][index] = self.icon  # cache the icon with number
            else:
                self.icon = self.battle.character_portraits[stat["ID"]]["control"][index]

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
                    ("forced move" not in self.current_action or (self.x_momentum or self.y_momentum)):
                hold_check = True

            done = self.play_battle_animation(dt, hold_check)
            self.finish_animation(done)

            if self.sprite_deal_damage and self.penetrate:
                self.hit_collide_check()
                if not self.penetrate and "run" in self.current_action:
                    # remove momentum in running attack animation when penetrate run out
                    self.x_momentum = 0

            self.move_logic(dt)  # Movement function, have to be here

            if self.update_sprite:
                self.reset_sprite()
                self.update_sprite = False

            if self.reach_camera_event and self.battle.base_camera_begin < self.base_pos[
                0] < self.battle.base_camera_end:
                # play event related to character reach inside camera
                for key, value in self.reach_camera_event.items():
                    for item in value:
                        self.character_event_process(item, item["Property"])
                        break  # play one child event at a time
                    if "repeat" not in item["Property"]:  # always have item in event data
                        value.remove(item)
                    break  # play one event at a time
                if not value:  # last event no longer have child event left, remove from dict
                    self.reach_camera_event.pop(key)

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
                    if self.is_general and not self.no_spirit:
                        self.current_action = self.spirit_command_action
                        self.show_frame = 0
                        self.frame_timer = 0
                        self.pick_animation()
                    else:  # non-general or those with no_spirit property do not play spirit animation
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

    def __init__(self, game_id: int, stat: dict,
                 main_character: BattleCharacter):
        """
        SubBattleCharacter object represent a battle character that is linked to a main BattleCharacter

        In that when the main character die, the sub character will also die even if they have separate health,
        sub character will also move along with the main character, they can attack while the main character move
        Some examples are archer on tower or big creature
        """
        BattleCharacter.__init__(self, game_id, stat, additional_layer=int(-main_character._layer / 10))
        self.anchor_pos = stat["Anchor POS"]
        self.pos = Vector2(((self.base_pos[0] + self.anchor_pos[0]) * self.screen_scale[0],
                            (self.base_pos[1] + self.anchor_pos[1]) * self.screen_scale[1]))
        self.main_character = main_character
        main_character.sub_characters.append(self)
        if self.main_character.max_enemy_range_check < self.max_enemy_range_check:
            self.main_character.max_enemy_range_check = self.max_enemy_range_check


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
        BattleCharacter.__init__(self, game_id, stat, is_commander=True, is_general=True, is_controllable=True,
                                 additional_layer=10000000000000)

