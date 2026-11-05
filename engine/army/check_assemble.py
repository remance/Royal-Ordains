from engine.constants import Turn_To_Phase


def check_assemble(self):
    """Check for follower assemble requirement and calculate the number of turn require to assemble each follower
    based on the army distance to nearest region with building that can hire it"""
    not_yet_assemble = 0
    already_assemble = 0

    self.can_assemble = {}

    can_assemble = self.can_assemble
    cache_assemble_time_check = {}

    if not self.current_region:  # army does not exist in any region, like reserve army in preset creation ui
        return
    character_recruit_building_list = self.character_recruit_building_list
    character_list = self.character_list
    current_campaign_state = self.grand.current_campaign_state
    owned_region_list = current_campaign_state["faction"][self.faction]["region"]
    region_campaign_state = current_campaign_state["region"]
    campaign_path_finding = current_campaign_state["pathfinding"]
    for key, followers in self.army_followers.items():
        for index, value in enumerate(followers):
            if value:
                if not value[1]:  # follower not yet assembled
                    not_yet_assemble += 1
                    character = value[0]
                    if character_list[character]["Is Unique"]:  # unique hero can assemble within 1 turn
                        can_assemble[(key, index, self.current_region)] = Turn_To_Phase
                    else:  # all other characters require check with building within faction to region
                        if character in cache_assemble_time_check:  # already has nearest check for same character
                            can_assemble[(key, index, cache_assemble_time_check[character][1])] = (
                                cache_assemble_time_check)[character][0]
                        else:
                            building_to_check = character_recruit_building_list[
                                character]  # already in [id, True, 0, True]
                            for region in owned_region_list:
                                region_building_list = region_campaign_state[region]["building"]
                                recruit_building_number = len([True for building in region_building_list if building in building_to_check])

                                if recruit_building_number:
                                    if self.current_region == region:  # same region use 1 turn, no need to check further
                                        can_assemble[(key, index, region)] = Turn_To_Phase  # convert to phase
                                        cache_assemble_time_check[character] = (Turn_To_Phase, region)
                                        break

                                    if (self.current_region, region) in campaign_path_finding:
                                        # different region must have possible route to this region
                                        how_long = len(campaign_path_finding[(self.current_region, region)]) + 1

                                        # each multiple building reduce assemble turn by 1
                                        how_long -= recruit_building_number
                                        if how_long < 1:  # cannot reduce lower than 1 turn requirement
                                            how_long = 1
                                        how_long *= Turn_To_Phase  # convert to phase
                                        index_assemble = (key, index, region)
                                        if index_assemble not in can_assemble or can_assemble[index_assemble] > how_long:
                                            can_assemble[(key, index, region)] = how_long
                                        cache_assemble_time_check[character] = (how_long, region)
                                        if how_long == 1:  # found nearest region, no need to check further
                                            break
                else:
                    already_assemble += 1
    self.assemble_percent = [not_yet_assemble, already_assemble]
