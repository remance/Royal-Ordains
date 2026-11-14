from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.grand.grand import Grand

from random import randint


def start_battle_engagement(self: Grand, armies: dict, base_pos: tuple):
    current_campaign_state = self.current_campaign_state
    campaign_battle_dot = current_campaign_state["battle"]["dot"]
    campaign_battle_armies = current_campaign_state["battle"]["army"]
    campaign_battle_factions = current_campaign_state["battle"]["faction"]

    campaign_battle_dot.append(base_pos)

    team_1_army = armies[1][0]  # attacker
    team_2_army = armies[2][0]  # defender

    team_sub_armies = {1: [], 2: []}
    for team, army_list in armies.items():
        for index, army in enumerate(army_list):
            if not index:
                team_sub_armies[team].append(army)

            army.can_assemble = {}  # cancel assembling
            if army not in campaign_battle_armies:
                campaign_battle_armies.append(army)
                army.activity = {"battle": True}

            if army.belong_to_player_faction:
                self.army_list_ui.reset_card(army)

    if team_1_army.current_region != self.region_list[team_1_army.current_region]["Settlement POS"]:
        # fight outside of settlement, used random generated template
        stage = self.region_list[team_1_army.current_region]["Route Stage Template"]
        self.map_data.read_map_data(self.campaign, stage)
        stage_len = randint(stage[1], stage[2])
    else:  # use specific stage preset
        stage = team_1_army.current_region
        self.map_data.read_map_data(self.campaign, stage)
        stage_len = len(
            [value for value in self.game.preset_map_data[stage]["data"].values() if "scene" in value["Type"]])

    campaign_battle_factions[base_pos] = [team_1_army.faction, team_2_army.faction]

    commander_1_stat = self.character_list[team_1_army.commander_id]
    commander_2_stat = self.character_list[team_2_army.commander_id]

    battle_state = {"team": {0: {"faction": "free", "culture": "free",
                                 "strategy_resource": 0, "start_pos": 0.5, "air_group": [],
                                 "active_leader": 0, "strategy": [], "strategy_cooldown": {},
                                 "main_army": None, "reinforcement_army": [],
                                 "supply_resource": 0, "supply_reserve": 0, "total_supply": 0, "leadership": 0,
                                 "leader_call_list": [], "troop_call_list": [],
                                 "commander_character": None, "unit": [], "air_unit": [], "later_reinforcement": {}},
                             1: {"faction": team_1_army.faction,
                                 "culture": team_1_army.culture,
                                 "strategy_resource": 0,
                                 "start_pos": 0, "air_group": [],
                                 "active_leader": 0, "strategy": [], "strategy_cooldown": {},
                                 "main_army": team_1_army,
                                 "reinforcement_army": team_sub_armies[1],
                                 "supply_resource": 0, "supply_reserve": 0, "total_supply": 0, "leadership": 0,
                                 "leader_call_list": [], "troop_call_list": [],
                                 "commander_character": None,
                                 "commander": {"aggressive": commander_1_stat["Commander AI Aggressiveness"],
                                               "clever": commander_1_stat["Commander AI Cleverness"],
                                               "swift": commander_1_stat["Commander AI Swiftness"]},
                                 "unit": [], "air_unit": [], "later_reinforcement": {}},
                             2: {"faction": team_2_army.faction,
                                 "culture": team_2_army.culture,
                                 "strategy_resource": 0,
                                 "start_pos": 1, "air_group": [],
                                 "active_leader": 0, "strategy": [], "strategy_cooldown": {},
                                 "main_army": team_2_army,
                                 "reinforcement_army": team_sub_armies[2],
                                 "supply_resource": 0, "supply_reserve": 0, "total_supply": 0, "leadership": 0,
                                 "leader_call_list": [], "troop_call_list": [],
                                 "commander_character": None,
                                 "commander": {"aggressive": commander_2_stat["Commander AI Aggressiveness"],
                                               "clever": commander_2_stat["Commander AI Cleverness"],
                                               "swift": commander_2_stat["Commander AI Swiftness"]},
                                 "unit": [], "air_unit": [], "later_reinforcement": {}}},
                    "army": armies, "weather": None,
                    "corpse": [], "stage": stage, "stage_size": stage_len}

    self.battle.setup_battle_start(self.campaign, stage, battle_state["team"], battle_state=battle_state)
    current_campaign_state["battle"]["battles"][base_pos] = battle_state
