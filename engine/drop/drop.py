from pygame import sprite, Vector2


class Drop(sprite.Sprite):
    battle = None
    drop_item_list = None
    effect_animation_pool = None

    ground_pos = 1000

    from engine.effect.adjust_sprite import adjust_sprite
    adjust_sprite = adjust_sprite

    from engine.effect.play_animation import play_animation
    play_animation = play_animation

    def __init__(self, base_pos, game_id, team):
        """
        Drop item object represent an item drop in the battle in stage
        """
        self._layer = 9999999999999999996
        sprite.Sprite.__init__(self, self.containers)
        self.screen_scale = self.battle.screen_scale
        self.fall_gravity = self.battle.original_fall_gravity
        self.show_frame = 0
        self.frame_timer = 0
        self.repeat_animation = True

        self.stat = self.drop_item_list[game_id]

        self.base_pos = base_pos

        self.team = team

        self.battle.all_team_drop[self.team].add(self)

        self.current_animation = self.effect_animation_pool[game_id][self.battle.chapter_sprite_ver]["Item"]

        self.base_image = self.current_animation[self.show_frame]
        self.image = self.base_image

        self.angle = 0
        self.scale = 1.0
        self.flip = 0
        self.pos = (self.base_pos[0] * self.screen_scale[0],
                    self.base_pos[1] * self.screen_scale[1])

        self.adjust_sprite()

    def update(self, dt):
        done, just_start = self.play_animation(0.1, dt)

        if self.base_pos[1] < self.ground_pos:  # fall down to ground
            self.base_pos[1] += self.fall_gravity * dt
            self.pos = (self.base_pos[0] * self.screen_scale[0],
                        self.base_pos[1] * self.screen_scale[1])
            self.adjust_sprite()

    def picked(self):
        self.battle.all_team_drop[self.team].remove(self)
        self.kill()
