import gc
from datetime import datetime
from os.path import join as path_join
from random import choices

from pygame.mixer import Channel

gear_reward_quantity_list = (1, 2, 3, 4, 5)
gear_reward_quantity_score = (50, 30, 20, 7, 3)
gear_type_list = ("weapon 1", "weapon 2", "head", "chest", "arm", "leg", "accessory")


def start_battle(self, chapter, mission, stage, players=None, scene=None):
    # self.error_log.write("\n Map: " + str(self.map_selected) + "\n")
    self.loading_screen("start")

    Channel(0).stop()
    self.battle.prepare_new_stage(chapter, mission, stage, players, scene=scene)
    next_battle = self.battle.run_game()  # run next stage
    self.battle.exit_battle()  # run exit battle for previous one

    # Finish battle, check for next one
    Channel(0).play(self.music_pool["menu"])
    gc.collect()  # collect no longer used object in previous battle from memory

    if stage + 1 not in self.preset_map_data[chapter][mission] and next_battle is True:
        # finish mission, update save data of the game first before individual save
        if self.save_data.save_profile["game"]["chapter"] < chapter:
            self.save_data.save_profile["game"]["chapter"] = chapter
            self.save_data.save_profile["game"]["mission"] = mission
        elif self.save_data.save_profile["game"]["mission"] < mission:
            self.save_data.save_profile["game"]["mission"] = mission
        self.save_data.make_save_file(path_join(self.main_dir, "save", "game.dat"),
                                      self.save_data.save_profile["game"])

        for player, slot in self.profile_index.items():  # check for update for all active players to update state
            if self.player_char_selectors[player].mode != "empty":
                # check for update for all active players to level up
                if self.save_data.save_profile["character"][slot]["chapter"] == chapter and \
                        self.save_data.save_profile["character"][slot]["mission"] == mission:
                    # update for player with this mission as last progress
                    if mission + 1 in self.preset_map_data[chapter]:
                        # update save state to next mission of the current chapter
                        self.save_data.save_profile["character"][slot]["mission"] = mission + 1
                    elif chapter + 1 in self.preset_map_data[chapter]:
                        # complete all chapter stage, update to next chapter
                        self.save_data.save_profile["character"][slot]["chapter"] = chapter + 1
                        self.save_data.save_profile["character"][slot]["mission"] = 1

                    # One time rewards
                    self.save_data.save_profile["character"][slot]["character"]["Status Remain"] += \
                        self.stage_reward[chapter][mission]["Status"]
                    self.save_data.save_profile["character"][slot]["character"]["Skill Remain"] += \
                        self.stage_reward[chapter][mission]["Skill"]

                    for follower in self.stage_reward[chapter][mission]["Follower Reward"]:
                        if follower not in self.save_data.save_profile["character"][slot]["follower list"]:
                            self.save_data.save_profile["character"][slot]["follower list"].append(follower)

                    if self.battle.decision_select.selected:  # choice reward
                        mission_str = str(chapter) + "." + str(mission) + "." + str(stage)
                        choice = self.battle.decision_select.selected
                        self.save_data.save_profile["character"][slot]["story choice"][
                            mission_str] = choice
                        for follower in self.choice_stage_reward[choice][chapter][mission][stage]["Follower Reward"]:
                            if follower not in self.save_data.save_profile["character"][slot]["follower list"]:
                                self.save_data.save_profile["character"][slot]["follower list"].append(follower)
                        for item in self.choice_stage_reward[choice][chapter][mission][stage]["Item Reward"]:
                            if item in self.save_data.save_profile["character"][slot]["storage"]:
                                self.save_data.save_profile["character"][slot]["storage"][item] += 1
                            else:
                                self.save_data.save_profile["character"][slot]["storage"][item] = 1
                        for item in self.choice_stage_reward[choice][chapter][mission][stage]["Gear Reward"]:
                            if item in self.save_data.save_profile["character"][slot]["storage"][item]:
                                self.save_data.save_profile["character"][slot]["storage"][item] += 1
                            else:
                                self.save_data.save_profile["character"][slot]["storage"][item] = 1
                        self.save_data.save_profile["character"][slot]["total golds"] += \
                            self.choice_stage_reward[choice][chapter][mission][stage]["Gold Reward"]

                # Multiple time rewards
                for item in self.battle_map_data.stage_reward[chapter][mission]["Item Reward"]:
                    if item in self.save_data.save_profile["character"][slot]["storage"]:
                        self.save_data.save_profile["character"][slot]["storage"][item] += 1
                    else:
                        self.save_data.save_profile["character"][slot]["storage"][item] = 1
                self.save_data.save_profile["character"][slot]["total golds"] += \
                    self.battle_map_data.stage_reward[chapter][mission]["Gold Reward"]
                quantity_roll = choices(gear_reward_quantity_list, gear_reward_quantity_score)[0]
                for i in range(quantity_roll):  # create random custom equipment
                    gear_type = choices(gear_type_list)[0]
                    rarity = choices(tuple(self.battle_map_data.stage_reward[chapter][mission]["Gear Reward"].keys()),
                                     tuple(
                                         self.battle_map_data.stage_reward[chapter][mission]["Gear Reward"].values()))[
                        0]
                    # new_gear = self.generate_custom_equipment(gear_type, rarity)  # TODO finish this
                    # for key in self.character_data.gear_mod_list:

    for player, slot in self.profile_index.items():
        save_profile = self.save_data.save_profile["character"][self.profile_index[player]]  # reset data for interface
        self.player_char_interfaces[player].add_profile(save_profile)
        self.save_data.save_profile["character"][slot]["last save"] = datetime.now().strftime(
            "%d/%m/%Y %H:%M:%S")

    write_all_player_save(self)

    self.battle.decision_select.selected = None  # reset decision here instead of in battle method
    self.battle.city_mode = False  # reset battle city mode so char interface not allow switching other modes when quit

    if next_battle is True:  # finish stage, continue to next one
        if stage + 1 in self.preset_map_data[chapter][mission]:  # has next stage
            self.start_battle(chapter, mission, stage + 1, players=players)
        elif mission + 1 in self.preset_map_data[chapter]:  # proceed next mission, go to city throne map
            self.start_battle(chapter, mission + 1, 0, players=players, scene="throne")
        elif chapter + 1 in self.preset_map_data[chapter]:  # complete all chapter stage, go to next chapter
            self.start_battle(chapter + 1, 1, 0, players=players, scene="throne")
        else:
            self.start_battle(chapter, mission, 0, players=players, scene="throne")
    elif type(next_battle) is str:  # city stage go to specific scene
        self.start_battle(chapter, mission, 0, players=players, scene=next_battle)
    elif next_battle is not False:  # start specific mission
        self.start_battle(chapter, next_battle, 1, players=players)

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


def write_all_player_save(self):
    for player, slot in self.profile_index.items():  # save data for all active player before start next mission
        if self.player_char_selectors[player].mode != "empty":
            self.save_data.make_save_file(path_join(self.main_dir, "save", str(slot) + ".dat"),
                                          self.battle.all_story_profiles[player])
