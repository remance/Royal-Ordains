def issue_commander_order(self, commander_order, false_order=False):
    """Recursively issue order to followers in the whole hierarchy"""
    self.commander_order = commander_order
    if not false_order:
        self.true_commander_order = commander_order
    else:
        self.false_commander_order = commander_order

    for follower in self.followers:
        follower.issue_commander_order(commander_order)
