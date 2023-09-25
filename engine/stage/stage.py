from pygame.sprite import Sprite


class Stage(Sprite):
    image = None

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
        self.current_frame = 1
        self.spawn_frame = 1
        self.camera_x = 0

    def update(self, camera_x):
        if self.data:
            self.camera_x = camera_x
            current_frame = self.camera_x / self.screen_width
            if current_frame == 1:
                self.current_frame = 2
                self.spawn_frame = 2
            if current_frame == 0.5:  # at center of first frame
                self.current_frame = 1
                self.spawn_frame = 1
            elif abs(current_frame - int(current_frame)) >= 0.5:  # at right half of frame
                self.current_frame = int(current_frame) + 1
                self.spawn_frame = int(current_frame) + 1
            else:
                self.current_frame = int(current_frame)  # at left half of frame
                self.spawn_frame = int(current_frame) + 1
            camera_scale = (self.camera_x - (self.screen_width * self.current_frame)) / self.screen_width

            if abs(camera_scale - int(camera_scale)) != 0.5:
                if camera_scale > 0.5:
                    camera_scale = (camera_scale, 1 - camera_scale)
                elif camera_scale > -0.5:
                    camera_scale = (0.5 + camera_scale, -camera_scale + 0.5)
                else:
                    camera_scale = (-camera_scale, camera_scale)

                if self.current_frame in self.data:
                    frame_one = self.images[self.data[self.current_frame]]
                    rect = frame_one.get_rect(midright=(self.screen_width - (self.screen_width * camera_scale[0]),
                                                        frame_one.get_height() / 2))
                    self.image.blit(frame_one, rect)

                if self.current_frame + 1 in self.data:
                    frame_two = self.images[self.data[self.current_frame + 1]]
                    rect = frame_two.get_rect(midleft=(self.screen_width * camera_scale[1], frame_two.get_height() / 2))
                    self.image.blit(frame_two, rect)
            else:
                if self.current_frame in self.data:
                    frame_image = self.images[self.data[self.current_frame]]
                    rect = frame_image.get_rect(center=(frame_image.get_width() / 2, frame_image.get_height() / 2))
                    self.image.blit(frame_image, rect)
        elif self.images:
            self.image.blit(self.images[0], (0, 0))

    def clear_image(self):
        self.data = {}
        self.images = {}
        self.camera_x = -1000
        self.current_frame = 1
        self.spawn_frame = 1
