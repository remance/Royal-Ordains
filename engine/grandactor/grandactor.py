from pygame import sprite, Vector2, draw, Surface, SRCALPHA
from pygame.transform import smoothscale

from engine.battleobject.adjust_sprite import adjust_sprite
from engine.character.reset_sprite import reset_sprite
from engine.constants import Base_Animation_Frame_Play_Time
from engine.grandactor.pick_animation import pick_animation
from engine.grandactor.play_animation import play_animation
from engine.utils.common import clean_object


class GrandActor(sprite.Sprite):
    adjust_sprite = adjust_sprite
    clean_object = clean_object
    play_animation = play_animation
    pick_animation = pick_animation
    reset_sprite = reset_sprite

    containers = None
    grand = None
    faction_circles = {}

    def __init__(self, sprite_id, army, faction, base_pos):
        if type(base_pos) is str:
            self.base_pos = Vector2([float(item) for item in base_pos.split(",")])
        else:
            self.base_pos = Vector2([float(item) for item in base_pos])
        self.pos = Vector2(army.pos)
        self._layer = 100 + (self.pos[1] * 1000000)
        sprite.Sprite.__init__(self, self.containers)
        self.army = army
        army.commander_actor = self
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
        self.circle = GrandFactionActorCircle(self, faction)

        self.pick_animation("Idle")
        self.reset_sprite()

    def update(self, dt):
        if self.army.pos != self.pos:
            self.pos = Vector2(self.army.pos)
            self.grand.grand_camera_object_drawer.change_layer(100 + (self.pos[1] * 10))
            if len(self.army.travel_route) > 1:
                self.direction = "left"
                if self.army.travel_route[0][0] > self.army.travel_route[1][0]:
                    self.direction = "right"
        self.play_animation(dt)
        if self.update_sprite:
            self.reset_sprite()
            self.update_sprite = False


class GrandFactionActorCircle(sprite.Sprite):
    containers = None
    faction_circle_cache = {}
    screen_scale = None
    grand = None

    def __init__(self, actor, faction):
        self._layer = actor.pos[1]
        sprite.Sprite.__init__(self, self.containers)
        self.actor = actor
        if faction not in self.faction_circle_cache:
            image = Surface((100 * self.screen_scale[0], 50 * self.screen_scale[1]), SRCALPHA)
            selected_image = image.copy()
            draw.ellipse(image, (0, 0, 0),
                         (0, 0, image.get_width(), image.get_height()))
            draw.ellipse(image, self.grand.faction_list[faction]["Colour"],
                         (image.get_width() * 0.05, image.get_height() * 0.05,
                          image.get_width() * 0.9, image.get_height() * 0.9))

            draw.ellipse(selected_image, (240, 240, 240),
                         (0, 0, image.get_width(), selected_image.get_height()))
            draw.ellipse(selected_image, self.grand.faction_list[faction]["Colour"],
                         (selected_image.get_width() * 0.05, selected_image.get_height() * 0.05,
                          selected_image.get_width() * 0.9, selected_image.get_height() * 0.9))

            self.faction_circle_cache[faction] = (image, selected_image)

        self.not_selected_image = self.faction_circle_cache[faction][0]
        self.selected_image = self.faction_circle_cache[faction][1]
        self.image = self.not_selected_image
        self.pos = actor.pos.copy()

        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt):
        if self.actor.army in self.grand.player_selected_army:
            self.image = self.selected_image
        else:
            self.image = self.not_selected_image

        actor_pos = self.actor.pos
        if self.pos != actor_pos:
            self.pos = actor_pos.copy()
            self.grand.grand_camera_object_drawer.change_layer(actor_pos[1])
        self.rect.center = self.pos
