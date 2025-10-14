from math import radians
from random import choice, uniform

from pygame import Vector2
from pygame.sprite import Sprite, collide_mask

from engine.constants import *
from engine.character.apply_status import apply_status

from engine.effect.adjust_sprite import adjust_sprite, damage_effect_adjust_sprite
from engine.effect.cal_dmg import cal_dmg
from engine.effect.find_random_direction import find_random_direction
from engine.effect.hit_collide_check import hit_collide_check
from engine.effect.hit_register import hit_register
from engine.effect.move_logic import move_logic
from engine.effect.play_animation import play_animation
from engine.effect.reach_target import reach_target
from engine.effect.remain_logic import remain_logic

from engine.utils.common import calculate_projectile_velocity, clean_object
from engine.utils.rotation import set_rotate, convert_projectile_degree_angle


class Effect(Sprite):
    apply_status = apply_status
    clean_object = clean_object
    set_rotate = set_rotate

    effect_animation_pool = None
    effect_list = None
    sound_effect_pool = {}
    battle = None
    screen_scale = (1, 1)

    height_map = None

    adjust_sprite = adjust_sprite
    cal_dmg = cal_dmg
    find_random_direction = find_random_direction
    hit_collide_check = hit_collide_check
    hit_register = hit_register
    move_logic = move_logic
    play_animation = play_animation
    reach_target = reach_target
    remain_logic = remain_logic

    Base_Animation_Play_Time = Base_Animation_Play_Time
    Default_Ground_Pos = Default_Ground_Pos

    def __init__(self, owner, part_stat, layer, moveset=None, base_target_pos=None, from_owner=True,
                 reach_effect=None):
        """Effect sprite that does not affect character on its own but can travel and
        create other Effect when reach target"""
        # TODO add end effect animation before removal

        self.y_move = False
        if layer:  # use layer for checking if effect move in vertical angle as well
            self.y_move = True
        self._layer = 999999999999999999999997

        Sprite.__init__(self, self.containers)
        self.battle_camera = self.battle.battle_cameras["battle"]
        self.battle_camera.add(self)
        self.show_frame = 0
        self.frame_timer = 0
        self.renew_sprite = True
        self.repeat_animation = False
        self.base_stage_end = self.battle.base_stage_end
        self.is_effect_type = True
        self.base_target_pos = base_target_pos

        self.owner = owner
        self.part_stat = part_stat
        self.effect_name = self.part_stat[0]
        self.part_name = self.part_stat[1]
        if self.part_name.split("_")[-1].isdigit():
            self.part_name = " ".join(self.part_name.split("_")[:-1])

        if self.owner and from_owner:
            self.pos = Vector2(self.owner.pos[0] + (self.part_stat[2] * self.screen_scale[0]),
                               self.owner.pos[1] + (self.part_stat[3] * self.screen_scale[1]))
            self.base_ground_pos = self.owner.base_ground_pos
        else:
            self.pos = Vector2(self.part_stat[2], self.part_stat[3])
            self.base_ground_pos = self.Default_Ground_Pos
        self.grid_range = range(0, 1)
        self.base_pos = Vector2(self.pos[0] / self.screen_scale[0], self.pos[1] / self.screen_scale[1])
        self.start_pos = Vector2(self.base_pos)
        self.angle = self.part_stat[4]
        self.sprite_flip = self.part_stat[5]
        self.width_scale = self.part_stat[7]
        self.height_scale = self.part_stat[8]
        self.remain_reach = False
        self.remain_timer = 0
        self.reach_effect = reach_effect
        self.one_hit_per_enemy = False

        self.travel_distance = 0
        self.travel_progress = 0
        self.travel = False

        self.sound_effect = None
        self.sound_timer = 0
        self.sound_duration = 0
        self.shake_value = 0
        self.duration = 0
        self.max_duration = 0
        self.x_momentum = 0  # only use for reach bouncing off
        self.y_momentum = 0

        self.random_move = False

        self.other_property = None
        if self.owner:
            self.offence = self.owner.offence
            self.dmg = self.owner.dmg
            self.element = self.owner.element
            self.impact = self.owner.impact
            self.impact_sum = self.owner.impact_sum
            self.critical_chance = self.owner.critical_chance
            self.enemy_status_effect = self.owner.enemy_status_effect
            self.no_defence = self.owner.no_defence
            self.no_dodge = self.owner.no_dodge
            self.team = self.owner.team
            self.enemy_collision_grids = self.owner.ground_enemy_collision_grids
            self.penetrate = self.owner.penetrate
        self.current_moveset = moveset

        self.speed = 0
        if self.effect_name in self.effect_list:
            self.effect_stat = self.effect_list[self.effect_name]
            self.speed = self.effect_stat["Travel Speed"]
            self.reach_effect = self.effect_stat["After Reach Effect"]
            self.remain_reach = self.effect_stat["Reach Effect"]
            self.duration = self.effect_stat["Duration"]
            self.shake_value = self.effect_stat["Shake Value"]
            self.max_duration = self.duration
            if self.max_duration:
                self.repeat_animation = True
            if self.effect_stat["Sound Effect"] and self.effect_stat["Sound Effect"] in self.sound_effect_pool:
                self.sound_distance = self.effect_stat["Sound Distance"]
                self.sound_effect = choice(self.sound_effect_pool[self.effect_stat["Sound Effect"]])
                self.sound_duration = self.sound_effect.get_length()
                self.sound_timer = self.sound_duration
                if self.sound_duration > 2 and self.travel_distance:
                    self.sound_timer = self.sound_duration / 0.5

            if moveset:
                self.other_property = moveset["Property"]
                if self.current_moveset["Range"] and "no travel" not in self.effect_stat["Property"]:
                    # effect in moveset with range mean the effect can move on its own
                    self.travel = True
                    self.travel_distance = self.current_moveset["Range"]
                if "random move" in moveset["Property"]:
                    self.random_move = True
                if "one hit per enemy" in moveset["Property"]:
                    self.one_hit_per_enemy = True

                if ("enemy" in self.current_moveset["AI Condition"] and
                        "target_type" in self.current_moveset["AI Condition"]["enemy"] and
                        self.current_moveset["AI Condition"]["enemy"]["target_type"] == "air"):
                    # effect intend to hit air enemy only
                    self.enemy_collision_grids = self.owner.air_enemy_collision_grids

        if self.base_target_pos:
            if "no target" not in self.current_moveset["Property"]:
                target_distance = self.base_target_pos[0] - self.base_pos[0]
                if self.travel_distance > target_distance:
                    self.travel_distance = target_distance
            if "arc" in self.current_moveset["Property"]:
                # arc effect destination is enemy target rather than as far as it can travel
                if self.current_moveset["Property"]["arc"] == "high":  # change angle for arc projectile effect
                    self.angle = uniform(60, 85)
                else:
                    self.angle = uniform(30, 55)
                if self.owner.direction == "left":
                    self.angle *= -1

                if self.current_moveset:
                    offence_mistake = self.offence
                    if offence_mistake > 100:
                        offence_mistake = 100
                    offence_mistake = 1 - (offence_mistake / 100)
                    if offence_mistake < 0:
                        offence_mistake = 0
                    offence_mistake = self.travel_distance / 2 * offence_mistake
                    self.travel_distance = uniform(self.travel_distance - offence_mistake,
                                                   self.travel_distance + offence_mistake)
            else:
                # convert from data angle to projectile calculable
                self.angle = convert_projectile_degree_angle(self.angle)

            self.velocity = calculate_projectile_velocity(self.angle, self.travel_distance)
            if type(self.velocity) is complex:
                self.velocity = 10000
            # print(self.velocity, self.angle, self.travel_distance)

        if not self.speed:  # reset travel distance for effect with no speed
            self.travel_distance = 0

        self.projectile_angle = radians(self.angle)

        self.animation_pool = self.effect_animation_pool[self.effect_name]
        self.current_animation = self.animation_pool[self.part_name][self.sprite_flip][self.width_scale][
            self.height_scale]

        self.animation_play_time = self.Base_Animation_Play_Time
        if len(self.current_animation) == 1:  # effect with no animation play a bit longer
            self.animation_play_time = 0.2

        self.base_image = self.current_animation[self.show_frame]
        self.image = None
        self.adjust_sprite()

    def update(self, dt):
        if self.remain_timer:  # already reach target and now either sticking or bouncing off
            self.remain_logic(dt)

        else:
            if self.sound_effect:
                if self.sound_timer < self.sound_duration:
                    self.sound_timer += dt
                else:  # play sound
                    self.battle.add_sound_effect_queue(self.sound_effect, self.pos,
                                                       self.sound_distance, self.shake_value)
                    self.sound_effect = None

            done, just_start = self.play_animation(self.animation_play_time, dt, False)

            if self.move_logic(dt, done):
                return

    def cutscene_update(self, dt):
        """All type of effect update the same during cutscene"""
        self.update(dt)


class DamageEffect(Effect):
    adjust_sprite = damage_effect_adjust_sprite
    collision_grid_width = 0

    def __init__(self, owner, stat, layer, moveset, base_target_pos=None, from_owner=True):
        Effect.__init__(self, owner, stat, layer, moveset=moveset, base_target_pos=base_target_pos,
                        from_owner=from_owner)
        self.impact_effect = None
        self.already_hit = []  # list of character already got hit with time by sprite for sprite with no duration

        self.enemy_status_effect = self.current_moveset["Enemy Status"]

    def update(self, dt):
        if self.remain_timer:  # already reach target and now either sticking or bouncing off
            self.remain_logic(dt)
        else:
            if self.sound_effect:
                if self.sound_timer < self.sound_duration:
                    self.sound_timer += dt
                else:  # play sound
                    self.battle.add_sound_effect_queue(self.sound_effect, self.pos,
                                                       self.sound_distance, self.shake_value)
                    self.sound_effect = None

            if not self.hit_collide_check():
                if self.duration:  # only clear for sprite with duration
                    self.duration -= dt
                    if self.duration <= 0:
                        self.reach_target()
                        return

                done, just_start = self.play_animation(self.animation_play_time, dt, False)

                if just_start and self.duration and not self.one_hit_per_enemy:
                    # reset already hit every animation frame for effect with duration and not with one hit condition
                    self.already_hit = []
                self.move_logic(dt, done)


class TrapEffect(Effect):
    adjust_sprite = damage_effect_adjust_sprite

    def __init__(self, owner, stat, layer, moveset, from_owner=True):
        """Trap sprite generated from moveset rather than its own character that can trigger when character come near,
        the trap sprite itself does no damage"""
        Effect.__init__(self, owner, stat, layer, moveset=moveset, from_owner=from_owner)
        self.activate = False
        self.impact_effect = None
        self.moveset = moveset
        # self.travel_distance = 0
        # if not layer:  # layer 0 in animation part data mean the effect can move on its own
        #     self.travel_distance = self.moveset["Range"]

        self.other_property = self.moveset["Property"]

    def update(self, dt):
        if self.sound_effect and self.sound_timer < self.sound_duration:
            self.sound_timer += dt

        done, just_start = self.play_animation(self.animation_play_time, dt)

        if self.activate and done:
            if self.sound_effect:
                # play sound, check for distance here to avoid timer reset when not on screen
                self.battle.add_sound_effect_queue(self.sound_effect, self.pos,
                                                   self.sound_distance, 0)
            self.reach_target()
            return

        if self.duration > 0:
            self.duration -= dt
            if self.duration <= 0:  # activate when trap duration run out
                self.activate_trap()

        for enemy in self.enemy_collision_grids:
            if enemy.health and collide_mask(self, enemy):
                # activate when enemy collide
                self.activate_trap()
                break

    def activate_trap(self):
        # change image to activate
        self.current_animation = self.animation_pool["Activate"][self.sprite_flip][self.width_scale][self.height_scale]
        self.animation_play_time = self.Base_Animation_Play_Time  # reset animation play speed
        if len(self.current_animation) == 1:  # effect with no animation play a bit longer
            self.animation_play_time = 0.2
        self.base_image = self.current_animation[self.show_frame]
        self.renew_sprite = True
        self.adjust_sprite()
        self.activate = True
        self.repeat_animation = False


class StatusEffect(Effect):
    def __init__(self, owner, stat, layer):
        Effect.__init__(self, owner, stat, layer, None)
        self.pos = self.owner.pos
        self.rect.midbottom = self.owner.pos

    def update(self, dt):
        done, just_start = self.play_animation(self.animation_play_time, dt)
        self.pos = self.owner.pos
        self.rect.midbottom = self.owner.pos

        if self.sound_effect and self.sound_timer < self.sound_duration:
            self.sound_timer += dt

        if self.sound_effect and self.sound_timer >= self.sound_duration and \
                self.sound_distance > self.battle.camera_pos.distance_to(self.pos):
            # play sound, check for distance here to avoid timer reset when not on screen
            self.battle.add_sound_effect_queue(self.sound_effect, self.pos,
                                               self.sound_distance, 0)
            self.sound_effect = None

        if done:  # no duration, kill effect when animation end
            self.clean_object()
            return
