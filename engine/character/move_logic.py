from pygame import Vector2

infinity = float("inf")


def move_logic(self, dt):
    """Calculate and move character position according to speed"""
    # animation allow movement
    if "movable" in self.current_action:
        # animation allow movement or in air which always allow movement
        if "walk" in self.current_action:
            self.move_speed = self.walk_speed
        elif "run" in self.current_action:
            self.move_speed = self.run_speed
        elif "speed" in self.current_action:
            self.move_speed = self.current_action["speed"]
        else:
            self.move_speed = abs(self.x_momentum * 2) + abs(self.y_momentum * 2)
            if self.move_speed < 500:
                self.move_speed = 500

    if self.x_momentum or self.y_momentum:  # has movement
        if "movable" in self.current_action:
            new_pos = self.base_pos + Vector2(self.x_momentum, -self.y_momentum)
            move = new_pos - self.base_pos
            if move.length():
                move.normalize_ip()
                move *= self.move_speed * dt
                self.base_pos += move
                if self.base_pos[1] < -1500:  # cannot go too far off top screen
                    self.base_pos[1] = -1500
                    self.y_momentum = -self.Character_Gravity
                elif self.base_pos[1] > self.base_ground_pos:
                    self.base_pos[1] = self.base_ground_pos

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
                    if self.base_pos[1] < self.base_ground_pos:
                        self.x_momentum -= dt * 10
                    else:
                        self.x_momentum -= dt * self.move_speed
                    if self.x_momentum < 0.1:
                        self.x_momentum = 0
                else:  # going left
                    if self.base_pos[1] < self.base_ground_pos:
                        self.x_momentum += dt * 10
                    else:
                        self.x_momentum += dt * self.move_speed
                    if self.x_momentum > 0.1:
                        self.x_momentum = 0
            if self.y_momentum > 0:  # climbing through air
                if self.base_pos[1] < self.base_ground_pos:
                    self.y_momentum -= dt * self.move_speed
                    self.move_speed += self.y_momentum
                    if self.y_momentum <= 0:  # reach highest y momentum now fall down
                        self.y_momentum = -self.Character_Gravity

            elif self.y_momentum < 0:  # no more velocity to go up, must go down
                if self.base_pos[1] < self.base_ground_pos:
                    self.move_speed += self.Character_Gravity

                    # falling down if not flying and not in temporary stopping or dead
                    self.y_momentum = -self.Character_Gravity
                    if "drop speed" in self.current_action:
                        self.move_speed *= self.current_action["drop speed"]
                        self.y_momentum = -self.move_speed * 10
                else:  # reach ground, stop all momentum
                    self.y_momentum = 0
                    self.x_momentum = 0

        else:  # no movement allow for action that is not movable
            self.x_momentum = 0
            self.y_momentum = 0

    elif self.current_action:  # not movable animation, reset speed
        if "movable" in self.current_action:  # in moving animation, interrupt it
            self.interrupt_animation = True


def sub_move_logic(self, dt: float):
    """Sub character does not move by itself but rather along with main character based on anchor point"""
    if self.main_character:
        if self.base_pos != self.main_character.base_pos:
            self.base_pos = Vector2(self.main_character.base_pos)
            self.pos = Vector2(((self.base_pos[0] + self.anchor_pos[0]) * self.screen_scale[0],
                                (self.base_pos[1] + self.anchor_pos[1]) * self.screen_scale[1]))
            self.update_sprite = True
    else:
        move_logic(self, dt)


def air_move_logic(self, dt):
    """Calculate and move character position according to speed"""
    # all animations must allow movement for air unit
    if not self.alive:
        self.y_momentum = -self.Character_Gravity
        self.move_speed = self.Character_Gravity
    elif "walk" in self.current_action:
        self.move_speed = self.walk_speed
    elif "run" in self.current_action:
        self.move_speed = self.run_speed
        # if self.game_id == 2:
    elif "speed" in self.current_action:
        self.move_speed = self.current_action["speed"]
    else:
        self.move_speed = 1000 + abs(self.x_momentum * 2)

    if self.x_momentum or self.y_momentum:  # has movement
        if "movable" in self.current_action:
            new_pos = self.base_pos + Vector2(self.x_momentum, -self.y_momentum)
            move = new_pos - self.base_pos
            if move.length():
                move.normalize_ip()
                move *= self.move_speed * dt
                self.base_pos += move
                if "forced move" not in self.current_action:  # die, knockdown does not change direction
                    if self.x_momentum > 0:
                        self.new_direction = "right"
                    elif self.x_momentum < 0:
                        self.new_direction = "left"

                if self.base_pos[1] > self.base_ground_pos:
                    self.base_pos[1] = self.base_ground_pos

                if (self.retreat_stage_start > self.base_pos[0] or
                        self.base_pos[0] >= self.retreat_stage_end):
                    self.x_momentum = 0
                    if "back" in self.commander_order:
                        self.active = False
                        self.battle_camera_drawer.remove(self)

                self.pos = Vector2((self.base_pos[0] * self.screen_scale[0],
                                    self.base_pos[1] * self.screen_scale[1]))

                self.update_sprite = True

            # update momentum
            if self.x_momentum:
                if self.x_momentum > 0:  # going right
                    self.x_momentum -= dt * self.move_speed
                    if self.x_momentum < 0.1:
                        self.x_momentum = 0
                else:  # going left
                    self.x_momentum += dt * self.move_speed
                    if self.x_momentum > 0.1:
                        self.x_momentum = 0

            if self.y_momentum < 0:  # falling down
                if self.base_pos[1] < self.base_ground_pos:
                    self.move_speed += self.Character_Gravity
                    self.y_momentum = -self.Character_Gravity
                else:  # reach ground, stop all momentum
                    self.y_momentum = 0
                    self.x_momentum = 0

        else:  # no movement allow for action that is not movable
            self.x_momentum = 0
            self.y_momentum = 0
