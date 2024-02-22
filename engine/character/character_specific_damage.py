def vraesier_damage(self, dmg):
    if self.mode != "Demon":
        self.resource += dmg / 10
    else:
        self.resource += dmg / 20
    if self.resource > self.base_resource:
        self.resource = self.base_resource


damage_dict = {"Vraesier": vraesier_damage}
