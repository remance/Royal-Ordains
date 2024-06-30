from copy import deepcopy
from types import MethodType
from math import radians
from random import uniform

import pygame
from pygame import sprite, Vector2
from pygame.mask import from_surface

from engine.character.ai_combat import ai_combat_dict
from engine.character.ai_move import ai_move_dict
from engine.character.ai_retreat import ai_retreat_dict
from engine.character.character_specific_damage import damage_dict
from engine.character.character_specific_initiate import initiate_dict
from engine.character.character_specific_special import special_dict
from engine.character.character_specific_start_animation import animation_start_dict
from engine.character.character_specific_status_update import status_update_dict
from engine.character.character_specific_update import update_dict
from engine.data.datastat import final_parent_moveset, recursive_rearrange_moveset
from engine.uibattle.uibattle import CharacterIndicator, CharacterSpeechBox
from engine.utils.common import empty_method

rotation_list = (90, -90)
rotation_name = ("l_side", "r_side")
rotation_dict = {key: rotation_name[index] for index, key in enumerate(rotation_list)}

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
move loop = action involve repeating movement that can be cancel when movement change like walk to run
low level = indicate low level animation that can get replaced by command action without requiring interrupt_animation
walk, run, flee = indicate movement type for easy checking, walk and run also use for move_speed
stand, couch, ai = indicate position change after animation finish
land (stand) = indicate position change before animation start
weapon = weapon index of action for easy checking
no combat ai = prevent leader and troop AI from running combat attack AI method
pos = specific target pos
require input = animation action require input first and will keep holding first frame until this condition is removed 
                or interrupt
x_momentum or y_momentum = assign custom momentum value instead
swap weapon set = finish animation will make character swap weapon set based on provided value
freeze = assign freeze_timer value when start action
drop speed = assign value of dropping speed for air animation, higher value mean faster drop
"""


class Character(sprite.Sprite):
    battle = None
    character_data = None
    effect_list = None
    status_list = None
    sound_effect_pool = None

    image = pygame.Surface((0, 0))  # start with empty surface

    from engine.utils.common import clean_object
    clean_object = clean_object

    from engine.utils.rotation import set_rotate
    set_rotate = set_rotate

    from engine.character.add_gear_stat import add_gear_stat
    add_weapon_stat = add_gear_stat

    from engine.character.ai_combat import check_ai_condition
    check_ai_condition = check_ai_condition

    from engine.character.apply_status import apply_status
    apply_status = apply_status

    from engine.character.cal_loss import cal_loss
    cal_loss = cal_loss

    from engine.character.character_event_process import character_event_process
    character_event_process = character_event_process

    from engine.character.check_action_hold import check_action_hold
    check_action_hold = check_action_hold

    from engine.character.check_move_existence import check_move_existence, training_moveset_existence_check
    check_move_existence = check_move_existence
    training_moveset_existence_check = training_moveset_existence_check

    from engine.character.check_new_animation import check_new_animation
    check_new_animation = check_new_animation

    from engine.character.check_prepare_action import check_prepare_action
    check_prepare_action = check_prepare_action

    from engine.character.die import die
    die = die

    from engine.character.engage_combat import engage_combat
    engage_combat = engage_combat

    from engine.character.enter_stage import enter_stage
    enter_stage = enter_stage

    from engine.character.health_resource_logic import health_resource_logic
    health_stamina_logic = health_resource_logic

    from engine.character.move_logic import move_logic
    move_logic = move_logic

    from engine.character.pick_animation import pick_animation
    pick_animation = pick_animation

    from engine.character.pick_cutscene_animation import pick_cutscene_animation
    pick_cutscene_animation = pick_cutscene_animation

    from engine.character.play_animation import play_animation
    play_animation = play_animation

    from engine.character.play_cutscene_animation import play_cutscene_animation
    play_cutscene = play_cutscene_animation

    from engine.character.player_input_battle_mode import player_input_battle_mode
    player_input_battle_mode = player_input_battle_mode

    from engine.character.player_input_city_mode import player_input_city_mode
    player_input_city_mode = player_input_city_mode

    from engine.character.player_input_wheel_ui_mode import player_input_wheel_ui_mode
    player_input_wheel_ui_mode = player_input_wheel_ui_mode

    from engine.character.remove_moveset_not_match_stat_requirement import remove_moveset_not_match_stat_requirement
    remove_moveset_not_match_stat_requirement = remove_moveset_not_match_stat_requirement

    from engine.character.rotate_logic import rotate_logic
    rotate_logic = rotate_logic

    from engine.character.start_animation_body_part import start_animation_body_part
    start_animation_body_part = start_animation_body_part

    from engine.character.status_update import status_update
    status_update = status_update

    walk_command_action = {"name": "Walk", "movable": True, "walk": True}
    run_command_action = {"name": "Run", "movable": True, "run": True}
    flee_command_action = {"name": "FleeMove", "movable": True, "flee": True}
    halt_command_action = {"name": "Halt", "movable": True, "walk": True, "halt": True}
    dash_command_action = {"name": "Dash", "uncontrollable": True, "movable": True, "forced move": True, "no dmg": True,
                           "hold": True, "dash": True, "not_reset_special_state": True}

    relax_command_action = {"name": "Relax", "low level": True}
    special_relax_command = ()

    couch_command_action = {"name": "Couch", "couch": True}
    couch_stand_command_action = {"name": "Stand", "uncontrollable": True, "stand": True}

    weak_attack_command_action = {"name": "Weak Attack", "moveset": True, "weak": True}
    strong_attack_command_action = {"name": "Strong Attack", "moveset": True, "strong": True}
    weak_attack_run_command_action = {"name": "Weak Attack", "moveset": True, "movable": True, "weak": True,
                                      "run": True, "remove momentum when done": True}
    strong_attack_run_command_action = {"name": "Strong Attack", "moveset": True, "movable": True, "strong": True,
                                        "run": True, "remove momentum when done": True}
    weak_attack_hold_command_action = {"name": "Weak Attack", "hold": True, "moveset": True, "weak": True}
    strong_attack_hold_command_action = {"name": "Strong Attack", "hold": True, "moveset": True, "strong": True}
    special_command_action = {"name": "Special", "moveset": True, "special": True}
    special_hold_command_action = {"name": "Special", "hold": True, "moveset": True, "special": True}
    attack_command_actions = {"Weak": weak_attack_command_action, "Strong": strong_attack_command_action,
                              "Special": special_command_action}
    skill_command_action = {"name": "Skill", "moveset": True, "skill": True}
    activate_command_action = {"name": "Activate"}
    deactivate_command_action = {"name": "Deactivate"}

    guard_command_action = {"name": "Guard", "guard": True}
    guard_hold_command_action = {"name": "Guard", "guard": True, "hold": True}
    guard_move_command_action = {"name": "GuardWalk", "guard": True, "movable": True, "walk": True}
    guard_break_command_action = {"name": "GuardBreak", "uncontrollable": True}

    air_idle_command_action = {"name": "Idle", "movable": True}
    land_command_action = {"name": "Land", "uncontrollable": True, "stand": True}

    jump_command_action = {"name": "Jump", "air": True}
    runjump_command_action = {"name": "RunJump", "air": True}

    arrive_command_action = {"name": "Arrive", "movable": True, "arrive": True, "x_momentum": True}
    arrive_fly_command_action = {"name": "Arrive", "movable": True, "arrive": True, "fly": True, "x_momentum": True}

    useitem_command_action = {"name": "UseItem", "change_sprite": "Item"}

    heavy_damaged_command_action = {"name": "HeavyDamaged", "uncontrollable": True, "movable": True, "hold": True,
                                    "x_momentum": True, "y_momentum": True, "forced move": True, "heavy damaged": True}
    damaged_command_action = {"name": "SmallDamaged", "uncontrollable": True, "movable": True, "forced move": True,
                              "hold": True, "small damaged": True, "x_momentum": True, "y_momentum": True}
    standup_command_action = {"name": "Standup", "uncontrollable": True, "no dmg": True}
    liedown_command_action = {"name": "Liedown", "no dmg": True,
                              "knockdown": True, "freeze": 1, "next action": standup_command_action}
    knockdown_command_action = {"name": "Knockdown", "movable": True, "uncontrollable": True, "forced move": True,
                                "knockdown": True, "hold": True, "next action": liedown_command_action, "stand": True,
                                "x_momentum": True, "y_momentum": True,}
    stun_end_command_action = {"name": "StunEnd"}
    stun_command_action = {"name": "Stun", "forced move": True, "uncontrollable": True,
                           "knockdown": True, "freeze": 5, "hold": True, "next action": stun_end_command_action,
                           "stand": True}

    die_command_action = {"name": "Die", "uninterruptible": True, "uncontrollable": True, "stand": True,
                          "movable": True, "forced move": True, "die": True}

    submit_action = {"name": "Submit", "repeat": True, "die": True, "submit": True}
    execute_action = {"name": "Execute", "hold": True, "execute": True, "die": True}
    taunt_action = {"name": "Taunt", "movable": True, "taunt": True}
    cheer_action = {"name": "Cheer", "cheer": True}
    cheer_fast_action = {"name": "CheerFast", "cheer": True}

    default_item_drop_table = {"Speed Potion": 10, "Stone Potion": 10, "Reviving Seed": 1,
                               "Health Potion": 3, "Resource Potion": 2, "Bronze Coin": 30, "Silver Coin": 15,
                               "Gold Coin": 7, "Jewellery": 6, "Diamond": 0.3,
                               "Lute": 3, "Harp": 3, "Jar": 3, "Whetstone": 2, "Goblet": 3, "Beer Mug": 4, "Teapot": 3,
                               "Yarn": 4, "Horseshoe": 3, "Board Game": 2, "Saint Figurine": 1, "Ball": 2,
                               "Trumpet": 3, "Golden Goblet": 1, "Ruby": 0.8, "Ring": 1,
                               "Sapphire": 0.8, "Topaz": 0.8, "Emerald": 0.8, "Amethyst": 0.8, "Opal": 0.8,
                               "Rare Coin": 1, "Beer": 7, "Wine": 6}  # , "Kid Doll": 0.5,
    # "Rabbit Doll": 0.45, "Dog Doll": 0.3, "Cat Doll": 0.3, "Bear Doll": 0.2,
    # "Gryphon Doll": 0.1, "Unicorn Doll": 0.08, "Slime Doll": 0.06, "Dragon Doll": 0.05,
    # "Princess Doll": 0.03

    # drop that get added when playable character exist
    special_character_drop_table = {"Rodhinbar": {"Rodhinbar Arrow": 15},
                                    "Iri": {"Scrap": 15, "Trap Remain": 5},
                                    "Minara": {"Minara Bolt": 10}}
    # static variable
    default_animation_play_time = 0.1
    base_ground_pos = 1000

    def __init__(self, game_id, layer_id, stat, player_control=False):
        """
        Character object represent a character that may or may not fight in battle
        """
        sprite.Sprite.__init__(self, self.containers)
        self.screen_scale = self.battle.screen_scale
        self.game_id = game_id  # object ID for reference
        self.layer_id = layer_id  # ID for sprite layer calculation
        self.base_layer = 0
        self.name = stat["Name"]
        self.show_name = self.battle.localisation.grab_text(("character", stat["ID"] + self.battle.chapter, "Name"))
        if "(" in self.show_name and "," in self.show_name:
            self.show_name = self.battle.localisation.grab_text(("character", stat["ID"], "Name"))
        self.player_control = player_control  # character controlled by player
        self.indicator = None
        self.cutscene_event = None
        self.followers = []
        self.leader = None
        self.killer = None  # object that kill this character, for adding gold, score, and kill stat
        self.broken = False
        self.drops = {}
        self.spawns = {}

        self.current_action = {}  # action being performed
        self.command_action = {}  # next action to be performed
        self.animation_pool = {}  # list of animation sprite this character can play with its action
        self.status_animation_pool = {}
        self.current_animation = {}  # list of animation frames playing
        self.current_animation_direction = {}
        self.frame_timer = 0
        self.show_frame = 0  # current animation frame
        self.max_show_frame = 0
        self.stoppable_frame = False
        self.replace_idle_animation = None
        self.interrupt_animation = False
        self.freeze_timer = 0
        self.hold_timer = 0  # how long animation holding so far
        self.release_timer = 0  # time when hold release
        self.timer = uniform(0, 0.1)
        self.mode_timer = 0

        self.alive = True
        self.invisible = False
        self.blind = False
        self.invincible = False
        self.fly = False
        self.no_clip = False
        self.no_pickup = False
        self.hit_enemy = False
        self.is_boss = False
        self.is_summon = False
        self.can_combo_with_no_hit = False
        self.command_moveset = None
        self.current_moveset = None
        self.continue_moveset = None
        self.reach_camera_event = {}

        self.specific_animation_done = empty_method
        self.specific_special_check = empty_method
        self.specific_update = empty_method
        self.specific_status_update = empty_method
        self.special_damage = empty_method

        self.position = "Stand"
        self.combat_state = "City"
        self.mode = "City"
        self.just_change_mode = False
        self.equipped_weapon = "Preset"
        self.special_combat_state = 0
        self.mode_list = stat["Mode"]
        self.team = stat["Team"]

        # Variable related to sprite
        self.body_size = int(stat["Size"] / 10)
        if self.body_size < 1:
            self.body_size = 1
        self.sprite_size = stat["Size"] * 10 * self.screen_scale[
            1]  # use for pseudo sprite size of character for positioning of effect
        self.sprite_height = (100 + stat["Size"]) * self.screen_scale[1]
        self.arrive_condition = stat["Arrive Condition"]

        self.city_walk_speed = 500  # movement speed in city, not affected by anything
        self.ground_pos = self.base_ground_pos
        self.y_momentum = 0
        self.x_momentum = 0

        self.base_animation_play_time = self.default_animation_play_time
        self.animation_play_time = self.base_animation_play_time
        self.final_animation_play_time = self.animation_play_time

        self.fall_gravity = self.battle.base_fall_gravity
        self.angle = -90
        if "Angle" in stat:
            self.angle = stat["Angle"]
        self.new_angle = self.angle
        self.radians_angle = radians(360 - self.angle)  # radians for apply angle to position
        self.run_direction = 0  # direction check to prevent character able to run in opposite direction right away
        self.sprite_direction = rotation_dict[min(rotation_list,
                                                  key=lambda x: abs(
                                                      x - self.angle))]  # find closest in list of rotation for sprite direction

        self.char_id = str(stat["ID"])
        self.sprite_ver = str(stat["Sprite Ver"])
        if "Only Sprite Version" in stat and stat["Only Sprite Version"]:  # data suggest only one sprite version exist
            self.sprite_ver = str(stat["Only Sprite Version"])

        self.command_pos = Vector2(0, 0)

        if "Scene" in stat:  # data with scene positioning
            self.base_pos = Vector2(stat["POS"][0] + (1920 * (stat["Scene"] - 1)),
                                    stat["POS"][1])  # true position of character in battle
        else:  # character with no scene position data such as summon
            self.base_pos = Vector2(stat["POS"])  # true position of character in battle

        self.last_pos = None  # may be used by AI or specific character update check for position change
        self.pos = Vector2((self.base_pos[0] * self.screen_scale[0],
                            self.base_pos[1] * self.screen_scale[1]))
        self.cutscene_target_pos = None

        self.body_parts = {}

        for p in ("p1", "p2", "p3", "p4"):
            self.body_parts |= {p + "_head": None, p + "_neck": None, p + "_body": None,
                                p + "_r_arm_up": None, p + "_r_arm_low": None, p + "_r_hand": None,
                                p + "_l_arm_up": None, p + "_l_arm_low": None, p + "_l_hand": None,
                                p + "_r_leg_up": None, p + "_r_leg_low": None, p + "_r_foot": None,
                                p + "_l_leg_up": None, p + "_l_leg_low": None, p + "_l_foot": None,
                                p + "_main_weapon": None, p + "_sub_weapon": None,
                                p + "_special_1": None, p + "_special_2": None, p + "_special_3": None,
                                p + "_special_4": None, p + "_special_5": None, p + "_special_6": None,
                                p + "_special_7": None, p + "_special_8": None, p + "_special_9": None,
                                p + "_special_10": None}

        self.retreat_stage_end = self.battle.base_stage_end + self.sprite_size
        self.retreat_stage_start = -self.sprite_size

    def update(self, dt):
        self.ai_update(dt)

        if self.angle != self.new_angle:  # Rotate Function
            self.rotate_logic()
        self.move_logic(dt)  # Move function
        hold_check = self.check_action_hold(dt)
        done = self.play_animation(dt, hold_check)
        self.check_new_animation(done)

    @staticmethod
    def inactive_update(*args):
        pass

    def cutscene_update(self, dt):
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

                for part in self.body_parts.values():
                    part.re_rect()

        if self.alive or self.cutscene_event:  # only play animation for alive char or have event
            hold_check = False
            if ("hold" in self.current_animation_direction[self.show_frame][
                "property"] and "hold" in self.current_action) or \
                    not self.max_show_frame:
                hold_check = True
            done = self.play_cutscene_animation(dt, hold_check)
            if done or (self.cutscene_target_pos and self.cutscene_target_pos == self.base_pos):
                if done:
                    self.start_animation_body_part()
                    if self.cutscene_event and "die" in self.cutscene_event["Property"]:  # die animation
                        self.battle.cutscene_playing.remove(self.cutscene_event)
                        self.cutscene_target_pos = None
                        self.current_action = {}
                        self.cutscene_event = None
                        self.show_frame = self.max_show_frame
                        self.max_show_frame = 0  # reset max_show_frame to 0 to prevent restarting animation
                        self.start_animation_body_part()  # revert previous show_frame 0 animation start
                        return
                if self.current_action and ((self.cutscene_target_pos and self.cutscene_target_pos == self.base_pos) or \
                        (not self.cutscene_target_pos and "repeat" not in self.current_action and
                         "repeat after" not in self.current_action)):
                    # animation consider finish when reach target or finish animation with no repeat, pick idle animation
                    self.current_action = {}
                    self.pick_cutscene_animation({})
                if self.cutscene_event and "repeat" not in self.cutscene_event["Property"] and \
                        "interact" not in self.cutscene_event["Property"] and \
                        (not self.cutscene_target_pos or self.cutscene_target_pos == self.base_pos):
                    # finish animation, consider event done unless event require player interaction first or in repeat
                    self.cutscene_target_pos = None
                    if "repeat after" not in self.cutscene_event["Property"]:
                        if self.current_action:
                            self.current_action = {}
                            self.pick_cutscene_animation({})
                        self.command_action = {}
                    else:  # event indicate repeat animation after event end
                        self.current_action["repeat"] = True
                        if not self.alive:
                            self.current_action["die"] = True
                    if self.cutscene_event in self.battle.cutscene_playing:
                        self.battle.cutscene_playing.remove(self.cutscene_event)
                    self.cutscene_event = None

    def ai_update(self, dt):
        pass


class BattleCharacter(Character):
    # static variable
    knock_down_sound_distance = 1500
    knock_down_screen_shake = 15
    heavy_dmg_sound_distance = 100
    heavy_dmg_screen_shake = 7
    dmg_sound_distance = 80
    dmg_screen_shake = 2

    def __init__(self, game_id, layer_id, stat, player_control=False, leader=None, team_scaling=1):
        """
        BattleCharacter object represent a character that take part in the battle in stage
        Character has three different stage of stat;
        first: base stat (e.g., base_attack), this is their stat before and after calculating equipment
        second: stat with all effect (e.g., attack), this is their stat after calculating weather, and status effect

        Character can be a player, friendly AI, or enemy
        """
        Character.__init__(self, game_id, layer_id, stat, player_control=player_control)
        self.leader = leader

        self.moveset_command_key_input = ()

        self.enemy_list = self.battle.all_team_enemy[self.team]
        self.enemy_part_list = self.battle.all_team_enemy_part[self.team]
        self.ally_list = self.battle.all_team_character[self.team]
        self.near_ally = []
        self.near_enemy = []
        self.nearest_enemy = None
        self.nearest_enemy_distance = None
        self.nearest_ally = None
        self.nearest_ally_distance = None

        self.no_forced_move = False
        self.delete_death = False
        self.immune_weather = False
        self.hit_resource_regen = False
        self.crash_guard_resource_regen = False
        self.crash_haste = False
        self.slide_attack = False
        self.tackle_attack = False
        self.health_as_resource = False
        self.moveset_reset_when_relax_only = False
        self.money_score = False
        self.money_resource = False
        self.item_free_use_chance = False
        self.free_first_item_use = False
        self.combat_state = "Peace"
        self.mode = "Normal"
        self.stop_fall_duration = 0
        self.in_combat_timer = 0

        self.stun_threshold = 0
        self.stun_value = 0
        self.move_speed = 0  # speed of current movement

        self.resurrect_count = 0
        self.guarding = 0
        self.hold_power_bonus = 1
        self.attack_cooldown = {}  # character can attack with weapon only when cooldown reach attack speed
        self.gold_drop_modifier = 1
        self.status_effect = {}  # current status effect
        self.status_applier = {}
        self.status_duration = {}  # current status duration

        # find and set method specific to character
        if self.char_id in initiate_dict:
            initiate_dict[self.char_id](self)
        if self.char_id in animation_start_dict:
            self.specific_animation_done = MethodType(animation_start_dict[self.char_id], self)
        if self.char_id in special_dict:
            self.specific_special_check = MethodType(special_dict[self.char_id], self)
        if self.char_id in update_dict:
            self.specific_update = MethodType(update_dict[self.char_id], self)
        if self.char_id in status_update_dict:
            self.specific_status_update = MethodType(status_update_dict[self.char_id], self)
        if self.char_id in damage_dict:
            self.special_damage = MethodType(damage_dict[self.char_id], self)

        if self.battle.stage == "training":  # replace moveset check with training one
            self.battle_check_move_existence = self.check_move_existence
            self.check_move_existence = self.training_moveset_existence_check

        # Get char stat
        stat_boost = 0
        leader_charisma = 0
        if self.leader:  # character with leader get stat boost from leader charisma
            leader_charisma = self.leader.charisma
            stat_boost = int(leader_charisma / 5)
        self.strength = stat["Strength"] + (stat["Strength"] * (leader_charisma / 200)) + stat_boost
        self.dexterity = stat["Dexterity"] + (stat["Dexterity"] * (leader_charisma / 200)) + stat_boost
        self.agility = stat["Agility"] + (stat["Agility"] * (leader_charisma / 200)) + stat_boost
        self.constitution = stat["Constitution"] + (stat["Constitution"] * (leader_charisma / 200)) + stat_boost
        self.intelligence = stat["Intelligence"] + (stat["Intelligence"] * (leader_charisma / 200)) + stat_boost
        self.wisdom = stat["Wisdom"] + (stat["Wisdom"] * (leader_charisma / 200)) + stat_boost
        self.charisma = stat["Charisma"] + (stat["Charisma"] * (leader_charisma / 200)) + stat_boost

        self.moveset = deepcopy(stat["Move"])
        self.moveset_view = ()  # get add later in enter_stage
        self.skill = stat["Skill"].copy()
        self.available_skill = {"Couch": {}, "Stand": {}, "Air": {}}
        if "Drops" in stat and stat["Drops"]:  # add item drops when die, only add for character with drops data
            self.drops = stat["Drops"]

            for key, value in self.default_item_drop_table.items():  # add drop from common drop table
                if value > uniform(0, 100):  # random chance to be added
                    if key in self.drops:  # add chance to already exiting item
                        self.drops[key] += value
                    else:
                        self.drops[key] = value

            for key, value in self.special_character_drop_table.items():
                if key in self.battle.existing_playable_characters:
                    for key2, value2 in value.items():  # add drop item if playable character in battle
                        if key2 in self.drops:  # add chance to already exiting item
                            self.drops[key2] += value2
                        else:
                            self.drops[key2] = value2
        if "Spawns" in stat:  # add item drops when die, only add for character with drops data
            self.spawns = stat["Spawns"]

        self.score = 0  # character score for team when killed
        if "Score" in stat:
            self.score = stat["Score"]

        if "skill allocation" in stat:  # refind leveled skill allocated since name is only from first level
            for position_name, position in self.skill.items():
                for skill in tuple(position.keys()):
                    if position[skill]["Name"] in stat["skill allocation"] and \
                            stat["skill allocation"][position[skill]["Name"]]:
                        skill_id = skill[:3] + str(stat["skill allocation"][position[skill]["Name"]])
                        self.available_skill[position_name][skill_id] = position[skill_id]
        else:  # all skill available
            for position_name, position in self.skill.items():
                for skill in tuple(position.keys()):
                    self.available_skill[position_name][skill] = position[skill]

        self.remove_moveset_not_match_stat_requirement()

        for position in ("Couch", "Stand", "Air"):  # combine skill into moveset
            if position in self.skill:
                if position not in self.moveset:  # add position with no move
                    self.moveset[position] = {}

                # skill with no requirement move, not count skill with all child moveset
                button_key_skill_dict = {value["Buttons"]: {"Move": key} | value for key, value in
                                         self.available_skill[position].items() if
                                         "Requirement Move" not in value or not value["Requirement Move"]}

                for key, value in self.available_skill[position].items():  # check for skill with requirement move
                    if ("Requirement Move" in value and value["Requirement Move"]) or \
                            "all child moveset" in value["Property"]:
                        # add to parent moveset, all child moveset not count skill as parent move
                        skill_data_dict = {"Move": key} | {key2: value2 for key2, value2 in value.items()}
                        if "all child moveset" in value["Property"]:
                            parent_move_list = [key for key in stat["Move Original"][value["Position"]]]
                        else:
                            parent_move_list = value["Requirement Move"]
                        for parent_move in parent_move_list:
                            final_parent_moveset(self.moveset[position], value["Buttons"], skill_data_dict,
                                                 parent_move, [False], [])

                self.moveset[position] = button_key_skill_dict | self.moveset[position]
            already_check = []
            if position in self.moveset:
                for move in self.moveset[
                    position]:  # final rearrange of moveset to make complex button move first in listd
                    recursive_rearrange_moveset(self.moveset[position][move], already_check)

        self.max_physical = 1 + (self.strength / 50) + (self.wisdom / 200)
        self.min_physical = self.dexterity / 100

        self.max_elemental = 1 + (self.intelligence / 50) + (self.wisdom / 200)
        self.min_elemental = self.wisdom / 100

        self.item_carry_bonus = (self.strength / 25) + (self.wisdom / 50)

        self.base_health = int((stat["Base Health"] + (
                stat["Base Health"] * (self.constitution / 20))) * team_scaling)  # max health of character
        self.base_resource = int(stat["Max Resource"] + (stat["Max Resource"] * self.intelligence / 100))

        self.base_power_bonus = 0
        self.base_impact_modifier = 1  # extra impact for weapon attack
        self.base_critical_chance = int((self.dexterity / 500) + (self.wisdom / 1000))
        self.base_cast_speed = 1 / (1 + ((self.dexterity + self.intelligence) / 200))

        self.base_defence = ((self.agility / 20) + (self.constitution / 10) + (self.wisdom / 30)) / 100
        self.base_guard = 10 * self.constitution
        self.base_super_armour = self.constitution
        self.base_element_resistance = {key.split(" ")[0]: stat[key] for key in stat if " Resistance" in key}

        self.base_hp_regen = 0  # health regeneration modifier, will not resurrect dead char by default
        self.base_resource_regen = 0  # resource regeneration modifier
        self.item_effect_modifier = 1
        self.debuff_duration_modifier = 1
        self.buff_duration_modifier = 1

        self.base_animation_play_time = self.default_animation_play_time / (
                1 + (self.agility / 100))  # higher value mean longer play time
        self.base_speed = self.agility * 2
        self.base_dodge = (self.agility / 500) + (self.wisdom / 1000)

        self.base_resource_cost_modifier = 1
        self.base_guard_cost_modifier = 1

        # initiate equipment stat
        self.weight = 0

        # 17 stun, 18 poison, 20 burn, 21 freeze, 22 shock, 27 slow, 32 bleed, 96 curse
        self.attack_status_chance = {17: 0, 18: 0, 20: 0, 21: 0, 22: 0, 27: 0, 32: 0, 96: 0}
        self.attack_element = None  # all attack become specific element
        self.attack_penetrate = False
        self.attack_no_defence = False
        self.attack_no_guard = False
        self.attack_no_dodge = False

        if self.player_control:  # add equipment stat only for player character
            status_name = {"stun": 17, "poison": 18, "burn": 20, "freeze": 21, "shock": 22,
                           "slow": 27, "bleed": 32, "curse": 96}
            equipment = self.battle.all_story_profiles[int(self.game_id[1])]["equipment"]  # player game id in p+number
            for equip_slot in equipment:
                if equip_slot != "item":
                    if equipment[equip_slot] in self.battle.character_data.gear_list:
                        equip_stat = self.battle.character_data.gear_list[equipment[equip_slot]]
                    else:
                        equip_stat = equipment[equip_slot]
                    if equip_stat:
                        for mod, value in dict(equip_stat["Modifier"]).items():
                            if "_resist" in mod:
                                self.base_element_resistance[mod.split("_")[0].capitalize()] += value
                            elif "_chance" in mod:
                                self.attack_status_chance[status_name[mod.split("_")[0]]] += value
                            elif "attack_element_" in mod:
                                self.attack_element = mod.split("_")[-1].capitalize()
                            elif hasattr(self, mod):
                                if isinstance(value, (int, float)):
                                    # dynamically add mod value to stat
                                    exec(f"self.{mod} += value")
                                else:
                                    exec(f"self.{mod} = TRUE")
                        self.weight += equip_stat["Weight"]
            self.items = self.battle.all_story_profiles[int(self.game_id[1])]["equipment"]["item"]
            self.item_usage = {value: int(self.character_data.equip_item_list[value]["Capacity"] +
                                          (self.character_data.equip_item_list[value][
                                               "Capacity"] * self.item_carry_bonus))
                               for value in self.items.values() if value}
        else:
            self.item_usage = stat["Items"]

        self.attack_status_chance = {key: value for key, value in self.attack_status_chance.items() if value}
        self.body_mass = (stat["Size"] + self.weight) * 10
        self.base_dodge -= (self.weight / 1000)
        self.base_speed -= self.weight  # reduce speed with weight
        self.jump_power = 200 - self.weight
        if self.jump_power < 1:
            self.jump_power = 1

        # Final stat after receiving stat effect from various sources, reset every time status is updated
        self.power_bonus = self.base_power_bonus
        self.impact_modifier = self.base_impact_modifier
        self.critical_chance = self.base_critical_chance
        self.defence = self.base_defence
        self.super_armour = self.base_super_armour
        self.dodge = self.base_dodge
        self.element_resistance = self.base_element_resistance.copy()
        self.speed = self.base_speed
        self.hp_regen = self.base_hp_regen
        self.resource_regen = self.base_resource_regen
        self.animation_play_time = self.base_animation_play_time
        self.final_animation_play_time = self.animation_play_time
        self.guard = int(self.base_guard)
        self.max_guard = self.guard
        self.guard_meter20 = self.guard * 0.2
        self.guard_meter5 = self.guard * 0.05

        self.guard_cost_modifier = self.base_guard_cost_modifier
        self.resource_cost_modifier = self.base_resource_cost_modifier

        start_health = 1
        if "Start Health" in stat:
            start_health = stat["Start Health"]
        start_resource = 1
        if "Start Resource" in stat:
            start_resource = stat["Start Resource"]
        self.health = self.base_health * start_health
        self.resource05 = self.base_resource * 0.005
        self.resource1 = self.base_resource * 0.01
        self.resource2 = self.base_resource * 0.02
        self.resource10 = self.base_resource * 0.10
        self.resource25 = self.base_resource * 0.25
        self.resource50 = self.base_resource * 0.5
        self.resource75 = self.base_resource * 0.75
        self.resource = self.base_resource * start_resource

        self.run_speed = 600 + self.speed
        self.walk_speed = 350 + self.speed

        # Variables related to sound
        self.knock_down_sound_distance = self.knock_down_sound_distance + self.body_mass
        self.knock_down_screen_shake = self.knock_down_screen_shake + self.body_mass
        self.heavy_dmg_sound_distance = self.heavy_dmg_sound_distance + self.body_mass
        self.dmg_sound_distance = self.dmg_sound_distance + self.body_mass

        self.hit_volume_mod = self.body_mass / 10

    def update(self, dt):
        """Character update, run when cutscene not playing"""
        if self.health:  # only run these when not dead
            if dt:  # only run these when game not pause
                self.timer += dt

                if 0 < self.guarding < 1:
                    self.guarding += dt

                elif not self.guarding and self.guard < self.max_guard:
                    # replenish guard meter when not guarding, always 5 percent per second
                    self.guard += dt * self.guard_meter5
                    if self.guard > self.max_guard:
                        self.guard = self.max_guard

                if self.freeze_timer:
                    self.freeze_timer -= dt
                    if self.freeze_timer < 0:
                        self.freeze_timer = 0

                if self.stop_fall_duration:
                    self.stop_fall_duration -= dt
                    if self.stop_fall_duration < 0:
                        self.stop_fall_duration = 0

                self.ai_update(dt)

                if self.angle != self.new_angle:  # Rotate Function
                    self.rotate_logic()
                self.move_logic(dt)  # Move function

                if self.timer > 0.1:  # Update status and skill, every 1 second
                    if self.combat_state == "Combat" and self.position == "Stand":
                        self.in_combat_timer -= self.timer
                        if self.in_combat_timer <= 0:
                            if not self.current_action and not self.command_action:
                                # Idle in combat state go to peace state instead
                                self.in_combat_timer = 0
                                self.combat_state = "Peace"
                                self.command_action = self.relax_command_action
                                if self.special_combat_state:  # special relax state
                                    self.command_action = self.special_relax_command[self.special_combat_state]
                                    self.special_combat_state = 0
                            else:
                                self.in_combat_timer = 3

                    self.nearest_enemy = None
                    self.nearest_enemy_distance = None
                    self.nearest_ally = None
                    self.nearest_ally_distance = None
                    self.near_enemy = sorted({key: key.base_pos.distance_to(self.base_pos) for key in
                                              self.enemy_list}.items(),
                                             key=lambda item: item[1])  # sort the closest enemy
                    self.near_ally = sorted(
                        {key: key.base_pos.distance_to(self.base_pos) for key in self.ally_list}.items(),
                        key=lambda item: item[1])  # sort the closest friend
                    if self.near_enemy:
                        self.nearest_enemy = self.near_enemy[0][0]
                        self.nearest_enemy_distance = self.near_enemy[0][1]
                    if self.near_ally:
                        self.nearest_ally = self.near_ally[0][0]
                        self.nearest_ally_distance = self.near_ally[0][1]

                    if not self.invincible:
                        self.status_update()
                    self.specific_status_update()
                    self.timer -= 0.1

                    self.health_resource_logic(dt)
                    self.specific_update(dt)

                # Animation and sprite system
                if self.show_frame >= len(self.current_animation_direction):  # TODO remove when really fixed
                    print(self.name, self.show_frame, self.max_show_frame, self.current_animation, self.current_action)
                    print(self.current_animation_direction)
                    raise Exception()

                hold_check = self.check_action_hold(dt)

                done = self.play_animation(dt, hold_check)
                self.check_new_animation(done)

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

                if self.broken and (self.retreat_stage_end + self.sprite_size <= self.base_pos[0] or
                                    self.base_pos[0] <= self.retreat_stage_start):
                    self.alive = False  # remove character that pass stage border, enter dead state
                    self.health = 0
                    self.die(delete=True)

        else:  # die
            if self.alive:  # enter dead state
                self.attack_cooldown = {}  # remove all cooldown
                self.status_effect = {}
                self.status_duration = {}
                self.status_applier = {}
                self.alive = False  # enter dead state
                self.engage_combat()
                self.current_action = self.die_command_action
                self.stop_fall_duration = 0
                self.show_frame = 0
                self.frame_timer = 0
                self.pick_animation()

            if "die" in self.current_action:
                if self.show_frame < self.max_show_frame or self.x_momentum or self.y_momentum or \
                        "repeat" in self.current_action:  # play die animation
                    self.move_logic(dt)
                    hold_check = False
                    if self.x_momentum or self.y_momentum:  # keep holding while moving
                        hold_check = True
                    self.play_animation(dt, hold_check)
                else:  # finish die animation and reach ground
                    if self.resurrect_count:  # resurrect back
                        # self.resurrect_count -= 1
                        self.interrupt_animation = True
                        self.alive = True
                        self.command_action = self.standup_command_action
                        self.health = self.base_health
                    else:  # permanent death
                        if self.is_summon or self.delete_death:  # summon character does not leave corpse
                            self.die(delete=True)
                        else:
                            self.die()


class PlayerCharacter(BattleCharacter, Character):
    command_list = {"Down": "Attack", "Left": "Free", "Up": "Follow", "Right": "Stay"}
    command_name_list = tuple(command_list.values())

    def __init__(self, game_id, layer_id, stat):
        if self.battle.city_mode:
            Character.__init__(self, game_id, layer_id, stat, player_control=True)
            self.update = MethodType(Character.update, self)
            self.player_input = self.player_input_city_mode
        else:
            BattleCharacter.__init__(self, game_id, layer_id, stat, player_control=True)
            self.player_input = self.player_input_battle_mode

            common_skill = ("Ground Movement", "Air Movement", "Tinkerer", "Arm Mastery", "Wealth",
                            "Immunity", "Resourceful", "Combat Contest")

            self.common_skill = {skill: {1: False, 2: False, 3: False, 4: False, 5: False} for skill in common_skill}
            for skill in common_skill:
                if stat["skill allocation"][skill]:
                    for level in range(int(stat["skill allocation"][skill] + 1)):
                        self.common_skill[skill][level] = True

            self.slide_attack = False
            self.tackle_attack = False
            self.dash_move = False
            self.dodge_move = False
            if self.common_skill["Ground Movement"][1]:  # can slide attack
                self.slide_attack = True
                self.moveset["Stand"] |= {key: value for key, value in
                                          self.character_data.common_moveset_skill["Stand"].items() if key == "Slide"}
            if self.common_skill["Ground Movement"][2]:  # can tackle attack
                self.tackle_attack = True
                self.moveset["Stand"] |= {key: value for key, value in
                                          self.character_data.common_moveset_skill["Stand"].items() if key == "Tackle"}
            if self.common_skill["Ground Movement"][3]:  # can dash after attack
                self.dash_move = True
            if self.common_skill["Ground Movement"][4]:  # weight no longer affect movement speed
                self.base_speed += self.weight
            if self.common_skill["Ground Movement"][5]:  # can perform dodge move while moving
                self.dodge_move = True

            self.can_double_jump = False
            self.air_dash_move = False
            self.unlimited_jump = False
            self.double_jump = False
            self.double_air_impact_resistance = False
            self.hover = False

            if self.common_skill["Air Movement"][1]:  # can double jump
                self.double_jump = True
            if self.common_skill["Air Movement"][2]:  # can dash midair
                self.air_dash_move = True
            if self.common_skill["Air Movement"][3]:  # weight no longer affect jump power
                self.jump_power = 200
            if self.common_skill["Air Movement"][4]:  # increase impact resistant while in air position
                self.double_air_impact_resistance = True
            if self.common_skill["Air Movement"][1]:  # can hover in air
                self.hover = True

            self.item_free_use_chance = False
            self.unlock_secret_food_effect = False
            self.free_first_item_use = False
            if self.common_skill["Tinkerer"][1]:  # item have 30% chance to be used for free
                self.item_free_use_chance = True
            if self.common_skill["Tinkerer"][2]:  # first item use is 100% free
                self.free_first_item_use = True
            if self.common_skill["Tinkerer"][3]:  # item has double effect
                self.item_effect_modifier = 2
            if self.common_skill["Tinkerer"][4]:  # feast provide more effects
                self.unlock_secret_food_effect = True
            if self.common_skill["Tinkerer"][5]:  # can use summon drop skill
                pass

            self.double_pickup_usage = False
            if self.common_skill["Arm Mastery"][1]:  # pick-up weapon has double usage
                pass
            if self.common_skill["Arm Mastery"][2]:  # increase more pick-up weapon usage
                self.double_pickup_usage = True
            if self.common_skill["Arm Mastery"][3]:  # food has double effect
                pass
            if self.common_skill["Arm Mastery"][4]:  # can slide attack
                pass
            if self.common_skill["Arm Mastery"][5]:  # can slide attack
                pass

            self.money_score = False
            self.money_resource = False
            if self.common_skill["Wealth"][1]:  # money drop also increase mission score
                self.money_score = True
            if self.common_skill["Wealth"][2]:  # money drop also increase resource
                self.money_resource = True
            if self.common_skill["Wealth"][3]:  # increase gold from drop by 100%
                self.gold_drop_modifier += 1
            if self.common_skill["Wealth"][4]:  #
                pass
            if self.common_skill["Wealth"][5]:  #
                pass

            self.knock_recover = False
            self.immune_weather = False
            if self.common_skill["Immunity"][1]:  # can recover from knockdown with guard action
                self.knock_recover = True
            if self.common_skill["Immunity"][2]:  # shorten all debuff duration by half
                self.debuff_duration_modifier -= 0.5
            if self.common_skill["Immunity"][3]:  # increase resurrection count by 2
                self.resurrect_count += 2
            if self.common_skill["Immunity"][4]:  # immune to weather effect
                self.immune_weather = True
            if self.common_skill["Immunity"][5]:  # unlock immune barrier skill
                pass

            self.hit_resource_regen = False
            self.crash_guard_resource_regen = False
            if self.common_skill["Resourceful"][1]:  # add resource regen 0.5% per second
                self.base_resource_regen += self.base_resource * 0.005
            if self.common_skill["Resourceful"][2]:  # resource regen when hit enemy
                self.hit_resource_regen = True
            if self.common_skill["Resourceful"][3]:  # resource regen when crash and guard
                self.crash_guard_resource_regen = True
            if self.common_skill["Resourceful"][4]:  # double max resource, and auto regen to 1% per second
                self.base_resource += self.base_resource
                self.resource1 = self.base_resource * 0.01
                self.resource2 = self.base_resource * 0.02
                self.resource10 = self.base_resource * 0.10
                self.resource25 = self.base_resource * 0.25
                self.resource50 = self.base_resource * 0.5
                self.resource75 = self.base_resource * 0.75
                self.base_resource_regen += self.base_resource * 0.01
            if self.common_skill["Resourceful"][5]:
                pass

            self.guard_move = False
            self.crash_haste = False
            if self.common_skill["Combat Contest"][1]:  # increase max guard
                self.guard_meter = int(self.base_guard * 1.5)
                self.max_guard = self.guard_meter
                self.guard_meter20 = self.guard_meter * 0.2
                self.guard_meter5 = self.guard_meter * 0.05
            if self.common_skill["Combat Contest"][2]:  # can walk while guarding
                self.guard_move = True
            if self.common_skill["Combat Contest"][3]:  # guard cost half by default
                self.base_guard_cost_modifier -= 0.5
            if self.common_skill["Combat Contest"][4]:  # crash now give haste status
                self.crash_haste = True
            if self.common_skill["Combat Contest"][5]:  #
                pass

        self.command_key_input = []
        self.command_key_hold = None
        self.last_command_key_input = None
        self.input_mode = None

        self.indicator = CharacterIndicator(self)
        self.player_command_key_input = []
        self.player_key_input_timer = []
        self.player_key_hold_timer = {}
        self.resurrect_count = 2

        self.enter_stage(self.battle.character_animation_data)


class AICharacter(BattleCharacter, Character):
    def __init__(self, game_id, layer_id, stat, leader=None, team_scaling=1, specific_behaviour=None):
        if self.battle.city_mode:
            Character.__init__(self, game_id, layer_id, stat)
            self.update = MethodType(Character.update, self)
            ai_behaviour = "idle_city_ai"
            if specific_behaviour:
                ai_behaviour = specific_behaviour

            self.ai_move = ai_move_dict["default"]
            if ai_behaviour in ai_move_dict:
                self.ai_move = ai_move_dict[ai_behaviour]

            self.ai_combat = ai_combat_dict["default"]
            if ai_behaviour in ai_combat_dict:
                self.ai_combat = ai_combat_dict[ai_behaviour]

            self.city_walk_speed = 100
        else:
            BattleCharacter.__init__(self, game_id, layer_id, stat, leader=leader, team_scaling=team_scaling)

        self.ai_lock = True  # lock AI from activity when start battle, and it positions outside of scene lock
        self.event_ai_lock = False  # lock AI until event unlock it only

        if "Ground Y POS" in stat and stat["Ground Y POS"]:  # replace ground pos based on data in stage
            self.ground_pos = stat["Ground Y POS"]

        char_property = {}
        if "Property" in stat:
            char_property = {key: True for key in stat["Property"]}  # convert to dict first to combine with stage prop
        if "Stage Property" in stat:
            char_property |= stat["Stage Property"]
        for stuff in char_property:  # set attribute from property
            if stuff == "target":
                if type(char_property["target"]) is int:  # target is AI
                    target = char_property["target"]
                else:  # target is player
                    target = char_property["target"][-1]

                for this_char in self.battle.all_chars:
                    if target == this_char.game_id:  # find target char object
                        self.target = this_char
                        break
            elif stuff == "leader":  # find leader
                for char in self.battle.all_chars:
                    if char.game_id == char_property["leader"]:
                        self.leader = char
                        self.leader.followers.append(self)
                        break
            elif stuff == "idle":  # replace idle animation
                self.replace_idle_animation = char_property["idle"]
            else:
                self.__setattr__(stuff, char_property[stuff])

        self.ai_timer = 0  # for whatever timer require for AI action
        self.ai_movement_timer = 0  # timer to move for AI
        self.ai_attack_timer = 0  # timer to attack for AI
        self.end_ai_movement_timer = uniform(2, 6)

        self.enter_stage(self.battle.character_animation_data)

    def ai_update(self, dt):
        if self.ai_timer:
            self.ai_timer += dt
        if self.ai_movement_timer:
            self.ai_movement_timer -= dt
            if self.ai_movement_timer < 0:
                self.ai_movement_timer = 0
        self.ai_combat(self)
        self.ai_move(self)


class BattleAICharacter(AICharacter):
    def __init__(self, game_id, layer_id, stat, leader=None, specific_behaviour=None, team_scaling=1):
        AICharacter.__init__(self, game_id, layer_id, stat, leader=leader, team_scaling=team_scaling)

        self.old_cursor_pos = None
        self.is_boss = stat["Boss"]
        self.is_summon = stat["Summon"]
        self.follow_command = "Free"
        if self.is_boss:
            self.stun_threshold = self.base_health
        if self.is_summon:
            self.health_as_resource = True  # each time summon use resource it uses health instead
        if leader:
            self.follow_command = "Follow"
            if leader.player_control:  # only add indicator for player's follower
                self.indicator = CharacterIndicator(self)
            leader.followers.append(self)
            self.item_effect_modifier = leader.item_effect_modifier  # use leader item effect modifier
            self.gold_pickup_modifier = leader.gold_drop_modifier
        if "Ground Y POS" in stat and stat["Ground Y POS"]:  # replace ground pos based on data in stage
            self.ground_pos = stat["Ground Y POS"]

        ai_behaviour = stat["AI Behaviour"]
        if specific_behaviour:
            ai_behaviour = specific_behaviour

        self.ai_move = MethodType(ai_move_dict["default"], self)
        if (leader or self.leader) and not self.is_summon:  # summon use assigned behaviour in data instead of follower by default
            self.ai_move = MethodType(ai_move_dict["follower"], self)
        elif ai_behaviour in ai_move_dict:
            self.ai_move = MethodType(ai_move_dict[ai_behaviour], self)

        self.ai_combat = MethodType(ai_combat_dict["default"], self)
        if ai_behaviour in ai_combat_dict:
            self.ai_combat = MethodType(ai_combat_dict[ai_behaviour], self)

        self.ai_retreat = MethodType(ai_retreat_dict["default"], self)
        if ai_behaviour in ai_retreat_dict:
            self.ai_retreat = MethodType(ai_retreat_dict[ai_behaviour], self)

        self.ai_max_attack_range = 0
        self.ai_timer = 0  # for whatever timer require for AI action
        self.ai_movement_timer = 0  # timer to move for AI
        for position in self.moveset.values():
            for move in position.values():
                if "no max ai range" not in move["Property"] and self.ai_max_attack_range < move["AI Range"]:
                    self.ai_max_attack_range = move["AI Range"]

        self.resurrect_count = 0

    def ai_update(self, dt):
        if self.ai_lock and not self.event_ai_lock and self.battle.base_stage_end >= self.base_pos[0] >= self.battle.base_stage_start:
            # unlock once in active scene
            self.ai_lock = False
        if not self.ai_lock:
            if not self.broken:
                if self.ai_timer:
                    self.ai_timer += dt
                if self.ai_movement_timer:
                    self.ai_movement_timer -= dt
                    if self.ai_movement_timer < 0:
                        self.ai_movement_timer = 0
                if self.ai_attack_timer:
                    self.ai_attack_timer -= dt
                    if self.ai_attack_timer < 0:
                        self.ai_attack_timer = 0
                self.ai_combat()
                self.ai_move()
            else:
                self.ai_retreat()


class BodyPart(sprite.Sprite):
    battle = None
    body_sprite_pool = None
    empty_surface = pygame.Surface((0, 0))

    from engine.character.drop_collide_check import drop_collide_check

    from engine.effect.hit_collide_check import hit_collide_check
    hit_collide_check = hit_collide_check

    from engine.effect.hit_register import hit_register
    hit_register = hit_register

    from engine.effect.cal_dmg import cal_dmg
    cal_dmg = cal_dmg

    def __init__(self, owner, part, can_hurt=True):
        self.screen_scale = self.battle.screen_scale
        self.battle_camera = self.battle.battle_camera
        self.owner = owner
        self.team = self.owner.team
        self.owner_layer = 0
        self.dead_layer = 0
        self.angle = self.owner.angle
        self.invincible = self.owner.invincible
        self._layer = 10
        sprite.Sprite.__init__(self, self.containers)
        self.base_image_update_contains = []  # object that need updating when base_image get updated
        self.part = part
        self.part_name = self.part[3:]
        if self.part_name[0:2] == "l_" or self.part_name[0:2] == "r_":
            self.part_name = self.part_name[2:]
        if "special" in self.part:
            self.part = "_".join(self.part.split("_")[:-1])
        self.can_hurt = can_hurt
        self.can_deal_dmg = False
        self.dmg = None
        self.impact_sum = 0
        self.object_type = "body"
        self.no_dodge = False
        self.no_defence = False
        self.no_guard = False
        self.friend_status_effect = ()
        self.enemy_status_effect = ()
        self.impact = (0, 0)
        self.element = None
        self.critical_chance = 0
        self.mode = "Normal"
        self.already_hit = []
        self.base_image = self.empty_surface
        self.image = self.empty_surface
        self.data = ()  # index 1=part name, 2and3=pos xy, 4=angle, 5=flip, 6=layer , 7=scale, 8=deal damage or not
        self.sprite_ver = str(self.owner.sprite_ver)
        self.rect = self.image.get_rect(topleft=(0, 0))
        self.mask = from_surface(self.image)

        # Variables not really used or changed but required for same functions as Effect
        self.aoe = False
        self.duration = 0
        self.stick_reach = False  # not used for body parts but require for checking
        self.stick_timer = 0  # not used but require for checking
        self.penetrate = True  # part always penetrate if doing dmg

    def get_part(self, data, new_animation):
        self.dmg = 0
        self.impact_sum = 0
        self.can_deal_dmg = False
        self.angle = self.owner.angle
        self.mode = self.owner.mode_list[self.owner.mode][self.part]
        self.friend_status_effect = ()
        self.enemy_status_effect = ()
        if new_animation:
            self.already_hit = []
        elif self.owner.current_moveset and "multiple hits" in self.owner.current_moveset["Property"]:
            # multiple hits moveset reset already hit every frame instead of just when finish animation
            self.already_hit = []

        if data[8] and not self.battle.cutscene_playing:  # can do dmg, no check while in cutscene mode
            self.can_deal_dmg = True
            find_damage(self)
        if self.data != data or self.owner.just_change_mode:
            self.data = data
            sprite_type = self.data[0]
            sprite_name = self.data[1]
            if "weapon" in self.part_name:
                self.base_image = self.body_sprite_pool[self.data[0]][self.sprite_ver][self.mode][self.data[1]][
                    self.data[7]][self.data[5]]
            elif "special" in self.part_name:
                if sprite_name == "Template":  # template sprite that need replace
                    if "change_sprite" in self.owner.current_action:  # get new sprite type
                        sprite_type = self.owner.current_action["change_sprite"]
                        if sprite_type == "Item" and "item" in self.owner.current_action:  # change to item using
                            sprite_name = self.owner.current_action["item"]
                self.base_image = \
                    self.body_sprite_pool[sprite_type]["special"][self.sprite_ver][self.mode][sprite_name][
                        self.data[7]][self.data[5]]
            else:
                self.base_image = self.body_sprite_pool[self.data[0]][self.part_name][self.sprite_ver][self.mode][
                    self.data[1]][self.data[7]][self.data[5]]

            if self.base_image_update_contains:  # update any object after getting base image
                for item in self.base_image_update_contains:
                    item.update()

            self.image = self.base_image
            if self.data[4]:  # rotation
                self.angle = self.data[4]
                self.image = pygame.transform.rotate(self.base_image, self.angle)

            self.re_rect()
            if self in self.battle_camera:
                if not self.alive:
                    if self._layer != self.dead_layer + 100 - data[6]:
                        self.battle_camera.change_layer(self, self.dead_layer + 100 - data[6])
                elif self._layer != self.owner_layer + 100 - data[6]:
                    self.battle_camera.change_layer(self, self.owner_layer + 100 - data[6])

    def re_rect(self):
        if self.data:
            if self not in self.battle_camera:  # was remove because no data previously
                if not self.invincible:
                    for team in self.battle.all_team_enemy_part:
                        if team != self.team:  # add back part to enemy part list of other team
                            self.battle.all_team_enemy_part[team].add(self)
                if not self.owner.invisible:
                    self.battle_camera.add(self)
            elif self.owner.invisible:  # remove part from camera for invisible character
                self.battle_camera.remove(self)
            self.rect = self.image.get_rect(center=((self.owner.pos[0] + (self.data[2] * self.screen_scale[0])),
                                                    (self.owner.pos[1] + (self.data[3] * self.screen_scale[1]))))
            self.mask = from_surface(self.image)
        else:
            if self in self.battle_camera:
                for team in self.battle.all_team_enemy_part:
                    if team != self.team:  # remove part from enemy part list of other team
                        self.battle.all_team_enemy_part[team].remove(self)
                self.battle_camera.remove(self)

    def update(self, dt):
        if self.owner.alive and self.data:  # only update if owner alive and part exist (not empty data)
            if self.can_deal_dmg:
                self.hit_collide_check()
            if not self.owner.no_pickup:
                self.drop_collide_check()


def find_damage(self):
    # if not self.owner.current_moveset:  # TODO remove when stable
    #     print(self.name, self.owner.current_action, self.data)
    self.dmg = self.owner.current_moveset["Power"] + self.owner.power_bonus * self.owner.hold_power_bonus
    self.element = self.owner.current_moveset["Element"]
    self.impact = ((self.owner.current_moveset["Push Impact"] - self.owner.current_moveset["Pull Impact"]) *
                   self.owner.impact_modifier,
                   (self.owner.current_moveset["Down Impact"] - self.owner.current_moveset["Up Impact"]) *
                   self.owner.impact_modifier)
    self.impact_sum = abs(self.impact[0]) + abs(self.impact[1])
    if self.element == "Physical":
        max_dmg = self.dmg * self.owner.max_physical
        self.dmg = uniform(max_dmg * self.owner.min_physical, max_dmg)
    else:
        max_dmg = self.dmg * self.owner.max_elemental
        self.dmg = uniform(max_dmg * self.owner.min_elemental, max_dmg)
    if self.dmg < 1:
        self.dmg = 1
    self.critical_chance = self.owner.critical_chance + self.owner.current_moveset["Critical Chance Bonus"]
    self.friend_status_effect = self.owner.current_moveset["Status"]
    self.enemy_status_effect = self.owner.current_moveset["Enemy Status"]

    self.no_dodge = False
    self.no_defence = False
    self.no_guard = False
    if "no dodge" in self.owner.current_moveset["Property"]:
        self.no_dodge = True
    if "no defence" in self.owner.current_moveset["Property"]:
        self.no_defence = True
    if "no guard" in self.owner.current_moveset["Property"]:
        self.no_guard = True
