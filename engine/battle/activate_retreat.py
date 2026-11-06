from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.battle.battle import Battle


def activate_retreat(self: Battle, team: int):
    bad_drama = False
    if team == self.player_team:
        bad_drama = True
    self.drama_text.queue.append((bad_drama,
                                  self.grab_text(("ui", "Team")) + str(team) +
                                  self.grab_text(("ui", "retreats")),
                                  None))
    for character in self.battle.all_team_ally[team]:
        character.broken = True
        if character.is_summon:
            character.health = 0
    for air_group in self.battle.team_state[team]["air_group"]:
        for character in air_group:
            character.broken = True
