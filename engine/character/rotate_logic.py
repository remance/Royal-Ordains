from math import radians

from engine.character.character import rotation_dict


def rotate_logic(self):
    self.angle = self.new_angle  # arcade mode doesn't have gradual rotate, character can rotate at once
    self.radians_angle = radians(360 - self.angle)
    if self.new_angle:  # angle 0 mean not change direction
        if self.new_angle > 0:
            sprite_angle = 90
        else:
            sprite_angle = -90

        if self.sprite_direction != rotation_dict[sprite_angle]:
            self.sprite_direction = rotation_dict[sprite_angle]  # find closest in list of rotation for sprite direction
            self.current_animation_direction = self.current_animation[self.sprite_direction]
            # self.image = self.current_animation_direction[self.show_frame]["sprite"]
            # self.offset_pos = self.pos - self.current_animation_direction[self.show_frame]["offset"]
            # self.rect = self.image.get_rect(midbottom=self.offset_pos)

            for part in self.body_parts.values():
                part.re_rect()
