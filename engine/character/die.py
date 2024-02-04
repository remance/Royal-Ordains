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
    if self.player_control and int(self.game_id[-1]) in self.battle.player_objects:
        self.battle.player_objects.pop(int(self.game_id[-1]))

    self.current_action = {}

    if self.indicator:
        self.indicator.kill()
        self.indicator = None

    for speech in self.battle.speech_boxes:
        if speech.character == self:  # kill speech
            speech.kill()

    for follower in self.followers:
        follower.leader = None
    self.followers = []
    if self.leader:
        self.leader.followers.remove(self)

    if how == "flee":
        clean_group_object((self.body_parts,))
        clean_object(self)
    else:
        if self.team != 1:
            self.battle.increase_player_score(self.score)
            # self.battle.player_kill
        if self.drops:  # only drop items if dead
            for drop, chance in self.drops.items():
                drop_name = drop
                if "+" in drop_name:  # + indicate number of possible drop
                    drop_num = int(drop_name.split("+")[1])
                    drop_name = drop_name.split("+")[0]
                    for _ in range(drop_num):
                        if chance >= randint(0, 100):
                            Drop(Vector2(self.base_pos[0], self.base_pos[1] - (self.sprite_size * 2)), drop_name, 1,
                                 momentum=(randint(-200, 200), (randint(50, 150))))
                else:
                    if chance >= randint(0, 100):  # TODO change team later when add pvp mode or something
                        Drop(Vector2(self.base_pos[0], self.base_pos[1] - (self.sprite_size * 2)), drop, 1,
                             momentum=(randint(-200, 200), (randint(50, 150))))
