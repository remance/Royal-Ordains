def vraesier_status_update(self):
    if self.mode == "Demon":
        self.attack_impact_effect += 0.5
        self.power_bonus += 10
        self.super_armour *= 2


status_update_dict = {"Vraesier": vraesier_status_update}
