from random import uniform


def check_faction_region_number(self, value, faction):
    if len(self.current_campaign_state["faction"][faction]["region"]) < value:
        return False
    return True


def check_faction_building_build(self, value, faction):
    building_check = {key: value2 for key, value2 in value.items()}
    for region in self.current_campaign_state["faction"][faction]["region"]:  # check owned region
        for build_slot in self.current_campaign_state["region"][region]["buildings"]:  # check each building slot
            for building in tuple(building_check.keys()):
                # this slot has match building
                if building in build_slot and build_slot[1]:  # found active building
                    building_check[building] -= 1
                    if not building_check[building]:
                        building_check.pop(building)
                    if not building_check:  # condition pass
                        return True
                break

    return False


def check_faction_culture_higher(self, value, faction):
    faction_culture_state = self.current_campaign_state["faction"][faction]["culture"]
    for culture, culture_value in value.items():
        if culture not in faction_culture_state or faction_culture_state[culture]["influence"] < value:
            # influence not higher than condition
            return False
    return True


def check_faction_culture_lower(self, value, faction):
    faction_culture_state = self.current_campaign_state["faction"][faction]["culture"]
    for culture, culture_value in value.items():
        if culture in faction_culture_state and faction_culture_state[culture]["influence"] > value:
            # influence not lower than condition
            return False
    return True


def check_faction_control_region(self, value, faction):
    # check if region is controlled by this faction
    for region in value:
        if region not in self.current_campaign_state["faction"][faction]["region"]:
            return False


def check_faction_character_exist(self, value, faction):
    # check if character is employed in this faction
    if value not in self.current_campaign_state["faction"][faction]["character"]:
        return False


def check_faction_gold_higher(self, value, faction):
    if self.current_campaign_state["faction"][faction]["gold"] < value:
        return False


def check_faction_gold_lower(self, value, faction):
    if self.current_campaign_state["faction"][faction]["gold"] > value:
        return False


def check_faction_happiness_higher(self, value, faction):
    if self.current_campaign_state["faction"][faction]["happiness"] < value:
        return False


def check_faction_happiness_lower(self, value, faction):
    if self.current_campaign_state["faction"][faction]["happiness"] > value:
        return False


check_specific_faction_condition = {"region_number": check_faction_region_number,
                                    "building_build": check_faction_building_build,
                                    "culture>": check_faction_culture_higher,
                                    "culture<": check_faction_culture_lower,
                                    "control_region": check_faction_control_region,
                                    "character_exist": check_faction_character_exist,
                                    "gold>": check_faction_gold_higher,
                                    "gold<": check_faction_gold_lower,
                                    "happiness>": check_faction_happiness_higher,
                                    "happiness<": check_faction_happiness_lower}


def check_event(self):
    still_possible_events = self.current_campaign_state["possible_events"]
    current_turn = self.current_campaign_state["turn"]
    for event in tuple(still_possible_events.keys()):
        event_data = still_possible_events[event]
        event_faction = event_data["Faction"]
        event_occur = True
        for condition, value in event_data["Condition"].items():
            if condition == "turn":
                if value != current_turn:
                    event_occur = False
                    break
            elif condition == "random":
                if int(uniform(0, value)) != value:
                    event_occur = False
                    break
            else:  # conditions that require faction state check
                if event_faction != "any":  # specific faction
                    if not check_specific_faction_condition[condition](self, value, event_faction):
                        event_occur = False
                        break
                else:
                    for faction in self.current_campaign_state["faction"]:
                        if not check_specific_faction_condition[condition](self, value, event_faction):
                            event_occur = False
                            break
                        elif event_data["One Time Event"]:  # event pass but only one faction receive unique event
                            event_occur = event_faction
                            break
                    if not event_occur:
                        break

        if event_occur:
            if not self.player_faction or event_faction == self.player_faction or event_occur == self.player_faction:
                # add event log, popup and decision to ui for player faction
                if self.player_faction:
                    pass

            for effect in event_data["effect"]:
                if event_faction == "any":  # apply to all faction
                    if event_occur is not True:  # one-time event, apply to event_occur assigned faction
                        apply_faction = event_occur

                else:
                    apply_faction = event_faction

            if event_data["One Time Event"]:  # remove unique event
                still_possible_events.pop(event)
