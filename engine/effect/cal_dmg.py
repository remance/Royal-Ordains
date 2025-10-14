infinity = float("inf")
from random import uniform


def cal_dmg(self, target, critical: bool, front_hit: bool):
    """
    Calculate dmg on target
    :param self: DamageEffect object
    :param target: Target character object
    :param critical: Critical damage or not
    :param front_hit: Critical damage or not
    :return: Damage on health and element effect
    """

    target_defence = 0
    if not self.no_defence:
        target_defence = target.defence
        if not front_hit and not target.no_weak_side:
            # back attack use less target defence if target does not have no_weak_side property
            target_defence *= 0.5
        elif target.shield:  # front attack against shield give bonus defence
            target_defence *= 1.5
        target_defence = (uniform(target_defence * 0.5, target_defence * 1.5) - uniform(self.offence * 0.5,
                                                                                        self.offence * 1.5)) / 100
        if target_defence > 0.9:  # defence can not reduce more than 90% of damage
            target_defence = 0.9
        elif target_defence < 0:  # defence dmg reduction can not be negative
            target_defence = 0
    damage = int((self.dmg - (self.dmg * target_defence)) * (1 - target.element_resistance[self.element]))

    if critical:
        damage *= 2

    # Damage cannot be negative (it would heal instead)
    if damage < 0:
        damage = 0

    return damage
