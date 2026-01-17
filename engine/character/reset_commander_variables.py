infinity = float("inf")


def reset_commander_variables(self):
    """Update variable related to leader AI"""
    followers_len_check = [0, 0]
    total_range_power_score = 0
    total_offence_power_score = 0
    total_defence_power_score = 0
    if self.ai_behaviour == "range":
        total_range_power_score += self.power_score
    elif self.ai_behaviour == "melee":
        if self.melee_type == "offence":
            total_offence_power_score += self.power_score
        else:
            total_defence_power_score += self.power_score
    total_power_score = self.power_score

    for follower in self.ally_list:  # also include self
        if follower.ai_behaviour == "melee":
            followers_len_check[0] += 1
            if follower.melee_type == "offence":
                total_offence_power_score += follower.power_score
            else:
                total_defence_power_score += follower.power_score
        else:
            followers_len_check[1] += 1
            total_range_power_score += follower.power_score

        total_power_score += follower.power_score

    self.max_followers_len_check = sum(followers_len_check)

    self.followers_len_check = followers_len_check
    self.total_range_power_score = total_range_power_score
    self.total_offence_power_score = total_offence_power_score
    self.total_defence_power_score = total_defence_power_score
    self.total_power_score = total_power_score
