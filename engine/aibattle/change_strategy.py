def change_strategy(self):
    effect_list = self.battle.stat_data.effect_list

    self.own_strategy_type = {"weather": set(), "ally": set(), "enemy": set(), "summon": set(),
                              "cure": set(), "clarity": set()}

    for strategy in self.team_state["strategy_cooldown"]:
        stat = self.strategy_list[strategy]
        if stat["Power"] or stat["Enemy Status"]:  # attack/summon strategy to use at enemy
            self.own_strategy_type["enemy"].add(strategy)
        if stat["Summon"] or (stat["Damage Effects"] and
                              any(["summon" in effect_list[item[0]]["Property"] for item in stat["Damage Effects"]])):
            self.own_strategy_type["summon"].add(strategy)
        if stat["Status"]:
            if ("Cure" in stat["Status"] or "Clarity" in stat["Status"]) and len(stat["Status"]) == 1:
                # keep cure/clarity only strategy completely separate from buff strategy
                if "Cure" in stat["Status"]:
                    self.own_strategy_type["cure"].add(strategy)
                    self.has_cure_strategy = True
                if "Clarity" in stat["Status"]:
                    self.own_strategy_type["clarity"].add(strategy)
                    self.has_clarity_strategy = True
            else:  # any buff strategy
                self.own_strategy_type["ally"].add(strategy)

        if "weather" in stat["Property"]:
            self.own_strategy_type["weather"].add(strategy)

    self.enemy_strategy = tuple(self.battle.team_state[self.enemy_team]["strategy_cooldown"].keys())
    self.enemy_strategy_type = {"ally": set(), "enemy": set()}
    for strategy in self.enemy_strategy:
        stat = self.strategy_list[strategy]
        if stat["Power"] or stat["Enemy Status"]:
            self.enemy_strategy_type["enemy"].add(strategy)
        if stat["Status"]:
            self.enemy_strategy_type["ally"].add(strategy)
