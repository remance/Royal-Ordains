from pygame import sprite, Vector2


class Drop(sprite.Sprite):
    battle = None
    drop_item_list = None
    item_sprite_pool = None

    ground_pos = 1000

    from engine.effect.adjust_sprite import adjust_sprite
    adjust_sprite = adjust_sprite

    from engine.effect.play_animation import play_animation
    play_animation = play_animation

    def __init__(self, base_pos, game_id, team, momentum=()):
        """
        Drop item object represent an item drop in the battle in stage
        """
        self._layer = 9999999999999999996
        sprite.Sprite.__init__(self, self.containers)
        self.screen_scale = self.battle.screen_scale
        self.fall_gravity = self.battle.base_fall_gravity / 2  # fall a bit slower
        self.show_frame = 0
        self.frame_timer = 0
        self.x_momentum = 0
        self.y_momentum = 0
        self.pickable_timer = 1
        if momentum:
            self.x_momentum = momentum[0]
            self.y_momentum = momentum[1]
        self.repeat_animation = True

        self.stat = self.drop_item_list[game_id]

        self.base_pos = base_pos

        self.team = team

        self.battle.all_team_drop[self.team].add(self)
        self.current_animation = self.item_sprite_pool[self.battle.chapter]["Normal"][game_id][1]

        self.base_image = self.current_animation[self.show_frame]
        self.image = self.base_image

        self.angle = 0
        self.scale = 1.0
        self.flip = 0
        self.duration = 10
        self.pos = (self.base_pos[0] * self.screen_scale[0],
                    self.base_pos[1] * self.screen_scale[1])

        self.adjust_sprite()

    def update(self, dt):
        if self.pickable_timer:
            self.pickable_timer -= dt
            if self.pickable_timer < 0:
                self.pickable_timer = 0

        if self.x_momentum or self.y_momentum:  # sprite bounce after reach
            self.angle += (dt * 1000)
            if self.angle >= 360:
                self.angle = 0
            new_pos = self.base_pos + Vector2(self.x_momentum, -self.y_momentum)
            move = new_pos - self.base_pos
            if move.length():
                move.normalize_ip()
                self.base_pos += move
                if self.battle.base_stage_start > self.base_pos[0]:
                    self.base_pos[0] = self.battle.base_stage_start
                    self.x_momentum = 0
                elif self.base_pos[0] > self.battle.base_stage_end:
                    self.base_pos[0] = self.battle.base_stage_end
                    self.x_momentum = 0

                self.pos = Vector2(self.base_pos[0] * self.screen_scale[0],
                                   self.base_pos[1] * self.screen_scale[1])
                self.adjust_sprite()

            if self.x_momentum > 0:
                self.x_momentum -= dt * 50
                if self.x_momentum < 0.1:
                    self.x_momentum = 0
            elif self.x_momentum < 0:
                self.x_momentum += dt * 50
                if self.x_momentum > 0.1:
                    self.x_momentum = 0

            if self.y_momentum > 0:
                self.y_momentum -= dt * 100
                if self.y_momentum <= 0:
                    self.y_momentum = -200

            if self.base_pos[1] >= self.ground_pos:  # reach ground
                self.x_momentum = 0
                self.y_momentum = 0
        elif self.base_pos[1] < self.ground_pos:  # fall down to ground
            self.base_pos[1] += self.fall_gravity * dt
            self.pos = (self.base_pos[0] * self.screen_scale[0],
                        self.base_pos[1] * self.screen_scale[1])
            self.adjust_sprite()
        else:  # only start counting duration when reach ground
            self.duration -= dt
            if self.duration < 0:
                self.picked()

    def picked(self):
        self.battle.all_team_drop[self.team].remove(self)
        self.kill()
