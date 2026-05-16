def rotate_logic(self):
    if self.direction != self.new_direction:
        self.direction = self.new_direction  # character can rotate at once
        if self.sub_characters:
            for sub_characters in self.sub_characters:  # also change direction of idle sub characters
                if not sub_characters.current_action:
                    sub_characters.new_direction = self.new_direction
        self.current_animation_direction = self.current_animation_frame[self.direction]
        self.update_sprite = True
