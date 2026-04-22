# import uuid str(uuid.uuid1())

from pygame import Vector2

from engine.constants import Retinue_Leadership_Add_Modifier
from engine.army.change_active_commander_actor import change_active_commander_actor
from engine.army.change_phase import change_phase
from engine.army.deploy_from_reserve import deploy_from_reserve
from engine.army.issue_move_command import issue_move_command
from engine.army.remove_army_from_active import remove_army_from_active


class Army:
    character_list = None
    grand = None

    change_active_commander_actor = change_active_commander_actor
    change_phase = change_phase
    deploy_from_reserve = deploy_from_reserve
    issue_move_command = issue_move_command
    remove_army_from_active = remove_army_from_active

    def __init__(self, army_id: str, faction: str, culture: str, commander_char_id: str, leader_group: list,
                 ground_group: list, air_group: list, retinue: list, supply: int = 0, max_supply: int = 0,
                 custom_preset_id=None, current_region=None, travelling: dict = None, assembling: dict = None):
        self.game_id = army_id
        self.faction = faction
        self.culture = culture
        self.leader_group = [item for item in leader_group if item]  # remove 0 or empty item
        self.ground_group = [item for item in ground_group if item]
        self.air_group = [item for item in air_group if item]
        self.retinue = [item for item in retinue if item]
        self.commander_id = commander_char_id
        self.custom_preset_id = custom_preset_id
        self.commander_actor = None
        self.leadership = 0
        self.strategy_regen = 0
        self.total_number = 0
        self.cost = 0
        self.upkeep = 0
        self.power = 0
        self.total_supply_usage = 0
        self.travel_time_modifier = 1
        self.assembling = assembling
        self.supply = supply
        self.max_supply = max_supply

        self.current_region = current_region  # current region the army is at
        self.travel_remain = 0
        self.travelling = travelling

        self.base_pos = None
        include_culture_influence = False
        self.pathfinding_array = {}

        if current_region:  # active army in grand campaign exist in region, so can be used as purpose indication
            include_culture_influence = True
            if travelling:
                self.travel_remain = sum(travelling["remain_phase_require"])
                self.base_pos = travelling[1]
            else:
                self.base_pos = self.grand.region_list[current_region]["Settlement POS"]
            self.pathfinding_array = self.grand.current_campaign_state["pathfinding"]

        self.reset_stat(include_culture_influence=include_culture_influence)

    def reset_stat(self, include_culture_influence=True):
        self.leadership = 0
        self.cost = 0
        self.upkeep = 0
        self.power = 0
        self.total_number = 0
        self.total_supply_usage = 0

        for key, group in {"commander": [self.commander_id], "leader": self.leader_group, "ground": self.ground_group,
                           "air": self.air_group, "retinue": self.retinue}.items():
            if group:
                for character in group:
                    if character:
                        character_stat = self.character_list[character]
                        character_culture = character_stat["Culture"]
                        influence = 0
                        if include_culture_influence and character_culture != "free":
                            influence = 2
                            faction_culture = self.grand.current_campaign_state["faction"][self.faction]["culture"]
                            if character_culture in faction_culture:
                                # the lower the culture influence, the higher cost and upkeep
                                # e.g., 50% culture influence result in double cost, 0 = triple cost
                                influence = (1 - faction_culture[character_culture]["influence"]) * 2
                        self.cost += character_stat["Cost"] + (character_stat["Cost"] * influence)
                        self.upkeep -= character_stat["Upkeep"] + (character_stat["Upkeep"] * influence)
                        total_can_call = character_stat["Arrive Per Call"] * character_stat["Capacity"]

                        self.power += character_stat["Power Score"] * total_can_call
                        if key == "commander":
                            self.leadership += character_stat["Leadership"]
                            self.total_number += 1  # commander can't be called multiple time so only 1
                        elif key == "retinue":
                            self.leadership += character_stat["Leadership"] * Retinue_Leadership_Add_Modifier
                        else:
                            self.total_supply_usage += (character_stat["Supply"] * character_stat["Capacity"])
                            self.total_number += total_can_call

        self.strategy_regen = self.leadership / 100

    @property
    def to_dict(self) -> dict:
        return {"ID": self.game_id, "faction": self.faction, "culture": self.culture,
                "commander": self.commander_id, "leader_group": self.leader_group,
                "ground_group": self.ground_group, "air_group": self.ground_group,
                "retinue": self.retinue, "supply": self.supply, "custom_preset_id": self.custom_preset_id,
                "base_pos": self.base_pos, "current_region": self.current_region,
                "travel_route": self.travelling
                }

    @property
    def to_preset_dict(self) -> dict:
        return {"culture": self.culture, "commander": [self.commander_id], "leader": self.leader_group,
                "troop": self.ground_group, "air": self.ground_group, "retinue": self.retinue,
                "cost": self.cost, "leadership": self.leadership,
                "total_number": self.total_number, "upkeep": self.upkeep,
                "power": self.power, "supply": self.supply, "max_supply": self.max_supply,
                "strategy": [self.character_list[self.commander_id]["Strategy"]] +
                            [self.character_list[character]["Strategy"] for character in self.retinue],
                "total_supply_usage": self.total_supply_usage
                }
