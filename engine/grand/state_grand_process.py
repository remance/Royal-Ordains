def state_grand_process(self, dt):
    self.current_campaign_state["phase_timer"] += dt
    if self.current_campaign_state["phase_timer"] > 1:  # phase change every 1 second
        self.current_campaign_state["phase_timer"] -= 1
        if self.current_campaign_state["phase"] < 10:
            self.current_campaign_state["phase"] += 1
        else:  # pass phase 10, increase turn and reset phase
            self.current_campaign_state["phase"] = 1
            self.current_campaign_state["turn"] += 1
        self.mini_time_orb.update_time()
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
