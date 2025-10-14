from pygame import Vector2


def enter_stage(self):
    self.pick_animation()
    self.battle_camera.add(self)


def battle_character_enter_stage(self):
    """run once when scene start or character just get created"""
    # Add character to list
    if self.is_general:
        self.battle.all_team_general[self.team].add(self)
    self.ally_list.add(self)
    if not self.invincible:  # not add to list if can't take damage
        for team in self.battle.all_team_enemy_check:
            if team != self.team:
                if self.team != 0:  # team 0 is not part of condition check:
                    self.battle.all_team_enemy_check[team].add(self)

    self.pick_animation()
    self.battle_camera.add(self)


def delayed_enter_stage(self, dt):
    self.enter_delay -= dt

    if self.enter_delay <= 0:
        self.enter_delay = 0
        self.active = True
        if self.character_type == "air":
            self.base_pos = Vector2(self.enter_pos, self.Default_Air_Pos)
        else:
            self.base_pos = Vector2(self.enter_pos, self.Default_Ground_Pos)
        self.enter_stage()


def battle_air_character_enter_stage(self):
    """run once when scene start or character just get created"""
    # Add character to list, but not in victory condition list
    if self.active:
        self.pick_animation()
        self.battle_camera.add(self)
