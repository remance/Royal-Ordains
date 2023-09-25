infinity = float("inf")


def health_resource_logic(self, dt):
    """Health and resource calculation"""
    if self.health != infinity:
        self.health += self.hp_regen * dt  # use the same as positive regen (negative regen number * dt will reduce hp)

        if self.health < 0:
            self.health = 0  # can't have negative hp
        elif self.health > self.max_health:
            self.health = self.max_health  # hp can't exceed max hp

    if self.resource != infinity:
        if self.resource < self.max_resource:
            self.resource += (self.resource_regen * dt)  # regen
            if self.resource < 0:
                self.resource = 0
            elif self.resource > self.max_resource:  # resource cannot exceed the max resource
                self.resource = self.max_resource
