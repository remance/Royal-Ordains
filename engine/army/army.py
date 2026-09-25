from engine.army.change_active_commander_actor import change_active_commander_actor
from engine.army.change_phase import change_phase
from engine.army.check_can_assemble import check_can_assemble
from engine.army.issue_move_command import issue_move_command
from engine.army.remove_army_from_active import remove_army_from_active
from engine.army.reset_stat import reset_stat
from engine.grand.deploy_army_from_reserve import deploy_army_from_reserve


class Army:
    character_list = None
    grand = None

    change_active_commander_actor = change_active_commander_actor
    change_phase = change_phase
    check_can_assemble = check_can_assemble
    deploy_from_reserve = deploy_army_from_reserve
    issue_move_command = issue_move_command
    remove_army_from_active = remove_army_from_active
    reset_stat = reset_stat

    def __init__(self, army_id: str, faction: str, culture: str, commander_char_id: str, army_followers: dict,
                 supply: int = 0, max_supply: int = 0, custom_preset_id=None, current_region=None,
                 travelling: dict = None, travel_how=None,
                 assembling_followers: dict = None):
        self.game_id = army_id
        self.faction = faction
        self.culture = culture
        self.army_followers = army_followers
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
        self.assembling_followers = assembling_followers
        self.can_assemble = False
        self.supply = supply
        self.max_supply = max_supply

        self.current_region = current_region  # current region the army is at
        self.travel_remain = 0
        self.travelling = travelling
        self.travel_how = travel_how

        self.base_pos = None
        include_culture_influence = False
        self.pathfinding_array = {}
        self.direct_routing_array = {}

        if current_region:  # active army in grand campaign exist in region, so can be used as purpose indication
            self.base_world_map = self.grand.map_data.base_world_map
            include_culture_influence = True
            if travelling:
                self.travel_remain = sum(travelling["remain_phase_require"])
                self.base_pos = travelling[1]
            else:
                self.base_pos = self.grand.region_list[current_region]["Settlement POS"]
            self.pathfinding_array = self.grand.current_campaign_state["pathfinding"]
            self.direct_routing_array = self.grand.current_campaign_state["direct_routing"]
            self.grand.dots_army_occupation[self.base_pos][self.game_id] = self
            self.region_by_pos_index = self.grand.region_by_pos_index
            self.check_can_assemble()

        self.reset_stat(include_culture_influence=include_culture_influence)

    @property
    def to_dict(self) -> dict:
        return {"ID": self.game_id, "faction": self.faction, "culture": self.culture,
                "commander": self.commander_id, "army_followers": self.army_followers,
                "supply": self.supply, "custom_preset_id": self.custom_preset_id,
                "base_pos": self.base_pos, "current_region": self.current_region,
                "travel_route": self.travelling, "travel_how": self.travel_how,
                "assembling": self.assembling_followers
                }

    @property
    def to_preset_dict(self) -> dict:
        return {"culture": self.culture, "commander": [self.commander_id], "army_followers": self.army_followers,
                "cost": self.cost, "leadership": self.leadership,
                "total_number": self.total_number, "upkeep": self.upkeep,
                "power": self.power, "supply": self.supply, "max_supply": self.max_supply,
                "strategy": [self.character_list[self.commander_id]["Strategy"]] +
                            [self.character_list[character[0]]["Strategy"] for character in
                             self.army_followers["retinue"] if character],
                "total_supply_usage": self.total_supply_usage
                }
