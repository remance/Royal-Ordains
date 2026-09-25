def check_can_assemble(self):
    self.can_assemble = False
    for value in self.army_followers.items():
        if not value[1]:  # has a follower not yet assembled
            self.can_assemble = True
            break
