from engine.character.character import GrandAutoCharacter
from engine.constants import Phase_To_Round, Phase_To_Battle_Time


Tick_to_Second = Phase_To_Battle_Time / Phase_To_Round


class AutoBattle:
    def __init__(self, battle_state):
        self.battle_state = battle_state

    def change_phase(self):

        for tick in range(6):
            all_active_unit = []

            for team in (0, 1, 2):  # update unit
                # get all active units for acting
                team_state = self.battle_state[team]
                all_active_unit += team_state["unit"] + team_state[team]["air_unit"]

                # commander act first
                commander_character = team_state["commander"]
                commander_character.status_update(specific_dt=Tick_to_Second)

            # for auto battle unit take action queue based on their speed stat
            all_active_unit.sort(key=lambda x: x.speed, reverse=True)
            for unit in all_active_unit:
                # update status first
                unit.status_update(specific_dt=Tick_to_Second)
                # move or take action
                unit.ai_logic()

    def add_auto_character(self, team, character_id, is_commander: bool = False):

        self.battle_state[team]["unit"].append(GrandAutoCharacter(character_id, is_commander=is_commander))