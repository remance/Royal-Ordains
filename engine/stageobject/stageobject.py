from pygame import sprite, Vector2


class StageObject(sprite.Sprite):
    from engine.stageobject.play_animation import play_animation
    play_animation = play_animation

    from engine.stageobject.adjust_sprite import adjust_sprite
    adjust_sprite = adjust_sprite

    battle = None
    screen_scale = None
    stage_object_animation_pool = None

    def __init__(self, sprite_id, pos, game_id=0, angle=0,
                 sprite_flip=0, animation_speed=0.1, width_scale=1, height_scale=1):
        """Stage object with animation"""
        self._layer = 1
        sprite.Sprite.__init__(self, self.containers)
        self.battle_camera_drawer = self.battle.battle_camera_object_drawer
        self.battle_camera_drawer.add(self)
        self.game_id = game_id
        self.show_frame = 0
        self.frame_timer = 0
        self.animation_speed = animation_speed
        self.repeat_animation = True
        self.hold = False
        self.current_animation = self.stage_object_animation_pool[sprite_id][self.battle.chapter]

        self.base_image = self.current_animation[self.show_frame]
        self.image = self.base_image

        if type(pos) is str:
            self.base_pos = Vector2([float(item) for item in pos.split(",")])
        else:
            self.base_pos = Vector2([float(item) for item in pos])

        self.angle = angle
        self.sprite_flip = sprite_flip
        self.width_scale = width_scale
        self.height_scale = height_scale
        self.pos = Vector2((self.base_pos[0] * self.screen_scale[0],
                            self.base_pos[1] * self.screen_scale[1]))
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt):
        self.play_animation(self.animation_speed, dt, self.hold)  # TODO add sound effect to scene object


class RotateStageObject(StageObject):
    def __init__(self, sprite_id, pos, game_id=0, angle=0, flip=0, animation_speed=0.1, width_scale=1,
                 height_scale=1, rotate_speed=10, rotate_left=True):
        StageObject.__init__(self, sprite_id, pos, game_id, angle, flip, animation_speed, width_scale,
                             height_scale)
        self.rotate_speed = rotate_speed
        self.rotate_left = rotate_left
        self.hold = False

    def update(self, dt):
        if not self.hold:
            if self.rotate_left:
                self.angle += dt * self.rotate_speed
            else:
                self.angle -= dt * self.rotate_speed
            if self.angle > 360:  # reset back
                self.angle -= 360
            elif self.angle < 0:
                self.angle = 360
        self.play_animation(self.animation_speed, dt, self.hold)
