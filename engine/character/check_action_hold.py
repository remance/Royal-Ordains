def check_action_hold(self, dt):
    if "hold" in self.current_animation_direction[self.show_frame]["property"] and \
            "hold" in self.current_action and \
            ((not self.current_moveset and "forced move" not in self.current_action) or
             ("forced move" in self.current_action and (self.x_momentum or self.y_momentum)) or
             (self.current_moveset and "can_hold" in self.current_moveset["Property"])):
        if self.current_moveset and "can_hold" in self.current_moveset["Property"]:
            self.hold_timer += dt
            self.hold_power_bonus = 1
            if self.current_moveset["Property"]["can_hold"] == "power" and self.hold_timer >= 1:
                # hold beyond 1 second to hit harder
                self.hold_power_bonus = 2.5
            elif self.current_moveset["Property"]["can_hold"] == "timing" and 2 >= self.hold_timer >= 1:
                # hold release at specific time
                self.hold_power_bonus = 4
            elif self.current_moveset["Property"]["can_hold"] == "trigger" and self.hold_timer >= 0.5:
                self.hold_timer -= 0.5
                self.resource -= self.current_moveset["Resource Cost"]
                if self.resource < 0:
                    self.resource = 0
                elif self.resource > self.base_resource:
                    self.resource = self.base_resource

                if self.current_moveset["Status"]:  # apply status when auto trigger
                    for effect in self.current_moveset["Status"]:
                        self.apply_status(self, effect)
                        for ally in self.near_ally:
                            if ally[1] <= self.current_moveset["Range"]:
                                ally[0].apply_status(self, effect)
                            else:
                                break
        return True

    elif self.hold_timer > 0:  # no longer holding, reset timer
        self.hold_power_bonus = 1
        self.hold_timer = 0
