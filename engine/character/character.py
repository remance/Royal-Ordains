import copy
import types
from math import radians
from random import randint, random, uniform

import pygame
from pygame import sprite, Vector2
from pygame.mask import from_surface

from engine.uibattle.uibattle import CharacterSpeechBox

from engine.character.ai_combat import ai_combat_dict
from engine.character.ai_move import ai_move_dict
from engine.character.ai_retreat import ai_retreat_dict
from engine.character.character_specific_damage import damage_dict
from engine.character.character_specific_initiate import initiate_dict
from engine.character.character_specific_special import special_dict
from engine.character.character_specific_start_animation import animation_start_dict
from engine.character.character_specific_status_update import status_update_dict
from engine.character.character_specific_update import update_dict
from engine.data.datastat import final_recursive_dict
from engine.drop.drop import Drop
from engine.uibattle.uibattle import CharacterIndicator
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

    from engine.character.apply_status import apply_status
    apply_status = apply_status

    from engine.character.cal_loss import cal_loss
    cal_loss = cal_loss

    from engine.character.check_move_existence import check_move_existence
    check_move_existence = check_move_existence

    from engine.character.check_prepare_action import check_prepare_action
    check_prepare_action = check_prepare_action

    from engine.character.die import die
    die = die

    from engine.character.engage_combat import engage_combat
    engage_combat = engage_combat

    from engine.character.enter_battle import enter_battle
    enter_battle = enter_battle

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

    jump_idle_command_action = {"name": "Idle", "movable": True}
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

    heavy_damaged_command_action = {"name": "HeavyDamaged", "uncontrollable": True, "movable": True,
                                    "forced move": True, "heavy damaged": True}
    damaged_command_action = {"name": "SmallDamaged", "uncontrollable": True, "movable": True, "forced move": True,
                              "small damaged": True}
    standup_command_action = {"name": "Standup", "uncontrollable": True, "no dmg": True}
    liedown_command_action = {"name": "Liedown", "no dmg": True,
                              "knockdown": True, "freeze": 1, "next action": standup_command_action}
    knockdown_command_action = {"name": "Knockdown", "movable": True, "forced move": True,
                                "knockdown": True, "hold": True, "next action": liedown_command_action, "stand": True}

    die_command_action = {"name": "Die", "uninterruptible": True, "uncontrollable": True, "stand": True,
                          "forced move": True, "die": True}

    submit_action = {"name": "Submit", "repeat": True, "die": True, "submit": True}
    execute_action = {"name": "Execute", "hold": True, "execute": True, "die": True}
    taunt_action = {"name": "Taunt", "movable": True, "taunt": True}
    cheer_action = {"name": "Cheer", "cheer": True}
    cheer_fast_action = {"name": "CheerFast", "cheer": True}

    default_item_drop_table = {"Mystery Box": 0.5, "Speed Potion": 10, "Stone Potion": 10, "Reviving Seed": 1,
                               "Health Potion": 3, "Resource Potion": 2, "Bronze Coin": 30, "Silver Coin": 15,
                               "Gold Coin": 7, "Small Chest": 2, "Jewellery": 6, "Medium Chest": 0.7, "Diamond": 0.3,
                               "Lute": 3, "Harp": 3, "Jar": 3, "Whetstone": 2, "Goblet": 3, "Beer Mug": 4, "Teapot": 3,
                               "Yarn": 4, "Horseshoe": 3, "Board Game": 2, "Saint Figurine": 1, "Ball": 2,
                               "Trumpet": 3, "Golden Goblet": 1, "Ruby": 0.8, "Ring": 1,
                               "Sapphire": 0.8, "Topaz": 0.8, "Emerald": 0.8, "Amethyst": 0.8, "Opal": 0.8,
                               "Rare Coin": 1, "Beer": 7, "Wine": 6}  # , "Kid Doll": 0.5,
                               # "Rabbit Doll": 0.45, "Dog Doll": 0.3, "Cat Doll": 0.3, "Bear Doll": 0.2,
                               # "Gryphon Doll": 0.1, "Unicorn Doll": 0.08, "Slime Doll": 0.06, "Dragon Doll": 0.05,
                               # "Princess Doll": 0.03

    # drop that get added when playable character exist
    special_character_drop_table = {"Rodhinbar": {"Rodhinbar Arrow": 5},
                                    "Iri": {"Scrap": 15, "Trap Remain": 5}}
    # static variable
    default_animation_play_time = 0.1
    knock_down_sound_distance = 1500
    knock_down_screen_shake = 15
    heavy_dmg_sound_distance = 100
    heavy_dmg_screen_shake = 7
    dmg_sound_distance = 80
    dmg_screen_shake = 2
    original_ground_pos = 1000

    def __init__(self, game_id, layer_id, stat, player_control=False, leader=None, health_scaling=1):
        """
        Character object represent a character that take part in the battle in stage
        Character has three different stage of stat;
        first: original stat (e.g., original_attack), this is their stat before calculating equipment, and other effect
        second: troop base stat (e.g., base_attack), this is their stat after calculating equipment
        third: stat with all effect (e.g., attack), this is their stat after calculating weather, and status effect

        Character can be a player, friendly AI, or enemy
        """
        sprite.Sprite.__init__(self, self.containers)
        self.game_id = game_id
        self.layer_id = layer_id
        self.melee_target = None  # target for melee attacking
        self.player_control = player_control  # character controlled by player
        self.leader = leader
        self.taking_damage_angle = None
        self.indicator = None
        self.cutscene_event = None

        self.animation_pool = {}  # list of animation sprite this character can play with its action
        self.status_animation_pool = {}
        self.current_animation = {}  # list of animation frames playing
        self.current_animation_direction = {}
        self.show_frame = 0  # current animation frame
        self.max_show_frame = 0
        self.stoppable_frame = False
        self.hit_enemy = False
        self.is_boss = False
        self.is_summon = False
        self.frame_timer = 0
        self.effect_timer = 0
        self.effect_frame = 0
        self.max_effect_frame = 0
        self.current_effect = None
        self.interrupt_animation = False
        self.current_moveset = None
        self.continue_moveset = None
        self.current_action = {}  # action being performed
        self.command_action = {}  # next action to be performed
        self.command_key_input = []
        self.moveset_command_key_input = ()
        self.reach_camera_event = {}
        self.command_key_hold = None
        self.last_command_key_input = None

        self.team = stat["Team"]

        self.enemy_list = self.battle.all_team_enemy[self.team]
        self.enemy_part_list = self.battle.all_team_enemy_part[self.team]
        self.ally_list = self.battle.all_team_character[self.team]
        self.near_ally = []
        self.near_enemy = []
        self.nearest_enemy = None
        self.nearest_ally = None

        self.alive = True
        self.broken = False
        self.no_forced_move = False
        self.invisible = False
        self.stop_fall_duration = 0
        self.fly = False
        self.no_clip = False
        self.no_pickup = False
        self.invincible = False
        self.immune_weather = False
        self.hit_resource_regen = False
        self.crash_guard_resource_regen = False
        self.crash_haste = False
        self.slide_attack = False
        self.tackle_attack = False
        self.health_as_resource = False
        self.moveset_reset_when_relax_only = False
        self.combo_with_no_hit = False
        self.money_score = False
        self.money_resource = False
        self.position = "Stand"
        self.combat_state = "Peace"
        self.mode = "Normal"
        if self.battle.city_mode:
            self.combat_state = "City"
            self.mode = "City"
        self.special_combat_state = 0
        self.timer = random()
        self.in_combat_timer = 0
        self.default_sprite_size = 1

        self.move_speed = 0  # speed of current movement

        self.resurrect_count = 0
        self.guarding = 0
        self.attack_cooldown = {}  # character can attack with weapon only when cooldown reach attack speed
        self.attack_impact_effect = 1  # extra impact for weapon attack
        self.original_hp_regen = 0  # health regeneration modifier, will not resurrect dead troop by default
        self.original_resource_regen = 0  # resource regeneration modifier
        self.status_effect = {}  # current status effect
        self.status_duration = {}  # current status duration

        self.freeze_timer = 0
        self.hold_timer = 0  # how long animation holding so far
        self.release_timer = 0  # time when hold release

        self.screen_scale = self.battle.screen_scale

        self.command_pos = Vector2(0, 0)
        self.base_pos = Vector2(stat["POS"][0] + (1920 * (stat["Scene"] - 1)),
                                stat["POS"][1])  # true position of character in battle
        self.last_pos = None  # may be used by AI or specific character update check for position change
        self.pos = Vector2((self.base_pos[0] * self.screen_scale[0],
                            self.base_pos[1] * self.screen_scale[1]))
        self.cutscene_target_pos = None

        # Default element stat
        element_dict = {key.split(" ")[0]: 0 for key in stat if
                        " Resistance" in key}  # get resistance
        self.original_element_resistance = element_dict.copy()

        # initiate equipment stat
        self.equipped_weapon = "Preset"
        self.weight = 0

        # Get char stat
        self.name = stat["Name"]
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

        self.moveset = copy.deepcopy(stat["Move"])
        self.mode_list = stat["Mode"]
        self.skill = stat["Skill"].copy()
        self.available_skill = {"Couch": {}, "Stand": {}, "Air": {}}
        self.drops = {}
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

        self.score = 0  # enemy score for player when killed
        if "Score" in stat:
            self.score = stat["Score"]

        if "Skill Allocation" in stat:  # refind leveled skill allocated since name is only from first level
            for position_name, position in self.skill.items():
                for skill in tuple(position.keys()):
                    if position[skill]["Name"] in stat["Skill Allocation"] and \
                            stat["Skill Allocation"][position[skill]["Name"]]:
                        skill_id = skill[:3] + str(stat["Skill Allocation"][position[skill]["Name"]])
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

                button_key_skill_dict = {value["Buttons"]: {"Move": key} | value for key, value in
                                         self.available_skill[position].items() if
                                         "Requirement Move" not in value or not value["Requirement Move"]}
                for key, value in self.available_skill[position].items():  # check for skill with requirement move
                    if "Requirement Move" in value and value["Requirement Move"]:  # add to parent moveset
                        skill_data_dict = {"Move": key} | {key2: value2 for key2, value2 in value.items()}
                        final_recursive_dict(self.moveset[position], value["Buttons"], skill_data_dict,
                                             value["Requirement Move"], [False], [])

                self.moveset[position] = button_key_skill_dict | self.moveset[position]

        self.max_physical = 1 + (self.strength / 50) + (self.wisdom / 200)
        self.min_physical = self.dexterity / 100

        self.max_elemental = 1 + (self.intelligence / 50) + (self.wisdom / 200)
        self.min_elemental = self.wisdom / 100

        self.item_carry_bonus = int((self.strength / 10) + (self.wisdom / 40))

        self.original_critical_chance = 5 + int((self.dexterity / 10) + (self.wisdom / 30))

        self.original_defence = (self.agility / 20) + (self.constitution / 10) + (self.wisdom / 20)
        self.original_guard = 10 * self.constitution
        self.original_super_armour = self.constitution

        self.max_health = int((stat["Base Health"] + (stat["Base Health"] * (self.constitution / 100))) * health_scaling)  # health of character
        self.max_resource = int(stat["Max Resource"] + (stat["Max Resource"] * self.intelligence / 100))

        self.original_resource_cost_modifier = 1
        self.original_guard_cost_modifier = 1

        self.original_cast_speed = 1 / (1 + ((self.dexterity + self.intelligence) / 200))

        self.original_animation_play_time = self.default_animation_play_time / (
                1 + (self.agility / 100))  # higher value mean longer play time
        self.animation_play_time = self.original_animation_play_time
        self.final_animation_play_time = self.animation_play_time
        self.original_speed = self.agility * 2

        self.original_dodge = 1 + int((self.agility / 10) + (self.wisdom / 30))

        for element in self.original_element_resistance:  # resistance from
            self.original_element_resistance[element] = 0

        self.body_size = stat["Size"]
        self.body_size = int(self.body_size / 10)
        if self.body_size < 1:
            self.body_size = 1

        self.sprite_size = self.body_size * 100 * self.screen_scale[1]  # use for pseudo sprite size of character for positioning of effect

        self.base_body_mass = stat["Size"]
        self.body_mass = self.base_body_mass  # use for impact resistance when hit

        self.arrive_condition = stat["Arrive Condition"]

        self.ground_pos = self.original_ground_pos
        self.jump_power = 200 - self.weight
        self.y_momentum = 0
        self.x_momentum = 0

        self.fall_gravity = self.battle.original_fall_gravity

        self.items = {}

        # Stat after applying equipment
        self.base_power_bonus = 0
        self.base_defence = self.original_defence
        self.base_dodge = self.original_dodge - self.weight
        self.base_guard = self.original_guard
        self.base_critical_chance = self.original_critical_chance
        self.base_super_armour = self.original_super_armour

        self.base_element_resistance = self.original_element_resistance.copy()

        self.base_speed = (self.original_speed * (
                (100 - self.weight) / 100))  # finalise base speed with weight and grade bonus

        self.base_guard_cost_modifier = self.original_guard_cost_modifier
        self.base_resource_cost_modifier = self.original_resource_cost_modifier

        self.base_hp_regen = self.original_hp_regen
        self.base_resource_regen = self.original_resource_regen

        self.action_list = {}  # get added in change_equipment

        # Final stat after receiving stat effect from various sources, reset every time status is updated
        self.hold_power_bonus = 1
        self.power_bonus = self.base_power_bonus
        self.critical_chance = self.base_critical_chance
        self.defence = (100 - self.base_defence) / 100  # convert to percentage
        self.super_armour = self.base_super_armour
        self.dodge = self.base_dodge
        self.element_resistance = self.base_element_resistance.copy()
        self.speed = self.base_speed
        self.hp_regen = self.base_hp_regen
        self.resource_regen = self.base_resource_regen
        self.guard_meter = int(self.base_guard)
        self.max_guard = self.guard_meter
        self.guard_meter20 = self.guard_meter * 0.2
        self.guard_meter5 = self.guard_meter * 0.05

        self.guard_cost_modifier = self.base_guard_cost_modifier
        self.resource_cost_modifier = self.base_resource_cost_modifier

        self.health = self.max_health * stat["Start Health"] / 100
        self.resource1 = self.max_resource * 0.01
        self.resource2 = self.max_resource * 0.02
        self.resource10 = self.max_resource * 0.10
        self.resource25 = self.max_resource * 0.25
        self.resource50 = self.max_resource * 0.5
        self.resource75 = self.max_resource * 0.75
        self.resource = self.max_resource * stat["Start Resource"]

        self.run_speed = 1
        self.walk_speed = 1
        self.city_walk_speed = 500  # movement speed in city, not affected by anything

        # Variable related to sprite
        self.angle = -90
        if "Angle" in stat:
            self.angle = stat["Angle"]
        self.new_angle = self.angle
        self.radians_angle = radians(360 - self.angle)  # radians for apply angle to position
        self.run_direction = 0  # direction check to prevent character able to run in opposite direction right away
        self.sprite_direction = rotation_dict[min(rotation_list,
                                                  key=lambda x: abs(
                                                      x - self.angle))]  # find closest in list of rotation for sprite direction

        self.sprite_id = str(stat["ID"])
        self.sprite_ver = str(stat["Sprite Ver"])
        if "Only Sprite Version" in stat and stat["Only Sprite Version"]:  # data suggest only one sprite version exist
            self.sprite_ver = str(stat["Only Sprite Version"])

        self.retreat_stage_end = self.battle.base_stage_end + self.sprite_size
        self.retreat_stage_start = -self.sprite_size

        # find and set method specific to character
        if self.sprite_id in initiate_dict:
            initiate_dict[self.sprite_id](self)
        self.specific_animation_done = empty_method
        if self.sprite_id in animation_start_dict:
            self.specific_animation_done = types.MethodType(animation_start_dict[self.sprite_id], self)
        self.specific_special_check = empty_method
        if self.sprite_id in special_dict:
            self.specific_special_check = types.MethodType(special_dict[self.sprite_id], self)
        self.specific_update = empty_method
        if self.sprite_id in update_dict:
            self.specific_update = types.MethodType(update_dict[self.sprite_id], self)
        self.specific_status_update = empty_method
        if self.sprite_id in status_update_dict:
            self.specific_status_update = types.MethodType(status_update_dict[self.sprite_id], self)
        self.special_damage = empty_method
        if self.sprite_id in damage_dict:
            self.special_damage = types.MethodType(damage_dict[self.sprite_id], self)

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

        # Variables related to sound
        self.knock_down_sound_distance = self.knock_down_sound_distance * self.base_body_mass
        self.knock_down_screen_shake = self.knock_down_screen_shake * self.base_body_mass
        self.heavy_dmg_sound_distance = self.heavy_dmg_sound_distance * self.base_body_mass
        self.dmg_sound_distance = self.dmg_sound_distance * self.base_body_mass

        self.hit_volume_mod = self.base_body_mass / 10

    def update(self, dt):
        """Character update, run when cutscene not playing"""
        if self.health:  # only run these when not dead
            if dt:  # only run these when game not pause
                hold_check = False
                self.timer += dt

                if 0 < self.guarding < 1:
                    self.guarding += dt

                elif not self.guarding and self.guard_meter < self.max_guard:
                    # replenish guard meter when not guarding, always 5 percent per second
                    self.guard_meter += dt * self.guard_meter5
                    if self.guard_meter > self.max_guard:
                        self.guard_meter = self.max_guard

                if self.freeze_timer:
                    self.freeze_timer -= dt
                    if self.freeze_timer < 0:
                        self.freeze_timer = 0

                if self.stop_fall_duration:
                    self.stop_fall_duration -= dt
                    if self.stop_fall_duration < 0:
                        self.stop_fall_duration = 0

                self.taking_damage_angle = None
                self.ai_update(dt)

                if self.angle != self.new_angle:  # Rotate Function
                    self.rotate_logic()
                self.move_logic(dt)  # Move function

                if self.combat_state != "City":
                    if self.timer > 0.1:  # Update status and skill
                        if self.combat_state == "Combat" and self.position not in ("Air", "Couch"):
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
                                    self.in_combat_timer = 2

                        self.nearest_enemy = None
                        self.nearest_ally = None
                        self.near_enemy = sorted({key: key.base_pos.distance_to(self.base_pos) for key in
                                                  self.enemy_list}.items(),
                                                 key=lambda item: item[1])  # sort the closest enemy
                        self.near_ally = sorted(
                            {key: key.base_pos.distance_to(self.base_pos) for key in self.ally_list}.items(),
                            key=lambda item: item[1])  # sort the closest friend
                        if self.near_enemy:
                            self.nearest_enemy = self.near_enemy[0]
                        if self.near_ally:
                            self.nearest_ally = self.near_ally[0]

                        if not self.invincible:
                            self.status_update()
                        self.specific_status_update()
                        self.timer -= 0.1

                    self.health_resource_logic(dt)
                    self.specific_update(dt)

                # Animation and sprite system
                if self.show_frame >= len(self.current_animation_direction):  # TODO remove when really fixed
                    print(self.name, self.show_frame, self.current_animation, self.current_action)
                    raise Exception()

                if "hold" in self.current_animation_direction[self.show_frame]["property"] and \
                        "hold" in self.current_action and \
                        ((not self.current_moveset and "forced move" not in self.current_action) or
                         ("forced move" in self.current_action and (self.x_momentum or self.y_momentum)) or
                         (self.current_moveset and "hold" in self.current_moveset["Property"])):
                    hold_check = True
                    if self.current_moveset:
                        self.hold_timer += dt
                        self.hold_power_bonus = 1
                        if self.current_moveset["Property"]["hold"] == "power" and self.hold_timer >= 1:
                            # hold beyond 1 second to hit harder
                            self.hold_power_bonus = 2.5
                        elif self.current_moveset["Property"]["hold"] == "timing" and 2 >= self.hold_timer >= 1:
                            # hold release at specific time
                            self.hold_power_bonus = 4
                        elif self.current_moveset["Property"]["hold"] == "trigger" and self.hold_timer >= 0.5:
                            self.hold_timer -= 0.5
                            self.resource -= self.current_moveset["Resource Cost"]
                            if self.resource < 0:
                                self.resource = 0
                            elif self.resource > self.max_resource:
                                self.resource = self.max_resource

                            if self.current_moveset["Status"]:
                                for effect in self.current_moveset["Status"]:
                                    self.apply_status(effect)
                                    for ally in self.near_ally:
                                        if ally[1] <= self.current_moveset["Range"]:
                                            ally[0].apply_status(effect)
                                        else:
                                            break

                elif self.hold_timer > 0:  # no longer holding, reset timer
                    self.hold_power_bonus = 1
                    self.hold_timer = 0

                done = self.play_animation(dt, hold_check)

                # Pick new animation, condition to stop animation: get interrupt,
                # low level animation got replace with more important one, finish playing, skill animation and its effect end
                if (self.interrupt_animation and "uninterruptible" not in self.current_action) or \
                        (((not self.current_action or "low level" in self.current_action) and
                          self.command_action) or done):
                    # Change position
                    if done:
                        if self.current_moveset:
                            if "helper" in self.current_moveset["Property"]:
                                for key, value in self.current_moveset["Property"].items():
                                    if key == "drop_item":
                                        self.battle.helper.interrupt_animation = True
                                        self.battle.helper.command_action = {"name": "special",
                                                                             "drop": value}
                        if "drop" in self.current_action:
                            Drop(Vector2(self.base_pos), self.current_action["drop"], self.team)

                    # Reset action check
                    if "next action" in self.current_action and not self.interrupt_animation and \
                            (not self.current_moveset or "no auto next" not in self.current_moveset["Property"]):
                        # play next action from current first instead of command if not finish by interruption
                        self.current_action = self.current_action["next action"]
                    elif ("remove momentum when done" not in self.current_action and
                          (("x_momentum" in self.current_action and self.x_momentum) or
                           ("y_momentum" in self.current_action and self.y_momentum))) and not self.interrupt_animation:
                        # action that require movement to run out first before continue to next action
                        pass
                    elif "arrive" in self.current_action and "Arrive2" in self.skill[self.position]:
                        # has arrival (Arrive2) skill to use after finish arriving
                        self.moveset_command_key_input = self.skill[self.position]["Arrive2"]["Buttons"]
                        self.check_move_existence()
                        self.current_action = self.attack_command_actions["Special"]
                    elif "run" in self.current_action and not self.command_action:  # stop running, halt
                        self.current_action = self.halt_command_action
                        if self.sprite_direction == "r_side":
                            self.x_momentum = self.walk_speed
                        else:
                            self.x_momentum = -self.walk_speed
                    elif "halt" in self.current_action:  # already halting
                        self.x_momentum = 0
                        self.current_action = self.command_action  # continue next action when animation finish
                        self.command_action = {}
                    else:
                        self.current_action = self.command_action  # continue next action when animation finish
                        self.command_action = {}

                    self.specific_animation_done(done)

                    # reset animation playing related value
                    self.stoppable_frame = False
                    self.hit_enemy = False
                    self.interrupt_animation = False
                    self.release_timer = 0  # reset any release timer

                    self.show_frame = 0
                    self.frame_timer = 0
                    self.move_speed = 0

                    # check for new position before picking new animation
                    if "couch" in self.current_action:
                        self.position = "Couch"
                    elif "air" in self.current_action:
                        self.position = "Air"
                        self.y_momentum = self.jump_power
                        if self.x_momentum:  # increase y momentum a bit when has x momentum so jump not too short
                            self.y_momentum *= 1.3
                    elif "stand" in self.current_action:
                        self.position = "Stand"

                    self.pick_animation()

                    # new action property
                    if "freeze" in self.current_action:
                        self.freeze_timer = self.current_action["freeze"]

                    if "x_momentum" in self.current_action and type(self.current_action["x_momentum"]) is not str and \
                            not self.x_momentum:
                        if type(self.current_action["x_momentum"]) is not str:
                            if self.angle != 90:
                                self.x_momentum = self.current_action["x_momentum"]
                            else:
                                self.x_momentum = -self.current_action["x_momentum"]
                    if "y_momentum" in self.current_action and type(self.current_action["y_momentum"]) is not str:
                        self.y_momentum = self.current_action["y_momentum"]

                if self.reach_camera_event and self.battle.base_camera_begin < self.base_pos[0] < self.battle.base_camera_end:
                    # play event related to character reach inside camera
                    for key, value in self.reach_camera_event.items():
                        for item in value:
                            if item["Type"] == "speak":  # speak something
                                CharacterSpeechBox(self, self.battle.localisation.grab_text(("event",
                                                                                             item["Text ID"],
                                                                                             "Text")))
                            elif item["Type"] == "animation":  # play specific animation
                                self.command_action = item["Property"]
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
                    self.die("flee")

        else:  # die
            if self.alive:  # enter dead state
                self.attack_cooldown = {}  # remove all cooldown
                self.alive = False  # enter dead state
                self.engage_combat()
                self.current_action = self.die_command_action
                self.show_frame = 0
                self.frame_timer = 0
                self.pick_animation()

            if "die" in self.current_action:
                if self.show_frame < self.max_show_frame or self.base_pos[1] < self.ground_pos or \
                        "repeat" in self.current_action:  # play die animation
                    self.move_logic(dt)
                    self.play_animation(dt, False)
                else:  # finish die animation and reach ground
                    if self.resurrect_count:  # resurrect back
                        # self.resurrect_count -= 1
                        self.interrupt_animation = True
                        self.alive = True
                        self.command_action = self.standup_command_action
                        self.health = self.max_health
                    else:  # permanent death
                        if self.is_summon:  # summon character does not leave corpse
                            self.die("flee")
                        else:
                            self.die("dead")

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

        hold_check = False
        if ("hold" in self.current_animation_direction[self.show_frame]["property"] and "hold" in self.current_action) or \
                not self.max_show_frame:
            hold_check = True
        done = self.play_cutscene_animation(dt, hold_check)
        if done or (self.cutscene_target_pos and self.cutscene_target_pos == self.base_pos):
            if done:
                self.show_frame = 0
                self.frame_timer = 0
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
            if (self.cutscene_target_pos and self.cutscene_target_pos == self.base_pos) or \
                    (not self.cutscene_event or "repeat" not in self.cutscene_event["Property"]):
                # animation consider finish when reach target or finish animation with no repeat, pick idle animation
                self.show_frame = 0
                self.frame_timer = 0
                self.current_action = {}
                self.pick_cutscene_animation({})
            if self.cutscene_event and "repeat" not in self.cutscene_event["Property"] and \
                    "player_interact" not in self.cutscene_event["Property"] and \
                    (not self.cutscene_target_pos or self.cutscene_target_pos == self.base_pos):
                # finish animation, consider event done unless event require player interaction first or in repeat
                self.cutscene_target_pos = None
                self.current_action = {}
                self.command_action = {}
                self.battle.cutscene_playing.remove(self.cutscene_event)
                self.cutscene_event = None
                self.pick_cutscene_animation({})

    def ai_update(self, dt):
        pass


class PlayableCharacter(Character):
    def __init__(self, game_id, layer_id, stat):
        Character.__init__(self, game_id, layer_id, stat, player_control=True)
        self.player_input = self.player_input_battle_mode
        if self.battle.city_mode:
            self.player_input = self.player_input_city_mode

        self.indicator = CharacterIndicator(self)
        self.player_command_key_input = []
        self.player_key_input_timer = []
        self.player_key_hold_timer = {}
        self.resurrect_count = 2

        # Add equipment stat
        # self.current_weapon = None
        # self.weapons = {}
        # self.weapon_id = (self.primary_main_weapon[0], self.primary_sub_weapon[0])
        # self.weapon_data = ((self.character_data.weapon_list[self.primary_main_weapon[0]],
        #                      self.character_data.weapon_list[self.primary_sub_weapon[0]]))

        # self.add_gear_stat()

        # self.armour_gear = stat["Armour"]  # armour equipment
        # self.armour_id = 0
        # if self.armour_gear:
        #     self.armour_id = self.armour_gear[0]
        #     self.weight += self.character_data.armour_list[self.armour_id]["Weight"]  # Add weight from both armour
        #     armour_stat = self.character_data.armour_list[self.armour_id]
        #     armour_grade_mod = 1 + self.character_data.equipment_grade_list[self.armour_gear[1]]["Stat Modifier"]
        #     for element in self.original_element_resistance:  # resistance from armour
        #         self.original_element_resistance[element] += (armour_stat[element + " Resistance"] * armour_grade_mod)

        common_skill = ("Ground Movement", "Air Movement", "Tinkerer", "Arm Mastery", "Wealth",
                        "Immunity", "Resourceful", "Combat Contest")

        self.common_skill = {skill: {1: False, 2: False, 3: False, 4: False, 5: False} for skill in common_skill}

        for skill in common_skill:
            if stat["Skill Allocation"][skill]:
                for level in range(int(stat["Skill Allocation"][skill] + 1)):
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
            self.base_speed = self.original_speed
        if self.common_skill["Ground Movement"][5]:  # can perform dodge move while moving
            self.dodge_move = True

        self.can_double_jump = False
        self.unlimited_jump = False
        self.double_jump = False
        self.double_air_impact_resistance = False
        self.hover = False

        if self.common_skill["Air Movement"][1]:  # can double jump
            self.double_jump = True
        if self.common_skill["Air Movement"][2]:
            pass
        if self.common_skill["Air Movement"][3]:  # weight no longer affect jump power
            self.jump_power = 200
        if self.common_skill["Air Movement"][4]:  # increase impact resistant while in air position
            self.double_air_impact_resistance = True
        if self.common_skill["Air Movement"][1]:  # can hover in air
            self.hover = True

        self.item_free_use_chance = False
        self.double_food_effect = False
        if self.common_skill["Tinkerer"][1]:  # can slide attack
            pass
            # self.item
        if self.common_skill["Tinkerer"][2]:  # item may have a chance to be used for free
            self.item_free_use_chance = True
        if self.common_skill["Tinkerer"][3]:  # food has double effect
            self.double_food_effect = True
        if self.common_skill["Tinkerer"][4]:  # can slide attack
            pass
        if self.common_skill["Tinkerer"][5]:  # can slide attack
            pass

        self.double_pickup_usage = False
        if self.common_skill["Arm Mastery"][1]:  # pick-up weapon has double usage
            self.double_pickup_usage = True
        if self.common_skill["Arm Mastery"][2]:
            pass
        if self.common_skill["Arm Mastery"][3]:  # food has double effect
            pass
        if self.common_skill["Arm Mastery"][4]:  # can slide attack
            pass
        if self.common_skill["Arm Mastery"][5]:  # can slide attack
            pass

        self.money_score = False
        self.money_resource = False
        if self.common_skill["Wealth"][1]:  # money pickup also increase mission score
            self.money_score = True
        if self.common_skill["Wealth"][2]:  # money pickup also increase resource
            self.money_resource = True
        if self.common_skill["Wealth"][3]:  # food has double effect
            pass
        if self.common_skill["Wealth"][4]:  #
            pass
        if self.common_skill["Wealth"][5]:  #
            pass

        self.knock_recover = False
        self.immune_weather = False
        if self.common_skill["Immunity"][1]:  # can recover from knockdown with guard action
            self.knock_recover = True
        if self.common_skill["Immunity"][2]:  # shorten all debuff duration by half
            pass
        if self.common_skill["Immunity"][3]:  # increase resurrection count by 1
            pass
        if self.common_skill["Immunity"][4]:  # immune to weather effect
            self.immune_weather = True
        if self.common_skill["Immunity"][5]:  # unlock immune barrier skill
            pass

        self.hit_resource_regen = False
        self.crash_guard_resource_regen = False
        if self.common_skill["Resourceful"][1]:  # add resource regen
            self.base_resource_regen += self.max_resource * 0.01
        if self.common_skill["Resourceful"][2]:  # resource regen when hit enemy
            self.hit_resource_regen = True
        if self.common_skill["Resourceful"][3]:  # resource regen when crash and guard
            self.crash_guard_resource_regen = True
        if self.common_skill["Resourceful"][4]:  # double max resource, and auto regen
            self.max_resource += self.max_resource
            self.resource1 = self.max_resource * 0.01
            self.resource2 = self.max_resource * 0.02
            self.resource10 = self.max_resource * 0.10
            self.resource25 = self.max_resource * 0.25
            self.resource50 = self.max_resource * 0.5
            self.resource75 = self.max_resource * 0.75
            self.base_resource_regen += self.max_resource * 0.02
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
        if self.common_skill["Combat Contest"][5]:  # can slide attack
            pass

        self.enter_battle(self.battle.character_animation_data)


class AICharacter(Character):
    def __init__(self, game_id, layer_id, stat, leader=None, specific_behaviour=None, health_scaling=1):
        Character.__init__(self, game_id, layer_id, stat, leader=leader, health_scaling=health_scaling)
        self.old_cursor_pos = None
        self.is_boss = stat["Boss"]
        self.is_summon = stat["Summon"]
        self.ai_lock = False  # lock AI from activity when start battle, and it positions outside of scene lock
        if self.base_pos[0] > self.battle.base_stage_end:
            self.ai_lock = True
        if self.is_summon:
            self.health_as_resource = True  # each time summon use resource it uses health instead
        if self.leader:
            self.indicator = CharacterIndicator(self)
        if "Ground Y POS" in stat and stat["Ground Y POS"]:  # replace ground pos based on data in stage
            self.ground_pos = stat["Ground Y POS"]

        ai_behaviour = stat["AI Behaviour"]
        if specific_behaviour:
            ai_behaviour = specific_behaviour

        self.ai_move = types.MethodType(ai_move_dict["default"], self)
        if ai_behaviour in ai_move_dict:
            self.ai_move = types.MethodType(ai_move_dict[ai_behaviour], self)

        self.ai_combat = types.MethodType(ai_combat_dict["default"], self)
        if ai_behaviour in ai_combat_dict:
            self.ai_combat = types.MethodType(ai_combat_dict[ai_behaviour], self)

        self.ai_retreat = types.MethodType(ai_retreat_dict["default"], self)
        if ai_behaviour in ai_retreat_dict:
            self.ai_retreat = types.MethodType(ai_retreat_dict[ai_behaviour], self)

        for item in stat["Property"]:  # set attribute from property
            self.__setattr__(item, True)
        self.ai_max_attack_range = 0
        self.ai_timer = 0  # for whatever timer require for AI action
        self.ai_movement_timer = 0  # timer to move for AI
        self.end_ai_movment_timer = randint(2, 6)
        if self.is_boss:
            self.end_ai_movment_timer = 5
        for position in self.moveset.values():
            for move in position.values():
                if self.ai_max_attack_range < move["AI Range"]:
                    self.ai_max_attack_range = move["AI Range"]

        if "Stage Property" in stat:
            for stuff in stat["Stage Property"]:
                if stuff == "target":
                    if type(stat["Stage Property"]["target"]) is int:  # target is AI
                        target = stat["Stage Property"]["target"]
                    else:  # target is player
                        target = stat["Stage Property"]["target"][-1]

                    for this_char in self.battle.all_chars:
                        if target == this_char.game_id:  # find target char object
                            self.target = this_char
                            break
                else:
                    self.__setattr__(stuff, True)

        self.resurrect_count = 0

        self.enter_battle(self.battle.character_animation_data)

    def ai_update(self, dt):
        self.ai_timer = 0  # for whatever timer require for AI action
        self.ai_movement_timer = 0  # timer to move for AI
        if self.ai_timer:
            self.ai_timer += dt
        if self.ai_movement_timer:
            self.ai_movement_timer += dt
        if not self.broken:
            self.ai_combat()
            self.ai_move(dt)
        else:
            self.ai_retreat()


class CityAICharacter(Character):
    def __init__(self, game_id, layer_id, stat, leader=None, specific_behaviour=None):
        Character.__init__(self, game_id, layer_id, stat, leader=leader)

        if "Ground Y POS" in stat and stat["Ground Y POS"]:  # replace ground pos based on data in stage
            self.ground_pos = stat["Ground Y POS"]

        ai_behaviour = "idle_city_npc"
        if specific_behaviour:
            ai_behaviour = specific_behaviour

        self.ai_move = ai_move_dict["default"]
        if ai_behaviour in ai_move_dict:
            self.ai_move = ai_move_dict[ai_behaviour]

        self.ai_combat = ai_combat_dict["default"]
        if ai_behaviour in ai_combat_dict:
            self.ai_combat = ai_combat_dict[ai_behaviour]

        self.ai_timer = 0  # for whatever timer require for AI action
        self.ai_movement_timer = 0  # timer to move for AI
        self.end_ai_movment_timer = randint(2, 6)

        self.enter_battle(self.battle.character_animation_data)

    def ai_update(self, dt):
        if self.ai_timer:
            self.ai_timer += dt
        if self.ai_movement_timer:
            self.ai_movement_timer += dt
        self.ai_combat(self)
        self.ai_move(self, dt)

#
# class CutsceneCharacter:
#     def __init__(self, game_id, layer_id):
#
#
#     def update(self, dt):

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
        self.original_can_hurt = can_hurt
        self.can_hurt = can_hurt
        self.can_deal_dmg = False
        self.dmg = None
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
        self.data = []  # index 1=part name, 2and3=pos xy, 4=angle, 5=flip, 6=layer , 7=scale, 8=deal damage or not
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
        if self.data != data:
            self.data = data
            if "weapon" in self.part_name:
                self.base_image = self.body_sprite_pool[self.data[0]][self.sprite_ver][self.mode][self.data[1]][
                    self.data[7]][self.data[5]]
            elif "special" in self.part_name:
                self.base_image = \
                self.body_sprite_pool[self.data[0]]["special"][self.sprite_ver][self.mode][self.data[1]][
                    self.data[7]][self.data[5]]
            else:
                self.base_image = self.body_sprite_pool[self.data[0]][self.part_name][self.sprite_ver][self.mode][
                    self.data[1]][self.data[7]][self.data[5]]

            if self.base_image_update_contains:  # update any object after getting base image
                for item in self.base_image_update_contains:
                    item.update()

            self.image = self.base_image
            if self.data[4]:  # rotation
                self.image = pygame.transform.rotate(self.base_image, self.data[4])

            self.re_rect()
            if self._layer != self.owner_layer + 100 - data[6]:
                self.battle_camera.change_layer(self, self.owner_layer + 100 - data[6])

    def re_rect(self):
        if self.data:
            if self not in self.battle_camera:  # was remove because no data previously
                if not self.invincible:
                    for team in self.battle.all_team_enemy_part:
                        if team != self.team:  # add back part to enemy part list of other team
                            self.battle.all_team_enemy_part[team].add(self)
                self.battle_camera.add(self)

            self.rect = self.image.get_rect(center=((self.owner.pos[0] + (self.data[2] * self.screen_scale[0])),
                                                    (self.owner.pos[1] + (self.data[3] * self.screen_scale[1]))))
            self.mask = from_surface(self.image)
        else:
            if self in self.battle_camera:
                for team in self.battle.all_team_enemy_part:
                    if team != self.team:  # remove part from enemy part list of other team
                        self.battle.all_team_enemy_part[team].remove(self)
                self.battle_camera.remove(self)
            # self.rect = self.image.get_rect(topleft=(0, 0))

    def update(self, dt):
        if self.owner.alive and self.data:  # only update if owner alive and part exist (not empty data)
            if self.can_deal_dmg:
                self.hit_collide_check()
            if not self.owner.no_pickup:
                self.drop_collide_check()


def find_damage(self):
    # if not self.owner.current_moveset:  # TODO remove later
    #     (self.owner.name, self.owner.current_action, self.owner.show_frame)
    self.dmg = self.owner.current_moveset["Power"] + self.owner.power_bonus * self.owner.hold_power_bonus
    self.element = self.owner.current_moveset["Element"]
    self.impact = ((self.owner.current_moveset["Push Impact"] - self.owner.current_moveset["Pull Impact"]) *
                   self.owner.attack_impact_effect,
                   (self.owner.current_moveset["Down Impact"] - self.owner.current_moveset["Up Impact"]) *
                   self.owner.attack_impact_effect)
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
