from random import choice, uniform

from pygame.sprite import spritecollide

from engine.character.character import Character
from engine.drop.drop import Drop
from engine.uibattle.uibattle import DamageNumber


def drop_collide_check(self):
    collide_list = spritecollide(self, self.battle.all_team_drop[self.team], False)
    for item in collide_list:
        if not item.pickable_timer and (not item.stat["Specific Receiver"] or
                                        self.owner.char_id == item.stat["Specific Receiver"]):
            # can pick this drop
            if item.stat["Health"]:
                self.owner.health += item.stat["Health"] * self.owner.item_effect_modifier
                if self.owner.health > self.owner.base_health:
                    self.owner.health = self.owner.base_health
                DamageNumber(str(int(item.stat["Health"])), self.rect.midtop, False, "health")
            if item.stat["Resource"]:
                self.owner.resource += item.stat["Resource"] * self.owner.item_effect_modifier
                if self.owner.resource > self.owner.base_resource:
                    self.owner.resource = self.owner.base_resource
                DamageNumber(str(int(item.stat["Resource"])), self.rect.midbottom, False, "resource")
            if item.stat["Status"]:
                for effect in item.stat["Status"]:
                    self.owner.apply_status(self.owner, effect)
            if item.stat["Gold"]:
                self.battle.stage_gold[self.owner.team] += item.stat["Gold"] * self.owner.gold_drop_modifier
                if self.owner.money_score:
                    self.battle.increase_team_score(self.owner.team, item.stat["Gold"])
                if self.owner.money_resource:
                    self.owner.resource += item.stat["Gold"] / 100
                    if self.owner.resource > self.owner.base_resource:
                        self.owner.resource = self.owner.base_resource
            if item.stat["Revive"]:
                self.owner.resurrect_count += item.stat["Revive"] * self.owner.item_effect_modifier
                DamageNumber("+" + str(int(item.stat["Revive"])), self.rect.midtop, False, "revive")
            if item.stat["Property"]:
                for item2 in item.stat["Property"]:
                    if "random" in item2:
                        drop_list = tuple(Character.default_item_drop_table.keys())
                        # create random item from default drop table when picked, all item have same chance
                        if "+" in item2:  # multiple item
                            for item3 in range(int(item2.split("+")[-1])):
                                Drop(item.base_pos, choice(drop_list), self.owner.team,
                                     momentum=(uniform(-200, 200), (uniform(150, 350))))
                        else:
                            Drop(item.base_pos, choice(drop_list), self.owner.team,
                                 momentum=(uniform(-200, 200), (uniform(150, 350))))

            item.picked()
