import uuid

from engine.army.armycharacter import ArmyCharacter
from engine.grandobject.grandobject import GrandArmyActor


class Army:
    character_list = None
    grand = None

    def __init__(self, commander: (ArmyCharacter, str), leader_group: list,
                 ground_group: list, air_group: list, retinue: list, supply: int = 0, custom_preset_id=None):
        self.game_id = str(uuid.uuid1())
        self.leader_group = leader_group
        self.ground_group = ground_group
        self.commander_id = None
        if commander:
            if type(commander) is not ArmyCharacter:
                self.commander_id = commander
            else:
                self.commander_id = commander.char_id
        self.custom_preset_id = custom_preset_id

        self.commander_actor = None
        self.air_group = air_group
        self.retinue = retinue
        self.cost = 0
        self.upkeep = 0
        self.supply = supply
        self.travel_speed = 0
        self.sum_mass = 0
        self.sum_travel_speed = 0
        self.len_travel_speed = 0
        self.discipline = 100
        self.base_pos = (0, 0)
        self.pos = (0, 0)
        self.current_region = None
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
