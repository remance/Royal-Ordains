import uuid

from pygame import Vector2

from engine.constants import Retinue_Leadership_Add_Modifier
from engine.grandactor.grandactor import GrandActor


class Army:
    character_list = None
    grand = None

    def __init__(self, faction: str, culture: str, commander: (GrandActor, str), leader_group: list,
                 ground_group: list, air_group: list, retinue: list, supply: int = 0, max_supply: int = 0,
                 custom_preset_id=None, current_region=None, travel_route=(), broken=False):
        self.game_id = str(uuid.uuid1())
        self.faction = faction
        self.culture = culture
        self.leader_group = [item for item in leader_group if item]  # remove 0 or empty item
        self.ground_group = [item for item in ground_group if item]
        self.air_group = [item for item in air_group if item]
        self.retinue = [item for item in retinue if item]
        self.commander_id = None
        if commander:
            if type(commander) is not GrandActor:
                self.commander_id = commander
            else:
                self.commander_id = commander.char_id
        self.custom_preset_id = custom_preset_id
        self.commander_actor = None
        self.leadership = 0
        self.strategy_regen = 0
        self.cost = 0
        self.upkeep = 0
        self.supply = supply
        self.max_supply = max_supply
        self.travel_speed = 0
        self.sum_mass = 0
        self.sum_travel_speed = 0
        self.len_travel_speed = 0

        self.current_region = current_region
        self.travel_route = travel_route
        self.base_pos = None
        self.pos = None
        include_influence = False

        if current_region:  # active army in grand campaign exist in region, so can be used as purpose indication
            include_influence = True
            if self.travel_route:
                self.base_pos = self.travel_route[0]
            else:
                self.base_pos = self.grand.region_list[current_region]["Settlement POS"]
            self.pos = Vector2((self.base_pos[0] * self.grand.map_shown_to_actual_scale_width,
                                self.base_pos[1] * self.grand.map_shown_to_actual_scale_height))
        self.broken = broken

        self.reset_stat(include_influence=include_influence)

    def reset_stat(self, include_influence=True):
        travel_speed = []
        self.leadership = 0
        self.sum_mass = 0
        self.cost = 0
        self.upkeep = 0

        for key, group in {"commander": [self.commander_id], "leader": self.leader_group, "ground": self.ground_group,
                           "air": self.air_group, "retinue": self.retinue}.items():
            if group:
                for character in group:
                    if character:
                        character_stat = self.character_list[self.commander_id]
                        character_culture = character_stat["Culture"]
                        influence = 0
                        if include_influence:
                            influence = 2
                            faction_culture = self.grand.current_campaign_state["faction"][self.faction]["culture"]
                            if character_culture in faction_culture:
                                # the lower the culture influence, the higher cost and upkeep
                                # e.g., 50% culture influence result in double cost, 0 = triple cost
                                influence = (1 - faction_culture[character_culture]["influence"]) * 2
                        self.cost += character_stat["Cost"] + (character_stat["Cost"] * influence)
                        self.upkeep += character_stat["Upkeep"] + (character_stat["Upkeep"] * influence)

                        if key == "commander":
                            self.leadership += character_stat["Leadership"]
                            travel_speed.append(character_stat["Speed"])
                            self.sum_mass += character_stat["Mass"]

                        elif key == "retinue":
                            self.leadership += character_stat["Leadership"] * Retinue_Leadership_Add_Modifier

                        elif key in ("leader", "ground"):
                            travel_speed.append(character_stat["Speed"])
                            self.sum_mass += character_stat["Mass"]
                            self.cost += character_stat["Cost"]
                            self.upkeep += character_stat["Upkeep"]

        self.strategy_regen = self.leadership / 100
        self.sum_travel_speed = sum(travel_speed)
        self.len_travel_speed = len(travel_speed)

    def set_in_grand_map(self, pos):
        self.pos = pos
        self.commander_actor.pos = self.pos

    def update(self, dt):
        region_colour = tuple(self.grand.grand_map.true_map_image.get_at((int(self.base_pos[0]),
                                                                          int(self.base_pos[1]))))[:3]
        self.current_region = self.grand.region_by_colour_list[region_colour]

        self.travel_speed = (self.sum_travel_speed / (
                self.sum_mass * route_travel_modify)) * dt  # use avg speed of all ground characters

        self.set_in_grand_map()

    @property
    def to_dict(self) -> dict:
        return {"faction": self.faction, "culture": self.culture,
                "commander": self.commander_id, "leader_group": self.leader_group,
                "ground_group": self.ground_group, "air_group": self.ground_group,
                "retinue": self.retinue, "supply": self.supply, "custom_preset_id": self.custom_preset_id,
                "base_pos": self.base_pos, "current_region": self.current_region,
                "travel_route": self.travel_route, "broken": self.broken
                }
