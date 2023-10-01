from math import cos, sin, radians
from random import choice, uniform, randint

from pygame import sprite, mixer, Vector2


class Effect(sprite.Sprite):
    from engine.character.apply_status import apply_status
    apply_status = apply_status

    from engine.utils.common import clean_object
    clean_object = clean_object
    from engine.utils.rotation import set_rotate
    set_rotate = set_rotate

    effect_sprite_pool = None
    effect_animation_pool = None
    effect_list = None
    sound_effect_pool = {}
    battle = None
    screen_scale = (1, 1)

    height_map = None

    from engine.effect.adjust_sprite import adjust_sprite
    adjust_sprite = adjust_sprite

    from engine.effect.cal_dmg import cal_dmg
    cal_dmg = cal_dmg

    from engine.effect.find_random_direction import find_random_direction
    find_random_direction = find_random_direction

    from engine.effect.hit_collide_check import hit_collide_check
    hit_collide_check = hit_collide_check

    from engine.effect.hit_register import hit_register
    hit_register = hit_register

    from engine.effect.play_animation import play_animation
    play_animation = play_animation

    def __init__(self, owner, stat, layer, from_owner=True):
        """Effect sprite that does not affect character in any way"""

        if layer:  # use layer based on owner and animation data
            self._layer = layer
        else:  # effect with 0 layer 0 will always be at top instead
            self._layer = 9999999999999999997
        sprite.Sprite.__init__(self, self.containers)

        self.show_frame = 0
        self.frame_timer = 0
        self.timer = 0
        self.repeat_animation = False
        self.stage_end = self.battle.base_stage_end

        self.owner = owner
        self.stat = stat
        effect_name = self.stat[0]
        part_name = self.stat[1]
        if self.owner and from_owner:
            self.sprite_ver = self.owner.sprite_ver
            self.pos = Vector2(self.owner.pos[0] + (self.stat[2] * self.screen_scale[0]),
                               self.owner.pos[1] + (self.stat[3] * self.screen_scale[1]))
        else:
            self.pos = Vector2(self.stat[2], self.stat[3])
            self.sprite_ver = str(self.battle.chapter)
        self.base_pos = Vector2(self.pos[0] / self.screen_scale[0], self.pos[1] / self.screen_scale[1])

        self.angle = self.stat[4]

        self.sound_effect_name = None
        self.sound_timer = 0
        self.sound_duration = 0
        self.scale_size = 1

        if effect_name in self.effect_list:
            self.effect_stat = self.effect_list[effect_name]
            self.speed = self.effect_stat["Travel Speed"]

            if effect_name in self.sound_effect_pool:
                self.travel_sound_distance = self.effect_stat["Sound Distance"]
                self.travel_shake_power = self.effect_stat["Shake Power"]
                self.sound_effect_name = choice(self.sound_effect_pool[effect_name])
                self.sound_duration = mixer.Sound(self.sound_effect_name).get_length()
                self.sound_timer = 0  # start playing right away when first update

        self.animation_pool = self.effect_animation_pool[effect_name][self.sprite_ver]
        self.current_animation = self.animation_pool[part_name]

        self.image = self.current_animation[self.show_frame]
        if len(self.current_animation) == 1:  # one frame mean no animation
            self.current_animation = {}

        self.adjust_sprite()

    def update(self, dt):
        done, just_start = self.play_animation(0.1, dt)

        if self.sound_effect_name and self.sound_timer < self.sound_duration:
            self.sound_timer += dt

        if self.sound_effect_name and self.sound_timer >= self.sound_duration and \
                self.travel_sound_distance > self.battle.camera_pos.distance_to(self.pos):
            # play sound, check for distance here to avoid timer reset when not on screen
            self.battle.add_sound_effect_queue(self.sound_effect_name, self.pos,
                                               self.travel_sound_distance,
                                               self.travel_shake_power)
            self.sound_timer = 0

        if done:  # no duration, kill effect when animation end
            self.clean_object()
            return


class DamageEffect(Effect):
    def __init__(self, owner, stat, layer, moveset, from_owner=True, arc_shot=False, degrade_when_travel=True,
                 degrade_when_hit=True, random_direction=False, random_move=False, reach_effect=None):
        """Effect damage sprite that can affect character in some ways such as arrow, explosion, buff magic"""
        Effect.__init__(self, owner, stat, layer, from_owner=from_owner)
        self.impact_effect = None
        self.arc_shot = arc_shot
        self.reach_effect = reach_effect

        self.degrade_when_travel = degrade_when_travel
        self.degrade_when_hit = degrade_when_hit
        self.random_direction = random_direction
        self.random_move = random_move

        self.max_duration = 0
        self.duration = 0
        self.sound_effect_name = None
        self.stamina_dmg_bonus = 0
        self.sprite_direction = ""
        self.attacker_sprite_direction = self.owner.sprite_direction
        self.already_hit = []  # list of character already got hit with time by sprite for sprite with no duration

        self.dmg = 0
        self.moveset = moveset
        self.other_property = self.moveset["Property"]
        self.find_damage(self.moveset)
        self.deal_dmg = False
        self.penetrate = False
        if self.dmg:  # has damage to deal
            self.deal_dmg = True
            if "penetrate" in self.moveset["Damage Effect Property"]:
                self.penetrate = True

        self.friend_status_effect = self.moveset["Status"]
        self.enemy_status_effect = self.moveset["Enemy Status"]

        self.travel_distance = 0
        if not layer:  # layer 0 in animation part data mean the effect can move on its own
            self.travel_distance = self.moveset["Range"]

        if "Duration" in self.moveset:
            self.max_duration = self.duration
            self.duration = self.moveset["Duration"]
            self.repeat_animation = True
        self.distance_progress = 0

        if self.stat[0] in self.sound_effect_pool:
            self.travel_sound_distance = self.effect_stat["Sound Distance"]
            self.travel_shake_power = self.effect_stat["Shake Power"]
            self.sound_effect_name = choice(self.sound_effect_pool[self.stat[0]])
            self.sound_duration = mixer.Sound(self.sound_effect_name).get_length()
            self.sound_timer = self.sound_duration
            self.travel_sound_distance_check = self.travel_sound_distance * 2
            if self.sound_duration > 2:
                self.sound_timer = self.sound_duration / 0.5

    def find_damage(self, moveset):
        self.dmg = moveset["Power"] + self.owner.power_bonus * self.owner.hold_power_bonus
        self.element = moveset["Element"]
        self.impact = ((moveset["Push Impact"] - moveset["Pull Impact"]) *
                       self.owner.attack_impact_effect,
                       (moveset["Down Impact"] - moveset["Up Impact"]) *
                       self.owner.attack_impact_effect)
        if self.element == "Physical":
            self.dmg = uniform(self.dmg * self.owner.min_physical, self.dmg * self.owner.max_physical)
        else:
            self.dmg = uniform(self.dmg * self.owner.min_elemental, self.dmg * self.owner.max_elemental)
        self.critical_chance = self.owner.critical_chance + moveset["Critical Chance Bonus"]
        self.friend_status_effect = moveset["Status"]
        self.enemy_status_effect = moveset["Enemy Status"]

    def reach_target(self, how=None):
        self.deal_dmg = False
        if self.reach_effect:
            effect_stat = self.effect_list[self.reach_effect]
            DamageEffect(self.owner, effect_stat, self._layer, (), from_owner=False,
                         reach_effect=effect_stat["After Reach Effect"])

        if "End Effect" in self.stat:
            finish_effect = self.stat["End Effect"]
            if finish_effect:
                effect_stat = self.effect_list[finish_effect]
                DamageEffect(self.owner, effect_stat, self._layer, (), from_owner=False,
                             reach_effect=effect_stat["After Reach Effect"])

        if self.other_property:
            if "spawn" in self.other_property and "spawn_after" in self.other_property and how == "border":
                if "spawn_same" in self.other_property:  # spawn same effect
                    stat = self.stat.copy()
                    if "spawn_sky" in self.other_property:
                        stat[3] = -100
                    if "spawn_target" in self.other_property:
                        if self.owner.nearest_enemy:  # find the nearest enemy to target
                            if self.owner.sprite_direction == "l_side":
                                stat[2] = uniform(self.owner.nearest_enemy[0].pos[0],
                                                  self.owner.nearest_enemy[0].pos[0] + (200 * self.screen_scale[0]))
                            else:
                                stat[2] = uniform(self.owner.nearest_enemy[0].pos[0] - (200 * self.screen_scale[0]),
                                                  self.owner.nearest_enemy[0].pos[0])

                            self.pos = (stat[2], stat[3])
                            stat[4] = self.set_rotate(self.owner.nearest_enemy[0].pos, use_pos=True)

                        else:  # random target instead
                            stat[2] = uniform(self.pos[0] - (self.travel_distance * self.screen_scale[0]),
                                              self.pos[0] + (self.travel_distance * self.screen_scale[0]))
                            if self.owner.sprite_direction == "l_side":
                                stat[4] = randint(160, 180)
                            else:
                                stat[4] = randint(-180, -160)

                    moveset = self.moveset.copy()
                    moveset["Property"] = [item for item in moveset["Property"] if
                                           item != "spawn"]  # remove spawn property so it not loop spawn
                    DamageEffect(self.owner, stat, 0, moveset, from_owner=False,
                                 reach_effect=self.reach_effect)

        self.clean_object()

    def update(self, dt):
        # for key in tuple(self.already_hit.keys()):
        #     self.already_hit[key] -= dt
        #     if self.already_hit[key] <= 0:
        #         self.already_hit.pop(key)

        if not self.hit_collide_check(effect=True):
            if self.sound_effect_name and self.sound_timer < self.sound_duration:
                self.sound_timer += dt

            self.timer += dt

            if self.duration > 0:  # only clear for sprite with duration
                self.duration -= dt

            done, just_start = self.play_animation(0.05, dt, False)

            if self.travel_distance:  # damage sprite that can move
                new_pos = Vector2(self.base_pos[0] - (self.speed * sin(radians(self.angle))),
                                  self.base_pos[1] - (self.speed * cos(radians(self.angle))))
                move = new_pos - self.base_pos
                if move.length():  # sprite move
                    move.normalize_ip()
                    move = move * self.speed * dt

                    self.base_pos += move
                    self.travel_distance -= move.length()
                    self.pos = Vector2(self.base_pos[0] * self.screen_scale[0], self.base_pos[1] * self.screen_scale[1])
                    self.rect.center = self.pos

                    if not self.random_move and (
                            self.base_pos[0] <= 0 or self.base_pos[0] > self.stage_end or
                            self.base_pos[1] >= self.owner.original_ground_pos or
                            self.base_pos[1] < -500):  # pass outside of map
                        self.reach_target("border")
                        return

                    if self.degrade_when_travel and self.dmg:  # dmg power drop the longer damage sprite travel
                        if self.dmg > 1:
                            self.dmg -= 0.1

            if self.travel_distance <= 0 or (done and self.max_duration and self.duration <= 0):
                self.reach_target("border")
                return

            if self.sound_effect_name and self.sound_timer >= self.sound_duration and \
                    self.travel_sound_distance_check > self.battle.camera_pos.distance_to(self.pos):
                # play sound, check for distance here to avoid timer reset when not on screen
                self.battle.add_sound_effect_queue(self.sound_effect_name, self.pos,
                                                   self.travel_sound_distance,
                                                   self.travel_shake_power)
                self.sound_timer = 0


class StatusEffect(Effect):
    def __init__(self, owner, stat, layer):
        Effect.__init__(self, owner, stat, layer)
        self.pos = self.owner.pos
        self.rect.midbottom = self.owner.pos

    def update(self, dt):
        done, just_start = self.play_animation(0.1, dt)
        self.pos = self.owner.pos
        self.rect.midbottom = self.owner.pos

        if self.sound_effect_name and self.sound_timer < self.sound_duration:
            self.sound_timer += dt

        if self.sound_effect_name and self.sound_timer >= self.sound_duration and \
                self.travel_sound_distance > self.battle.camera_pos.distance_to(self.pos):
            # play sound, check for distance here to avoid timer reset when not on screen
            self.battle.add_sound_effect_queue(self.sound_effect_name, self.pos,
                                               self.travel_sound_distance,
                                               self.travel_shake_power)
            self.sound_timer = 0

        if done:  # no duration, kill effect when animation end
            self.clean_object()
            return
