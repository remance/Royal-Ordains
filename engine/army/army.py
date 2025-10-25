import uuid


class Army:
    character_list = None

    def __init__(self, generals: list, air_group: list, retinue: list):
        self.controllable = True
        self.generals = []
        for general in generals:  # create unique id for each general
            self.generals.append({(str(uuid.uuid1()), key): value for key, value in general.items()})
        self.commander_id = None
        if generals:
            self.commander_id = tuple(generals[0].keys())[0]

        self.air_group = air_group
        self.retinue = retinue
        self.upkeep = 0
        self.supply = 0
        self.reset_stat()

    def reset_stat(self):
        for unit in self.generals:
            for leader, follower_list in unit.items():
                self.upkeep += self.character_list[leader[1]]["Upkeep"]
                self.supply += self.character_list[leader[1]]["Supply"]
                for follower in follower_list:
                    for key, follower_number in follower.items():
                        self.upkeep += (self.character_list[key]["Upkeep"] * follower_number)
                        self.supply += (self.character_list[key]["Supply"] * follower_number)
        for unit in self.air_group:
            for key, follower_number in unit.items():
                self.upkeep += (self.character_list[key]["Upkeep"] * follower_number)
                self.supply += (self.character_list[key]["Supply"] * follower_number)

    def update(self, dt):
        pass


class GarrisonArmy(Army):
    def __init__(self, generals: list, air_group: list, retinue: list):
        """Garrison in city, has no upkeep and supply use, generals will appear as uncontrollable in battle while
        air_group appear as reinforcement"""
        Army.__init__(self, generals, air_group, retinue)
        self.controllable = False
        self.upkeep = 0
        self.supply = 0
