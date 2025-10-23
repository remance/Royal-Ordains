infinity = float("inf")


def reset_general_variables(self):
    """Update variable related to leader AI"""
    self.followers_len_check = [0, 0]
    self.total_range_power_score = 0
    if self.ai_behaviour == "range":
        self.total_range_power_score += self.power_score
    self.total_melee_power_score = 0
    if self.ai_behaviour == "melee":
        self.total_melee_power_score += self.power_score
    self.total_power_score = self.power_score
    if self.followers:
        for follower in self.followers:
            recursive_check_followers_of_followers(self, follower)

    if self.max_followers_len_check is None:
        self.max_followers_len_check = sum(self.followers_len_check)


def recursive_check_followers_of_followers(self, follower):
    if follower.ai_behaviour == "melee":
        self.followers_len_check[0] += 1
        self.total_melee_power_score += follower.power_score
    else:
        self.followers_len_check[1] += 1
        self.total_range_power_score += follower.power_score

    self.total_power_score += follower.power_score

    for follower2 in follower.followers:
        recursive_check_followers_of_followers(self, follower2)

