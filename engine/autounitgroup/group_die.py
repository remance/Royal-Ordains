from engine.utils.common import clean_object


def group_die(self):
    battle = self.battle
    if self.is_commander:
        self.team_state["commander_character"] = None
        battle.team_commander[self.team] = None
    else:
        self.team_state["unit"].remove(self)
    battle.all_team_ally[self.team].remove(self)
    for team in battle.all_team_enemy:
        if team != self.team:
            if self in battle.all_team_ground_enemy_collision_grids[team][0]:
                battle.all_team_ground_enemy_collision_grids[team][0].remove(self)
            elif self in battle.all_team_air_enemy_collision_grids[team][0]:
                battle.all_team_air_enemy_collision_grids[team][0].remove(self)
        if self in battle.all_team_enemy[team]:
            battle.all_team_enemy[team].remove(self)
    self.kill()
    clean_object(self)
    self.alive = False
