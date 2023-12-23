def increase_player_score(self, score):
    self.mission_score += score
    self.total_score += score
    if self.mission_score >= self.last_resurrect_mission_score:
        self.last_resurrect_mission_score += self.last_resurrect_mission_score * 2
        self.reserve_resurrect_mission_score += 1
