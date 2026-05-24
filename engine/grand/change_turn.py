from engine.constants import Culture_Policy_Integration


def change_turn(self, turn_change=True):
    """
    Update campaign state when turn change
    @param self: Grand object
    @param turn_change: turn actually change or not, function can be used for campaign setup when False
    @return:
    """
    for faction in self.current_campaign_state["faction"]:
        faction_state = self.current_campaign_state["faction"][faction]

        if turn_change:
            # event duration is based on turn rather than phase
            faction_state["event"] = {event: value - 1 for event, value in faction_state["event"].items() if value > 1}

            # faction_region_control = self.current_campaign_state["region"]["control"][faction]
            for faction_culture in faction_state["culture"].values():
                # increase or decrease integration every turn
                policy_integration_cap = Culture_Policy_Integration[faction_culture["policy"]]
                if faction_culture["integration"] < policy_integration_cap:
                    faction_culture["integration"] += 0.01
                elif faction_culture["integration"] > policy_integration_cap:
                    faction_culture["integration"] -= 0.01

            faction_state["gold"] += faction_state["gold_income"]
            if faction_state["gold"] < 0:
                faction_state["gold"] = 0
            faction_state["supply"] += faction_state["supply_income"]
            if faction_state["supply"] < 0:
                faction_state["supply"] = 0

        self.cal_faction_culture(faction)

        for region in faction_state["region"]:
            self.cal_region_income(region)

        for army in faction_state["army"]:
            army.reset_stat()

        self.cal_faction_income(faction)

