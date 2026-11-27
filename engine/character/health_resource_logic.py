from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.character.character import AirCombatCharacter


def health_resource_logic(self):
    """Health and resource regen calculation"""
    health = self.health
    if health < self.base_health and self.health_regen:
        # negative regen number will reduce hp here
        health += self.health_regen * self.timer
        if health < 0:
            health = 0  # can't have negative hp
        elif health > self.base_health:
            health = self.base_health  # hp can't exceed max hp
        self.health = health

    resource = self.resource
    if resource < self.base_resource and self.resource_regen:
        resource += self.resource_regen * self.timer
        if resource < 0:
            resource = 0
        elif resource > self.base_resource:  # resource cannot exceed the max resource
            resource = self.base_resource
        self.resource = resource


def air_health_resource_logic(self: AirCombatCharacter):
    """Health and resource regen calculation for air character that has active and non active state"""
    health = self.health
    resource = self.resource
    if self.active:
        if health < self.base_health and self.health_regen:
            # negative regen number will reduce hp here
            health += self.health_regen * self.timer
            if health < 0:
                health = 0  # can't have negative hp
            elif health > self.base_health:
                health = self.base_health  # hp can't exceed max hp

        if resource < self.base_resource and self.resource_regen:
            resource -= self.timer
            if resource <= self.min_resource_move:
                resource = 0
                self.issue_commander_order(("back", self.retreat_pos))
    else:
        # replenish health and resource while not active in battle
        if health < self.base_health and self.health_regen:
            health += 10 * self.timer

        if resource < self.base_resource and self.resource_regen:
            resource += (self.resource_regen * 2) * self.timer

    self.health = health
    self.resource = resource
