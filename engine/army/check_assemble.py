from engine.constants import Turn_To_Phase


def check_assemble(self):
    """Check for follower assemble requirement and calculate the number of turn require to assemble each follower
    based on the army distance to nearest region with building that can hire it"""
    not_yet_assemble = 0
    already_assemble = 0

    self.can_assemble = {}

    can_assemble = self.can_assemble
    assemble_time_check_cache = {}

    character_recruit_building_list = self.character_recruit_building_list
    character_list = self.character_list
    owned_region_list = self.grand.current_campaign_state["faction"][self.faction]["region"]
    region_campaign_state = self.grand.current_campaign_state["region"]
    for key, followers in self.army_followers.items():
        for index, value in enumerate(followers):
            if value:
                if not value[1]:  # follower not yet assembled
                    not_yet_assemble += 1
                    character = value[0]
                    if character_list[character]["Is Unique"]:  # unique hero can assemble within 1 turn
                        can_assemble[(key, index)] = Turn_To_Phase
                    else:  # all other characters require check with building within faction to region
                        if character in assemble_time_check_cache:  # already has nearest check for same character
                            can_assemble[(key, index)] = assemble_time_check_cache[character]
                        else:
                            building_to_check = character_recruit_building_list[
                                character]  # already in [id, True, 0, True]
                            for region in owned_region_list:
                                region_building_list = region_campaign_state[region]["building"]
                                recruit_building_number = len([True for building in region_building_list if building in building_to_check])

                                if recruit_building_number:
                                    if self.current_region == region:  # same region use 1 turn, no need to check further
                                        can_assemble[(key, index)] = Turn_To_Phase
                                        assemble_time_check_cache[character] = Turn_To_Phase
                                        break
                                    if (self.current_region, region) in self.pathfinding_array:
                                        # different region must have possible route to this region
                                        how_long = len(self.pathfinding_array[(self.current_region, region)])

                                        # each multiple building reduce assemble turn by 1
                                        how_long -= recruit_building_number
                                        if how_long < 1:  # cannot reduce lower than 1 turn requirement
                                            how_long = 1
                                        index_assemble = (key, index)
                                        if index_assemble not in can_assemble or can_assemble[index_assemble] > how_long:
                                            can_assemble[(key, index)] = how_long
                                        assemble_time_check_cache[character] = how_long
                                        if how_long == 1:  # found nearest region, no need to check further
                                            break
                else:
                    already_assemble += 1

    self.assemble_percent = [not_yet_assemble, already_assemble]
