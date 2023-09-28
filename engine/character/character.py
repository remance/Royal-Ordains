from math import radians
from random import randint, random, uniform

import pygame
from pygame import sprite, Vector2

from engine.drop.drop import Drop

from engine.utils.common import empty_method
from engine.utils.rotation import set_rotate

from engine.character.character_specific_special import special_dict
from engine.character.character_specific_damage import damage_dict
from engine.character.character_specific_update import update_dict
from engine.character.character_specific_status_update import status_update_dict

from engine.character.ai_combat import ai_combat_dict
from engine.character.ai_move import ai_move_dict
from engine.character.ai_retreat import ai_retreat_dict

from engine.uibattle.uibattle import CharacterIndicator

rotation_list = (90, -90)
rotation_name = ("l_side", "r_side")
rotation_dict = {key: rotation_name[index] for index, key in enumerate(rotation_list)}

infinity = float("inf")


"""Command dict Guide
Key:
name = action name that will be used to find animation, name with "Action" will find attack action of weapon for animation name
main_weapon = animation use one with common main weapon action name regardless of input
move attack = indicate using move attack animation
melee attack = indicate animation performing melee attack for spawning damage sprite in frame that can spawn it
range attack = indicate animation performing range attack for spawning bullet sprite when finish
repeat = keep repeating this animation until canceled, should only be used for action that can be controlled like walk
movable = can move during action
controllable = can perform controllable action during action like walk or attack
next action = action that will be performed after the current one finish
uninterruptible = action can not be interrupt with interrupt_animation variable
move loop = action involve repeating movement that can be cancel when movement change like walk to run
charge = indicate charging action
less mass = character has mass is divided during animation based on value provide
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
"""


class Character(sprite.Sprite):
    battle = None
    character_data = None
    effect_list = None
    status_list = None
    sound_effect_pool = None

    image = pygame.Surface((0, 0))  # start with empty surface

    set_rotate = set_rotate

    from engine.character.add_gear_stat import add_gear_stat
    add_weapon_stat = add_gear_stat

    from engine.character.apply_status import apply_status
    apply_status = apply_status

    from engine.character.cal_loss import cal_loss
    cal_loss = cal_loss

    from engine.character.check_element_effect import check_element_effect
    check_element_effect = check_element_effect

    from engine.character.check_element_threshold import check_element_threshold
    check_element_threshold = check_element_threshold

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

    from engine.character.play_animation import play_animation
    play_animation = play_animation

    from engine.character.player_input import player_input
    player_input = player_input

    from engine.character.rotate_logic import rotate_logic
    rotate_logic = rotate_logic

    from engine.character.start_animation_body_part import start_animation_body_part
    start_animation_body_part = start_animation_body_part

    from engine.character.status_update import status_update
    status_update = status_update

    from engine.character.use_skill import use_skill
    use_skill = use_skill

    walk_command_action = {"name": "Walk", "movable": True, "walk": True}
    run_command_action = {"name": "Run", "movable": True, "run": True}
    flee_command_action = {"name": "FleeMove", "movable": True, "flee": True}
    halt_command_action = {"name": "Halt", "uncontrollable": True, "movable": True, "walk": True, "halt": True}

    jump_idle_command_action = {"name": "Idle", "movable": True}
    relax_command_action = {"name": "Relax"}

    couch_command_action = {"name": "Couch", "couch": True}
    couch_stand_command_action = {"name": "Stand", "uncontrollable": True, "stand": True}

    weak_attack_command_action = {"name": "Weak Attack", "moveset": True, "weak": True}
    strong_attack_command_action = {"name": "Strong Attack", "moveset": True, "strong": True}
    weak_attack_hold_command_action = {"name": "Weak Attack", "hold": True, "moveset": True, "weak": True}
    strong_attack_hold_command_action = {"name": "Strong Attack", "hold": True, "moveset": True, "strong": True}
    special_command_action = {"name": "Special", "moveset": True, "special": True}
    special_hold_command_action = {"name": "Special", "hold": True, "moveset": True, "special": True}
    skill_command_action = {"name": "Skill", "moveset": True, "skill": True}
    activate_command_action = {"name": "Activate"}
    deactivate_command_action = {"name": "Deactivate"}

    guard_command_action = {"name": "Guard", "guard": True}
    guard_hold_command_action = {"name": "Guard", "guard": True, "hold": True}
    guard_move_command_action = {"name": "Guard", "guard": True, "movable": True, "walk": True}

    air_idle_command_action = {"name": "Idle", "movable": True}
    land_command_action = {"name": "Land", "uncontrollable": True, "land": True}

    jump_command_action = {"name": "Jump", "air": True}
    runjump_command_action = {"name": "RunJump", "air": True}

    arrive_command_action = {"name": "Arrive", "movable": True, "arrive": True, "x_momentum": True}
    arrive_fly_command_action = {"name": "Arrive", "movable": True, "arrive": True, "fly": True, "x_momentum": True}

    heavy_damaged_command_action = {"name": "HeavyDamaged", "uncontrollable": True, "movable": True, "forced move": True,
                                    "heavy damaged": True}
    damaged_command_action = {"name": "SmallDamaged", "uncontrollable": True, "movable": True, "forced move": True,
                              "small damaged": True}
    standup_command_action = {"name": "Standup", "uncontrollable": True, "no dmg": True}
    knockdown_command_action = {"name": "Knockdown", "uncontrollable": True, "movable": True, "forced move": True,
                                "no dmg": True, "knockdown": True, "hold": True,
                                "next action": standup_command_action, "stand": True}

    die_command_action = {"name": "Die", "uninterruptible": True, "uncontrollable": True, "stand": True,
                          "forced move": True, "die": True}

    # static variable
    default_animation_play_time = 0.1
    knock_down_sound_distance = 1500
    knock_down_sound_shake = 1000
    heavy_dmg_sound_distance = 1000
    heavy_dmg_sound_shake = 500
    dmg_sound_distance = 800
    dmg_sound_shake = 200
    original_ground_pos = 1000

    def __init__(self, game_id, stat, player_control=False):
        """
        Character object represent a character that take part in the battle in stage
        Character has three different stage of stat;
        first: original stat (e.g., original_attack), this is their stat before calculating equipment, and other effect
        second: troop base stat (e.g., base_attack), this is their stat after calculating equipment
        third: stat with all effect (e.g., attack), this is their stat after calculating weather, and status effect

        Character can be a player or enemy
        """
        sprite.Sprite.__init__(self, self.containers)
        self.game_id = game_id
        self.melee_target = None  # target for melee attacking
        self.player_control = player_control  # character controlled by player
        self.taking_damage_angle = None
        self.indicator = None

        self.animation_pool = {}  # list of animation sprite this character can play with its action
        self.status_animation_pool = {}
        self.current_animation = {}  # list of animation frames playing
        self.current_animation_direction = {}
        self.show_frame = 0  # current animation frame
        self.max_show_frame = 0
        self.stoppable_frame = False
        self.hit_enemy = False
        self.is_boss = False
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
        self.not_movable = False
        self.invisible = False
        self.fly = False
        self.no_clip = False
        self.no_pickup = False
        self.invincible = False
        self.position = "Stand"
        self.combat_state = "Peace"
        self.mode = "Normal"
        self.timer = random()
        self.in_combat_timer = 0
        self.default_sprite_size = 1
        self.resource = 0  # skill resource

        self.move_speed = 0  # speed of current movement

        self.resurrect_count = 0
        self.guarding = 0
        self.attack_cooldown = {}  # character can attack with weapon only when cooldown reach attack speed
        self.attack_impact_effect = 1  # extra impact for weapon attack
        self.original_hp_regen = 0  # health regeneration modifier, will not resurrect dead troop by default
        self.original_resource_regen = 0  # resource regeneration modifier
        self.status_effect = {}  # current status effect
        self.status_duration = {}  # current status duration
        self.skill_effect = {}  # activate skill effect
        self.skill_duration = {}  # current active skill duration

        self.freeze_timer = 0
        self.hold_timer = 0  # how long animation holding so far
        self.release_timer = 0  # time when hold release

        self.screen_scale = self.battle.screen_scale

        self.command_pos = Vector2(0, 0)
        self.base_pos = Vector2(stat["POS"])  # true position of character in battle
        self.last_pos = None  # may be used by AI or specific character update check for position change
        self.pos = Vector2((self.base_pos[0] * self.screen_scale[0],
                            self.base_pos[1] * self.screen_scale[1]))

        # Default element stat
        element_dict = {key.split(" ")[0]: 0 for key in stat if
                        " Resistance" in key}  # get resistance
        self.element_status_check = element_dict.copy()  # element threshold count
        self.original_element_resistance = element_dict.copy()

        # initiate equipment stat
        self.equipped_weapon = "Preset"
        self.weight = 0
        self.weapon_weight = {0: 0, 1: 0}

        # Get char stat
        self.name = stat["Name"]
        self.strength = stat["Strength"]
        self.dexterity = stat["Dexterity"]
        self.agility = stat["Agility"]
        self.constitution = stat["Constitution"]
        self.intelligence = stat["Intelligence"]
        self.wisdom = stat["Wisdom"]
        self.charisma = stat["Charisma"]

        self.moveset = stat["Move"].copy()
        self.mode_list = stat["Mode"]
        self.skill = stat["Skill"].copy()

        if "Skill Allocation" in stat:
            for skill in tuple(self.skill.keys()):
                if skill not in stat["Skill Allocation"]:
                    self.skill.pop(skill)

        for position in ("Couch", "Stand", "Air"):  # combine skill into moveset
            if position in self.skill:
                if position not in self.moveset:
                    self.moveset[position] = {}
                button_key_skill_dict = {value["Buttons"]: {"Move": key} | value for key, value in self.skill[position].items()}
                self.moveset[position] = button_key_skill_dict | self.moveset[position]

        self.max_physical = 1 + (self.strength / 50) + (self.wisdom / 200)
        self.min_physical = self.dexterity / 100

        self.max_elemental = 1 + (self.intelligence / 50) + (self.wisdom / 200)
        self.min_elemental = self.wisdom / 100

        self.item_carry_bonus = int((self.strength / 10) + (self.wisdom / 40))

        self.original_critical_chance = 5 + int((self.dexterity / 10) + (self.wisdom / 30))

        self.original_defense = (self.agility / 20) + (self.constitution / 10) + (self.wisdom / 20)
        self.original_guard = 10 * self.constitution
        self.original_super_armour = self.constitution

        self.health = stat["Base Health"] + (stat["Base Health"] * (self.constitution / 100))  # health of character

        self.max_resource = int(stat["Max Resource"])
        self.resource25 = self.max_resource * 0.25
        self.resource50 = self.max_resource * 0.5
        self.resource75 = self.max_resource * 0.75

        self.original_cast_speed = 1 / (1 + ((self.dexterity + self.intelligence) / 200))

        self.original_animation_play_time = self.default_animation_play_time / (1 + (self.agility / 200))
        self.animation_play_time = self.original_animation_play_time
        self.original_speed = self.agility / 2

        self.original_dodge = 1 + int((self.agility / 10) + (self.wisdom / 30))

        for element in self.original_element_resistance:  # resistance from
            self.original_element_resistance[element] = 0

        self.body_size = stat["Size"]
        self.body_size = int(self.body_size / 10)
        if self.body_size < 1:
            self.body_size = 1

        self.sprite_size = self.body_size * 100

        if self.player_control:
            self._layer = int(game_id * self.body_size * 100000000)
        else:
            self._layer = int(game_id * self.body_size * 100000)

        self.base_body_mass = stat["Size"]
        self.body_mass = self.base_body_mass

        self.ground_pos = self.original_ground_pos
        self.jump_power = 200 - self.weight
        self.y_momentum = 0
        self.x_momentum = 0

        self.fall_gravity = self.battle.original_fall_gravity

        self.items = {}
        # Stat after applying gear
        self.base_power_bonus = 0
        self.base_defense = self.original_defense
        self.base_dodge = self.original_dodge - self.weight
        self.base_guard = self.original_guard
        self.base_critical_chance = self.original_critical_chance
        self.base_super_armour = self.original_super_armour

        self.base_element_resistance = self.original_element_resistance.copy()

        self.base_speed = (self.original_speed * (
                    (100 - self.weight) / 100))  # finalise base speed with weight and grade bonus

        self.base_hp_regen = self.original_hp_regen
        self.base_resource_regen = self.original_resource_regen

        self.action_list = {}  # get added in change_equipment

        # Final stat after receiving stat effect from various sources, reset every time status is updated
        self.hold_power_bonus = 1
        self.power_bonus = self.base_power_bonus
        self.critical_chance = self.base_critical_chance
        self.defense = (100 - self.base_defense) / 100
        self.super_armour = self.base_super_armour
        self.dodge = self.base_dodge
        self.element_resistance = self.base_element_resistance.copy()
        self.speed = self.base_speed
        self.hp_regen = self.base_hp_regen
        self.resource_regen = self.base_resource_regen
        self.guard_meter = self.base_guard
        self.max_guard = int(self.guard_meter)
        self.guard_meter20 = self.guard_meter * 0.2
        self.guard_meter5 = self.guard_meter * 0.05

        # self.max_melee_range = self.melee_range[0]
        # self.max_shoot_range = self.shoot_range[0]

        self.max_health = int(self.health)
        self.health *= stat["Start Health"] / 100

        self.run_speed = 1
        self.walk_speed = 1

        self.angle = 0
        self.new_angle = self.angle
        self.radians_angle = radians(360 - self.angle)  # radians for apply angle to position
        self.run_direction = 0  # direction check to prevent character able to run in opposite direction right away
        self.sprite_direction = rotation_dict[min(rotation_list,
                                                  key=lambda x: abs(x - self.angle))]  # find closest in list of rotation for sprite direction

        self.sprite_id = str(stat["ID"])
        self.sprite_ver = str(stat["Sprite Ver"])
        if "Only Sprite Version" in stat and stat["Only Sprite Version"]:  # data suggest only one sprite version exist
            self.sprite_ver = str(stat["Only Sprite Version"])

        self.arrive_condition = stat["Arrive Condition"]

        self.specific_special_check = empty_method
        if self.sprite_id in special_dict:
            self.specific_special_check = special_dict[self.sprite_id]
        self.specific_update = empty_method
        if self.sprite_id in update_dict:
            self.specific_update = update_dict[self.sprite_id]
        self.specific_status_update = empty_method
        if self.sprite_id in status_update_dict:
            self.specific_status_update = status_update_dict[self.sprite_id]
        self.special_damage = empty_method
        if self.sprite_id in damage_dict:
            self.special_damage = damage_dict[self.sprite_id]

        self.retreat_stage_end = self.battle.base_stage_end + self.sprite_size
        self.retreat_stage_start = -self.sprite_size

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
        self.knock_down_sound_shake = self.knock_down_sound_shake * self.base_body_mass
        self.heavy_dmg_sound_distance = self.heavy_dmg_sound_distance * self.base_body_mass
        self.dmg_sound_distance = self.dmg_sound_distance * self.base_body_mass

        self.hit_volume_mod = self.base_body_mass / 10

    def update(self, dt):
        if self.health:  # only run these when not dead
            if dt:  # only run these when game not pause
                hold_check = False
                self.timer += dt

                if self.health < self.max_health and self.hp_regen:
                    self.health += self.hp_regen * dt
                    if self.health > self.max_health:
                        self.health = self.max_health

                if 0 < self.guarding < 1:
                    self.guarding += dt

                elif not self.guarding and self.guard_meter < self.base_guard:
                    # replenish guard meter when not guarding, always 5 percent per second
                    self.guard_meter += dt * self.guard_meter5
                    if self.guard_meter > self.base_guard:
                        self.guard_meter = self.base_guard

                if self.freeze_timer:
                    self.freeze_timer -= dt
                    if self.freeze_timer < 0:
                        self.freeze_timer = 0

                if self.timer > 0.1:  # Update status and skill
                    if self.combat_state == "Combat" and self.position not in ("Air", "Couch"):
                        self.in_combat_timer -= self.timer
                        if self.in_combat_timer <= 0:
                            if not self.current_action and not self.command_action:
                                # Idle in combat state go to peace state instead
                                self.in_combat_timer = 0
                                self.combat_state = "Peace"
                                self.command_action = self.relax_command_action
                            else:
                                self.in_combat_timer = 2

                    self.nearest_enemy = None
                    self.nearest_ally = None
                    self.near_enemy = sorted({key: key.base_pos.distance_to(self.base_pos) for key in
                                              self.enemy_list}.items(), key=lambda item: item[1])  # sort the closest enemy
                    self.near_ally = sorted(
                        {key: key.base_pos.distance_to(self.base_pos) for key in self.ally_list}.items(),
                        key=lambda item: item[1])  # sort the closest friend
                    if self.near_enemy:
                        self.nearest_enemy = self.near_enemy[0]
                    if self.near_ally:
                        self.nearest_ally = self.near_ally[0]

                    if not self.invincible:
                        self.status_update()
                    self.specific_status_update(self)
                    self.timer -= 0.1

                self.taking_damage_angle = None
                self.ai_update(dt)
                if self.angle != self.new_angle:  # Rotate Function
                    self.rotate_logic()

                self.move_logic(dt)  # Move function

                if self.base_pos[1] < self.ground_pos:
                    self.position = "Air"

                self.health_resource_logic(dt)
                self.specific_update(self, dt)

                # Animation and sprite system
                if self.show_frame >= len(self.current_animation_direction):  # TODO remove when fixed
                    print(self.name, self.show_frame, self.current_animation, self.current_action)

                if "hold" in self.current_animation_direction[self.show_frame]["property"] and \
                    "hold" in self.current_action and \
                        ((not self.current_moveset and "forced move" not in self.current_action) or
                         ("forced move" in self.current_action and (self.x_momentum or self.y_momentum)) or
                         (self.current_moveset and "hold" in self.current_moveset["Property"])):
                    hold_check = True
                    self.hold_timer += dt
                    if self.current_moveset:
                        self.hold_power_bonus = 1
                        if "hold+power" in self.current_moveset["Property"] and self.hold_timer > 1:
                            # hold beyond 1 second to hit harder
                            self.hold_power_bonus = 2.5
                        if "hold+timing" in self.current_moveset["Property"] and 2 >= self.hold_timer >= 1:
                            # hold release at specific time
                            self.hold_power_bonus = 4
                elif self.hold_timer > 0:  # no longer holding, reset timer
                    self.hold_power_bonus = 1
                    self.hold_timer = 0

                done = self.play_animation(dt, hold_check)

                # Pick new animation, condition to stop animation: get interrupt,
                # low level animation got replace with more important one, finish playing, skill animation and its effect end
                if (self.interrupt_animation and "uninterruptible" not in self.current_action) or \
                        ((not self.current_action and self.command_action) or done):
                    # Change position
                    if "couch" in self.current_action:
                        self.position = "Couch"
                    elif "air" in self.current_action:
                        self.position = "Air"
                        self.y_momentum = self.jump_power
                        if self.x_momentum:  # increase y momentum a bit when has x momentum so jump not too short
                            self.y_momentum *= 1.3
                    elif "stand" in self.current_action:
                        self.position = "Stand"

                    if done:
                        if self.current_moveset:
                            if "helper" in self.current_moveset["Property"]:
                                for item in self.current_moveset["Property"]:
                                    if "helper:" in item:
                                        self.battle.helper.interrupt_animation = True
                                        self.battle.helper.command_action = {"name": "special",
                                                                             "drop": item.split(":")[1]}
                        if "drop" in self.current_action:
                            Drop(Vector2(self.base_pos), self.current_action["drop"], self.team)

                    # Reset action check
                    if "next action" in self.current_action and not self.interrupt_animation:
                        # play next action first instead of command if not finish by interruption
                        self.current_action = self.current_action["next action"]
                    elif ("x_momentum" in self.current_action and self.x_momentum) or \
                            ("y_momentum" in self.current_action and self.y_momentum):
                        # action that require movement to run out first before continue to next action
                        pass
                    elif "arrive" in self.current_action and "Arrive2" in self.skill[self.position]:
                        # has arrival (Arrive2) skill to use after finish arriving
                        self.moveset_command_key_input = self.skill[self.position]["Arrive2"]["Buttons"]
                        self.current_action = self.use_skill(self.moveset[self.position][self.moveset_command_key_input])
                    elif "run" in self.current_action and not self.command_action:  # stop running, halt
                        self.current_action = self.halt_command_action
                        if self.angle != 90:
                            self.x_momentum = self.walk_speed
                        else:
                            self.x_momentum = -self.walk_speed
                    elif "halt" in self.current_action:
                        self.x_momentum = 0
                        self.current_action = self.command_action  # continue next action when animation finish
                        self.command_action = {}
                    else:
                        self.current_action = self.command_action  # continue next action when animation finish
                        self.command_action = {}

                    if "land" in self.current_action:
                        # enforce stand position right when start next animation instead of after
                        self.position = "Stand"

                    if "x_momentum" in self.current_action and type(self.current_action["x_momentum"]) is not str and \
                            not self.x_momentum:
                        if type(self.current_action["x_momentum"]) is not str:
                            if self.angle != 90:
                                self.x_momentum = self.current_action["x_momentum"]
                            else:
                                self.x_momentum = -self.current_action["x_momentum"]
                    if "y_momentum" in self.current_action and type(self.current_action["y_momentum"]) is not str and \
                            not self.y_momentum:
                        self.x_momentum = self.current_action["y_momentum"]

                    self.stoppable_frame = False
                    self.hit_enemy = False
                    self.interrupt_animation = False
                    self.release_timer = 0  # reset any release timer

                    self.show_frame = 0
                    self.frame_timer = 0
                    self.move_speed = 0
                    self.pick_animation()

                    self.animation_play_time = self.original_animation_play_time

                if self.broken and (self.retreat_stage_end + self.sprite_size <= self.base_pos[0] or
                                    self.base_pos[0] <= self.retreat_stage_start):
                    self.alive = False  # remove character that pass stage border, enter dead state
                    self.health = 0
                    self.die("flee")

        else:  # die
            if self.alive:  # enter dead state
                self.attack_cooldown = {}  # remove all cooldown
                self.skill_effect = {}  # remove all skill effects
                self.alive = False  # enter dead state
                self.engage_combat()
                self.current_action = self.die_command_action
                self.show_frame = 0
                self.frame_timer = 0
                self.pick_animation()

            if "die" in self.current_action:
                if self.show_frame < self.max_show_frame:  # play die animation
                    self.play_animation(dt, False)
                else:  # finish die animation
                    if self.resurrect_count:  # resurrect back
                        # self.resurrect_count -= 1
                        self.interrupt_animation = True
                        self.alive = True
                        self.command_action = self.standup_command_action
                        self.health = self.max_health
                    else:  # permanent death
                        self.die("dead")
            else:
                self.play_animation(dt, False)

    def ai_update(self, dt):
        pass


class PlayableCharacter(Character):
    def __init__(self, game_id, stat, player_control):
        Character.__init__(self, game_id, stat, player_control=player_control)
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
            if stat[skill]:
                for level in range(int(stat[skill] + 1)):
                    self.common_skill[skill][level] = True

        self.slide_attack = False
        self.tackle_attack = False
        self.dodge_move = False
        if self.common_skill["Ground Movement"][1]:  # can slide attack
            self.slide_attack = True
        if self.common_skill["Ground Movement"][2]:  # can tackle attack
            self.tackle_attack = True
        if self.common_skill["Ground Movement"][3]:  # can slide attack
            pass
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
        if self.common_skill["Air Movement"][3]:  # reduce effect of weight to jump by half
            self.jump_power = 200 - (self.weight / 2)
        if self.common_skill["Air Movement"][4]:  # increase impact resistant while in air position
            self.double_air_impact_resistance = True
        if self.common_skill["Air Movement"][1]:  # can hover in air
            self.hover = True

        self.item_free_use_chance = False
        self.double_food_effect = False
        if self.common_skill["Tinkerer"][1]:  # can slide attack
            self.item
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

        if self.common_skill["Wealth"][1]:  # can slide attack
            pass
        if self.common_skill["Wealth"][2]:  # item may have a chance to be used for free
            pass
        if self.common_skill["Wealth"][3]:  # food has double effect
            pass
        if self.common_skill["Wealth"][4]:  # can slide attack
            pass
        if self.common_skill["Wealth"][5]:  # can slide attack
            pass

        if self.common_skill["Immunity"][1]:  # can slide attack
            pass
        if self.common_skill["Immunity"][2]:  # item may have a chance to be used for free
            pass
        if self.common_skill["Immunity"][3]:  # food has double effect
            pass
        if self.common_skill["Immunity"][4]:  # can slide attack
            pass
        if self.common_skill["Immunity"][5]:  # can slide attack
            pass

        self.hit_resource_regen = False
        self.crash_guard_resource_regen = False
        if self.common_skill["Resourceful"][1]:  # add resource regen
            self.base_resource_regen += self.max_resource * 0.05
        if self.common_skill["Resourceful"][2]:  # resource regen when hit enemy
            self.hit_resource_regen = True
        if self.common_skill["Resourceful"][3]:  # resource regen when crash and guard
            self.crash_guard_resource_regen = True
        if self.common_skill["Resourceful"][4]:  # can slide attack
            pass
        if self.common_skill["Resourceful"][5]:  # can slide attack
            pass

        self.can_crash_boss = False
        self.walk_guard = False
        if self.common_skill["Combat Contest"][1]:  # increase max guard
            self.guard_meter = int(self.base_guard * 1.5)
            self.max_guard = int(self.guard_meter)
            self.guard_meter20 = self.guard_meter * 0.2
            self.guard_meter5 = self.guard_meter * 0.05
        if self.common_skill["Combat Contest"][2]:  # can walk while guarding
            self.walk_guard = True
        if self.common_skill["Combat Contest"][3]:  # can crash boss attack
            self.can_crash_boss = True
        if self.common_skill["Combat Contest"][4]:  # can slide attack
            self.item_free_use_chance = True
        if self.common_skill["Combat Contest"][5]:  # can slide attack
            pass

        self.enter_battle(self.battle.character_animation_data)


class AICharacter(Character):
    def __init__(self, game_id, stat, leader=None):
        Character.__init__(self, game_id, stat)
        self.old_cursor_pos = None
        self.leader = leader
        self.is_boss = stat["Boss"]
        if self.leader:
            self.indicator = CharacterIndicator(self)
        self.ai_move = ai_move_dict["default"]
        if "Ground Y POS" in stat and stat["Ground Y POS"]:  # replace ground pos based on data in stage
            self.ground_pos = stat["Ground Y POS"]

        if stat["AI Behaviour"] in ai_move_dict:
            self.ai_move = ai_move_dict[stat["AI Behaviour"]]

        self.ai_combat = ai_combat_dict["default"]
        if stat["AI Behaviour"] in ai_combat_dict:
            self.ai_combat = ai_combat_dict[stat["AI Behaviour"]]

        self.ai_retreat = ai_retreat_dict["default"]
        if stat["AI Behaviour"] in ai_retreat_dict:
            self.ai_retreat = ai_retreat_dict[stat["AI Behaviour"]]

        for item in stat["Property"]:  # set attribute from property
            self.__setattr__(item, True)
        self.max_attack_range = 0
        self.resurrect_count = 0
        self.ai_timer = 0  # for whatever timer require for AI action
        self.ai_movement_timer = 0  # timer to move for AI
        self.end_ai_movment_timer = randint(2, 6)

        for position in self.moveset.values():
            for move in position.values():
                if self.max_attack_range < move["Range"]:
                    self.max_attack_range = move["Range"]

        self.enter_battle(self.battle.character_animation_data)

    def ai_update(self, dt):
        if self.ai_timer:
            self.ai_timer += dt
        if self.ai_movement_timer:
            self.ai_movement_timer += dt
        if not self.broken:
            self.ai_combat(self)
            self.ai_move(self, dt)
        else:
            self.ai_retreat(self)


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
        self.owner_layer = self.owner.layer
        self.angle = self.owner.angle
        self._layer = 10
        sprite.Sprite.__init__(self, self.containers)
        self.part = part
        self.part_name = self.part[3:]
        if self.part_name[0:2] == "l_" or self.part_name[0:2] == "r_":
            self.part_name = self.part_name[2:]
        if "special" in self.part:
            self.part = self.part[:-2]
        self.original_can_hurt = can_hurt
        self.can_hurt = can_hurt
        self.can_deal_dmg = False
        self.aoe = False
        self.dmg = None
        self.friend_status_effect = ()
        self.enemy_status_effect = ()
        self.impact = (0, 0)
        self.element = None
        self.critical_chance = None
        self.mode = "Normal"
        self.already_hit = []
        self.image = self.empty_surface
        self.data = []
        self.sprite_ver = str(self.owner.sprite_ver)
        self.rect = self.image.get_rect(topleft=(0, 0))

    def get_part(self, data, new_animation):
        self.dmg = 0
        self.can_deal_dmg = False
        self.angle = self.owner.angle
        self.mode = self.owner.mode_list[self.owner.mode][self.part]
        self.friend_status_effect = ()
        self.enemy_status_effect = ()
        if new_animation:
            self.already_hit = []
        elif self.owner.current_moveset and "multiframehit" in self.owner.current_moveset["Property"]:
            self.already_hit = []

        if data[8]:
            self.can_deal_dmg = True
            find_damage(self)
        if self.data != data:
            self.data = data
            if "weapon" in self.part_name:
                self.image = self.body_sprite_pool[self.data[0]][self.sprite_ver][self.mode][self.data[1]]
            elif "special" in self.part_name:
                self.image = self.body_sprite_pool[self.data[0]]["special"][self.sprite_ver][self.mode][self.data[1]]
            else:
                self.image = self.body_sprite_pool[self.data[0]][self.part_name][self.sprite_ver][self.mode][self.data[1]]
            if self.data[7] != 1:  # scale size
                self.image = pygame.transform.smoothscale(self.image, (self.image.get_width() * self.data[7],
                                                                       self.image.get_height() * self.data[7]))
            if self.data[5]:  # flip
                if self.data[5] == 1:
                    self.image = pygame.transform.flip(self.image, True, False)
                elif self.data[5] == 2:
                    self.image = pygame.transform.flip(self.image, False, True)
                elif self.data[5] == 3:
                    self.image = pygame.transform.flip(self.image, True, True)
            if self.data[4]:  # rotation
                self.image = pygame.transform.rotate(self.image, self.data[4])
            self.re_rect()
            if self._layer != self.owner_layer + 100 - data[6]:
                self.battle_camera.change_layer(self, self.owner_layer + 100 - data[6])

    def re_rect(self):
        if self.data:
            if self not in self.battle_camera:  # was remove because no data previously
                for team in self.battle.all_team_enemy_part:
                    if team != self.team:  # add back part to enemy part list of other team
                        self.battle.all_team_enemy_part[team].add(self)
                self.battle_camera.add(self)

            self.rect = self.image.get_rect(center=((self.owner.pos[0] + (self.data[2] * self.screen_scale[0])),
                                                    (self.owner.pos[1] + (self.data[3] * self.screen_scale[1]))))
        else:
            if self in self.battle_camera:
                for team in self.battle.all_team_enemy_part:
                    if team != self.team:  # remove part from enemy part list of other team
                        self.battle.all_team_enemy_part[team].remove(self)
                self.battle_camera.remove(self)
            # self.rect = self.image.get_rect(topleft=(0, 0))

    def update(self, dt):
        if self.owner.alive:
            if self.can_deal_dmg:
                self.hit_collide_check()
            if not self.owner.no_pickup:
                self.drop_collide_check()


def find_damage(self):
    if not self.owner.current_moveset:  # TODO remove later
        print(self.owner.name, self.owner.current_action, self.owner.show_frame)
    self.dmg = self.owner.current_moveset["Power"] + self.owner.power_bonus * self.owner.hold_power_bonus
    self.element = self.owner.current_moveset["Element"]
    self.impact = ((self.owner.current_moveset["Push Impact"] - self.owner.current_moveset["Pull Impact"]) *
                   self.owner.attack_impact_effect,
                   (self.owner.current_moveset["Down Impact"] - self.owner.current_moveset["Up Impact"]) *
                   self.owner.attack_impact_effect)
    if self.element == "Physical":
        self.dmg = uniform(self.dmg * self.owner.min_physical, self.dmg * self.owner.max_physical)
    else:
        self.dmg = uniform(self.dmg * self.owner.min_elemental, self.dmg * self.owner.max_elemental)
    self.critical_chance = self.owner.critical_chance + self.owner.current_moveset["Critical Chance Bonus"]
    self.friend_status_effect = self.owner.current_moveset["Status"]
    self.enemy_status_effect = self.owner.current_moveset["Enemy Status"]
