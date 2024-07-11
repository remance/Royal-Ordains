def cal_follower_stat_with_chr(leader_chr, stat):
    return [item + (item * (leader_chr / 200)) + int(leader_chr / 5) for item in stat]


print(cal_follower_stat_with_chr(50, (17, 25, 25, 31, 18, 32, 48)))
