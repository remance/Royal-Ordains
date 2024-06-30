from math import radians
from random import uniform, choice

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

    from engine.effect.move_logic import move_logic
    move_logic = move_logic

    from engine.effect.play_animation import play_animation
    play_animation = play_animation

    default_animation_speed = 0.1

    def __init__(self, owner, part_stat, layer, moveset=None, from_owner=True):
        """Effect sprite that does not affect character on its own but can travel and
        create other Effect when reach target"""
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

        self.fall_gravity = self.battle.base_fall_gravity

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
            self.sprite_ver = self.battle.chapter
        self.base_pos = Vector2(self.pos[0] / self.screen_scale[0], self.pos[1] / self.screen_scale[1])
        self.angle = self.part_stat[4]
        self.scale = self.part_stat[7]
        self.flip = self.part_stat[5]

        self.deal_dmg = False
        self.reach_effect = None
        self.stick_reach = False
        self.stuck_part = None  # part or pos that effect get stick at
        self.base_stuck_stat = ()
        self.stick_timer = 0
        self.travel_distance = 0
        self.travel = False
        self.one_hit_per_enemy = False

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
        self.moveset = moveset

        if self.effect_name in self.effect_list:
            self.effect_stat = self.effect_list[self.effect_name]
            self.speed = self.effect_stat["Travel Speed"]
            self.reach_effect = self.effect_stat["After Reach Effect"]
            self.stick_reach = self.effect_stat["Reach Effect"]
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
                if not layer and self.moveset["Range"] and "no travel" not in self.effect_stat["Property"]:
                    # layer 0 in animation part data mean the effect can move on its own
                    self.travel = True
                    self.travel_distance = self.moveset["Range"]
                if "random move" in moveset["Property"]:
                    self.random_move = True
                if "one hit per enemy" in moveset["Property"]:
                    self.one_hit_per_enemy = True

        self.animation_pool = self.effect_animation_pool[self.effect_name][self.sprite_ver]
        self.current_animation = self.animation_pool[self.part_name][self.scale]

        self.animation_speed = self.default_animation_speed
        if len(self.current_animation) == 1:  # effect with no animation play a bit longer
            self.animation_speed = 0.2

        self.base_image = self.current_animation[self.show_frame][self.flip]
        self.image = self.base_image

        self.adjust_sprite()

    def update(self, dt):
        done, just_start = self.play_animation(self.animation_speed, dt)

        if self.move_logic(dt, done):
            return

        if self.sound_effect:
            if self.sound_timer < self.sound_duration:
                self.sound_timer += dt
            else:  # play sound
                self.battle.add_sound_effect_queue(self.sound_effect, self.pos,
                                                   self.sound_distance, self.shake_value)
                self.sound_timer = 0

        if not self.travel_distance and done:  # no duration and no travel, kill effect when animation end
            self.clean_object()
            return

    def cutscene_update(self, dt):
        """All type of effect update the same during cutscene"""
        self.update(dt)

    def reach_target(self, how=None):
        self.deal_dmg = False
        if self.reach_effect:
            spawn_number = 1
            if "spawn number" in self.effect_stat["Property"]:
                spawn_number = self.effect_stat["Property"]["spawn number"]
            for _ in range(spawn_number):
                new_pos = self.pos
                stat = [self.reach_effect, "Base", new_pos[0], new_pos[1], 0, 0, 0, 1]
                if "reach spawn ground" in self.effect_stat[
                    "Property"]:  # reach effect spawn with rect bottom on ground
                    height = self.effect_animation_pool[self.reach_effect][self.sprite_ver]["Base"][self.scale][0][
                                 self.flip].get_height() / 4
                    stat[3] = self.pos[1] - height
                if "spawn all angle" in self.effect_stat["Property"]:
                    stat[4] = uniform(0, 359)
                if "spawn same angle" in self.effect_stat["Property"]:
                    stat[4] = self.angle + uniform(-10, 10)
                layer = 0
                if "no dmg" in self.effect_stat["Property"]:
                    Effect(self.owner, stat, layer, moveset=self.moveset, from_owner=False)
                else:
                    DamageEffect(self.owner, stat, layer, moveset=self.moveset, from_owner=False)

        if self.other_property:
            if "spawn" in self.other_property and "spawn after" in self.other_property and how == "border":
                effect_stat = None
                if "spawn same" in self.other_property:  # spawn same effect
                    effect_stat = list(self.part_stat)
                elif "spawn other" in self.other_property:
                    effect_stat = [self.other_property["spawn other"][0], self.other_property["spawn other"][1],
                                   self.part_stat[2], self.part_stat[3],
                                   self.part_stat[4], self.part_stat[5], self.part_stat[6], self.part_stat[7]]
                if effect_stat:
                    spawn_number = 1
                    if "spawn number" in self.other_property:
                        spawn_number = int(self.other_property["spawn number"])
                    for _ in range(spawn_number):
                        stat = effect_stat
                        if "spawn sky" in self.other_property:
                            stat[3] = -100
                        if self.owner.nearest_enemy and "aim" in self.other_property:
                            # find the nearest enemy to target
                            if self.other_property["aim"] == "target":
                                if self.owner.angle == 90:
                                    stat[2] = uniform(self.owner.nearest_enemy.pos[0],
                                                      self.owner.nearest_enemy.pos[0] + (200 * self.screen_scale[0]))
                                else:
                                    stat[2] = uniform(self.owner.nearest_enemy.pos[0] - (200 * self.screen_scale[0]),
                                                      self.owner.nearest_enemy.pos[0])

                                self.pos = (stat[2], stat[3])
                                stat[4] = self.set_rotate(self.owner.nearest_enemy.pos, use_pos=True)

                            elif self.other_property["aim"] == "near target":
                                if self.owner.nearest_enemy:  # find the nearest enemy to target
                                    if self.owner.angle == 90:
                                        stat[2] = uniform(self.owner.nearest_enemy.pos[0],
                                                          self.owner.nearest_enemy.pos[0] + (
                                                                  500 * self.screen_scale[0]))
                                    else:
                                        stat[2] = uniform(
                                            self.owner.nearest_enemy.pos[0] - (500 * self.screen_scale[0]),
                                            self.owner.nearest_enemy.pos[0])

                                    self.pos = (stat[2], stat[3])
                                    target_pos = (uniform(self.owner.nearest_enemy.pos[0] - 200,
                                                          self.owner.nearest_enemy.pos[0] + 200),
                                                  self.owner.nearest_enemy.pos[1])
                                    stat[4] = self.set_rotate(target_pos, use_pos=True)

                        else:  # random target instead
                            stat[2] = uniform(self.pos[0] - (self.travel_distance * self.screen_scale[0]),
                                              self.pos[0] + (self.travel_distance * self.screen_scale[0]))
                            if self.owner.angle == 90:
                                stat[4] = uniform(160, 180)
                            else:
                                stat[4] = uniform(-180, -160)

                        moveset = self.moveset.copy()
                        moveset["Property"] = [item for item in moveset["Property"] if
                                               item != "spawn"]  # remove spawn property so it not loop spawn
                        DamageEffect(self.owner, stat, 0, moveset=moveset, from_owner=False)
        self.clean_object()


class DamageEffect(Effect):
    def __init__(self, owner, part_stat, layer, moveset, from_owner=True, arc_shot=False, reach_effect=None):
        """Effect damage sprite that can affect character in some ways such as arrow, explosion, buff magic"""
        Effect.__init__(self, owner, part_stat, layer, moveset=moveset, from_owner=from_owner)
        self.impact_effect = None
        self.arc_shot = arc_shot
        self.reach_effect = reach_effect

        self.stamina_dmg_bonus = 0
        self.sprite_direction = ""
        self.attacker_sprite_direction = self.owner.sprite_direction
        self.already_hit = []  # list of character already got hit with time by sprite for sprite with no duration

        self.dmg = 0
        self.find_damage(self.moveset)
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

    def find_damage(self, moveset):
        self.dmg = moveset["Power"] + self.owner.power_bonus * self.owner.hold_power_bonus
        self.element = moveset["Element"]
        self.impact = ((moveset["Push Impact"] - moveset["Pull Impact"]) *
                       self.owner.impact_modifier,
                       (moveset["Down Impact"] - moveset["Up Impact"]) *
                       self.owner.impact_modifier)
        self.impact_sum = abs(self.impact[0]) + abs(self.impact[1])
        if self.element == "Physical":
            self.dmg = uniform(self.dmg * self.owner.min_physical, self.dmg * self.owner.max_physical)
        else:
            self.dmg = uniform(self.dmg * self.owner.min_elemental, self.dmg * self.owner.max_elemental)
        if self.dmg < 0:
            self.dmg = 0
        self.critical_chance = self.owner.critical_chance + moveset["Critical Chance Bonus"]
        self.friend_status_effect = moveset["Status"]
        self.enemy_status_effect = moveset["Enemy Status"]

    def update(self, dt):
        if self.stick_timer:  # already reach target and now either sticking or bouncing off
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

                if self.base_pos[1] >= self.owner.base_ground_pos:  # reach ground
                    self.x_momentum = 0
                    self.y_momentum = 0

            else:  # no longer bouncing, start countdown stick timer or find new pos for stuck part
                if self.stuck_part:  # find new pos based on stuck part
                    if not hasattr(self.stuck_part, "data"):
                        print(self.stuck_part)
                        print(self.stuck_part.owner,)
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
                    self.reach_target()
                    return

        else:
            if self.sound_effect:
                if self.sound_timer < self.sound_duration:
                    self.sound_timer += dt
                else:  # play sound
                    self.battle.add_sound_effect_queue(self.sound_effect, self.pos,
                                                       self.sound_distance, self.shake_value)
                    self.sound_timer = 0

            if not self.hit_collide_check(check_damage_effect=self.effect_collide_check):
                if self.duration > 0:  # only clear for sprite with duration
                    self.duration -= dt
                    if self.duration <= 0:
                        self.reach_target()
                        return

                done, just_start = self.play_animation(self.animation_speed, dt, False)

                if just_start and self.duration and not self.one_hit_per_enemy:
                    # reset already hit every animation frame for effect with duration and not with one hit condition
                    self.already_hit = []
                if self.move_logic(dt, done):
                    return


class TrapEffect(Effect):

    def __init__(self, owner, stat, layer, moveset, from_owner=True):
        """Trap sprite that can trigger when character come near, the trap sprite itself does no damage"""
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

        done, just_start = self.play_animation(self.animation_speed, dt)

        if self.activate and done:
            if self.sound_effect:
                # play sound, check for distance here to avoid timer reset when not on screen
                self.battle.add_sound_effect_queue(self.sound_effect, self.pos,
                                                   self.sound_distance, 0)
            if "drop" in self.effect_stat["Property"]:  # drop item after destroyed, slightly above trap sprite
                Drop(Vector2((self.base_pos[0], self.base_pos[1] - 50)),
                     self.effect_stat["Property"]["drop"], self.owner.team)
            self.reach_target()
            return

        if self.duration > 0:
            self.duration -= dt
            if self.duration <= 0:  # activate when trap duration run out
                self.activate_trap()

        if spritecollide(self, self.owner.enemy_part_list, False, collided=collide_mask):
            # activate when enemy collide
            self.activate_trap()

    def activate_trap(self):
        self.current_animation = self.animation_pool["Activate"][self.scale]  # change image to base
        self.animation_speed = self.default_animation_speed  # reset animation play speed
        if len(self.current_animation) == 1:  # effect with no animation play a bit longer
            self.animation_speed = 0.2
        self.base_image = self.current_animation[self.show_frame][self.flip]
        self.adjust_sprite()
        self.activate = True
        self.repeat_animation = False


class StatusEffect(Effect):
    def __init__(self, owner, stat, layer):
        Effect.__init__(self, owner, stat, layer, None)
        self.pos = self.owner.pos
        self.rect.midbottom = self.owner.pos

    def update(self, dt):
        done, just_start = self.play_animation(self.animation_speed, dt)
        self.pos = self.owner.pos
        self.rect.midbottom = self.owner.pos

        if self.sound_effect and self.sound_timer < self.sound_duration:
            self.sound_timer += dt

        if self.sound_effect and self.sound_timer >= self.sound_duration and \
                self.sound_distance > self.battle.camera_pos.distance_to(self.pos):
            # play sound, check for distance here to avoid timer reset when not on screen
            self.battle.add_sound_effect_queue(self.sound_effect, self.pos,
                                               self.sound_distance, 0)
            self.sound_timer = 0

        if done:  # no duration, kill effect when animation end
            self.clean_object()
            return
