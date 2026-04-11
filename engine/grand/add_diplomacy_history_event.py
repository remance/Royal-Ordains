def add_diplomacy_history_event(self, main_faction, event_faction, event_type, value, turn):
    faction_behaviour = self.faction_list[main_faction]  # TODO add ai behaviour modifier
    self.current_campaign_state["faction"][main_faction]["diplomacy"][event_faction]["history"].append([event_type, value, turn])