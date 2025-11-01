infinity = float("inf")


def health_resource_logic(self):
    """Health and resource calculation"""
    if self.health != infinity:
        if self.health_regen:
            # negative regen number will reduce hp here
            self.health += self.health_regen * self.timer
            if self.health < 0:
                self.health = 0  # can't have negative hp
            elif self.health > self.base_health:
                self.health = self.base_health  # hp can't exceed max hp

    if self.resource != infinity:
        if self.resource_regen:
            self.resource += self.resource_regen * self.timer
            if self.resource < 0:
                self.resource = 0
            elif self.resource > self.base_resource:  # resource cannot exceed the max resource
                self.resource = self.base_resource


def air_health_resource_logic(self):
    """Health and resource calculation"""
    if self.active:
        if self.health != infinity:
            if self.health_regen:
                # negative regen number will reduce hp here
                self.health += self.health_regen * self.timer
                if self.health < 0:
                    self.health = 0  # can't have negative hp
                elif self.health > self.base_health:
                    self.health = self.base_health  # hp can't exceed max hp

        if self.resource != infinity:
            self.resource -= self.timer
            if self.resource <= 0:
                self.resource = 0
                self.issue_commander_order(("back", self.start_pos))
    else:
        # replenish health and resource while not active in battle
        if self.health != infinity and self.health < self.base_health:
            self.health += 10 * self.timer

        if self.resource != infinity and self.resource < self.base_resource:
            self.resource += (self.resource_regen * 2) * self.timer
