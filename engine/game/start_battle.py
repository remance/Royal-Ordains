import gc
import random
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
    # for _ in range(100):
    #     new_custom_equip = tuple(self.generate_custom_equipment((gear_type_list)[random.randint(0, 6)], "Standard").items())
    #     self.save_data.save_profile["character"][1]["storage"][new_custom_equip] = 1
    self.battle.prepare_new_stage(chapter, mission, stage, players, scene=scene)
    next_battle = self.battle.run_game()  # run next stage
    self.battle.exit_battle()  # run exit battle for previous one

    music.play()
    gc.collect()  # collect no longer used object in previous battle from memory

    # Finish battle, check for next one
    self.battle.change_game_state("battle")  # reset battle game state when end

    save_profile = self.save_data.save_profile

    if next_battle is True and str(int(stage) + 1) not in self.preset_map_data[chapter][mission]:  # need to use is True
        # finish all stage in the mission, update save data of the game first before individual save
        if int(save_profile["game"]["chapter"]) < int(chapter):
            save_profile["game"]["chapter"] = chapter
            save_profile["game"]["mission"] = mission
        elif int(save_profile["game"]["mission"]) < int(mission):
            save_profile["game"]["mission"] = mission

        for player, slot in self.profile_index.items():  # check for update for all active players to update state
            if self.player_char_selectors[player].mode != "empty":
                save_profile["character"][slot]["playtime"] += self.battle.play_time
                save_profile["character"][slot]["total scores"] += self.battle.stage_score[self.battle.player_team[player]]
                save_profile["character"][slot]["total golds"] += self.battle.stage_gold[self.battle.player_team[player]]
                save_profile["character"][slot]["total kills"] += self.battle.player_kill[player]
                save_profile["character"][slot]["boss kills"] += self.battle.player_boss_kill[player]
                save_profile["character"][slot]["last save"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

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
                        reward_list["one"][follower] = 1
                        if follower not in save_profile["character"][slot]["follower list"]:
                            save_profile["character"][slot]["follower list"].append(follower)
                        if follower not in save_profile["game"]["unlock"]["character"]:
                            save_profile["game"]["unlock"]["character"].append(follower)

                # Choice reward, can be obtained multiple time for gold and items
                if self.battle.decision_select.selected:
                    mission_str = chapter + "." + mission + "." + stage
                    choice = self.battle.decision_select.selected
                    if mission_str in save_profile["character"][slot]["story choice"]:
                        # get previous choice instead regardless of main profile choice here
                        choice = save_profile["character"][slot]["story choice"][mission_str]
                    choice_reward = self.choice_stage_reward[choice][chapter][mission][stage]

                    if mission_str not in save_profile["character"][slot]["story choice"]:  # one time reward and check
                        save_profile["character"][slot]["story choice"][mission_str] = choice
                        if save_profile["character"][slot] == self.battle.main_story_profile:
                            event_queue_data = save_profile["character"][slot]["interface event queue"]
                            if int(chapter) < 3:  # civil war level
                                change = str(self.battle.cal_civil_war())
                                sound_name = "War+1"
                                if choice == "no":
                                    sound_name = "War-1"
                                war_level = self.localisation.grab_text(("ui", "civilwar" + change))
                                event_queue_data["inform"].append((self.localisation.grab_text(("ui", "civil_war_level")) + ": " + war_level +
                                                                   "(" + change + ")", sound_name))
                            if "Court Change" in choice_reward and choice_reward["Court Change"]:
                                event_queue_data["court"] |= choice_reward["Court Change"]
                            event_queue_data["mission"].append((chapter, mission))

                        for follower in choice_reward["Follower Reward"]:
                            reward_list["choice"][follower] = 1
                            if follower not in save_profile["character"][slot]["follower list"]:
                                save_profile["character"][slot]["follower list"].append(follower)
                            if follower not in save_profile["game"]["unlock"]["character"]:
                                save_profile["game"]["unlock"]["character"].append(follower)

                        for item in choice_reward["Unique Gear Reward"]:
                            # unique gear that only gave out once in first win and only one can exist
                            if item not in save_profile["character"][slot]["storage"]:
                                save_profile["character"][slot]["storage"][item] = 1
                                save_profile["character"][slot]["storage_new"].append(item)
                            reward_list["choice"][item] = 1

                    for item in choice_reward["Item Reward"]:
                        item_num = choice_reward["Item Reward"][item]
                        if item in save_profile["character"][slot]["storage"]:
                            save_profile["character"][slot]["storage"][item] += item_num
                        else:
                            save_profile["character"][slot]["storage"][item] = item_num
                            save_profile["character"][slot]["storage_new"].append(item)
                        reward_list["choice"][item] = item_num

                    if choice_reward["Gold Reward"]:
                        reward_list["choice"]["gold"] = choice_reward["Gold Reward"]
                        save_profile["character"][slot]["total golds"] += choice_reward["Gold Reward"]

                # Multiple time rewards
                for item in self.battle_map_data.stage_reward[chapter][mission]["Item Reward"]:
                    item_num = self.battle_map_data.stage_reward[chapter][mission]["Item Reward"][item]
                    if item in save_profile["character"][slot]["storage"]:
                        save_profile["character"][slot]["storage"][item] += item_num
                    else:
                        save_profile["character"][slot]["storage"][item] = item_num
                        save_profile["character"][slot]["storage_new"].append(item)
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
                    new_custom_equip = tuple(self.generate_custom_equipment(gear_type, rarity).items())
                    save_profile["character"][slot]["storage"][new_custom_equip] = 1
                    save_profile["character"][slot]["storage_new"].append(new_custom_equip)
                    reward_list["multi"][new_custom_equip] = 1

                self.player_char_interfaces[player].add_profile(save_profile["character"][slot])
                self.player_char_interfaces[player].reward_list = reward_list
                self.player_char_interfaces[player].change_mode("reward")
                self.battle.change_game_state("reward")
                self.battle.add_ui_updater(self.battle.player_char_base_interfaces[player],
                                           self.battle.player_char_interfaces[player])

    self.write_all_player_save()

    self.save_data.make_save_file(path_join(self.main_dir, "save", "game.dat"),
                                  save_profile["game"])

    players = {key: save_profile["character"][self.profile_index[key]]["character"] for key, value in
               self.player_char_select.items() if value}

    self.battle.decision_select.selected = None  # reset decision here instead of in battle method
    self.battle.city_mode = False  # reset battle city mode so char interface not allow switching other modes when quit
    if next_battle is True:  # finish stage, continue to next one
        if str(int(stage) + 1) in self.preset_map_data[chapter][mission]:  # has next stage
            self.start_battle(chapter, mission, str(int(stage) + 1), players=players)
        else:
            self.start_battle(self.battle.main_story_profile["chapter"],
                              self.battle.main_story_profile["mission"], "0", players=players, scene="throne")

    elif next_battle == "training":  # start training ground
        self.start_battle(self.battle.main_story_profile["chapter"], self.battle.main_story_profile["mission"],
                          "training", players=players)
    elif next_battle and not any(i.isdigit() for i in next_battle):  # city stage go to specific city scene
        self.start_battle(self.battle.main_story_profile["chapter"], self.battle.main_story_profile["mission"],
                          "0", players=players, scene=next_battle)
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
