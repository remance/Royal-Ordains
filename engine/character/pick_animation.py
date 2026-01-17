from random import uniform


def pick_animation(self):
    if self.current_action:  # pick animation with current action
        if "direction" in self.current_action:
            self.new_direction = self.current_action["direction"]

        if "moveset" in self.current_action:
            animation_name = None

            if self.current_moveset:  # has moveset to perform
                if "no prepare" not in self.current_action:
                    resource_cost = self.current_moveset["Resource Cost"]
                    if self.current_moveset["Resource Cost"] > 0:
                        # only apply cost modifier for move that reduce resource
                        resource_cost = self.current_moveset["Resource Cost"] * self.resource_cost_modifier
                    if self.resource >= resource_cost or self.is_summon:
                        # has enough resource to perform the moveset or summon that can use health as resource
                        self.get_damage()
                        if self.resource >= resource_cost:
                            self.resource -= resource_cost
                            if self.resource < 0:
                                self.resource = 0
                            elif self.resource > self.base_resource:
                                self.resource = self.base_resource
                        if self.is_summon:
                            # summon also use health
                            self.health -= resource_cost

                        # check if action has prepare/after animation for the moveset
                        self.current_action = self.current_action | self.current_moveset["Property"] | {
                            "no prepare": True}
                        self.current_action["name"] = self.current_moveset["Move"]
                        if self.current_moveset["After Animation"]:
                            self.current_action["next action"] = (
                                    self.current_moveset["After Animation"] | {"no prepare": True})

                        if self.current_moveset[
                            "Prepare Animation"]:  # has animation to do first before performing main animation
                            self.current_action = (self.current_moveset["Prepare Animation"] | {"no prepare": True}
                                                   | {"next action": self.current_action})

                        animation_name = self.current_action["name"]

                        if ("moveset" in self.current_action and not self.battle.ai_battle_speak_timer and
                                "hit" in self.ai_speak_list and uniform(0, 10) > 8):
                            self.ai_speak("hit")

                    else:  # no resource to start the move, reset to idle
                        self.current_moveset = None
                else:
                    animation_name = self.current_action["name"]

            if not animation_name:  # None animation_name from no moveset found, use idle
                self.current_moveset = None
                self.current_action = {}
                animation_name = "Idle"
                self.current_animation = self.animation_pool[animation_name]

        else:  # animation that is not related to action moveset
            self.current_moveset = None
            animation_name = self.current_action["name"]

    else:  # idle animation
        self.current_moveset = None
        if not self.replace_idle_animation:
            animation_name = "Idle"
        else:
            animation_name = self.replace_idle_animation

    # new action property
    if "x_momentum" in self.current_action:
        x_momentum = self.current_action["x_momentum"]
        if type(x_momentum) is tuple:
            x_momentum = uniform(self.current_action["x_momentum"][0], self.current_action["x_momentum"][1])
        if self.new_direction == "right":
            self.x_momentum = x_momentum
        else:
            self.x_momentum = -x_momentum
    if "y_momentum" in self.current_action:
        y_momentum = self.current_action["y_momentum"]
        if type(y_momentum) is tuple:
            y_momentum = uniform(self.current_action["y_momentum"][0], self.current_action["y_momentum"][1])
        self.y_momentum = y_momentum

    if animation_name in self.animation_pool:
        self.current_animation = self.animation_pool[animation_name]
    else:  # animation not found, use default  # TODO remove this in stable
        print("notfound", self.name, animation_name, self.current_action, self.command_action, self.alive,
              self.invincible, self.health)
        self.current_animation = self.animation_pool["Default"]

    if "reverse" not in self.current_action:
        self.max_show_frame = self.current_animation["max frame"]
    else:
        self.max_show_frame = 0
        self.show_frame = self.current_animation["max frame"]

    self.current_animation_frame = self.current_animation[self.show_frame]
    self.current_animation_direction = self.current_animation_frame[self.direction]

    self.final_animation_frame_play_time = self.animation_frame_play_time  # get new play speed
    if "fixed play speed" in self.current_action:  # moveset does not allow animation speed modifier effect
        self.final_animation_frame_play_time = self.Base_Animation_Frame_Play_Time
    if "play_time_mod" in self.current_animation_frame:
        self.final_animation_frame_play_time *= self.current_animation_frame["play_time_mod"]

    if self.current_animation_frame["sound_effect"]:  # play sound from animation
        sound = self.current_animation_frame["sound_effect"]
        self.battle.add_sound_effect_queue(self.sound_effect_pool[sound[0]][0],
                                           self.pos, sound[1], sound[2])

    self.animation_name = animation_name
    self.update_sprite = True
