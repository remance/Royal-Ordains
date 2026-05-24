from engine.constants import Phase_To_Game_Time, Turn_To_Phase


def grand_process(self, dt):
    self.phase_timer += dt
    if self.phase_timer > Phase_To_Game_Time:
        self.phase_timer -= Phase_To_Game_Time
        if self.current_campaign_state["phase"] < Turn_To_Phase:
            self.current_campaign_state["phase"] += 1
            self.change_phase()
        else:  # pass phase 10, increase turn and reset phase
            self.current_campaign_state["phase"] = 1
            self.current_campaign_state["turn"] += 1
            self.change_turn()

        return True
    return False
