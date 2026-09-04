from math import radians

from engine.grandarmyactor.move_logic import move_logic
from pygame import Vector2, draw, Surface, SRCALPHA
from pygame.sprite import Sprite

from engine.utils.common import clean_object
from engine.utils.rotation import set_rotate, rotation_xy

same_dot_placement_pos_offset = []

for y in range(1, 10):
    if y == 1:
        x_list = (0, -1, 1)
    else:
        x_list = (0, -1, 1, -2, 2)
    for x in x_list:
        same_dot_placement_pos_offset.append(Vector2(x * 5, y * 10))

circle_colour = {"player": (50, 50, 200), "ally": (50, 200, 50), "enemy": (200, 50, 50),
                 "neutral": (50, 50, 50)}


class GrandArmyActor(Sprite):
    clean_object = clean_object
    move_logic = move_logic

    containers = None
    grand = None

    actor_circle_cache = {}

    def __init__(self, army, faction):
        self.map_shown_to_base_scale_width = self.grand.map_shown_to_base_scale_width
        self.map_shown_to_base_scale_height = self.grand.map_shown_to_base_scale_height

        self.army_pos = Vector2(army.base_pos)
        self.previous_army_pos = self.army_pos
        self.pos = Vector2((self.army_pos[0] * self.map_shown_to_base_scale_width,
                            self.army_pos[1] * self.map_shown_to_base_scale_height))
        self._layer = 100 + self.pos[1]
        Sprite.__init__(self, self.containers)
        self.dots_army_occupation = self.grand.dots_army_occupation
        self.drawer = self.grand.grand_camera_object_drawer

        self.skip_move_length = 100 * self.map_shown_to_base_scale_width

        self.current_slot = None
        self.army = army
        self.army_id = self.army.game_id
        army.commander_actor = self
        self.faction = faction
        self.active = True
        self.circle_not_selected_image = None
        self.circle_selected_image = None
        self.current_selected = False
        self.image = None
        self.change_team_state()

        slot = tuple(self.dots_army_occupation[army.base_pos].keys()).index(self.army_id)
        # change pos to based on slot
        target_pos = rotation_xy(self.army_pos, self.army_pos + same_dot_placement_pos_offset[slot],
                                 radians(-set_rotate(self.previous_army_pos, self.army_pos)))
        self.pos = Vector2(((target_pos[0]) * self.map_shown_to_base_scale_width,
                            (target_pos[1]) * self.map_shown_to_base_scale_height))
        self.target_pos = self.pos

        self.rect = self.image.get_rect(center=self.pos)

    def change_team_state(self):
        actor_image = self.grand.sprite_data.character_portraits[self.army.commander_id]["mini"]["right"]
        current_campaign_state = self.grand.current_campaign_state
        team = "player"
        army_faction = self.army.faction
        player_faction = self.grand.player_faction
        if army_faction != self.grand.player_faction:
            team = "neutral"
            if player_faction:
                player_alliance = current_campaign_state["faction"][player_faction]["alliance"]
                if player_alliance and current_campaign_state["alliance"][player_alliance]:
                    team = "ally"
                elif army_faction in current_campaign_state["faction"][player_faction]["hostile"]:
                    team = "enemy"
        if actor_image not in self.actor_circle_cache:
            self.actor_circle_cache[actor_image] = {}
        if army_faction not in self.actor_circle_cache[actor_image]:
            image = Surface((actor_image.get_width() * 1.2, actor_image.get_height() * 1.2), SRCALPHA)
            selected_image = image.copy()
            draw.circle(image, (0, 0, 0),
                        (image.get_width() / 2, image.get_height() / 2), image.get_width() / 2)
            draw.circle(image, circle_colour[team],
                        (image.get_width() / 2, image.get_height() / 2), image.get_width() * 0.45)

            draw.circle(selected_image, (240, 240, 240),
                        (image.get_width() / 2, image.get_height() / 2), image.get_width() / 2)
            draw.circle(selected_image, circle_colour[team],
                        (image.get_width() / 2, image.get_height() / 2), image.get_width() * 0.45)
            image.blit(actor_image, actor_image.get_rect(center=(image.get_width() / 2, image.get_height() / 2)))
            selected_image.blit(actor_image, actor_image.get_rect(center=(selected_image.get_width() / 2,
                                                                          selected_image.get_height() / 2)))
            self.actor_circle_cache[actor_image][army_faction] = (image, selected_image)
        self.circle_not_selected_image = self.actor_circle_cache[actor_image][army_faction][0]
        self.circle_selected_image = self.actor_circle_cache[actor_image][army_faction][1]
        self.image = self.circle_not_selected_image

    def update(self, true_dt, dt):
        army = self.army

        layer_change = False

        if army in self.grand.player_selected_army:
            if not self.current_selected:
                layer_change = True
                self.current_selected = True
            self.image = self.circle_selected_image
        else:
            if self.current_selected:
                layer_change = True
                self.current_selected = False
            self.image = self.circle_not_selected_image

        slot = tuple(self.dots_army_occupation[army.base_pos].keys()).index(self.army_id)
        if slot != self.current_slot or army.base_pos != self.army_pos:
            if army.base_pos != self.army_pos:  # moving to new dot point
                self.previous_army_pos = self.army_pos
                self.army_pos = Vector2(army.base_pos)

            self.current_slot = slot
            target_pos = rotation_xy(self.army_pos, self.army_pos + same_dot_placement_pos_offset[slot],
                                     radians(-set_rotate(self.previous_army_pos, self.army_pos)))
            self.target_pos = Vector2(((target_pos[0]) * self.map_shown_to_base_scale_width,
                                       (target_pos[1]) * self.map_shown_to_base_scale_height))

        if self.pos != self.target_pos:
            layer_change = True
            self.move_logic(dt)

        if layer_change:
            if self.current_selected:
                self.drawer.change_layer(self, 10000 + self.pos[1])
            else:
                self.drawer.change_layer(self, 100 + self.pos[1])
