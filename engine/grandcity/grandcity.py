from math import radians
from random import uniform

from pygame import Vector2, draw, Surface, SRCALPHA
from pygame.sprite import Sprite

from engine.battleobject.adjust_sprite import adjust_sprite
from engine.character.reset_sprite import reset_sprite
from engine.constants import Base_Animation_Frame_Play_Time
from engine.grandactor.pick_animation import pick_animation
from engine.grandactor.play_animation import play_animation
from engine.utils.common import clean_object


class GrandCity(Sprite):
    adjust_sprite = adjust_sprite
    clean_object = clean_object
    play_animation = play_animation
    pick_animation = pick_animation
    reset_sprite = reset_sprite

    containers = None
    grand = None
    faction_circles = {}

    def __init__(self, base_pos, sprite_id, region_id):
        self.map_shown_to_actual_scale_width = self.grand.map_shown_to_actual_scale_width
        self.map_shown_to_actual_scale_height = self.grand.map_shown_to_actual_scale_height
        self.base_pos = base_pos
        self.pos = Vector2((base_pos[0] * self.map_shown_to_actual_scale_width,
                            base_pos[1] * self.map_shown_to_actual_scale_height))
        self._layer = 100 + (self.pos[1] * 100)
        Sprite.__init__(self, self.containers)
        self.region_id = region_id
        self.dots_army_occupation = self.grand.dots_army_occupation
        self.drawer = self.grand.grand_camera_object_drawer

        self.max_show_frame = 0
        self.show_frame = 0
        self.frame_timer = 0
        self.update_sprite = False
        self.animation_frame_play_time = Base_Animation_Frame_Play_Time
        self.final_animation_frame_play_time = self.animation_frame_play_time
        self.animation_pool = self.grand.sprite_data.grand_actor_animation_pool[sprite_id]
        self.current_animation = self.animation_pool["Idle"]
        self.current_animation_frame = self.current_animation[self.show_frame]
        self.image = self.current_animation_frame["sprite"]

        self.rect = self.image.get_rect(center=self.pos)

        self.animation_name = "Idle"
        self.pick_animation("Idle")
        self.reset_sprite()

    def update(self, true_dt, dt):
        if self.animation_name != "Idle":
            self.pick_animation("Idle")

        done = self.play_animation(true_dt)  # actor play animation based on real-time instead of game speed
        if done and self.animation_name == "Attack":  # finish attack animation revert to idle
            self.pick_animation("Idle")
        if self.update_sprite:
            self.reset_sprite()
            self.update_sprite = False
