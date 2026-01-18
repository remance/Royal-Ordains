def finish_animation(self, done):
    # Pick new action and animation, either when animation finish or get interrupt,
    # action that require movement to run out first before continue to next action

    if ((self.interrupt_animation and "uninterruptible" not in self.current_action) or
            (("x_momentum" in self.current_action and not self.x_momentum) or
             ("y_momentum" in self.current_action and not self.y_momentum) or
             ("end_when_done" in self.current_action and done)) or
            ("repeat" not in self.current_action and ((not self.current_action and self.command_action) or done))):
        # finish current action
        self.already_hit = []
        if self.current_moveset:
            # add move cooldown when the animation is completely done or interrupted
            if ("next action" not in self.current_action or self.interrupt_animation) and self.current_moveset[
                "Cooldown"]:
                self.move_cooldown[self.current_moveset["Move"]] = self.current_moveset["Cooldown"]
            if done:
                if self.current_moveset["Status"]:  # moveset apply status effect
                    for effect in self.current_moveset["Status"]:
                        self.apply_status(effect)
                        for ally in self.near_ally:
                            if ally[0] is not self:
                                if ally[1] <= self.current_moveset["Range"]:  # apply status based on range
                                    ally[0].apply_status(effect)
                                else:
                                    break

        if "next action" in self.current_action and (not self.interrupt_animation or
                                                     "interruptable" in self.command_action) and \
                (not self.current_moveset or "no auto next" not in self.current_moveset["Property"]):
            # play next action from current set first instead of next command if not finish by interruption
            self.current_action = self.current_action["next action"]
        else:
            self.current_action = self.command_action  # continue next command action when animation set finish
            self.command_moveset = {}
            self.command_action = {}

        # reset animation playing related value
        self.interrupt_animation = False
        self.hold_too_long_timer = 0
        self.hold_timer = 0
        self.show_frame = 0
        self.frame_timer = 0

        self.pick_animation()
