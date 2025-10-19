from random import uniform

import engine.character.character
from engine.utils.common import clean_object


def die(self):
    """Character dead"""
    # remove from updater
    if self in self.battle.ai_process_list:
        self.battle.ai_process_list.remove(self)
    self.ally_list.remove(self)
    if self.is_general:
        self.battle.all_team_general[self.team].remove(self)
        if self.team == 1 and self.is_controllable:
            if self in self.battle.player_selected_generals:
                self.battle.player_selected_generals.remove(self)

    for team in self.battle.all_team_enemy_check:
        if team != self.team:
            for grid in self.grid_range:
                self.all_team_enemy_collision_grids[team][grid].remove(self)
            if self in self.battle.all_team_enemy_check[team]:
                self.battle.all_team_enemy_check[team].remove(self)

    if self.indicator:
        clean_object(self.indicator)
        self.indicator = None

    if self.main_character:
        self.main_character.sub_characters.remove(self)
        if (not self.main_character.sub_characters and not self.main_character.active_without_sub_character and
                self.main_character.health):
            # main character no longer has sub characters, check if main character is consider no longer active
            # does not include main character that is dead already
            self.main_character.die()
    self.main_character = None

    if "die" in self.ai_speak_list:
        self.ai_speak("die")

    for follower in self.followers:
        if self.leader and self.leader.alive:  # transfer leadership to its leader, use less leadership to boost stat
            follower.base_offence = follower.original_offence * (self.leader.leadership / 200)
            follower.base_defence = follower.original_defence * (self.leader.leadership / 200)
            follower.leadership = follower.original_leadership * (self.leader.leadership / 200)
            follower.leader = self.leader
            self.leader.followers.append(follower)
        else:  # revert follower stat to no leadership when it die and no general to transfer
            follower.base_offence = follower.original_offence
            follower.base_defence = follower.original_defence
            follower.leadership = follower.original_leadership
            follower.leader = None
            follower.general = None

    self.followers = []
    for sub_character in self.sub_characters:
        sub_character.main_character = None
    self.sub_characters = []

    if self.leader:  # remove self from leader stuff
        if self.leader.alive and self in self.leader.followers:
            self.leader.followers.remove(self)
        self.leader = None

    if self.general:
        if self.general.alive:
            self.general.reset_general_variables()
        self.general = None

    if self.spawns:
        for spawn, chance in self.spawns.items():
            spawn_name = spawn
            if "+" in spawn_name:  # + indicate number of possible drop
                spawn_num = int(spawn_name.split("+")[1])
                spawn_name = spawn_name.split("+")[0]
                for _ in range(spawn_num):
                    if chance >= uniform(0, 100):
                        start_pos = (self.base_pos[0] + uniform(-200, 200),
                                     self.base_pos[1])
                        engine.character.character.BattleCharacter(self.battle.last_char_game_id,
                                                                   self.character_data.character_list[spawn_name] |
                                                                   {"ID": spawn_name,
                                                                    "Angle": self.angle,
                                                                    "Team": self.team, "POS": start_pos,
                                                                    "Arrive Condition": ()})
                        self.battle.last_char_game_id += 1
            else:
                if chance >= uniform(0, 100):
                    start_pos = (self.base_pos[0] + uniform(-200, 200),
                                 self.base_pos[1])
                    engine.character.character.BattleCharacter(self.battle.last_char_game_id,
                                                               self.character_data.character_list[spawn_name] |
                                                               {"ID": spawn_name,
                                                                "Angle": self.angle,
                                                                "Team": self.team, "POS": start_pos,
                                                                "Arrive Condition": ()})
                    self.battle.last_char_game_id += 1

    self.status_effect = {}
    self.status_duration = {}


def air_die(self):
    for air_group in self.battle.team_stat[self.team]["air_group"]:
        if self in air_group:
            air_group.remove(self)
            break
    die(self)


def commander_die(self):
    for character in self.battle.all_team_ally[self.team]:
        character.broken = True
    for air_group in self.battle.team_stat[self.team]["air_group"]:
        for character in air_group:
            character.broken = True
    die(self)
