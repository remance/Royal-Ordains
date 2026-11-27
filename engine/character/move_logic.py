from pygame import Vector2

infinity = float("inf")


def move_logic(self, dt):
    """Calculate and move character position according to speed"""
    # animation allow movement
    current_action = self.current_action
    move_speed = 0
    ground_pos = self.base_ground_pos
    base_pos = self.base_pos

    if base_pos[1] < ground_pos and self.y_momentum < 1:
        self.y_momentum = -self.Character_Gravity

    if "movable" in current_action or base_pos[1] < ground_pos:
        # animation allow movement or in air which always allow movement
        if "walk" in current_action:
            move_speed = self.walk_speed
        elif "run" in current_action:
            move_speed = self.run_speed
        elif "speed" in current_action:
            move_speed = current_action["speed"]
        else:
            move_speed = abs(self.x_momentum) + abs(self.y_momentum)
            if move_speed < 500:
                move_speed = 500
            elif move_speed > 10000:
                move_speed = 10000

    if self.x_momentum or self.y_momentum:  # has movement
        if "movable" in current_action or base_pos[1] < ground_pos:
            # movable or in process of falling
            x_momentum = self.x_momentum
            y_momentum = self.y_momentum

            new_pos = base_pos + Vector2(x_momentum, -y_momentum)
            move = new_pos - base_pos
            if move.length():
                move.normalize_ip()
                move *= move_speed * dt
                base_pos += move
                if base_pos[1] < -1500:  # cannot go too far off top screen
                    base_pos[1] = -1500
                    y_momentum = -self.Character_Gravity
                elif base_pos[1] > ground_pos:
                    base_pos[1] = ground_pos

                if not self.broken and "broken" not in self.commander_order:
                    # non broken character cannot go pass stage border
                    if self.battle.base_stage_start > base_pos[0]:
                        base_pos[0] = self.battle.base_stage_start
                        x_momentum = 0
                    elif base_pos[0] > self.battle.base_stage_end:
                        base_pos[0] = self.battle.base_stage_end
                        x_momentum = 0

                self.pos = Vector2((base_pos[0] * self.screen_scale_width,
                                    base_pos[1] * self.screen_scale_height))

                self.update_sprite = True

            # update momentum
            if x_momentum:
                if x_momentum > 0:  # going right
                    if base_pos[1] < ground_pos:
                        x_momentum -= dt * 10
                    else:
                        x_momentum -= dt * move_speed
                    if x_momentum < 0.1:
                        x_momentum = 0
                else:  # going left
                    if base_pos[1] < ground_pos:
                        x_momentum += dt * 10
                    else:
                        x_momentum += dt * move_speed
                    if x_momentum > 0.1:
                        x_momentum = 0

            if y_momentum > 0:  # climbing through air
                if base_pos[1] < ground_pos:
                    move_speed += y_momentum
                    y_momentum -= dt * move_speed
                    if y_momentum <= 0:  # reach highest y momentum now fall down
                        y_momentum = -self.Character_Gravity
            elif y_momentum < 0:  # no more momentum to go up, must go down
                if base_pos[1] < ground_pos:
                    move_speed += self.Character_Gravity
                    # falling down if not flying and not in temporary stopping or dead
                    y_momentum = -self.Character_Gravity
                    if "drop speed" in current_action:
                        move_speed *= current_action["drop speed"]
                        y_momentum = -move_speed * 10
                else:  # reach ground, stop all momentum
                    y_momentum = 0
                    x_momentum = 0

            self.x_momentum = x_momentum
            self.y_momentum = y_momentum
        else:  # no movement allow for action that is not movable
            self.x_momentum = 0
            self.y_momentum = 0

    elif "movable" in current_action and "forced move" not in self.current_action:
        # in non-forced moving animation, interrupt it
        self.interrupt_animation = True


def sub_move_logic(self, dt: float):
    """Sub character does not move by itself but rather along with main character based on anchor point"""
    main_character = self.main_character
    if main_character:
        if self.base_pos != main_character.base_pos:
            self.base_pos = Vector2(main_character.base_pos)
            if main_character.direction == "right":
                self.pos = Vector2(((self.base_pos[0] - self.anchor_pos[0]) * self.screen_scale_width,
                                    (self.base_pos[1] + self.anchor_pos[1]) * self.screen_scale_height))
            else:
                self.pos = Vector2(((self.base_pos[0] + self.anchor_pos[0]) * self.screen_scale_width,
                                    (self.base_pos[1] + self.anchor_pos[1]) * self.screen_scale_height))
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
            x_momentum = self.x_momentum
            y_momentum = self.y_momentum
            base_pos = self.base_pos
            new_pos = base_pos + Vector2(x_momentum, -y_momentum)
            move = new_pos - base_pos
            if move.length():
                move.normalize_ip()
                move *= move_speed * dt
                base_pos += move
                if "forced move" not in self.current_action:  # die, knockdown does not change direction
                    if x_momentum > 0:
                        self.new_direction = "right"
                    elif x_momentum < 0:
                        self.new_direction = "left"

                if base_pos[1] > self.base_ground_pos:
                    base_pos[1] = self.base_ground_pos

                if self.retreat_stage_start > base_pos[0] or base_pos[0] >= self.retreat_stage_end:
                    x_momentum = 0
                    if "back" in self.commander_order:
                        self.issue_commander_order(())  # remove order
                        self.ally_list.remove(self)
                        self.active = False
                        self.battle_camera_drawer.remove(self)
                        self.in_drawer = False
                        self.invisible = True
                        if not self.invincible:
                            for team in self.battle.all_team_enemy:
                                if team != self.team:
                                    if self.team != 0:  # team 0 is not part of condition check:
                                        self.battle.all_team_enemy[team].remove(self)

                self.pos = Vector2((base_pos[0] * self.screen_scale_width,
                                    base_pos[1] * self.screen_scale_height))

                self.update_sprite = True

            # update momentum
            if x_momentum:
                if x_momentum > 0:  # going right
                    x_momentum -= dt * move_speed
                    if x_momentum < 0.1:
                        x_momentum = 0
                else:  # going left
                    x_momentum += dt * move_speed
                    if x_momentum > 0.1:
                        x_momentum = 0

            if y_momentum < 0:  # falling down
                if base_pos[1] < self.base_ground_pos:
                    move_speed += self.Character_Gravity
                    y_momentum = -self.Character_Gravity
                else:  # reach ground, stop all momentum
                    y_momentum = 0
                    x_momentum = 0

            self.x_momentum = x_momentum
            self.y_momentum = y_momentum

        else:  # no movement allow for action that is not movable
            self.x_momentum = 0
            self.y_momentum = 0
