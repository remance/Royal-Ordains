from pygame import Vector2


def remain_logic(self, dt):
    if self.after_reach == "move":  # keep moving until reach ground or out of map
        self.move_logic(dt, False)
    else:
        if self.x_momentum or self.y_momentum:  # sprite bounce after reach
            self.renew_sprite = True
            self.angle += (dt * 1000)
            if self.angle >= 360:
                self.angle = 0
            new_pos = self.base_pos + Vector2(self.x_momentum, -self.y_momentum)
            move = new_pos - self.base_pos

            if move.length():
                move.normalize_ip()
                self.base_pos += move * dt * 500
                self.pos = Vector2(self.base_pos[0] * self.screen_scale[0],
                                   self.base_pos[1] * self.screen_scale[1])
                self.adjust_sprite()

                if move[0] > 0:
                    self.x_momentum -= dt * 100
                elif move[0] < 0:
                    self.x_momentum += dt * 100

                self.y_momentum -= dt * 200

            if self.base_pos[1] >= self.base_ground_pos:  # reach ground
                self.x_momentum = 0
                self.y_momentum = 0
                self.reach_target("ground")

        else:  # no longer bouncing, remove effect
            self.reach_target()
