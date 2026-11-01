def destroy_army(self):
    if self.faction == "free":
        current_campaign_state["free_character"].remove(rebel_army["Commander"])