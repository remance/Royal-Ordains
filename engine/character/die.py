from random import randint

from pygame import Vector2

from engine.drop.drop import Drop
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

    self.current_action = {}

    if self.indicator:
        self.indicator.kill()
        self.indicator = None

    if how == "flee":
        clean_group_object((self.body_parts,))
        clean_object(self)
    else:
        if self.drops:  # only drop items if dead
            for drop, chance in self.drops.items():
                if chance >= randint(0, 100):  # TODO change team later when add pvp mode or something
                    Drop(Vector2(self.base_pos[0], self.base_pos[1] - (self.sprite_size * 2)), drop, 1)
