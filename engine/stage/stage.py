from pygame.sprite import Sprite


class Stage(Sprite):
    image = None
    camera_center_y = None  # get add later when Battle is initiate

    def __init__(self, layer):
        from engine.game.game import Game

        self.main_dir = Game.main_dir
        self.data_dir = Game.data_dir
        self.screen_scale = Game.screen_scale
        self.screen_size = Game.screen_size
        self.screen_width = self.screen_size[0]
        self.screen_height = self.screen_size[1]
        self.half_screen = self.screen_width / 2
        self.battle = Game.battle
        self._layer = layer
        Sprite.__init__(self)
        self.data = {}
        self.images = {}
        self.current_scene = 1  # index of current scene
        self.spawn_check_scene = 1  # index of current scene, can be higher than current scene when
        self.reach_scene = 1  # next scene that camera reach

        self.alpha = 0
        self.fade_speed = 1
        self.fade_start = False
        self.fade_in = False
        self.fade_out = False
        self.fade_delay = 0

    def update(self, shown_camera_pos, camera_pos):
        camera_y_shift = self.camera_center_y - shown_camera_pos[1]
        current_frame = camera_pos[0] / self.screen_width
        if current_frame == 0.5:  # at center of first scene
            self.current_scene = 1
            self.spawn_check_scene = 1
            self.reach_scene = 1
        elif abs(current_frame - int(current_frame)) >= 0.5:  # at right half of scene
            self.current_scene = int(current_frame) + 1
            self.spawn_check_scene = self.current_scene
            self.reach_scene = self.current_scene + 1
        else:
            self.current_scene = int(current_frame)  # at left half of scene
            self.spawn_check_scene = self.current_scene + 1
            self.reach_scene = self.current_scene
        camera_scale = (camera_pos[0] - (self.screen_width * self.current_scene)) / self.screen_width

        if abs(camera_scale - int(camera_scale)) != 0.5:  # two frames shown in one screen
            if camera_scale > 0.5:
                camera_scale = (camera_scale, 1 - camera_scale)
            elif camera_scale > -0.5:
                camera_scale = (0.5 + camera_scale, -camera_scale + 0.5)
            else:
                camera_scale = (-camera_scale, camera_scale)

            if self.current_scene in self.data:
                frame_one = self.images[self.data[self.current_scene]]
                rect = frame_one.get_rect(topright=(self.screen_width - (self.screen_width * camera_scale[0]),
                                                    camera_y_shift))
                self.image.blit(frame_one, rect)

            if self.current_scene + 1 in self.data:
                frame_two = self.images[self.data[self.current_scene + 1]]
                rect = frame_two.get_rect(topleft=(self.screen_width * camera_scale[1], camera_y_shift))
                self.image.blit(frame_two, rect)
        else:
            if self.current_scene in self.data:
                frame_image = self.images[self.data[self.current_scene]]
                rect = frame_image.get_rect(midtop=(frame_image.get_width() / 2, camera_y_shift))
                self.image.blit(frame_image, rect)

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

    def clear_image(self):
        self.data = {}
        self.images = {}
        self.camera_x = -1000
        self.old_camera_pos = None
        self.current_scene = 1
        self.spawn_check_scene = 1
