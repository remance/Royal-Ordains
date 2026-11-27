def character_die(self, character, retreat=False):
    self.group_character.remove(character)

    # return supply when die or retreat, summon does not give supply
    if not self.is_summon:
        if retreat:
            # manage to retreat mean return some supply but not give any to enemy
            self.battle.team_state[self.team]["supply_reserve"] += self.supply * 0.5
        else:
            self.battle.team_state[self.team]["supply_reserve"] += self.supply * 0.5
            self.battle.team_state[self.enemy_team]["supply_reserve"] += self.supply * 0.25
