from math import cos, sin, tan, radians

from pygame import Vector2


def move_logic(self, dt, done):
    """
    Sprite movement logic
    @param self: Effect object
    @param dt: game time
    @param done: animation done playing
    @return: True if sprite reach target and is killed
    """
    if self.travel_distance:  # sprite that can move
        if self.direct_shot:
            new_pos = Vector2(self.base_pos[0] - (self.speed * self.sin_angle),
                              self.base_pos[1] - (self.speed * self.cos_angle))
        else:
            move_x = self.travel_distance / (self.speed * dt)
            x = self.travel_progress + move_x
            y = (x * self.tan_angle - 0.5 * (x ** 2) /
                 (self.velocity ** 2 * self.cos_angle ** 2))

            new_pos = Vector2(self.base_pos[0] + move_x, self.start_pos[1] - y)
        move = new_pos - self.base_pos
        if move.length():  # sprite move
            move.normalize_ip()
            move *= self.speed * dt
            new_pos = self.base_pos + move
            new_angle = self.set_rotate(new_pos)
            self.angle = new_angle
            self.base_pos = new_pos
            self.travel_progress += move[0]
            self.pos = Vector2(self.base_pos[0] * self.screen_scale[0], self.base_pos[1] * self.screen_scale[1])
            self.renew_sprite = True

            if not self.random_move and (
                    self.base_pos[0] <= 0 or self.base_pos[0] > self.base_stage_end or
                    self.base_pos[1] >= self.base_ground_pos or
                    self.base_pos[1] < -5000):  # pass outside of map

                if self.base_pos[1] >= self.base_ground_pos:
                    # reach ground
                    self.travel_distance = 0
                    self.current_animation = self.animation_pool["Base"][self.sprite_flip][self.width_scale][
                        self.height_scale]  # change image to base
                    self.base_image = self.current_animation[self.show_frame]
                    self.adjust_sprite()
                    self.reach_target("ground")
                    return True
                else:
                    self.reach_target("border")
                    return True

            self.adjust_sprite()

    elif done:
        self.reach_target()
