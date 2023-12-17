from pygame.sprite import spritecollide
from random import choice, randint

from engine.character.character import Character
from engine.drop.drop import Drop


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
            if item.stat["Gold"]:
                self.battle.player_gold += item.stat["Gold"]
                if self.owner.money_score:
                    self.battle.increase_player_score(item.stat["Gold"])
                if self.owner.money_resource:
                    self.owner.resource += item.stat["Gold"] / 100
                    if self.owner.resource > self.owner.max_resource:
                        self.owner.resource = self.owner.max_resource
            if item.stat["Revive"]:
                self.owner.resurrect_count += item.stat["Revive"]
            if item.stat["Property"]:
                for item2 in item.stat["Property"]:
                    if "random" in item2:
                        # create random item from default drop table when picked, all item have same chance
                        if "+" in item2:
                            Drop(item.base_pos, choice(Character.default_item_drop_table.keys()), self.onwer.team,
                                 momentum=(randint(-200, 200), (randint(150, 350))))
                        else:
                            for item3 in range(int(item2[-1])):
                                Drop(item.base_pos, choice(Character.default_item_drop_table.keys()), self.onwer.team,
                                     momentum=(randint(-200, 200), (randint(150, 350))))

            item.picked()
