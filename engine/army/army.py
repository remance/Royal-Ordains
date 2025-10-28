import uuid


class Army:
    character_list = None

    def __init__(self, group: dict, air_group: list, retinue: list):
        self.controllable = True
        self.group = group
        self.commander_id = None
        if group:
            self.commander_id = tuple(group.keys())[0].char_id

        self.air_group = air_group
        self.retinue = retinue
        self.upkeep = 0
        self.supply = 0
        self.reset_stat()

    def reset_stat(self):
        for general, follower_list in self.group.items():
            self.upkeep += self.character_list[general.char_id]["Upkeep"]
            self.supply += self.character_list[general.char_id]["Supply"]
            for follower in follower_list:
                for key, follower_number in follower.items():
                    self.upkeep += (self.character_list[key]["Upkeep"] * follower_number)
                    self.supply += (self.character_list[key]["Supply"] * follower_number)
        for air_group in self.air_group:
            for key, follower_number in air_group.items():
                self.upkeep += (self.character_list[key]["Upkeep"] * follower_number)
                self.supply += (self.character_list[key]["Supply"] * follower_number)

    def update(self, dt):
        pass


class GarrisonArmy(Army):
    def __init__(self, group: dict, air_group: list, retinue: list):
        """Garrison in city, has no upkeep and supply use, generals will appear as uncontrollable in battle while
        air_group appear as reinforcement"""
        Army.__init__(self, group, air_group, retinue)
        self.controllable = False
        self.upkeep = 0
        self.supply = 0
