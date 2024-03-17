def pick_cutscene_animation(self, action):
    """Pick animation to play for cutscene, simpler than normal pick_animation"""
    # reset various animation variable and position
    self.stoppable_frame = False
    self.hit_enemy = False
    self.interrupt_animation = False
    self.show_frame = 0
    self.frame_timer = 0
    self.release_timer = 0
    self.x_momentum = 0
    self.y_momentum = 0
    self.current_moveset = None
    self.continue_moveset = None
    if self.special_combat_state:
        self.special_combat_state = 0
    self.move_speed = 0
    self.freeze_timer = 0

    self.position = "Stand"
    if self.base_pos[1] < self.ground_pos and not self.fly:
        self.base_pos[1] = self.ground_pos

    self.command_action = {}
    self.current_action = action
    if self.current_action:  # pick animation with cutscene animation data
        animation_name = self.current_action["name"]
        # self.angle = self.current_action["angle"]
    else:  # idle animation
        if not self.replace_idle_animation:
            animation_name = self.equipped_weapon + self.combat_state + self.position + "Idle"
        else:
            animation_name = self.replace_idle_animation

    if animation_name in self.animation_pool:
        self.current_animation = self.animation_pool[animation_name]
    else:  # animation not found, use default
        print("cutsceneanimationnotfound", self.name, animation_name, self.current_action)
        animation_name = "Default"
        self.current_animation = self.animation_pool["Default"]

    self.current_animation_direction = self.current_animation[self.sprite_direction]
    self.current_animation_data = self.animation_data_pool[animation_name]

    self.max_show_frame = len(self.current_animation_direction) - 1

    if self.cutscene_event and "start_frame" in self.cutscene_event["Property"]:
        self.show_frame = int(self.cutscene_event["Property"]["start_frame"])
        if self.show_frame < 0:
            self.show_frame += len(self.current_animation_direction)
            if self.show_frame < 0:
                self.show_frame = 0

    self.start_animation_body_part(new_animation=True)
    self.final_animation_play_time = self.default_animation_play_time  # use default play speed
    if "play_time_mod" in self.current_animation_direction[self.show_frame]:
        self.final_animation_play_time *= self.current_animation_direction[self.show_frame]["play_time_mod"]
