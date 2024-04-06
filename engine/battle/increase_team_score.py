def increase_team_score(self, team, score):
    self.stage_score[team] += score
    if self.stage_score[team] >= self.last_resurrect_stage_score[team]:
        self.last_resurrect_stage_score[team] += self.last_resurrect_stage_score[team] * 2
        self.reserve_resurrect_stage_score[team] += 1
