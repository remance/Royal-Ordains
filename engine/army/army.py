import uuid

from engine.army.armycharacter import ArmyCharacter
from engine.grandobject.grandobject import GrandArmyActor


class Army:
    character_list = None
    grand = None

    def __init__(self, faction: str, culture: str, commander: (ArmyCharacter, str), leader_group: list,
                 ground_group: list, air_group: list, retinue: list, supply: int = 0, custom_preset_id=None,
                 base_pos=(0, 0), current_region=None, destination=None, travel_route=(), broken=False
                 ):
        self.game_id = str(uuid.uuid1())
        self.faction = faction
        self.culture = culture
        self.leader_group = [item for item in leader_group if item]  # remove 0 or empty item
        self.ground_group = [item for item in ground_group if item]
        self.commander_id = None
        if commander:
            if type(commander) is not ArmyCharacter:
                self.commander_id = commander
            else:
                self.commander_id = commander.char_id
        self.custom_preset_id = custom_preset_id

        self.commander_actor = None
        self.air_group = [item for item in air_group if item]
        self.retinue = retinue
        self.cost = 0
        self.upkeep = 0
        self.supply = supply
        self.travel_speed = 0
        self.sum_mass = 0
        self.sum_travel_speed = 0
        self.len_travel_speed = 0
        self.base_pos = base_pos
        self.current_region = current_region
        self.destination = destination
        self.travel_route = travel_route
        self.broken = broken
        self.reset_stat()

    def reset_stat(self):
        travel_speed = []
        self.sum_mass = 0
        if self.commander_id:
            travel_speed.append(self.character_list[self.commander_id]["Speed"])
            self.sum_mass += self.character_list[self.commander_id]["Mass"]
            self.cost += self.character_list[self.commander_id]["Cost"]
            self.upkeep += self.character_list[self.commander_id]["Upkeep"]

        for group in (self.leader_group, self.ground_group):
            for character in group:
                travel_speed.append(self.character_list[character]["Speed"])
                self.sum_mass += self.character_list[character]["Mass"]
                self.cost += self.character_list[character]["Cost"]
                self.upkeep += self.character_list[character]["Upkeep"]
        for air_group in self.air_group:
            self.cost += self.character_list[air_group]["Cost"]
            self.upkeep += self.character_list[air_group]["Upkeep"]

        self.sum_travel_speed = sum(travel_speed)
        self.len_travel_speed = len(travel_speed)

    def setup_for_grand_map(self):
        self.commander_actor = GrandArmyActor(self.commander_id, self.pos)

    def set_in_grand_map(self, pos):
        self.pos = pos
        self.commander_actor.pos = self.pos

    def update(self, dt):
        region_colour = tuple(self.grand.grand_map.true_map_image.get_at((int(self.base_pos[0]),
                                                                          int(self.base_pos[1]))))[:3]
        self.current_region = self.grand.regions[region_colour]

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
                "destination": self.destination, "travel_route": self.travel_route, "broken": self.broken
                }
