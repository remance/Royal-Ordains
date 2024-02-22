def iri_status_update(self):
    """Suffer from speed debuff based on remaining resources"""
    if self.mode == "Normal":
        self.speed -= 100
    elif self.mode == "Half":
        self.speed -= 50
    elif self.mode == "Near":
        self.speed -= 15


def nayedien_status_update(self):
    if self.combat_state == "Combat":
        self.super_armour *= 2


def vraesier_status_update(self):
    if self.mode == "Demon":
        self.impact_modifier += 0.5
        self.power_bonus += 10
        self.super_armour *= 2


status_update_dict = {"Vraesier": vraesier_status_update, "Iri": iri_status_update, "Nayedien": nayedien_status_update}
