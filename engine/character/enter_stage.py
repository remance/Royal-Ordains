from pygame import Vector2


def enter_stage(self):
    self.pick_animation()


def battle_character_enter_stage(self):
    """run once when scene start or character just get created"""
    # Add character to list
    self.ally_list.add(self)
    if self.is_commander:
        self.battle.team_stat[self.team]["strategy_resource"] = self.leadership
    if not self.invincible:  # not add to list if can't take damage
        for team in self.battle.all_team_enemy_check:
            if team != self.team and not self.no_target:
                self.battle.all_team_enemy_check[team].add(self)
    self.enemy_commander = self.battle.team_commander[self.enemy_team]
    self.pick_animation()


def delayed_enter_stage(self, dt):
    self.enter_delay -= dt

    if self.enter_delay <= 0:
        self.enter_delay = 0
        self.active = True
        if self.character_type == "air":
            self.invisible = False
            self.base_pos = Vector2(self.start_pos, self.Default_Air_Pos)
        else:
            self.base_pos = Vector2(self.start_pos, self.Default_Ground_Pos)
        battle_character_enter_stage(self)


def battle_air_character_enter_stage(self):
    """run once when scene start or character just get created"""
    # Add character to list, but not in victory condition list
    if self.active:
        self.pick_animation()
