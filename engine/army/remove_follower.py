def remove_follower(self, follower_type, index):
    self.army_followers[follower_type][index] = []  # remove to empty
    self.check_assemble(specific=(follower_type, index))
