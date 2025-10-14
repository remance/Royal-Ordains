def pick_cutscene_animation(self, action):
    """Pick animation to play for cutscene, simpler than normal pick_animation"""
    # reset various animation variable
    self.interrupt_animation = False
    self.show_frame = 0
    self.frame_timer = 0
    self.x_momentum = 0
    self.y_momentum = 0
    self.move_speed = 0
    self.command_action = {}

    self.current_action = action
    if "name" in self.current_action:  # pick animation with cutscene animation data
        animation_name = self.current_action["name"]
        # self.angle = self.current_action["angle"]
    else:  # idle animation
        if not self.replace_idle_animation:
            animation_name = "Idle"
        else:
            animation_name = self.replace_idle_animation

    if animation_name in self.animation_pool:
        self.current_animation = self.animation_pool[animation_name]
    else:  # animation not found, use default
        print("cutscene_animation_not_found", self.name, animation_name, self.current_action)

        self.current_animation = self.animation_pool["Default"]

    if "reverse" not in self.current_action:
        self.max_show_frame = self.current_animation["max frame"]
    else:
        self.max_show_frame = 0
        self.show_frame = self.current_animation["max frame"]
    if "start_frame" in self.current_action:
        self.show_frame = int(self.cutscene_event["Property"]["start_frame"])
        if self.show_frame < 0:
            self.show_frame += len(self.current_animation_direction)
            if self.show_frame < 0:
                self.show_frame = 0

    self.current_animation_frame = self.current_animation[self.show_frame]
    self.current_animation_direction = self.current_animation_frame[self.direction]

    self.final_animation_play_time = self.default_animation_play_time  # use default play speed
    if "play_time_mod" in self.current_animation:
        self.final_animation_play_time *= self.current_animation_frame["play_time_mod"]

    if self.current_animation_frame["sound_effect"]:  # play sound from animation
        sound = self.current_animation_frame["sound_effect"]
        self.battle.add_sound_effect_queue(self.sound_effect_pool[sound[0]][0],
                                           self.pos, sound[1], sound[2])

    self.update_sprite = True
