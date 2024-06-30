from engine.uibattle.uibattle import DamageNumber


def pick_animation(self):
    if self.current_action:  # pick animation with current action
        if "moveset" in self.current_action:
            animation_name = None
            if self.current_moveset:  # has moveset to perform
                animation_name = self.equipped_weapon + "Combat" + self.position + \
                                 self.current_moveset["Move"]

                if "no prepare" not in self.current_action:  # check if action has prepare animation to perform
                    self.current_action = self.check_prepare_action(
                        self.current_moveset)  # check for prepare animation first
                if "sub action" not in self.current_action:  # main action now, not prepare or after action
                    resource_cost = self.current_moveset["Resource Cost"]
                    if self.current_moveset["Resource Cost"] > 0:
                        # only apply cost modifier for move that reduce resource
                        resource_cost = self.current_moveset["Resource Cost"] * self.resource_cost_modifier
                    if (self.resource >= resource_cost or (self.health_as_resource and
                                                           (self.health > resource_cost or self.is_summon))) and \
                            self.current_moveset["Move"] not in self.attack_cooldown:
                        self.current_action = self.current_action | self.current_moveset["Property"]  # add property

                        if self.resource >= resource_cost:
                            self.resource -= resource_cost
                            if self.resource < 0:
                                self.resource = 0
                            elif self.resource > self.base_resource:
                                self.resource = self.base_resource
                        else:  # use health, no need require check since condition above should do it already
                            self.health -= resource_cost

                        if self.current_moveset["Cooldown"]:
                            self.attack_cooldown[self.current_moveset["Move"]] = self.current_moveset["Cooldown"]

                    else:  # no resource to do the move, reset to idle
                        if self.current_moveset["Move"] in self.attack_cooldown:  # add cooldown value to screen
                            DamageNumber(str(round(self.attack_cooldown[self.current_moveset["Move"]], 1)),
                                         (self.pos[0], self.pos[1] - (self.sprite_height * 2)), False, self.team,
                                         move=False)
                        self.current_moveset = None
                        self.continue_moveset = None
                        animation_name = self.equipped_weapon + self.combat_state + self.position + "Idle"
                        if self.special_combat_state:
                            self.special_combat_state = 0

                else:  # prepare animation simply play without action related stuff
                    animation_name = self.equipped_weapon + self.combat_state + self.position + self.current_action[
                        "name"]

            if not animation_name:  # None animation_name from no moveset found, use idle
                self.current_moveset = None
                self.continue_moveset = None
                self.current_action = {}
                animation_name = self.equipped_weapon + self.combat_state + self.position + "Idle"
                self.current_animation = self.animation_pool[animation_name]

        else:  # animation that is not related to action moveset
            self.current_moveset = None
            self.continue_moveset = None
            animation_name = self.equipped_weapon + self.combat_state + self.position + self.current_action["name"]

    else:  # idle animation
        self.current_moveset = None
        self.continue_moveset = None
        if not self.fly and self.position == "Air" and self.y_momentum < 0:  # air fall animation
            animation_name = self.equipped_weapon + "CombatAirFall"
        else:  # idle
            if not self.replace_idle_animation:
                animation_name = self.equipped_weapon + self.combat_state + self.position + "Idle"
            else:
                animation_name = self.replace_idle_animation
            if self.special_combat_state and self.combat_state == "Combat":
                # use special idle if char has special state
                animation_name += str(self.special_combat_state)

    if "guard" in self.current_action:
        self.guarding = 0.1
    else:  # no longer guard
        self.guarding = 0

    if animation_name in self.animation_pool:
        self.current_animation = self.animation_pool[animation_name]
    else:  # animation not found, use default  # TODO remove in stable?
        print("notfound", self.name, animation_name, self.current_action, self.command_action, self.alive)
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
