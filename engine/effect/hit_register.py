from random import uniform


def hit_register(self, target):
    """Calculate whether target dodge hit, then calculate damage"""
    hit_angle = -90
    front_hit = False
    if self.base_pos[0] >= target.base_pos[0]:
        hit_angle = 90
        if target.direction == "right":  # frontal attack collide
            front_hit = True
    elif target.direction == "left":
        front_hit = True

    if self.power:
        critical = False
        if self.critical_chance >= uniform(0, 1):
            critical = True
        final_dmg = self.cal_damage(target, critical, front_hit)

        if self.power:  # effect has damage to deal (some may simply be for apply status)
            target.cal_loss(self.owner, final_dmg, self.impact, hit_angle, critical)

        if not self.penetrate:
            if self.is_effect_type and self.after_reach:
                self.remain_check = True
        if self.enemy_status_effect:
            for effect in self.enemy_status_effect:
                target.apply_status(effect)
