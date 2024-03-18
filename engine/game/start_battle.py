import gc
from datetime import datetime
from os.path import join as path_join
from random import choices

from pygame.mixer import music

gear_reward_quantity_list = (1, 2, 3, 4, 5)
gear_reward_quantity_score = (50, 30, 20, 7, 3)
gear_type_list = ("weapon 1", "weapon 2", "head", "chest", "arm", "leg", "accessory")


def start_battle(self, chapter, mission, stage, players=None, scene=None):
    # self.error_log.write("\n Map: " + str(self.map_selected) + "\n")
    self.loading_screen("start")

    music.stop()
    self.battle.prepare_new_stage(chapter, mission, stage, players, scene=scene)
    next_battle = self.battle.run_game()  # run next stage
    self.battle.exit_battle()  # run exit battle for previous one

    # Finish battle, check for next one
    music.play()
    gc.collect()  # collect no longer used object in previous battle from memory

    save_profile = self.save_data.save_profile

    if next_battle is True and str(int(stage) + 1) not in self.preset_map_data[chapter][mission]:  # need to use is True
        # finish mission, update save data of the game first before individual save
        if save_profile["game"]["chapter"] < chapter:
            save_profile["game"]["chapter"] = chapter
            save_profile["game"]["mission"] = mission
        elif save_profile["game"]["mission"] < mission:
            save_profile["game"]["mission"] = mission

        for player, slot in self.profile_index.items():  # check for update for all active players to update state
            if self.player_char_selectors[player].mode != "empty":
                reward_list = {"one": {}, "multi": {}, "choice": {}}

                # check for update for all active players to level up
                if save_profile["character"][slot]["chapter"] == chapter and \
                        save_profile["character"][slot]["mission"] == mission:
                    # update for player with this mission as last progress
                    if str(int(mission) + 1) in self.preset_map_data[chapter]:
                        # update save state to next mission of the current chapter
                        save_profile["character"][slot]["mission"] = str(int(mission) + 1)
                    elif str(int(chapter) + 1) in self.preset_map_data[chapter]:
                        # complete all chapter stage, update to next chapter
                        save_profile["character"][slot]["chapter"] = str(int(chapter) + 1)
                        save_profile["character"][slot]["mission"] = "1"

                    # One time rewards
                    if self.stage_reward[chapter][mission]["Status"]:
                        save_profile["character"][slot]["character"]["Status Remain"] += \
                            self.stage_reward[chapter][mission]["Status"]
                        reward_list["one"]["stat"] = self.stage_reward[chapter][mission]["Status"]
                    if self.stage_reward[chapter][mission]["Skill"]:
                        save_profile["character"][slot]["character"]["Skill Remain"] += \
                            self.stage_reward[chapter][mission]["Skill"]
                        reward_list["one"]["skill"] = self.stage_reward[chapter][mission]["Skill"]

                    for follower in self.stage_reward[chapter][mission]["Follower Reward"]:
                        reward_list["one"][follower] = "Recruitable"
                        if follower not in save_profile["character"][slot]["follower list"]:
                            save_profile["character"][slot]["follower list"].append(follower)
                        if follower not in save_profile["game"]["unlock"]["character"]:
                            save_profile["game"]["unlock"]["character"].append(follower)

                    # Choice reward
                    if self.battle.decision_select.selected:
                        mission_str = chapter + "." + mission + "." + stage
                        choice = self.battle.decision_select.selected
                        save_profile["character"][slot]["story choice"][
                            mission_str] = choice
                        for follower in self.choice_stage_reward[choice][chapter][mission][stage]["Follower Reward"]:
                            reward_list["choice"][follower] = "Recruitable"
                            if follower not in save_profile["character"][slot]["follower list"]:
                                save_profile["character"][slot]["follower list"].append(follower)
                            if follower not in save_profile["game"]["unlock"]["character"]:
                                save_profile["game"]["unlock"]["character"].append(follower)
                        for item in self.choice_stage_reward[choice][chapter][mission][stage]["Item Reward"]:
                            item_num = self.choice_stage_reward[choice][chapter][mission][stage]["Item Reward"][item]
                            if item in save_profile["character"][slot]["storage"]:
                                save_profile["character"][slot]["storage"][item] += item_num
                            else:
                                save_profile["character"][slot]["storage"][item] = item_num
                            reward_list["choice"][item] = item_num

                        for item in self.choice_stage_reward[choice][chapter][mission][stage]["Gear Reward"]:
                            item_num = self.choice_stage_reward[choice][chapter][mission][stage]["Gear Reward"][item]
                            if item in save_profile["character"][slot]["storage"][item]:
                                save_profile["character"][slot]["storage"][item] += item_num
                            else:
                                save_profile["character"][slot]["storage"][item] = item_num
                            reward_list["choice"][item] = item_num

                        reward_list["choice"]["gold"] = self.choice_stage_reward[choice][chapter][mission][stage][
                            "Gold Reward"]
                        save_profile["character"][slot]["total golds"] += \
                            self.choice_stage_reward[choice][chapter][mission][stage]["Gold Reward"]

                # Multiple time rewards
                for item in self.battle_map_data.stage_reward[chapter][mission]["Item Reward"]:
                    item_num = self.battle_map_data.stage_reward[chapter][mission]["Item Reward"][item]
                    if item in save_profile["character"][slot]["storage"]:
                        save_profile["character"][slot]["storage"][item] += item_num
                    else:
                        save_profile["character"][slot]["storage"][item] = item_num
                    reward_list["multi"][item] = item_num
                reward_list["multi"]["gold"] = self.battle_map_data.stage_reward[chapter][mission]["Gold Reward"]
                save_profile["character"][slot]["total golds"] += \
                    self.battle_map_data.stage_reward[chapter][mission]["Gold Reward"]
                quantity_roll = choices(gear_reward_quantity_list, gear_reward_quantity_score)[0]
                for i in range(quantity_roll):  # create random custom equipment
                    gear_type = choices(gear_type_list)[0]
                    rarity = choices(tuple(self.battle_map_data.stage_reward[chapter][mission]["Gear Reward"].keys()),
                                     tuple(
                                         self.battle_map_data.stage_reward[chapter][mission]["Gear Reward"].values()))[
                        0]
                    save_profile["storage"][self.generate_custom_equipment(gear_type, rarity)] = 1
                    reward_list["multi"][self.generate_custom_equipment(gear_type, rarity)] = 1

                self.player_char_interfaces[player].reward_list = reward_list
                self.player_char_interfaces[player].change_mode("reward")
                self.battle.game_state = "reward"

    for player, slot in self.profile_index.items():
        if self.player_char_selectors[player].mode != "empty":
            self.player_char_interfaces[player].add_profile(save_profile["character"][slot])
            save_profile["character"][slot]["last save"] = datetime.now().strftime(
                "%d/%m/%Y %H:%M:%S")

    self.write_all_player_save()

    self.save_data.make_save_file(path_join(self.main_dir, "save", "game.dat"),
                                  save_profile["game"])

    players = {key: save_profile["character"][self.profile_index[key]]["character"] for key, value in
               self.player_char_select.items() if value}

    self.battle.decision_select.selected = None  # reset decision here instead of in battle method
    self.battle.city_mode = False  # reset battle city mode so char interface not allow switching other modes when quit

    if next_battle is True:  # finish stage, continue to next one
        if stage + 1 in self.preset_map_data[chapter][mission]:  # has next stage
            self.start_battle(chapter, mission, str(int(stage) + 1), players=players)
        elif mission + 1 in self.preset_map_data[chapter]:  # proceed next mission, go to city throne map
            self.start_battle(chapter, str(int(mission) + 1), "0", players=players, scene="throne")
        elif chapter + 1 in self.preset_map_data[chapter]:  # complete all chapter stage, go to next chapter
            self.start_battle(str(int(chapter + 1)), "1", "0", players=players, scene="throne")
        else:
            self.start_battle(chapter, mission, "0", players=players, scene="throne")

    elif next_battle == "training":
        self.start_battle(chapter, mission, "training", players=players)
    elif not any(i.isdigit() for i in next_battle):  # city stage go to specific scene
        self.start_battle(chapter, mission, "0", players=players, scene=next_battle)
    elif next_battle is not False:  # start specific mission need to contain number
        self.start_battle(chapter, next_battle, "1", players=players)

    # for when memory leak checking
    # logging.warning(mem_top())
    # print(len(vars(self)))
    # print(len(gc.get_objects()))
    # self.error_log.write(str(new_gc_collect).encode('unicode_escape').decode('unicode_escape'))

    # print(vars(self))
    # from engine.character.character import Character
    # type_count = {}
    # for item in gc.get_objects():
    #     if type(item) not in type_count:
    #         type_count[type(item)] = 1
    #     else:
    #         type_count[type(item)] += 1
    # type_count = sorted({key: value for key, value in type_count.items()}.items(), key=lambda item: item[1],
    #                     reverse=True)
    # print(type_count)
    # print(item.current_animation)
    #     print(vars(item))
    # asdasd
    # except NameError:
    #     asdasdasd
    # except:
    #     pass
    # print(gc.get_referrers(self.unit_animation_pool))
