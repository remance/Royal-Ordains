def cal_civil_war(self):
    score = 0
    for story_choice in self.main_story_profile["story choice"].values():
        if story_choice == "yes":
            score += 1
        else:
            score -= 1
    return score
