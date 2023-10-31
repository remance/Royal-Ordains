from engine.uibattle.uibattle import DamageNumber


def pick_animation(self):
    if self.current_action:  # pick animation with current action
        if "moveset" in self.current_action:
            animation_name = None
            if self.continue_moveset:  # find next moveset that can continue from previous one first
                for move in self.continue_moveset:
                    if tuple(self.moveset_command_key_input[-len(move):]) == move:
                        animation_name = self.equipped_weapon + self.combat_state + self.position + \
                                         self.continue_moveset[move]["Move"]
                        self.current_moveset = self.continue_moveset[move]
                        if "Next Move" in self.continue_moveset[move]:
                            self.continue_moveset = self.continue_moveset[move]["Next Move"]
                        else:
                            self.continue_moveset = None
                        break
            if not animation_name:
                self.continue_moveset = None
                for move in self.moveset[self.position]:
                    if tuple(self.moveset_command_key_input[-len(move):]) == move:
                        animation_name = self.equipped_weapon + "Combat" + self.position + \
                                         self.moveset[self.position][move]["Move"]
                        self.current_moveset = self.moveset[self.position][move]
                        if "skill" not in self.current_action and "Next Move" in self.moveset[self.position][move]:
                            # not skill action check for combo
                            self.continue_moveset = self.current_moveset["Next Move"]
                        break

            if self.current_moveset:
                if self.resource >= self.current_moveset["Resource Cost"] and \
                        self.current_moveset["Move"] not in self.attack_cooldown:

                    self.current_action = self.current_action | self.current_moveset["Property"]  # add property

                    self.resource -= self.current_moveset["Resource Cost"]
                    if self.current_moveset["Cooldown"]:
                        self.attack_cooldown[self.current_moveset["Move"]] = self.current_moveset["Cooldown"]

                    if self.resource < 0:
                        self.resource = 0
                    elif self.resource > self.max_resource:
                        self.resource = self.max_resource

                    if self.current_moveset["Status"]:  # TODO move this? need to make it for effect/other char too
                        for effect in self.current_moveset["Status"]:
                            self.apply_status(effect)
                            for ally in self.near_ally:
                                if ally[1] <= self.current_moveset["Range"]:
                                    ally[0].apply_status(effect)
                                else:
                                    break

                else:  # no resource to do the move, reset to idle
                    if self.current_moveset["Move"] in self.attack_cooldown:  # add cooldown value to screen
                        DamageNumber(str(round(self.attack_cooldown[self.current_moveset["Move"]], 1)),
                                     (self.pos[0], self.pos[1] - (self.sprite_size * 2)), False, self.team, move=False)
                    self.current_moveset = None
                    self.continue_moveset = None
                    animation_name = self.equipped_weapon + self.combat_state + self.position + "Idle"

        else:
            if "guard" in self.current_action:
                self.guarding = 0.1
            else:  # no longer guard
                self.guarding = 0
            self.current_moveset = None
            self.continue_moveset = None
            animation_name = self.equipped_weapon + self.combat_state + self.position + self.current_action["name"]

    else:  # idle animation
        self.current_moveset = None
        self.continue_moveset = None
        animation_name = self.equipped_weapon + self.combat_state + self.position + "Idle"

    if animation_name in self.animation_pool:
        self.current_animation = self.animation_pool[animation_name]
    else:  # animation not found, use default
        print("notfound", self.name, animation_name, self.current_action, self.command_action,
              self.moveset_command_key_input)
        animation_name = "Default"
        self.current_animation = self.animation_pool["Default"]

        # self.current_moveset = None
        # self.continue_moveset = None
        # animation_name = self.equipped_weapon + self.combat_state + self.position + "Idle"
        # self.current_animation = self.animation_pool[animation_name]

    self.current_animation_direction = self.current_animation[self.sprite_direction]
    self.current_animation_data = self.animation_data_pool[animation_name]

    self.max_show_frame = len(self.current_animation_direction) - 1

    self.start_animation_body_part(new_animation=True)
    self.final_animation_play_time = self.animation_play_time  # get new play speed
    if "play_time_mod" in self.current_animation_direction[self.show_frame]:
        self.final_animation_play_time *= self.current_animation_direction[self.show_frame]["play_time_mod"]
