from engine.constants import Phase_To_Game_Time, Turn_To_Phase


def state_grand_process(self, dt):
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
        self.mini_time_orb_ui.update_time()

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

    # if self.current_campaign_state["battle"]["manual"]:
    #     self.battle.grand_event_notification
