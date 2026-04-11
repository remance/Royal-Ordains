from pygame import sprite, Vector2

from engine.battleobject.adjust_sprite import adjust_sprite
from engine.character.reset_sprite import reset_sprite
from engine.grandactor.play_animation import play_animation
from engine.grandactor.pick_animation import pick_animation
from engine.constants import Base_Animation_Frame_Play_Time
from engine.utils.common import clean_object


class GrandActor(sprite.Sprite):
    adjust_sprite = adjust_sprite
    clean_object = clean_object
    play_animation = play_animation
    pick_animation = pick_animation
    reset_sprite = reset_sprite

    containers = None
    grand = None
    screen_scale = None

    def __init__(self, sprite_id, army, faction, base_pos):
        if type(base_pos) is str:
            self.base_pos = Vector2([float(item) for item in base_pos.split(",")])
        else:
            self.base_pos = Vector2([float(item) for item in base_pos])

        self.pos = Vector2((self.base_pos[0] * self.grand.map_shown_to_actual_scale_width,
                            self.base_pos[1] * self.grand.map_shown_to_actual_scale_height))
        self._layer = 100 + self.pos[1]
        sprite.Sprite.__init__(self, self.containers)
        self.army = army
        self.faction = faction
        self.max_show_frame = 0
        self.show_frame = 0
        self.frame_timer = 0
        self.update_sprite = False
        self.animation_frame_play_time = Base_Animation_Frame_Play_Time
        self.final_animation_frame_play_time = self.animation_frame_play_time
        self.active = True
        self.height_scale = 1
        self.width_scale = 1
        self.animation_pool = self.grand.sprite_data.grand_actor_animation_pool[sprite_id]
        self.direction = "right"
        self.current_action = {}
        self.current_animation = self.animation_pool["Idle"]
        self.current_animation_frame = self.current_animation[self.show_frame]
        self.current_animation_direction = self.current_animation_frame[self.direction]
        self.image = self.current_animation_direction["sprite"]
        self.rect = self.image.get_rect(center=self.pos)

        self.pick_animation("Idle")

    def update(self, dt):
        if self.army.pos != self.pos:
            self.pos = Vector2(self.army.pos)
            if len(self.army.travel_route) > 1:
                self.direction = "left"
                if self.army.travel_route[0][0] > self.army.travel_route[1][0]:
                    self.direction = "right"
        self.play_animation(dt)
        if self.update_sprite:
            self.reset_sprite()
            self.update_sprite = False
