from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.battle.battle import Battle


def add_strategy_to_team_state(self: Battle, team_state: dict, strategy_id: str):
    if strategy_id not in team_state["strategy_cooldown"]:
        team_state["strategy_cooldown"][strategy_id] = [0]
    else:
        team_state["strategy_cooldown"][strategy_id].append(0)
