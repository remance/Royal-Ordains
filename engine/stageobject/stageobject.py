from pygame import sprite, Vector2


class StageObject(sprite.Sprite):
    from engine.stageobject.play_animation import play_animation
    play_animation = play_animation

    from engine.effect.adjust_sprite import adjust_sprite
    adjust_sprite = adjust_sprite

    battle = None
    screen_scale = None
    stage_object_animation_pool = None

    def __init__(self, sprite_id, pos):
        """Stage object with animation"""
        self._layer = 1
        sprite.Sprite.__init__(self, self.containers)
        self.show_frame = 0
        self.frame_timer = 0
        self.repeat_animation = True
        self.current_animation = self.stage_object_animation_pool[sprite_id][self.battle.chapter]

        self.image = self.current_animation[self.show_frame]

        self.base_pos = Vector2([int(item) for item in pos.split(",")[0:2]])
        self.pos = Vector2((self.base_pos[0] * self.screen_scale[0],
                            self.base_pos[1] * self.screen_scale[1]))
        self.angle = int(pos.split(",")[2])
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt):
        self.play_animation(0.1, dt)  # TODO add sound effect to stage object
