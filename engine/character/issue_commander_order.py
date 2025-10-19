def issue_commander_order(self, commander_order, issue_to_follower=True, false_order=False):
    """Recursively issue order to followers in the whole hierarchy"""
    self.commander_order = commander_order
    if not false_order:
        self.true_commander_order = commander_order
    if issue_to_follower:
        for follower in self.followers:
            follower.issue_commander_order(commander_order, false_order=false_order)
