from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.grand.grand import Grand

from engine.constants import Round_To_Game_Time, Turn_To_Phase, Phase_To_Round


def grand_process(self: Grand, dt: float):
    self.round_timer += dt
    if self.round_timer > Round_To_Game_Time:
        self.round_timer -= Round_To_Game_Time
        if self.current_campaign_state["round"] < Phase_To_Round:
            self.current_campaign_state["round"] += 1
        else:
            self.current_campaign_state["round"] = 1
            if self.current_campaign_state["phase"] < Turn_To_Phase:
                self.current_campaign_state["phase"] += 1
            else:  # pass final phase, increase turn and reset phase
                self.current_campaign_state["phase"] = 1
                self.current_campaign_state["turn"] += 1
                self.change_turn()
            self.change_phase()
        self.change_round()

        # if self.ai_process_list:
        #     limit = int(len(self.ai_process_list) / 20)
        #     if limit < 20:
        #         limit = 20
        #         if limit > len(self.ai_process_list):
        #             limit = len(self.ai_process_list)
        #     for index in range(limit):
        #         this_character = self.ai_process_list[index]
        #         if this_character.alive:
        #             this_character.ai_prepare()
        #
        #     self.ai_process_list = self.ai_process_list[limit:]
        #
        # for battle_ai_commander in self.all_battle_ai_commanders:
        #     battle_ai_commander.update(dt)

        return True
    return False
