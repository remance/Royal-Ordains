from math import cos, sin, radians
from random import uniform, randint

from pygame import sprite, Vector2
from pygame.sprite import spritecollide, collide_mask

from engine.drop.drop import Drop
from engine.utils.rotation import rotation_xy


class Effect(sprite.Sprite):
    from engine.character.apply_status import apply_status
    apply_status = apply_status

    from engine.utils.common import clean_object
    clean_object = clean_object
    from engine.utils.rotation import set_rotate
    set_rotate = set_rotate

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

    def __init__(self, owner, part_stat, layer, from_owner=True):
        """Effect sprite that does not affect character in any way"""
        # TODO add end effect animation before removal

        if layer:  # use layer based on owner and animation data
            self._layer = layer
        else:  # effect with 0 layer 0 will always be at top instead
            self._layer = 9999999999999999997
        sprite.Sprite.__init__(self, self.containers)

        self.show_frame = 0
        self.frame_timer = 0
        self.repeat_animation = False
        self.stage_end = self.battle.base_stage_end

        self.object_type = "effect"

        self.fall_gravity = self.battle.original_fall_gravity

        self.owner = owner
        self.part_stat = part_stat
        self.effect_name = self.part_stat[0]
        self.part_name = self.part_stat[1]
        if self.part_name.split(" ")[-1].isdigit():
            self.part_name = " ".join(self.part_name.split(" ")[:-1])

        if self.owner and from_owner:
            self.sprite_ver = self.owner.sprite_ver
            self.pos = Vector2(self.owner.pos[0] + (self.part_stat[2] * self.screen_scale[0]),
                               self.owner.pos[1] + (self.part_stat[3] * self.screen_scale[1]))
        else:
            self.pos = Vector2(self.part_stat[2], self.part_stat[3])
            self.sprite_ver = str(self.battle.chapter)
        self.base_pos = Vector2(self.pos[0] / self.screen_scale[0], self.pos[1] / self.screen_scale[1])
        self.angle = self.part_stat[4]
        self.scale = self.part_stat[7]
        self.flip = self.part_stat[5]

        self.sound_effect_name = None
        self.sound_timer = 0
        self.sound_duration = 0
        self.duration = 0
        self.max_duration = 0
        self.x_momentum = 0  # only use for reach bouncing off
        self.y_momentum = 0

        self.stick_reach = False
        self.stuck_part = None  # part or pos that effect get stick at
        self.base_stuck_stat = ()
        self.stick_timer = 0

        if self.effect_name in self.effect_list:
            self.effect_stat = self.effect_list[self.effect_name]
            self.speed = self.effect_stat["Travel Speed"]

            self.stick_reach = self.effect_stat["Reach Effect"]
            self.duration = self.effect_stat["Duration"]
            self.max_duration = self.duration
            if self.max_duration:
                self.repeat_animation = True

            # if self.effect_name in self.sound_effect_pool:
            #     self.travel_sound_distance = self.effect_stat["Sound Distance"]
            #     self.sound_effect_name = choice(self.sound_effect_pool[self.effect_name])
            #     self.sound_duration = mixer.Sound(self.sound_effect_name).get_length()
            #     self.sound_timer = self.sound_duration
            #     self.travel_sound_distance_check = self.travel_sound_distance * 2
            #     if self.sound_duration > 2:
            #         self.sound_timer = self.sound_duration / 0.5

        self.animation_pool = self.effect_animation_pool[self.effect_name][self.sprite_ver]
        self.current_animation = self.animation_pool[self.part_name][self.scale]

        self.base_image = self.current_animation[self.show_frame][self.flip]
        self.image = self.base_image

        self.adjust_sprite()

    def update(self, dt):
        done, just_start = self.play_animation(0.05, dt)

        if self.sound_effect_name and self.sound_timer < self.sound_duration:
            self.sound_timer += dt

        if self.sound_effect_name and self.sound_timer >= self.sound_duration and \
                self.travel_sound_distance > self.battle.camera_pos.distance_to(self.pos):
            # play sound, check for distance here to avoid timer reset when not on screen
            self.battle.add_sound_effect_queue(self.sound_effect_name, self.pos,
                                               self.travel_sound_distance, 0)
            self.sound_timer = 0

        if done:  # no duration, kill effect when animation end
            self.clean_object()
            return

    def cutscene_update(self, dt):
        """All type of effect update the same during cutscene"""
        self.update(dt)


class DamageEffect(Effect):
    def __init__(self, owner, part_stat, layer, moveset, from_owner=True, arc_shot=False, degrade_when_travel=True,
                 degrade_when_hit=True, random_direction=False, random_move=False, reach_effect=None):
        """Effect damage sprite that can affect character in some ways such as arrow, explosion, buff magic"""
        Effect.__init__(self, owner, part_stat, layer, from_owner=from_owner)
        self.impact_effect = None
        self.arc_shot = arc_shot
        self.reach_effect = reach_effect

        self.degrade_when_travel = degrade_when_travel
        self.degrade_when_hit = degrade_when_hit
        self.random_direction = random_direction
        self.random_move = random_move

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
        self.no_dodge = False
        self.no_defence = False
        self.no_guard = False
        if self.dmg:  # has damage to deal
            self.deal_dmg = True
        if "penetrate" in self.moveset["Property"]:
            self.penetrate = True
        if "no dodge" in self.moveset["Property"]:
            self.no_dodge = True
        if "no defence" in self.moveset["Property"]:
            self.no_defence = True
        if "no guard" in self.moveset["Property"]:
            self.no_guard = True

        self.effect_collide_check = True
        if "no effect collision" in self.effect_stat["Property"]:
            self.battle.all_damage_effects.remove(self)
            self.effect_collide_check = False

        self.friend_status_effect = self.moveset["Status"]
        self.enemy_status_effect = self.moveset["Enemy Status"]

        self.travel_distance = 0
        self.travel = False
        if not layer and self.moveset["Range"]:
            # layer 0 in animation part data mean the effect can move on its own
            self.travel = True
            self.travel_distance = self.moveset["Range"]

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
        if self.dmg < 0:
            self.dmg = 0
        self.critical_chance = self.owner.critical_chance + moveset["Critical Chance Bonus"]
        self.friend_status_effect = moveset["Status"]
        self.enemy_status_effect = moveset["Enemy Status"]

    def reach_target(self, how=None):
        self.deal_dmg = False
        if self.reach_effect:
            effect_stat = self.effect_list[self.reach_effect]
            new_pos = self.pos
            if "reach spawn ground" in self.effect_stat["Property"]:  # reach effect spawn with rect bottom on ground
                height = self.effect_animation_pool[self.reach_effect][self.sprite_ver]["Base"][self.scale][0][
                             self.flip].get_height() / 4
                new_pos = (self.pos[0], self.pos[1] - height)
            DamageEffect(self.owner, (self.reach_effect, "Base", new_pos[0], new_pos[1], 0, 0, 0, 1),
                         self._layer, self.moveset, from_owner=False,
                         reach_effect=effect_stat["After Reach Effect"])

        if self.other_property:
            if "spawn" in self.other_property and "spawn_after" in self.other_property and how == "border":
                if "spawn_same" in self.other_property:  # spawn same effect
                    spawn_number = 1
                    if "spawn_number" in self.other_property:
                        spawn_number = int(self.other_property["spawn_number"])
                    for _ in range(spawn_number):
                        stat = self.part_stat.copy()
                        if "spawn_sky" in self.other_property:
                            stat[3] = -100
                        if self.owner.nearest_enemy:  # find the nearest enemy to target
                            if "spawn_target" in self.other_property:
                                if self.owner.sprite_direction == "l_side":
                                    stat[2] = uniform(self.owner.nearest_enemy[0].pos[0],
                                                      self.owner.nearest_enemy[0].pos[0] + (200 * self.screen_scale[0]))
                                else:
                                    stat[2] = uniform(self.owner.nearest_enemy[0].pos[0] - (200 * self.screen_scale[0]),
                                                      self.owner.nearest_enemy[0].pos[0])

                                self.pos = (stat[2], stat[3])
                                stat[4] = self.set_rotate(self.owner.nearest_enemy[0].pos, use_pos=True)

                            elif "spawn_near_target" in self.other_property:
                                if self.owner.nearest_enemy:  # find the nearest enemy to target
                                    if self.owner.sprite_direction == "l_side":
                                        stat[2] = uniform(self.owner.nearest_enemy[0].pos[0],
                                                          self.owner.nearest_enemy[0].pos[0] + (
                                                                  500 * self.screen_scale[0]))
                                    else:
                                        stat[2] = uniform(
                                            self.owner.nearest_enemy[0].pos[0] - (500 * self.screen_scale[0]),
                                            self.owner.nearest_enemy[0].pos[0])

                                    self.pos = (stat[2], stat[3])
                                    target_pos = (uniform(self.owner.nearest_enemy[0].pos[0] - 100,
                                                          self.owner.nearest_enemy[0].pos[0] + 100),
                                                  self.owner.nearest_enemy[0].pos[1])
                                    stat[4] = self.set_rotate(target_pos, use_pos=True)

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
        if self.stick_timer:
            if self.x_momentum or self.y_momentum:  # sprite bounce after reach
                self.angle += (dt * 1000)
                if self.angle >= 360:
                    self.angle = 0
                new_pos = self.base_pos + Vector2(self.x_momentum, -self.y_momentum)
                move = new_pos - self.base_pos
                if move.length():
                    move.normalize_ip()
                    self.base_pos += move
                    self.travel_distance -= move.length()
                    self.pos = Vector2(self.base_pos[0] * self.screen_scale[0],
                                       self.base_pos[1] * self.screen_scale[1])
                    self.adjust_sprite()

                if self.x_momentum > 0:
                    self.x_momentum -= dt * 50
                    if self.x_momentum < 0.1:
                        self.x_momentum = 0
                elif self.x_momentum < 0:
                    self.x_momentum += dt * 50
                    if self.x_momentum > 0.1:
                        self.x_momentum = 0

                if self.y_momentum > 0:
                    self.y_momentum -= dt * 100
                    if self.y_momentum <= 0:
                        self.y_momentum = -200

                if self.base_pos[1] >= self.owner.original_ground_pos:  # reach ground
                    self.x_momentum = 0
                    self.y_momentum = 0

            else:  # no longer bouncing, start countdown stick timer or find new pos for stuck part
                if self.stuck_part:  # find new pos based on stuck part
                    if self.stuck_part.data:
                        self.pos = list(self.stuck_part.rect.center)
                        self.angle = self.base_stuck_stat[1]
                        scale_diff = 1 + (self.stuck_part.data[7] - self.base_stuck_stat[2][7])
                        x_diff = self.base_stuck_stat[0][0]
                        if self.stuck_part.owner.angle != self.base_stuck_stat[3]:
                            # different animation direction
                            x_diff = -x_diff
                            self.angle = -self.angle
                        # if self.stuck_part.data[5] != self.base_stuck_stat[2][5] and \
                        #         (self.stuck_part.data[5] in (1, 3) or self.base_stuck_stat[2][5] in (1, 3)):
                        #     # part has opposite horizontal flip
                        #     self.pos[0] -=x_diff * scale_diff
                        #     self.angle = (self.angle - 180)
                        # else:
                        self.pos[0] += x_diff * scale_diff

                        # if self.stuck_part.data[5] != self.base_stuck_stat[2][5] and \
                        #         (self.stuck_part.data[5] >= 2 or self.base_stuck_stat[2][5] >= 2):
                        #     # part has opposite vertical flip
                        #     self.pos[1] -= self.base_stuck_stat[0][1] * scale_diff
                        #     self.angle = (180 - self.angle)
                        # else:
                        self.pos[1] += self.base_stuck_stat[0][1] * scale_diff

                        if self.stuck_part.data[4] != self.base_stuck_stat[2][4]:  # stuck part data change
                            if self.stuck_part.owner.angle != self.base_stuck_stat[3]:  # different direction
                                angle_dif = self.stuck_part.data[4] + self.base_stuck_stat[2][4]
                                self.angle += self.stuck_part.data[4] + self.base_stuck_stat[2][4]
                            else:
                                angle_dif = self.stuck_part.data[4] - self.base_stuck_stat[2][4]
                                self.angle += self.stuck_part.data[4] - self.base_stuck_stat[2][4]
                            radians_angle = radians(360 - angle_dif)
                            if angle_dif < 0:
                                radians_angle = radians(-angle_dif)
                            self.pos = rotation_xy(self.stuck_part.rect.center, self.pos,
                                                   radians_angle)  # find new pos after rotation
                        self.adjust_sprite()
                    else:  # stuck part disappear for whatever reason
                        self.stick_timer = 0  # remove effect
                self.stick_timer -= dt
                if self.stick_timer <= 0:
                    self.reach_target("border")
                    return

        elif not self.hit_collide_check(check_damage_effect=self.effect_collide_check):
            if self.sound_effect_name and self.sound_timer < self.sound_duration:
                self.sound_timer += dt

            if self.duration > 0:  # only clear for sprite with duration
                self.duration -= dt
                if self.duration <= 0:
                    self.reach_target("border")
                    return

            done, just_start = self.play_animation(0.05, dt, False)

            if just_start and self.duration:  # reset already hit every animation frame for effect with duration
                self.already_hit = []

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
                        if self.stick_reach == "stick" and self.base_pos[1] >= self.owner.original_ground_pos:
                            # stuck at ground
                            self.travel_distance = 0
                            self.stick_timer = 5
                            self.current_animation = self.animation_pool["Base"][self.scale]  # change image to base
                            self.base_image = self.current_animation[self.show_frame][self.flip]
                            self.adjust_sprite()
                            self.battle.all_damage_effects.remove(self)
                        else:
                            self.reach_target("border")
                            return

                    if self.degrade_when_travel and self.dmg:  # dmg power drop the longer damage sprite travel
                        if self.dmg > 1:
                            self.dmg -= 0.1

            if ((self.travel and self.travel_distance <= 0) or (not self.travel and done)) \
                    and not self.stick_timer and not self.max_duration:
                self.reach_target("border")
                return

            if self.sound_effect_name and self.sound_timer >= self.sound_duration and \
                    self.travel_sound_distance_check > self.battle.camera_pos.distance_to(self.pos):
                # play sound, check for distance here to avoid timer reset when not on screen
                self.battle.add_sound_effect_queue(self.sound_effect_name, self.pos,
                                                   self.travel_sound_distance, 0)
                self.sound_timer = 0


class TrapEffect(Effect):
    reach_target = DamageEffect.reach_target

    def __init__(self, owner, stat, layer, moveset, from_owner=True, reach_effect=None):
        """Trap sprite that can trigger when character come near, the trap sprite itself does no damage"""
        Effect.__init__(self, owner, stat, layer, from_owner=from_owner)
        self.activate = False
        self.impact_effect = None
        self.reach_effect = reach_effect
        self.moveset = moveset
        # self.travel_distance = 0
        # if not layer:  # layer 0 in animation part data mean the effect can move on its own
        #     self.travel_distance = self.moveset["Range"]

        self.other_property = self.moveset["Property"]

    def update(self, dt):
        if self.sound_effect_name and self.sound_timer < self.sound_duration:
            self.sound_timer += dt

        done, just_start = self.play_animation(0.05, dt)

        if self.activate and done:
            if "drop" in self.effect_stat["Property"]:  # drop item after destroyed, slightly above trap sprite
                Drop(Vector2((self.base_pos[0], self.base_pos[1] - 50)),
                     self.effect_stat["Property"]["drop"], self.owner.team)
            self.reach_target()
            return

        if self.duration > 0:
            self.duration -= dt
            if self.duration <= 0:  # activate when trap duration run out
                self.activate_trap()

        # if self.travel_distance:  # damage sprite that can move
        #     print(self.travel_distance)
        #     new_pos = Vector2(self.base_pos[0] - (self.speed * sin(radians(self.angle))),
        #                       self.base_pos[1] - (self.speed * cos(radians(self.angle))))
        #     move = new_pos - self.base_pos
        #     if move.length():  # sprite move
        #         move.normalize_ip()
        #         move = move * self.speed * dt
        #
        #         self.base_pos += move
        #         self.travel_distance -= move.length()
        #         if self.base_pos[0] <= 0:  # trap cannot be thrown pass map border
        #             self.base_pos[0] = 0
        #         elif self.base_pos[0] > self.stage_end:
        #             self.base_pos[0] = self.stage_end
        #         if self.base_pos[1] >= self.owner.original_ground_pos:  # reach ground
        #             self.base_pos[1] = self.owner.original_ground_pos
        #
        #         self.pos = Vector2(self.base_pos[0] * self.screen_scale[0], self.base_pos[1] * self.screen_scale[1])
        #         self.rect.center = self.pos
        # else:  # keep checking for collide to activate trap
        if spritecollide(self, self.owner.enemy_part_list, False, collided=collide_mask):
            # activate when enemy collide
            self.activate_trap()

    def activate_trap(self):
        self.current_animation = self.animation_pool["Activate"][self.scale]  # change image to base
        self.base_image = self.current_animation[self.show_frame][self.flip]
        self.adjust_sprite()
        self.activate = True
        self.repeat_animation = False


class StatusEffect(Effect):
    def __init__(self, owner, stat, layer):
        Effect.__init__(self, owner, stat, layer)
        self.pos = self.owner.pos
        self.rect.midbottom = self.owner.pos

    def update(self, dt):
        done, just_start = self.play_animation(0.05, dt)
        self.pos = self.owner.pos
        self.rect.midbottom = self.owner.pos

        if self.sound_effect_name and self.sound_timer < self.sound_duration:
            self.sound_timer += dt

        if self.sound_effect_name and self.sound_timer >= self.sound_duration and \
                self.travel_sound_distance > self.battle.camera_pos.distance_to(self.pos):
            # play sound, check for distance here to avoid timer reset when not on screen
            self.battle.add_sound_effect_queue(self.sound_effect_name, self.pos,
                                               self.travel_sound_distance, 0)
            self.sound_timer = 0

        if done:  # no duration, kill effect when animation end
            self.clean_object()
            return
