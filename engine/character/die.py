from random import uniform

from pygame import Vector2

from engine.drop.drop import Drop
from engine.utils.common import clean_group_object


def die(self, delete=False):
    """Character left battle, either dead or flee"""
    from engine.character.character import BattleAICharacter

    # remove from updater
    self.battle.all_team_character[self.team].remove(self)
    for team in self.battle.all_team_enemy_part:
        if team != self.team:
            for part in self.body_parts.values():
                self.battle.all_team_enemy_part[team].remove(part)
            if self in self.battle.all_team_enemy[team]:
                self.battle.all_team_enemy[team].remove(self)
            if self in self.battle.all_team_enemy_check[team]:
                self.battle.all_team_enemy_check[team].remove(self)
    if self.player_control and int(self.game_id[-1]) in self.battle.player_objects:
        self.battle.player_objects.pop(int(self.game_id[-1]))

    self.current_action = {}

    if self.indicator:
        self.indicator.kill()
        self.indicator = None

    if delete:
        for speech in self.battle.speech_boxes:
            if speech.character == self:  # kill any current speech
                speech.kill()
        for body_part in self.body_parts.values():
            if body_part.stuck_effect:
                for stuck_object in body_part.stuck_effect:  # remove stuck effect as well
                    stuck_object.reach_target()
                body_part.stuck_effect = []
        clean_group_object((self.body_parts,))  # remove only body parts, self will be deleted later
        self.battle.character_updater.remove(self)
    elif self.invisible:  # add back sprite for invisible character that die
        self.invisible = False
        for part in self.body_parts.values():
            part.re_rect()

    for follower in self.followers:
        follower.leader = None
    self.followers = []
    if self.leader:
        if self.leader.player_control and not delete and not self.battle.follower_talk_timer and "die" in self.follower_speak:
            self.follower_talk("die")
        self.leader.followers.remove(self)

    if self.killer:  # has killer
        self.battle.increase_team_score(self.killer.team, self.score)
        if self.killer.player_control:
            # target die, add kill stat if attacker is player
            self.battle.player_kill[int(self.killer.game_id[-1])] += 1
            if self.is_boss:
                self.battle.player_boss_kill[int(self.killer.game_id[-1])] += 1
        self.killer = None

    self.status_effect = {}
    self.status_duration = {}
    self.status_applier = {}

    if self.drops:  # only drop items if dead
        for drop, chance in self.drops.items():
            drop_name = drop
            if "+" in drop_name:  # + indicate number of possible drop
                drop_num = int(drop_name.split("+")[1])
                drop_name = drop_name.split("+")[0]
                for _ in range(drop_num):
                    if chance >= uniform(0, 100):
                        Drop(Vector2(self.base_pos[0], self.base_pos[1] - (self.sprite_height * 2)), drop_name, 1,
                             momentum=(uniform(-200, 200), (uniform(50, 150))))
            else:
                if chance >= uniform(0, 100):  # TODO change team later when add pvp mode or something
                    Drop(Vector2(self.base_pos[0], self.base_pos[1] - (self.sprite_height * 2)), drop, 1,
                         momentum=(uniform(-200, 200), (uniform(50, 150))))
    if self.spawns:
        for spawn, chance in self.spawns.items():
            spawn_name = spawn
            if "+" in spawn_name:  # + indicate number of possible drop
                spawn_num = int(spawn_name.split("+")[1])
                spawn_name = spawn_name.split("+")[0]
                for _ in range(spawn_num):
                    self.battle.last_char_id += 1  # id continue from last chars
                    if chance >= uniform(0, 100):
                        start_pos = (self.base_pos[0] + uniform(-200, 200),
                                     self.base_pos[1])
                        BattleAICharacter(self.battle.last_char_id, self.battle.last_char_id,
                                          self.character_data.character_list[spawn_name] |
                                          {"ID": spawn_name,
                                           "Sprite Ver": self.sprite_ver, "Angle": self.angle,
                                           "Team": self.team, "POS": start_pos,
                                           "Arrive Condition": ()})
            else:
                if chance >= uniform(0, 100):
                    self.battle.last_char_id += 1  # id continue from last chars
                    start_pos = (self.base_pos[0] + uniform(-200, 200),
                                 self.base_pos[1])
                    BattleAICharacter(self.battle.last_char_id, self.battle.last_char_id,
                                      self.character_data.character_list[spawn_name] |
                                      {"ID": spawn_name,
                                       "Sprite Ver": self.sprite_ver, "Angle": self.angle,
                                       "Team": self.team, "POS": start_pos,
                                       "Arrive Condition": ()})
