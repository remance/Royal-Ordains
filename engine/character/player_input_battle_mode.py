rotation_list = (90, -90)
rotation_name = ("Left", "Right")
rotation_dict = {key: rotation_list[index] for index, key in enumerate(rotation_name)}


def player_input_battle_mode(self, player_index, dt):
    if self.alive:
        # for key in self.battle.command_key_hold:
        run_input = False
        self.command_key_hold = []
        if "uncontrollable" not in self.current_action:
            for key, pressed in self.battle.player_key_press[player_index].items():
                if pressed:
                    new_key = key
                    if key in ("Left", "Right"):  # replace left right input with forward one for moveset check
                        if rotation_dict[key] == self.angle:
                            new_key = "Forward"
                        else:
                            new_key = "Backward"
                    self.player_command_key_input.append(key)
                    self.command_key_input.append(new_key)
                    self.player_key_input_timer.append(0.5)
                    self.last_command_key_input = key

            for key, pressed in self.battle.player_key_hold[player_index].items():
                if pressed:
                    if key not in self.player_key_hold_timer:  # start holding
                        self.player_key_hold_timer[key] = 0
                    else:  # increase hold timer
                        self.player_key_hold_timer[key] += dt
                        if self.player_key_hold_timer[key] > 0.05:  # only count as start holding after specific time
                            self.command_key_hold.append(key)
                elif key in self.player_key_hold_timer:  # no longer hold
                    self.player_key_hold_timer.pop(key)

            self.player_command_key_input = self.player_command_key_input[-5:]
            self.command_key_input = self.command_key_input[-5:]  # keep only last 5 inputs
            self.player_key_input_timer = self.player_key_input_timer[-5:]

            if self.player_key_input_timer:
                self.player_key_input_timer = [item - dt for item in self.player_key_input_timer]
                for index, item in reversed(tuple(enumerate(self.player_key_input_timer))):
                    if item <= 0:  # remove input older that timer run out
                        self.command_key_input.pop(index)
                        self.player_key_input_timer.pop(index)

            if (self.command_key_input and 0.2 <= self.player_key_input_timer[-1] <= 0.4) or self.command_key_hold:
                # delay input a bit so a bit of time pass before taking action
                if "knockdown" in self.current_action:
                    if self.knock_recover and self.last_command_key_input == "Guard":
                        # restore from knockdown action
                        self.interrupt_animation = True
                        self.freeze_timer = 0
                        self.x_momentum = 0
                else:
                    if self.last_command_key_input == "Weak":
                        if "moveset" not in self.current_action or \
                                ("moveset" not in self.command_action and self.stoppable_frame):
                            self.moveset_command_key_input = tuple(self.command_key_input)
                            if "run" in self.current_action and self.slide_attack:
                                self.command_action = self.weak_attack_run_command_action
                                self.current_moveset = self.moveset[self.position]["Slide"]
                            elif self.check_move_existence():
                                self.engage_combat()
                                self.command_action = self.weak_attack_command_action

                    elif self.last_command_key_input == "Strong":
                        if "moveset" not in self.current_action or \
                                ("moveset" not in self.command_action and self.stoppable_frame):
                            self.moveset_command_key_input = tuple(self.command_key_input)
                            if "run" in self.current_action and self.tackle_attack:
                                self.command_action = self.strong_attack_run_command_action
                                self.current_moveset = self.moveset[self.position]["Tackle"]
                            elif self.check_move_existence():
                                self.engage_combat()
                                self.command_action = self.strong_attack_command_action

                    elif self.last_command_key_input == "Guard" or "Guard" in self.command_key_hold:
                        self.engage_combat()
                        if "guard" in self.current_action and "Guard" in self.command_key_hold:
                            if self.position not in ("Air", "Couch") and \
                                    self.guard_move and (self.command_key_hold and
                                                         self.command_key_hold[-1] == "Left" or
                                                         self.command_key_hold[-1] == "Right"):
                                # move while guarding, only in standing position
                                if self.command_key_hold[-1] == "Left":
                                    self.x_momentum = -self.walk_speed / 10
                                else:
                                    self.x_momentum = self.walk_speed / 10
                                self.current_action = self.guard_move_command_action
                                self.command_action = self.guard_move_command_action
                            elif "movable" not in self.current_action:
                                self.current_action = self.guard_hold_command_action

                        elif "run" in self.current_action and self.dash_move:
                            self.interrupt_animation = True
                            self.command_action = self.dash_command_action
                            if self.sprite_direction == "r_side":
                                self.x_momentum = self.run_speed
                            else:
                                self.x_momentum = -self.run_speed

                        elif (not self.current_action or self.stoppable_frame) and \
                                self.guard_meter >= self.guard_meter20:
                            # can only start guarding when meter higher than 20%
                            if self.stoppable_frame:
                                self.interrupt_animation = True
                            self.command_action = self.guard_command_action

                    elif self.last_command_key_input == "Special":
                        if "moveset" not in self.current_action or \
                                ("moveset" not in self.command_action and self.stoppable_frame):
                            self.moveset_command_key_input = tuple(self.command_key_input)
                            self.specific_special_check()

                    elif "moveset" in self.current_action:  # check for holding attack
                        if self.command_key_hold:
                            if "Weak" in self.command_key_hold and "weak" in self.current_action:
                                self.current_action = self.weak_attack_hold_command_action

                            elif "Strong" in self.command_key_hold and "strong" in self.current_action:
                                self.current_action = self.strong_attack_hold_command_action

                            elif "Special" in self.command_key_hold and "special" in self.current_action:
                                self.current_action = self.special_hold_command_action

                    elif self.last_command_key_input == "Down" and "couch" not in self.current_action and \
                            "air" not in self.current_action and self.position == "Stand":
                        self.engage_combat()
                        if self.stoppable_frame:
                            self.interrupt_animation = True
                        self.command_action = self.couch_command_action

                    if self.position == "Stand" and "air" not in self.command_action and \
                            "dash" not in self.command_action:
                        # character movement during stand position
                        if self.last_command_key_input == "Up":  # jump
                            self.engage_combat()
                            self.interrupt_animation = True
                            self.command_action = self.jump_command_action

                            if "run" in self.current_action:
                                self.command_action = self.runjump_command_action

                            if "Left" in self.command_key_hold:
                                self.x_momentum = -self.jump_power
                            elif "Right" in self.command_key_hold:
                                self.x_momentum = self.jump_power

                        elif self.last_command_key_input == "Left" or \
                                (self.command_key_hold and self.command_key_hold[-1] == "Left"):
                            if len(self.command_key_input) > 1:  # check for run input with double press
                                if self.player_command_key_input[-1] == "Left" and \
                                        self.player_command_key_input[-2] == "Left":
                                    # double press move to run
                                    if "moveset" in self.current_action and self.dash_move:  # dash during attack
                                        self.interrupt_animation = True
                                        self.command_action = self.dash_command_action
                                        self.x_momentum = -self.run_speed / 2
                                    elif "dash" not in self.current_action:
                                        run_input = True
                                        self.x_momentum = -self.run_speed / 10
                                elif self.player_command_key_input[-1] == "Right" and "run" in self.current_action:
                                    # halt
                                    self.interrupt_animation = True
                                    self.command_action = self.halt_command_action
                                    self.x_momentum = -self.walk_speed
                                    self.player_command_key_input = []
                                    self.command_key_input = []
                                    self.player_key_input_timer = []
                            else:
                                self.new_angle = 90
                                if not self.current_action or "movable" in self.current_action:
                                    self.x_momentum = -self.walk_speed / 10

                        elif self.last_command_key_input == "Right" or \
                                (self.command_key_hold and self.command_key_hold[-1] == "Right"):
                            if len(self.command_key_input) > 1:  # check for run input with double press
                                if self.player_command_key_input[-1] == "Right" and \
                                        self.player_command_key_input[-2] == "Right":
                                    # double press move to run
                                    if "moveset" in self.current_action and self.dash_move:  # dash during attack
                                        self.interrupt_animation = True
                                        self.command_action = self.dash_command_action
                                        self.x_momentum = self.run_speed / 2
                                    elif "dash" not in self.current_action:
                                        run_input = True
                                        self.x_momentum = self.run_speed / 10
                                elif self.player_command_key_input[-1] == "Left" and "run" in self.current_action:
                                    # halt
                                    self.interrupt_animation = True
                                    self.command_action = self.halt_command_action
                                    self.x_momentum = self.walk_speed
                                    self.player_command_key_input = []
                                    self.command_key_input = []
                                    self.player_key_input_timer = []
                            else:
                                self.new_angle = -90
                                if not self.current_action or "movable" in self.current_action:
                                    self.x_momentum = self.walk_speed / 10

                        if self.x_momentum:
                            if "air" not in self.current_action and "guard" not in self.current_action and \
                                    self.position != "Air" and "dash" not in self.current_action:
                                # movement with air does not use specific command action
                                if not self.command_action:
                                    self.command_action = self.walk_command_action
                                    if run_input or "run" in self.current_action:
                                        self.engage_combat()
                                        if "walk" in self.current_action:  # reset walk animation to run
                                            self.interrupt_animation = True
                                        self.command_action = self.run_command_action

                    elif self.position == "Air":
                        if (self.double_jump and self.can_double_jump) or self.unlimited_jump:
                            if self.last_command_key_input == "Up":
                                self.interrupt_animation = True
                                self.command_action = self.jump_command_action
                                if self.position == "Air":
                                    self.can_double_jump = False

                                if self.command_key_hold and self.command_key_hold[-1] == "Left":
                                    self.x_momentum = -self.jump_power
                                elif self.command_key_hold and self.command_key_hold[-1] == "Right":
                                    self.x_momentum = self.jump_power

                    elif self.position == "Couch":  # switch direction during couch
                        if "Down" in self.command_key_hold:
                            if self.last_command_key_input == "Left":
                                self.new_angle = 90

                            elif self.last_command_key_input == "Right":
                                self.new_angle = -90

                self.last_command_key_input = None

            if "guard" in self.current_action and "hold" in self.current_action and "Guard" not in self.command_key_hold:
                # release guard holding
                self.current_action = self.guard_command_action

            elif "hold" in self.current_action:  # no longer hold attack move
                if "weak" in self.current_action and "Weak" not in self.command_key_hold:
                    self.current_action = self.weak_attack_command_action

                elif "strong" in self.current_action and "Strong" not in self.command_key_hold:
                    self.current_action = self.strong_attack_command_action

                elif "special" in self.current_action and "Special" not in self.command_key_hold:
                    self.current_action = self.special_command_action

            elif self.position == "Couch" and "Down" not in self.command_key_hold:  # couch require holding down button
                self.command_action = self.couch_stand_command_action
