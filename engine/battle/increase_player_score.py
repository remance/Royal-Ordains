def increase_player_score(self, score):
    self.stage_score += score
    if self.stage_score >= self.last_resurrect_stage_score:
        self.last_resurrect_stage_score += self.last_resurrect_stage_score * 2
        self.reserve_resurrect_stage_score += 1
