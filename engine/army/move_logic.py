from pygame import Vector2

infinity = float("inf")


def move_logic(self, dt):
    """Calculate and move character position according to speed"""
    ground_pos = self.base_ground_pos
    move_speed = self.walk_speed

    if self.route:  # has movement
        new_pos = self.base_pos + Vector2(self.x_momentum, -self.y_momentum)
        move = new_pos - self.base_pos
        if move.length():
            move.normalize_ip()
            move *= move_speed * dt
            self.base_pos += move
            if self.base_pos[1] < -1500:  # cannot go too far off top screen
                self.base_pos[1] = -1500
                self.y_momentum = -self.Character_Gravity
            elif self.base_pos[1] > ground_pos:
                self.base_pos[1] = ground_pos

            if not self.broken and "broken" not in self.commander_order:
                # non broken character cannot go pass stage border
                if self.battle.base_stage_start > self.base_pos[0]:
                    self.base_pos[0] = self.battle.base_stage_start
                    self.x_momentum = 0
                elif self.base_pos[0] > self.battle.base_stage_end:
                    self.base_pos[0] = self.battle.base_stage_end
                    self.x_momentum = 0

            self.pos = Vector2((self.base_pos[0] * self.screen_scale[0],
                                self.base_pos[1] * self.screen_scale[1]))

            self.update_sprite = True

            # update momentum
            if self.x_momentum:
                if self.x_momentum > 0:  # going right
                    if self.base_pos[1] < ground_pos:
                        self.x_momentum -= dt * 10
                    else:
                        self.x_momentum -= dt * move_speed
                    if self.x_momentum < 0.1:
                        self.x_momentum = 0
                else:  # going left
                    if self.base_pos[1] < ground_pos:
                        self.x_momentum += dt * 10
                    else:
                        self.x_momentum += dt * move_speed
                    if self.x_momentum > 0.1:
                        self.x_momentum = 0
