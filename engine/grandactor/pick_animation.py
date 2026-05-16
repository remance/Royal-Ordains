def pick_animation(self, animation_name):
    """Pick animation to play for cutscene, simpler than normal pick_animation"""
    # reset various animation variable
    self.show_frame = 0
    self.frame_timer = 0
    if animation_name in self.animation_pool:
        self.current_animation = self.animation_pool[animation_name]
    else:  # animation not found, use default
        print("grand_animation_not_found", self.name, animation_name)

        self.current_animation = self.animation_pool["Default"]

    self.max_show_frame = len(self.current_animation) - 1
    self.current_animation_frame = self.current_animation[self.show_frame]
    self.current_animation_direction = self.current_animation_frame[self.direction]

    self.final_animation_frame_play_time = self.animation_frame_play_time  # use default play speed
    if "play_time_mod" in self.current_animation:
        self.final_animation_frame_play_time *= self.current_animation_frame["play_time_mod"]

    self.animation_name = animation_name
    self.update_sprite = True
