def issue_commander_order(self, commander_order, false_order=False):
    if not false_order:
        if not self.false_order:
            self.commander_order = commander_order
        self.true_commander_order = commander_order
    else:
        self.false_order = True
        self.commander_order = commander_order
