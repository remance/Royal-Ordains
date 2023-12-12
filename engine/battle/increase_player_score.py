def increase_player_score(self, score):
    self.player_score += score
    if self.player_score >= self.next_resurrect_mission_score:
        self.next_resurrect_mission_score += self.next_resurrect_mission_score * 2
        self.reserve_resurrect_mission_score += 1
