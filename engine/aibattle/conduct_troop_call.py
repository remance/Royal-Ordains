from random import uniform, randint, choice

troop_class_to_call = {"attack_melee": ("light_melee", "medium_melee"),
                       "defend_melee": ("medium_melee", "heavy_melee"),
                       "melee_cavalry": ("medium_cavalry", "heavy_cavalry"),
                       "range_cavalry": ("light_cavalry",),
                       "attack_range": ("light_range", "medium_range", "heavy_range"),
                       "defend_range": ("siege", "support", "heavy_range")}


def conduct_troop_call(self):
    """Conduct troop call based on info and commander personality"""
    # commander = self.commander
    current_info = self.current_info
    if self.team == 1:
        leader_call_cooldown = self.battle.team1_call_leader_cooldown_reinforcement
        troop_call_cooldown = self.battle.team1_call_troop_cooldown_reinforcement
    else:
        leader_call_cooldown = self.battle.team2_call_leader_cooldown_reinforcement
        troop_call_cooldown = self.battle.team2_call_troop_cooldown_reinforcement

    current_supply = self.team_stat["supply_resource"]

    # plan for troop related
    troop_available_to_call = [item for index, item in enumerate(self.team_stat["troop_call_list"]) if
                               index not in troop_call_cooldown and current_supply >= item[2]]
    leader_available_to_call = [index for index, item in enumerate(self.team_stat["leader_call_list"]) if
                                index not in leader_call_cooldown and current_supply >= item[2]]

    troop_class_available_to_call = {index: self.character_list[item[0]]["Class"] for index, item in
                                     enumerate(troop_available_to_call)}
    check_troop_class = tuple(set(troop_class_available_to_call.values()))

    troop_not_available_to_call = [item for item in self.team_stat["troop_call_list"] if
                                   item not in troop_available_to_call]
    leader_not_available_to_call = [item for item in self.team_stat["leader_call_list"] if
                                    item not in leader_available_to_call]

    call_now = True

    if self.current_info:
        if "future_supply" in self.current_info:
            if current_info["total_power_comparison"] * uniform(0.5, 1.1) < (
                    (current_supply + self.current_info["future_supply"]) / sum(
                    self.current_info["enemy_supply"])) * uniform(0.5, 1.25):
                # higher power with more supply than enemy will make AI likely to reserve supply
                call_now = False

    if call_now:
        if troop_available_to_call or leader_available_to_call:
            roulette = {0: None}
            if "light_melee" in check_troop_class or "medium_melee" in check_troop_class:
                roulette[
                    next(reversed(roulette)) + self.commander_attack_melee_prefer + randint(1, 10)] = "attack_melee"
            if "medium_melee" in check_troop_class or "heavy_melee" in check_troop_class or "heavy_range" in check_troop_class:
                roulette[
                    next(reversed(roulette)) + self.commander_defence_melee_prefer + randint(1, 10)] = "defend_melee"
            if "medium_cavalry" in check_troop_class or "heavy_cavalry" in check_troop_class:
                roulette[
                    next(reversed(roulette)) + self.commander_cavalry_melee_prefer + randint(1, 10)] = "melee_cavalry"
            if "light_cavalry" in check_troop_class:
                roulette[
                    next(reversed(roulette)) + self.commander_cavalry_range_prefer + randint(1, 10)] = "range_cavalry"
            if "light_range" in check_troop_class or "medium_range":
                roulette[next(reversed(roulette)) + self.commander_range_prefer + randint(1, 10)] = "attack_range"
            if "siege" in check_troop_class or "support" in check_troop_class:
                roulette[next(reversed(roulette)) + self.commander_siege_prefer + randint(1, 10)] = "defend_range"
            if leader_available_to_call:
                roulette[next(reversed(roulette)) + self.commander_leader_prefer + randint(1, 10)] = "leader"
            roulette_key = tuple(roulette.keys())
            what_to_call = roulette[
                min(roulette_key, key=lambda x: abs(x - randint(roulette_key[0], roulette_key[-1])))]
            if what_to_call:
                if what_to_call == "leader":
                    self.call_reinforcement(self.team, "leader", choice(leader_available_to_call))
                else:
                    class_to_call = troop_class_to_call[what_to_call]
                    list_to_call = [key for key, value in troop_class_available_to_call.items() if
                                    value in class_to_call]
                    if list_to_call:
                        self.call_reinforcement(self.team, "troop",
                                                choice(list_to_call))

    # print(self.team_stat)
    # print(self.team_stat["troop_call_list"], self.team_stat["leader_call_list"])
    # print(troop_available_to_call, leader_available_to_call)

    if current_info:
        if "own_air_group" in current_info:
            air_bomber_available_to_call = list(current_info["own_air_group"][False]["bomber"].keys()) + list(
                current_info["own_air_group"][False]["fighter"].keys())
            air_bomber_active = list(current_info["own_air_group"][True]["bomber"].keys()) + list(
                current_info["own_air_group"][True]["fighter"].keys())

            air_interceptor_available_to_call = list(current_info["own_air_group"][False]["interceptor"].keys()) + list(
                current_info["own_air_group"][False]["fighter"].keys())
            air_interceptor_active = list(current_info["own_air_group"][True]["interceptor"].keys()) + list(
                current_info["own_air_group"][True]["fighter"].keys())

            air_to_call = []
            if air_bomber_available_to_call and self.commander_air_prefer >= uniform(0, 50):
                for air_group in air_bomber_available_to_call:
                    if self.aggressive > uniform(0, 10):
                        air_to_call.append(air_group)

                if air_interceptor_available_to_call and self.commander_air_prefer >= uniform(0, 10):
                    # consider sending interceptor to go with bombers
                    for air_group in tuple(air_interceptor_available_to_call):
                        if self.aggressive > uniform(0, 10):
                            air_to_call.append(air_group)
                            air_interceptor_available_to_call.remove(air_group)

            if "enemy_air_group" in current_info and True in current_info["enemy_air_group"]:
                # enemy has active air group consider sending interceptor
                if air_interceptor_available_to_call and self.commander_air_prefer >= uniform(0, 10):
                    # consider sending interceptor to go with bombers
                    for air_group in tuple(air_interceptor_available_to_call):
                        if self.defensive > uniform(0, 10):
                            air_to_call.append(air_group)
                            air_interceptor_available_to_call.remove(air_group)

                if air_bomber_active:
                    # consider retreat bomber
                    send_back = 0.1 * self.defensive
                    if not air_interceptor_active:
                        send_back += 0.3 * self.defensive
                        if not air_interceptor_available_to_call:
                            send_back += 0.5 * self.defensive
                    else:  # compare power of own and enemy active interceptors
                        send_back += (current_info["enemy_air_group"][True]["interceptor"]["power"] -
                                      current_info["own_air_group"][True]["interceptor"]["power"])
                    if send_back > uniform(0, 10):
                        # call for retreat of bombers
                        for air_group in self.air_group:
                            for character in air_group:
                                if character.alive and character.active:
                                    character.issue_commander_order(("back", character.start_pos))

            elif air_interceptor_available_to_call and self.commander_air_prefer >= uniform(0, 10):
                # stupid commander randomly send interceptor
                for air_group in tuple(air_interceptor_available_to_call):
                    if self.defensive >= uniform(0, 10):
                        air_to_call.append(air_group)
                        air_interceptor_available_to_call.remove(air_group)

            if air_to_call:
                self.battle.call_in_air_group(self.team, air_to_call, self.team_stat["start_pos"])
    # print(air_available_to_call)
