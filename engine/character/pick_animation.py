from random import uniform


def pick_animation(self):
    current_action = self.current_action
    if current_action:  # pick animation with current action
        if "direction" in current_action:
            self.new_direction = current_action["direction"]

        if "moveset" in current_action:
            animation_name = None
            current_moveset = self.current_moveset
            if current_moveset:  # has moveset to perform
                if "no prepare" not in current_action:
                    resource_cost = current_moveset["Resource Cost"]
                    if current_moveset["Resource Cost"] > 0:
                        # only apply cost modifier for move that reduce resource
                        resource_cost = current_moveset["Resource Cost"] * self.resource_cost_modifier
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
                        current_action = current_action | self.current_moveset_property | {
                            "no prepare": True}
                        current_action["name"] = current_moveset["Move"]
                        if current_moveset["After Animation"]:
                            current_action["next action"] = (
                                    current_moveset["After Animation"] | {"no prepare": True})

                        if current_moveset["Prepare Animation"]:
                            # has animation to do first before performing main animation
                            current_action = (current_moveset["Prepare Animation"] | {"no prepare": True}
                                              | {"next action": current_action})

                        animation_name = current_action["name"]

                        if ("moveset" in current_action and not self.battle.ai_battle_speak_timer and
                                "hit" in self.ai_speak_list and uniform(0, 10) > 8):
                            self.ai_speak("hit")

                    else:  # no resource to start the move, reset to idle
                        self.current_moveset = None
                        self.current_moveset_property = None
                else:
                    animation_name = current_action["name"]

            if not animation_name:  # None animation_name from no moveset found, use idle
                self.current_moveset = None
                self.current_moveset_property = None
                current_action = {}
                animation_name = "Idle"
                self.current_animation = self.animation_pool[animation_name]

        else:  # animation that is not related to action moveset
            self.current_moveset = None
            self.current_moveset_property = None
            animation_name = current_action["name"]

    else:  # idle animation
        self.current_moveset = None
        self.current_moveset_property = None
        if not self.replace_idle_animation:
            animation_name = "Idle"
        else:
            animation_name = self.replace_idle_animation

    # new action property
    if "x_momentum" in current_action:
        x_momentum = current_action["x_momentum"]
        if type(x_momentum) is tuple:
            x_momentum = uniform(current_action["x_momentum"][0], current_action["x_momentum"][1])
        if self.new_direction == "right":
            self.x_momentum = x_momentum
        else:
            self.x_momentum = -x_momentum
    if "y_momentum" in current_action:
        y_momentum = current_action["y_momentum"]
        if type(y_momentum) is tuple:
            y_momentum = uniform(current_action["y_momentum"][0], current_action["y_momentum"][1])
        self.y_momentum = y_momentum

    if animation_name in self.animation_pool:
        self.current_animation = self.animation_pool[animation_name]
    else:  # animation not found, use default  # TODO remove this in stable
        print("notfound", self.name, animation_name, current_action, self.command_action)
        self.current_animation = self.animation_pool["Default"]

    if "reverse" not in current_action:
        self.max_show_frame = self.current_animation["max frame"]
    else:
        self.max_show_frame = 0
        self.show_frame = self.current_animation["max frame"]

    self.current_animation_frame = self.current_animation[self.show_frame]
    self.current_animation_direction = self.current_animation_frame[self.direction]

    self.final_animation_frame_play_time = self.animation_frame_play_time  # get new play speed
    if "fixed play speed" in current_action:  # moveset does not allow animation speed modifier effect
        self.final_animation_frame_play_time = self.Base_Animation_Frame_Play_Time
    if "play_time_mod" in self.current_animation_frame:
        self.final_animation_frame_play_time *= self.current_animation_frame["play_time_mod"]

    if self.current_animation_frame["sound_effect"]:  # play sound from animation
        sound = self.current_animation_frame["sound_effect"]
        self.battle.add_sound_effect_queue(self.sound_effect_pool[sound[0]][0],
                                           self.pos, sound[1], sound[2])

    self.current_action = current_action
    self.animation_name = animation_name
    self.update_sprite = True


def pick_cutscene_animation(self, action):
    """Pick animation to play for cutscene, simpler than normal pick_animation"""
    # reset various animation variable
    self.interrupt_animation = False
    self.show_frame = 0
    self.frame_timer = 0
    self.x_momentum = 0
    self.y_momentum = 0
    self.command_action = {}

    self.current_action = action
    if "name" in action:  # pick animation with cutscene animation data
        animation_name = action["name"]
        # self.angle = self.current_action["angle"]
    else:  # idle animation
        if not self.replace_idle_animation:
            animation_name = "Idle"
        else:
            animation_name = self.replace_idle_animation

    if animation_name in self.animation_pool:
        self.current_animation = self.animation_pool[animation_name]
    else:  # animation not found, use default
        print("cutscene_animation_not_found", self.name, animation_name, action)

        self.current_animation = self.animation_pool["Default"]

    if "reverse" not in action:
        self.max_show_frame = self.current_animation["max frame"]
    else:
        self.max_show_frame = 0
        self.show_frame = self.current_animation["max frame"]
    if "start_frame" in action:
        self.show_frame = int(self.cutscene_event["Property"]["start_frame"])
        if self.show_frame < 0:
            self.show_frame += len(self.current_animation_direction)
            if self.show_frame < 0:
                self.show_frame = 0

    self.current_animation_frame = self.current_animation[self.show_frame]
    self.current_animation_direction = self.current_animation_frame[self.direction]

    self.final_animation_frame_play_time = self.default_animation_play_time  # use default play speed
    if "play_time_mod" in self.current_animation:
        self.final_animation_frame_play_time *= self.current_animation_frame["play_time_mod"]

    if self.current_animation_frame["sound_effect"]:  # play sound from animation
        sound = self.current_animation_frame["sound_effect"]
        self.battle.add_sound_effect_queue(self.sound_effect_pool[sound[0]][0],
                                           self.pos, sound[1], sound[2])

    self.animation_name = animation_name
    self.update_sprite = True
