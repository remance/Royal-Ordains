def issue_commander_order(self, commander_order, false_order=False):
    self.commander_order = commander_order

    if not false_order:
        self.true_commander_order = commander_order
