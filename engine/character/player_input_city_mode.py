rotation_list = (90, -90)
rotation_name = ("Left", "Right")
rotation_dict = {key: rotation_list[index] for index, key in enumerate(rotation_name)}


def player_input_city_mode(self, player_index, dt):
    """Only take movement key command in city mode"""
    if self.alive:
        # for key in self.battle.command_key_hold:
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
                if self.last_command_key_input == "Left" or \
                        (self.command_key_hold and self.command_key_hold[-1] == "Left"):
                    self.new_angle = 90
                    if not self.current_action or "movable" in self.current_action:
                        self.x_momentum = -self.city_walk_speed / 10

                elif self.last_command_key_input == "Right" or \
                        (self.command_key_hold and self.command_key_hold[-1] == "Right"):
                    self.new_angle = -90
                    if not self.current_action or "movable" in self.current_action:
                        self.x_momentum = self.city_walk_speed / 10

                if self.x_momentum:
                    if not self.command_action:
                        self.command_action = self.walk_command_action

                self.last_command_key_input = None
