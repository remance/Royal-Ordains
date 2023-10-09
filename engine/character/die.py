from engine.utils.common import clean_group_object, clean_object


def die(self, how):
    """Character left battle, either dead or flee"""

    # remove from updater
    self.battle.all_team_character[self.team].remove(self)
    for team in self.battle.all_team_enemy_part:
        if team != self.team:
            for part in self.body_parts.values():
                self.battle.all_team_enemy_part[team].remove(part)
            self.battle.all_team_enemy[team].remove(self)
    if self.game_id in self.battle.player_objects:
        self.battle.player_objects.pop(self.game_id)

    if self.indicator:
        self.indicator.kill()
        self.indicator = None

    if how == "flee":
        clean_group_object((self.body_parts,))
        clean_object(self)
