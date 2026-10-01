from engine.army.change_active_commander_actor import change_active_commander_actor
from engine.army.change_phase import change_phase
from engine.army.check_assemble import check_assemble
from engine.army.issue_move_command import issue_move_command
from engine.army.remove_army_from_active import remove_army_from_active
from engine.army.reset_stat import reset_stat
from engine.grand.deploy_army_from_reserve import deploy_army_from_reserve


class Army:
    character_hire_building_list = None
    character_list = None
    grand = None

    change_active_commander_actor = change_active_commander_actor
    change_phase = change_phase
    check_assemble = check_assemble
    deploy_from_reserve = deploy_army_from_reserve
    issue_move_command = issue_move_command
    remove_army_from_active = remove_army_from_active
    reset_stat = reset_stat

    def __init__(self, army_id: str, faction: str, culture: str, commander_char_id: str, army_followers: dict,
                 supply: int = 0, max_supply: int = 0, custom_preset_id=None, grand_state=None):
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
        self.can_assemble = {}
        self.supply = supply
        self.max_supply = max_supply

        self.current_region = None  # current region the army is at
        self.assemble_percent = [0, 0]
        self.enable_resupply = 2
        self.enable_assemble = 2
        self.activity = {}

        self.base_pos = None
        include_culture_influence = False
        self.pathfinding_array = {}
        self.direct_routing_array = {}

        if grand_state:  # active army in grand campaign exist in region, so can be used as purpose indication
            self.enable_resupply = grand_state["enable_resupply"]
            self.enable_assemble = grand_state["enable_assemble"]
            self.activity = grand_state["activity"]
            self.current_region = grand_state["current_region"]  # current region the army is at

            self.base_world_map = self.grand.map_data.base_world_map
            include_culture_influence = True
            if "base_pos" in grand_state:
                self.base_pos = grand_state["base_pos"]
            else:
                self.base_pos = self.grand.region_list[self.current_region]["Settlement POS"]
            self.pathfinding_array = self.grand.current_campaign_state["pathfinding"]
            self.direct_routing_array = self.grand.current_campaign_state["direct_routing"]
            self.grand.dots_army_occupation[self.base_pos].append(self)
            self.region_by_pos_index = self.grand.region_by_pos_index
            self.check_assemble()

        self.reset_stat(include_culture_influence=include_culture_influence)

    @property
    def to_dict(self) -> dict:
        return {"ID": self.game_id, "faction": self.faction, "culture": self.culture,
                "commander": self.commander_id, "army_followers": self.army_followers,
                "supply": self.supply, "custom_preset_id": self.custom_preset_id,
                "grand_state": {"activity": self.activity, "enable_resupply": self.enable_resupply,
                                "enable_assemble": self.enable_assemble, "base_pos": self.base_pos,
                                "current_region": self.current_region, },
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
