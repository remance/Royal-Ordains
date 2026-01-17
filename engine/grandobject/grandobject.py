from pygame import sprite, Vector2

from engine.battleobject.adjust_sprite import adjust_sprite
from engine.battleobject.play_animation import play_animation
from engine.constants import Base_Animation_Frame_Play_Time
from engine.utils.common import clean_object


class GrandObject(sprite.Sprite):
    adjust_sprite = adjust_sprite
    clean_object = clean_object
    play_animation = play_animation

    grand = None
    screen_scale = None
    grand_object_animation_pool = None

    def __init__(self, sprite_id, pos, angle=0, animation_frame_play_time=0.15):
        if type(pos) is str:
            self.base_pos = Vector2([float(item) for item in pos.split(",")])
        else:
            self.base_pos = Vector2([float(item) for item in pos])

        self.pos = Vector2((self.base_pos[0] * self.grand.map_shown_to_actual_scale_width,
                            self.base_pos[1] * self.grand.map_shown_to_actual_scale_height))
        self._layer = 100 + self.pos[1]
        sprite.Sprite.__init__(self, self.containers)
        self.sprite_id = sprite_id
        self.show_frame = 0
        self.frame_timer = 0
        self.animation_frame_play_time = animation_frame_play_time
        self.repeat_animation = True
        self.hold = False
        self.active = True
        self.sprite_flip = False
        self.height_scale = 1
        self.width_scale = 1
        self.animation_pool = self.grand_object_animation_pool[sprite_id]
        self.current_animation = self.animation_pool["Base"]

        self.base_image = self.current_animation[self.show_frame]
        self.image = self.base_image
        self.angle = angle
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt):
        self.play_animation(self.animation_frame_play_time, dt, self.hold)  # TODO add sound effect to scene object

    def change_state(self):
        if self.active:
            self.active = False
            self.current_animation = self.animation_pool["Destroyed"]
        else:
            self.active = True
            self.current_animation = self.animation_pool["Base"]


class GrandArmyActor(sprite.Sprite):
    adjust_sprite = adjust_sprite
    clean_object = clean_object
    play_animation = play_animation

    grand = None
    screen_scale = None
    grand_object_animation_pool = None

    def __init__(self, sprite_id, pos):
        if type(pos) is str:
            self.base_pos = Vector2([float(item) for item in pos.split(",")])
        else:
            self.base_pos = Vector2([float(item) for item in pos])

        self.pos = Vector2((self.base_pos[0] * self.grand.map_shown_to_actual_scale_width,
                            self.base_pos[1] * self.grand.map_shown_to_actual_scale_height))
        self._layer = 100 + self.pos[1]
        sprite.Sprite.__init__(self, self.containers)
        self.sprite_id = sprite_id
        self.show_frame = 0
        self.frame_timer = 0
        self.animation_frame_play_time = Base_Animation_Frame_Play_Time
        self.repeat_animation = True
        self.hold = False
        self.active = True
        self.sprite_flip = False
        self.height_scale = 1
        self.width_scale = 1
        self.animation_pool = self.grand_actor_animation_pool[sprite_id]
        self.current_animation = self.animation_pool["Base"]

        self.base_image = self.current_animation[self.show_frame]
        self.image = self.base_image
        self.direction = "right"
        self.new_direction = self.direction
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt):
        self.play_animation(self.animation_frame_play_time, dt, self.hold)
