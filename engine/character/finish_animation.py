def finish_animation(self, done):
    # Pick new action and animation, either when animation finish or get interrupt,
    # action that require movement to run out first before continue to next action
    current_action = self.current_action
    command_action = self.command_action
    current_moveset = self.current_moveset
    if ((self.interrupt_animation and "uninterruptible" not in current_action) or
            (("x_momentum" in current_action and not self.x_momentum) or
             ("y_momentum" in current_action and not self.y_momentum) or
             ("end_when_done" in current_action and done)) or
            ("repeat" not in current_action and ((not current_action and command_action) or done))):
        # finish current action
        self.already_hit = []
        if current_moveset:
            # add move cooldown when the animation is completely done or interrupted
            if ("next action" not in current_action or self.interrupt_animation) and current_moveset["Cooldown"]:
                self.move_cooldown[current_moveset["Move"]] = current_moveset["Cooldown"]
            if done:  # apply status only for action animation that is finished playing, not interrupted
                if current_moveset["Status"]:  # moveset apply status effect to self and allies in range
                    for effect in current_moveset["Status"]:
                        self.apply_status(effect)
                        for ally in self.near_ally:  # loop ally after effect so effect apply loop is more efficient
                            if ally[1] <= current_moveset["Range"]:  # apply status based on range
                                ally[0].apply_status(effect)
                            else:  # further ally from range, no longer need to check
                                break

                if current_moveset["Enemy Status"]:
                    for enemy in self.near_enemy:
                        for effect in current_moveset["Enemy Status"]:
                            if enemy[1] <= current_moveset["Range"]:  # apply status based on range
                                enemy[0].apply_status(effect)
                            else:  # further enemy from range, no longer need to check
                                break

        if "next action" in current_action and (not self.interrupt_animation or
                                                "interruptable" in command_action) and \
                (not current_moveset or "no auto next" not in self.current_moveset_property):
            # play next action from current set first instead of next command if not finish by interruption
            self.current_action = current_action["next action"]
        else:
            self.current_action = command_action  # continue next command action when animation set finish
            self.command_action = {}

        # reset animation playing related value
        self.interrupt_animation = False
        self.hold_too_long_timer = 0
        self.hold_timer = 0
        self.show_frame = 0
        self.frame_timer = 0

        self.pick_animation()
