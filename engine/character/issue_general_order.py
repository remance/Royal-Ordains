def issue_general_order(self, general_order):
    self.general_order = general_order
    for follower in self.followers:
        follower.issue_general_order(general_order)
