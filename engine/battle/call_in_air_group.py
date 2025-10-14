def call_in_air_group(self, team, groups, pos):
    delay = 0.1
    for group_index in groups:
        for character in self.team_stat[team]["air_group"][group_index]:
            if not character.broken and character.alive:
                character.enter_delay = delay
                character.issue_commander_order(("attack", pos))
                delay += 0.2
