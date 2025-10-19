from pygame import SRCALPHA
from pygame.sprite import Sprite
from pygame.surface import Surface


class Scene(Sprite):
    image = None
    battle = None

    def __init__(self):
        from engine.game.game import Game
        self.main_dir = Game.main_dir
        self.data_dir = Game.data_dir
        self.screen_scale = Game.screen_scale
        self.screen_size = Game.screen_size
        self.screen_width = self.screen_size[0]
        self.screen_height = self.screen_size[1]
        self.half_screen = self.screen_width / 2
        self._layer = 0
        Sprite.__init__(self)
        self.data = {}
        self.images = {}
        self.full_scene_image = None
        self.current_scene_image = None
        self.shown_camera_pos = None
        self.camera_y_shift = None
        self.camera_left = None
        self.rect = None

        self.alpha = 0
        self.fade_speed = 1
        self.fade_start = False
        self.fade_in = False
        self.fade_out = False
        self.fade_delay = 0
        self.size_width = self.screen_width
        self.size_height = self.screen_height

    def setup(self):
        self.full_scene_image = Surface((self.screen_width * len(self.data), self.size_height), SRCALPHA)
        for scene_index, image in self.data.items():
            x = (scene_index - 1) * self.images[image].get_width()
            rect = self.images[image].get_rect(topleft=(x, 0))
            self.full_scene_image.blit(self.images[image], rect)
        self.current_scene_image = Surface.subsurface(self.full_scene_image, (self.battle.camera_left, 0,
                                                                              self.size_width, self.size_height))

    def update(self):
        if self.camera_left != self.battle.camera_left:
            self.camera_left = self.battle.camera_left
            self.current_scene_image = Surface.subsurface(self.full_scene_image, (self.camera_left, 0,
                                                                                  self.size_width, self.size_height))
        if self.camera_y_shift != self.battle.camera_y_shift:
            self.camera_y_shift = self.battle.camera_y_shift
            self.rect = self.current_scene_image.get_rect(midtop=(self.current_scene_image.get_width() / 2,
                                                                  self.camera_y_shift))
        self.image.blit(self.current_scene_image, self.rect)

        if self.fade_start:
            if self.fade_in:  # keep fading in
                self.alpha += self.battle.dt * self.fade_speed
                if self.alpha >= 255:
                    self.alpha = 255
                    self.fade_in = False
                self.image.fill((0, 0, 0, self.alpha))
            elif self.fade_out:
                self.alpha -= self.battle.dt * self.fade_speed
                if self.alpha <= 0:
                    self.alpha = 0
                    self.fade_out = False
                self.image.fill((0, 0, 0, self.alpha))

            if self.fade_delay:
                self.fade_delay -= self.battle.dt
                if self.fade_delay < 0:
                    self.fade_delay = 0
            if not self.fade_delay:
                self.fade_start = False
