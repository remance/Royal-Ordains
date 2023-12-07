infinity = float("inf")


def cal_dmg(self, target, critical):
    """
    Calculate dmg on target
    :param self: DamageEffect object
    :param target: Target character object
    :param critical: Critical damage or not
    :return: Damage on health and element effect
    """
    # attack pass through dodge now calculate defense

    # impact = self.knock_power
    damage, element_effect = cal_dmg_element(self, target, critical)

    # Damage cannot be negative (it would heal instead), same for morale dmg
    if damage < 0:
        damage = 0

    return damage, element_effect


def cal_dmg_element(self, target, critical):
    defence = target.defence
    if self.no_defence:
        defence = 1
    damage = int((self.dmg - (self.dmg * (target.element_resistance[self.element] / 100))) * defence)
    if critical:
        damage *= 2
    element_effect = {self.element: damage / 10}
    # damage *= self.owner.weapon_dmg_modifier

    return damage, element_effect
