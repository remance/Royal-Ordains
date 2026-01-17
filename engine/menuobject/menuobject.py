from pygame.transform import rotate, flip

from engine.uimenu.uimenu import UIMenu


class StaticImage(UIMenu):
    def __init__(self, pos, layer, image):
        self._layer = layer
        UIMenu.__init__(self, player_cursor_interact=False, has_containers=True)
        self.image = image
        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)


class MenuRotate(UIMenu):
    def __init__(self, pos, image, rotate_speed, layer, rotate_left=True, start_angle=0):
        self._layer = layer
        UIMenu.__init__(self, player_cursor_interact=False, has_containers=True)
        self.image = image
        self.base_image = self.image.copy()
        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)
        self.rotate_speed = rotate_speed
        self.rotate_left = rotate_left
        self.angle = start_angle
        if not self.rotate_left:
            self.angle = 360

    def update(self):
        if self.rotate_left:
            self.angle += self.game.dt * self.rotate_speed
        else:
            self.angle -= self.game.dt * self.rotate_speed
        if self.angle > 360:  # reset back
            self.angle -= 360
        elif self.angle < 0:
            self.angle = 360
        self.image = rotate(self.base_image, self.angle)
        self.rect = self.image.get_rect(center=self.pos)


class MenuActor(UIMenu):
    def __init__(self, pos, images, layer, animation_frame_play_time=0.1, start_frame=0, flip_sprite=False):
        self._layer = layer
        UIMenu.__init__(self, has_containers=True)
        self.current_animation = images
        self.pos = pos
        self.frame_timer = 0
        self.animation_frame_play_time = animation_frame_play_time
        self.show_frame = start_frame
        self.flip_sprite = flip_sprite
        self.image = self.current_animation[self.show_frame]
        if self.flip_sprite:
            self.image = flip(self.image, True, False)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self):
        if self.current_animation:  # play animation if more than 1 frame
            self.frame_timer += self.game.dt
            if self.frame_timer >= self.animation_frame_play_time:
                self.frame_timer = 0
                if self.show_frame < len(self.current_animation) - 1:
                    self.show_frame += 1
                    self.image = self.current_animation[self.show_frame]
                else:
                    self.show_frame = 0
                    self.image = self.current_animation[self.show_frame]
                if self.flip_sprite:
                    self.image = flip(self.image, True, False)
                self.rect = self.image.get_rect(center=self.pos)

        # self.image = rotate(self.image, self.angle)
