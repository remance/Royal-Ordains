from pygame import Vector2

infinity = float("inf")


def move_logic(self, dt):
    """Calculate and move character position according to speed"""
    # animation allow movement
    current_action = self.current_action
    move_speed = 0
    ground_pos = self.base_ground_pos

    if self.base_pos[1] < ground_pos and not self.y_momentum:
        self.y_momentum = -self.Character_Gravity

    if "movable" in current_action or self.base_pos[1] < ground_pos:
        # animation allow movement or in air which always allow movement
        if "walk" in current_action:
            move_speed = self.walk_speed
        elif "run" in current_action:
            move_speed = self.run_speed
        elif "speed" in current_action:
            move_speed = current_action["speed"]
        else:
            move_speed = abs(self.x_momentum * 2) + abs(self.y_momentum * 2)
            if move_speed < 500:
                move_speed = 500

    if self.x_momentum or self.y_momentum:  # has movement
        if "movable" in current_action or self.base_pos[1] < ground_pos:
            # movable or in process of falling
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

            if self.y_momentum > 0:  # climbing through air
                if self.base_pos[1] < ground_pos:
                    move_speed += self.y_momentum
                    self.y_momentum -= dt * move_speed
                    if self.y_momentum <= 0:  # reach highest y momentum now fall down
                        self.y_momentum = -self.Character_Gravity
            elif self.y_momentum < 0:  # no more velocity to go up, must go down
                if self.base_pos[1] < ground_pos:
                    move_speed += self.Character_Gravity
                    # falling down if not flying and not in temporary stopping or dead
                    self.y_momentum = -self.Character_Gravity
                    if "drop speed" in current_action:
                        move_speed *= current_action["drop speed"]
                        self.y_momentum = -move_speed * 10
                else:  # reach ground, stop all momentum
                    self.y_momentum = 0
                    self.x_momentum = 0

        else:  # no movement allow for action that is not movable
            self.x_momentum = 0
            self.y_momentum = 0

    elif current_action:  # not movable animation, reset speed
        if "movable" in current_action:  # in moving animation, interrupt it
            self.interrupt_animation = True


def sub_move_logic(self, dt: float):
    """Sub character does not move by itself but rather along with main character based on anchor point"""
    if self.main_character:
        if self.base_pos != self.main_character.base_pos:
            self.base_pos = Vector2(self.main_character.base_pos)
            if self.main_character.direction == "right":
                self.pos = Vector2(((self.base_pos[0] - self.anchor_pos[0]) * self.screen_scale[0],
                                    (self.base_pos[1] + self.anchor_pos[1]) * self.screen_scale[1]))
            else:
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
        move_speed = self.Character_Gravity
    elif "walk" in self.current_action:
        move_speed = self.walk_speed
    elif "run" in self.current_action:
        move_speed = self.run_speed
        # if self.game_id == 2:
    elif "speed" in self.current_action:
        move_speed = self.current_action["speed"]
    else:
        move_speed = 1000 + abs(self.x_momentum * 2)

    if self.x_momentum or self.y_momentum:  # has movement
        if "movable" in self.current_action:
            new_pos = self.base_pos + Vector2(self.x_momentum, -self.y_momentum)
            move = new_pos - self.base_pos
            if move.length():
                move.normalize_ip()
                move *= move_speed * dt
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
                        self.issue_commander_order(())  # remove order
                        self.ally_list.remove(self)
                        self.active = False
                        self.battle_camera_drawer.remove(self)
                        self.in_drawer = False
                        self.invisible = True
                        if not self.invincible:
                            for team in self.battle.all_team_enemy_check:
                                if team != self.team:
                                    if self.team != 0:  # team 0 is not part of condition check:
                                        self.battle.all_team_enemy_check[team].remove(self)

                self.pos = Vector2((self.base_pos[0] * self.screen_scale[0],
                                    self.base_pos[1] * self.screen_scale[1]))

                self.update_sprite = True

            # update momentum
            if self.x_momentum:
                if self.x_momentum > 0:  # going right
                    self.x_momentum -= dt * move_speed
                    if self.x_momentum < 0.1:
                        self.x_momentum = 0
                else:  # going left
                    self.x_momentum += dt * move_speed
                    if self.x_momentum > 0.1:
                        self.x_momentum = 0

            if self.y_momentum < 0:  # falling down
                if self.base_pos[1] < self.base_ground_pos:
                    move_speed += self.Character_Gravity
                    self.y_momentum = -self.Character_Gravity
                else:  # reach ground, stop all momentum
                    self.y_momentum = 0
                    self.x_momentum = 0

        else:  # no movement allow for action that is not movable
            self.x_momentum = 0
            self.y_momentum = 0
