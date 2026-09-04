from pygame import sprite, Vector2

from engine.utils.common import clean_object


class GrandObject(sprite.Sprite):
    clean_object = clean_object

    containers = None
    grand = None
    screen_scale = None

    def __init__(self, sprite_id, base_pos, active_state):
        if type(base_pos) is str:
            self.base_pos = Vector2([float(item) for item in base_pos.split(",")])
        else:
            self.base_pos = Vector2([float(item) for item in base_pos])

        self.pos = Vector2((self.base_pos[0] * self.grand.map_shown_to_base_scale_width,
                            self.base_pos[1] * self.grand.map_shown_to_base_scale_height))

        self._layer = 10 + self.pos[1]
        sprite.Sprite.__init__(self, self.containers)
        self.sprite_id = "test"
        if sprite_id in self.grand.building_portraits:
            self.sprite_id = sprite_id

        self.active_state = active_state
        self.image = self.grand.building_portraits[self.sprite_id]["building_ui"]
        self.change_state(self.active_state)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, true_dt, dt):
        pass

    def change_state(self, new_state):
        self.active_state = new_state
        self.image = self.grand.building_portraits[self.sprite_id]["building_ui"]
        if not self.active_state:
            self.image = self.image.copy()
