from math import cos, sin, radians

from pygame import Vector2


def move_logic(self, dt, done):
    """
    Sprite movement logic
    @param self: Effect object
    @param dt: game time
    @return: True if sprite reach target and is killed
    """
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
                    self.base_pos[1] >= self.owner.base_ground_pos or
                    self.base_pos[1] < -500):  # pass outside of map
                if self.stick_reach == "stick" and self.base_pos[1] >= self.owner.base_ground_pos:
                    # stuck at ground
                    self.travel_distance = 0
                    self.stick_timer = 5
                    self.current_animation = self.animation_pool["Base"][self.scale]  # change image to base
                    self.base_image = self.current_animation[self.show_frame][self.flip]
                    self.adjust_sprite()
                    self.battle.all_damage_effects.remove(self)
                else:
                    self.reach_target("border")
                    return True

    if self.travel and self.travel_distance <= 0 \
            and not self.stick_timer and not self.max_duration:  # reach max travel distance
        self.reach_target("border")
        return True
    elif not self.travel and done:
        self.reach_target()
        return True
