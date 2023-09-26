from pygame.sprite import spritecollide


def drop_collide_check(self):
    collide_list = spritecollide(self, self.battle.all_team_drop[self.team], False)
    for item in collide_list:
        if not item.stat["Specific Receiver"] or self.owner.sprite_id == item.stat["Specific Receiver"]:
            # can pick this drop
            if item.stat["Health"]:
                self.owner.health += item.stat["Health"]
                if self.owner.health > self.owner.max_health:
                    self.owner.health = self.owner.max_health
            if item.stat["Resource"]:
                self.owner.resource += item.stat["Resource"]
                if self.owner.resource > self.owner.max_resource:
                    self.owner.resource = self.owner.max_resource
            item.picked()