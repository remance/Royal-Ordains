from engine.grandobject.grandobject import GrandObject
from engine.utils.common import clean_object


class Region:
    clean_object = clean_object

    def __init__(self, region_id, colour_id, settlement_pos, current_campaign_state):
        self.region_id = region_id
        self.colour_id = colour_id
        self.settlement_pos = settlement_pos
        self.controller = current_campaign_state["region_control"][colour_id]
        self.buildings = current_campaign_state["region_buildings"][colour_id]
        self.build_objects = {}
        for build_index, build_data in current_campaign_state["region_objects"][colour_id].items():
            self.build_objects[build_index] = GrandObject(build_data[0],
                                                          (build_data[1], build_data[2]), build_data[3])
        self.gold_income = 0
        self.supply_income = 0
        self.happy_income = 0
        self.tech_unlock = []

    def change_state(self, current_campaign_state):
        self.controller = current_campaign_state["region_control"][self.colour_id]
        self.buildings = current_campaign_state["region_buildings"][self.colour_id]
