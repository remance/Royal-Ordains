from pygame import sprite, Vector2


class StageObject(sprite.Sprite):
    from engine.stageobject.play_animation import play_animation
    play_animation = play_animation

    from engine.effect.adjust_sprite import adjust_sprite
    adjust_sprite = adjust_sprite

    battle = None
    screen_scale = None
    stage_object_animation_pool = None

    def __init__(self, sprite_id, pos, game_id=0, angle=None, animation_speed=0.1):
        """Stage object with animation"""
        self._layer = 1
        sprite.Sprite.__init__(self, self.containers)
        self.game_id = game_id
        self.show_frame = 0
        self.frame_timer = 0
        self.animation_speed = animation_speed
        self.repeat_animation = True
        self.current_animation = self.stage_object_animation_pool[sprite_id][self.battle.chapter]

        self.base_image = self.current_animation[self.show_frame]
        self.image = self.base_image

        if type(pos) is str:
            self.base_pos = Vector2([int(item) for item in pos.split(",")[0:2]])
            self.angle = int(pos.split(",")[2])
        else:
            self.base_pos = Vector2(pos)
            self.angle = 0

        if angle is not None:
            self.angle = angle
        self.pos = Vector2((self.base_pos[0] * self.screen_scale[0],
                            self.base_pos[1] * self.screen_scale[1]))
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt):
        self.play_animation(self.animation_speed, dt)  # TODO add sound effect to stage object
