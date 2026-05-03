from engine.constants import Culture_Policy_Integration


def change_turn(self):
    for faction in self.current_campaign_state["faction"]:
        faction_state = self.current_campaign_state["faction"][faction]

        # event duration is based on turn rather than phase
        faction_state["event"] = {event: value - 1 for event, value in faction_state["event"].items() if value > 1}

        if faction != "free":
            # faction_region_control = self.current_campaign_state["region"]["control"][faction]
            for faction_culture in faction_state["culture"].values():
                # increase or decrease integration every turn
                policy_integration_cap = Culture_Policy_Integration[faction_culture["policy"]]
                if faction_culture["integration"] < policy_integration_cap:
                    faction_culture["integration"] += 0.01
                elif faction_culture["integration"] > policy_integration_cap:
                    faction_culture["integration"] -= 0.01

            self.cal_faction_culture(faction)

        for army in faction_state["army"]:
            army.reset_stat()

        self.cal_faction_income(faction)
