from pygame import Vector2

infinity = float("inf")


def move_logic(self, dt):
    """Calculate and move character position according to speed"""
    if "movable" in self.current_action or (self.position == "Air" and not self.fly):
        # animation allow movement or in air which always allow movement
        if "walk" in self.current_action:
            if self.combat_state != "City":
                self.move_speed = self.walk_speed
            else:
                self.move_speed = self.city_walk_speed
        elif "run" in self.current_action:
            self.move_speed = self.run_speed
        elif "fly" in self.current_action:
            self.move_speed = self.run_speed
        else:
            self.move_speed = 1000 + abs(self.x_momentum * 2)

        if self.x_momentum:
            if self.x_momentum > 0:  # going right
                if self.position == "Air":
                    if "dash" in self.current_action:
                        self.x_momentum -= dt * self.move_speed * 3
                        self.y_momentum = 0
                    else:
                        self.x_momentum -= dt * 10
                else:
                    self.x_momentum -= dt * self.move_speed
                if self.x_momentum < 0.1:
                    self.x_momentum = 0
            else:  # going left
                if self.position == "Air":
                    if "dash" in self.current_action:
                        self.x_momentum += dt * self.move_speed * 3
                        self.y_momentum = 0
                    else:
                        self.x_momentum += dt * 10
                else:
                    self.x_momentum += dt * self.move_speed
                if self.x_momentum > 0.1:
                    self.x_momentum = 0

        if self.y_momentum > 0:  # climbing through air
            self.y_momentum -= dt * 800
            self.move_speed += self.y_momentum
            if self.y_momentum <= 0:  # reach highest y momentum now fall down
                self.y_momentum = -self.fall_gravity
        if self.y_momentum < 0:  # no more velocity to go up, must go down
            if self.base_pos[1] >= self.ground_pos and not self.no_clip:
                # reach ground, start landing animation
                self.y_momentum = 0
                self.x_momentum = 0
                self.base_pos[1] = self.ground_pos
                if "forced move" not in self.current_action:  # only land for non forced move animation
                    self.interrupt_animation = True
                    self.command_action = self.land_command_action
                    self.can_double_jump = True
                self.position = "Stand"
            elif (not self.fly and "fly" not in self.current_action) or not self.alive:
                # falling down if not flying and not in temporary stopping or dead
                if "dash" in self.current_action:
                    self.move_speed += 2000
                elif "drop speed" in self.current_action:
                    self.move_speed = self.fall_gravity * self.current_action["drop speed"]
                elif "moveset" in self.current_action or self.stop_fall_duration:  # delay falling when attack midair
                    self.move_speed = 100
                elif "die" in self.current_action:
                    self.y_momentum = -self.fall_gravity
                    self.move_speed = self.fall_gravity
                elif self.y_momentum > -self.fall_gravity:  # use gravity if existing -y momentum is higher
                    self.move_speed = self.fall_gravity
                else:  # fall faster if -y momentum lower than gravity
                    self.move_speed = -self.y_momentum + self.fall_gravity
        elif self.y_momentum < 0 and self.base_pos[1] == self.ground_pos:  # reach ground, reset y momentum
            self.y_momentum = 0

        if self.x_momentum or self.y_momentum:  # has movement
            new_pos = self.base_pos + Vector2(self.x_momentum, -self.y_momentum)
            move = new_pos - self.base_pos
            if move.length():
                move.normalize_ip()
                move *= self.move_speed * dt
                self.base_pos += move
                if "forced move" not in self.current_action:  # die, knockdown does not change direction
                    if self.x_momentum > 0:
                        self.new_angle = -90
                    elif self.x_momentum < 0:
                        self.new_angle = 90

                if self.base_pos[1] < -1000:
                    self.base_pos[1] = -1000
                    self.y_momentum = -self.fall_gravity

                if self.player_control:  # player character cannot go pass camera
                    if self.battle.base_camera_begin > self.base_pos[0]:
                        self.base_pos[0] = self.battle.base_camera_begin
                        self.x_momentum = 0
                    elif self.base_pos[0] > self.battle.base_camera_end:
                        self.base_pos[0] = self.battle.base_camera_end
                        self.x_momentum = 0
                elif not self.broken:  # AI character cannot go pass stage border unless broken
                    if self.battle.base_stage_start > self.base_pos[0]:
                        self.base_pos[0] = self.battle.base_stage_start
                        self.x_momentum = 0
                    elif self.base_pos[0] > self.battle.base_stage_end:
                        self.base_pos[0] = self.battle.base_stage_end
                        self.x_momentum = 0

                self.pos = Vector2((self.base_pos[0] * self.screen_scale[0],
                                    self.base_pos[1] * self.screen_scale[1]))

                for part in self.body_parts.values():
                    part.re_rect()

        elif "fly" not in self.current_action:
            # reach target, interrupt moving animation
            self.interrupt_animation = True  # in moving animation, interrupt it

    elif self.current_action:  # not movable animation, reset speed
        if "movable" in self.current_action:  # in moving animation, interrupt it
            self.interrupt_animation = True

    if self.base_pos[1] < self.ground_pos:
        self.position = "Air"
