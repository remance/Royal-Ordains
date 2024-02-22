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
    damage = cal_dmg_element(self, target, critical)

    # Damage cannot be negative (it would heal instead) or 0, damage can only be 0 if original already 0
    if damage < 0:
        damage = 0

    return damage


def cal_dmg_element(self, target, critical):
    defence = 1 - target.defence
    if self.no_defence or self.owner.attack_no_defence:
        defence = 1
    element = self.element
    if self.owner.attack_element:
        element = self.owner.attack_element
    damage = int((self.dmg - (self.dmg * (target.element_resistance[element]))) * defence)
    if critical:
        damage *= 2

    return damage
