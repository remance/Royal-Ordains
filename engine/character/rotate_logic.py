def rotate_logic(self):
    if self.direction != self.new_direction:
        self.direction = self.new_direction  # character can rotate at once
        self.current_animation_direction = self.current_animation_frame[self.direction]
        self.update_sprite = True
