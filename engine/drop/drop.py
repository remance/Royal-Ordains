from pygame import sprite, Vector2


class Drop(sprite.Sprite):
    battle = None
    drop_item_list = None
    effect_sprite_pool = None

    ground_pos = 1000

    def __init__(self, base_pos, game_id, team):
        """
        Drop item object represent an item drop in the battle in stage
        """
        self._layer = 9999999999999999996
        sprite.Sprite.__init__(self, self.containers)
        self.screen_scale = self.battle.screen_scale
        self.fall_gravity = self.battle.original_fall_gravity

        self.stat = self.drop_item_list[game_id]

        self.base_pos = base_pos

        self.team = team

        self.battle.all_team_drop[self.team].add(self)

        self.image = self.effect_sprite_pool[game_id][self.battle.chapter_sprite_ver]["Item"]
        self.rect = self.image.get_rect(center=Vector2((self.base_pos[0] * self.screen_scale[0],
                                                        self.base_pos[1] * self.screen_scale[1])))

    def update(self, dt):
        if self.base_pos[1] < self.ground_pos:  # fall down to ground
            self.base_pos[1] += self.fall_gravity * dt
            self.rect.center = Vector2((self.base_pos[0] * self.screen_scale[0],
                                        self.base_pos[1] * self.screen_scale[1]))

    def picked(self):
        self.battle.all_team_drop[self.team].remove(self)
        self.kill()
