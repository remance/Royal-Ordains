infinity = float("inf")


def health_resource_logic(self, dt):
    """Health and resource calculation"""
    if self.health != infinity:
        if self.health < self.base_health and self.hp_regen:
            self.health += self.hp_regen * dt  # use the same as positive regen (negative regen number * dt will reduce hp)

        if self.health < 0:
            self.health = 0  # can't have negative hp
        elif self.health > self.base_health:
            self.health = self.base_health  # hp can't exceed max hp

    if self.resource != infinity:
        if self.resource < self.base_resource:
            self.resource += (self.resource_regen * dt)  # regen
            if self.resource < 0:
                self.resource = 0
            elif self.resource > self.base_resource:  # resource cannot exceed the max resource
                self.resource = self.base_resource
