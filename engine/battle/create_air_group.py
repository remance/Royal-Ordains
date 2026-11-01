from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.battle.battle import Battle

from engine.character.character import AirBattleCharacter, CommanderBattleCharacter


def create_air_group(self: Battle, character_id: str, team: int, commander_character: CommanderBattleCharacter):
    this_group = []
    number = self.character_list[character_id]["Arrive Per Call"]
    self.team_deployed[team] += number
    for _ in range(int(number)):
        this_group.append(
            AirBattleCharacter(self.last_char_game_id, self.character_list[character_id] |
                               {"ID": character_id, "Team": team, "POS": (-10000, 0)},
                               commander_character=commander_character))
        self.last_char_game_id += 1
    self.team_state[team]["air_group"].append(this_group)
