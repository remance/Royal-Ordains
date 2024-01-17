import gc
import os
from datetime import datetime

from pygame.mixer import music


def start_battle(self, chapter, mission, stage, players=None, scene=None):
    # self.error_log.write("\n Map: " + str(self.map_selected) + "\n")
    self.loading_screen("start")

    music.unload()
    music.set_endevent(self.SONG_END)
    self.battle.prepare_new_stage(chapter, mission, stage, players, scene=scene)
    next_battle = self.battle.run_game()  # run next stage
    # Finish battle, check for next one
    music.unload()
    music.set_endevent(self.SONG_END)
    music.load(self.music_list[0])
    music.play(-1)
    gc.collect()  # collect no longer used object in previous battle from memory

    if next_battle is True:  # finish stage, continue to next one
        if stage + 1 not in self.preset_map_data[chapter][mission]:
            # finish mission, update save data of the game first
            if self.save_data.save_profile["game"]["chapter"] < chapter:
                self.save_data.save_profile["game"]["chapter"] = chapter
                self.save_data.save_profile["game"]["mission"] = mission
            elif self.save_data.save_profile["game"]["mission"] < mission:
                self.save_data.save_profile["game"]["mission"] = mission
            self.save_data.make_save_file(os.path.join(self.main_dir, "save", "game.dat"),
                                          self.save_data.save_profile["game"])
            if self.battle.main_story_profile["chapter"] < chapter:
                self.battle.main_story_profile["chapter"] = chapter
                self.save_data.save_profile["game"]["mission"] = mission
            elif self.save_data.save_profile["game"]["mission"] < mission:
                self.save_data.save_profile["game"]["mission"] = mission

            for player, slot in self.profile_index.items():  # check for update for all active players to level up
                if self.player_char_selectors[player].mode != "empty":
                    # check for update for all active players to level up
                    if self.save_data.save_profile["character"][slot]["chapter"] == chapter and \
                            self.save_data.save_profile["character"][slot]["mission"] == mission:
                        self.save_data.save_profile["character"][slot]["mission"] = mission + 1
                        # add stat and skill point
                        self.save_data.save_profile["character"][slot]["Status Remain"] += \
                        self.battle_map_data.stage_level_up[chapter][mission]["Status"]
                        self.save_data.save_profile["character"][slot]["Skill Remain"] += \
                        self.battle_map_data.stage_level_up[chapter][mission]["Skill"]
                        self.save_data.save_profile["character"][slot]["last save"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        write_all_player_save(self)

        if stage + 1 in self.preset_map_data[chapter][mission]:  # has next stage
            self.start_battle(chapter, mission, stage + 1, players=players)
        elif mission + 1 in self.preset_map_data[chapter]:  # proceed next mission, go to city throne map
            self.start_battle(chapter, mission + 1, 0, players=players, scene="throne")
        elif chapter + 1 in self.preset_map_data[chapter]:  # complete all chapter stage, go to next chapter
            self.start_battle(chapter + 1, 1, 0, players=players, scene="throne")
        else:
            self.start_battle(chapter, mission, 0, players=players, scene="throne")
    elif next_battle == "city":
        write_all_player_save(self)

        self.start_battle(chapter, mission, 0, players=players, scene="throne")
    elif next_battle is not False:  # start specific mission
        write_all_player_save(self)

        self.start_battle(chapter, next_battle, 1, players=players)


def write_all_player_save(self):
    for player, slot in self.profile_index.items():  # save data for all active player before start next mission
        if self.player_char_selectors[player].mode != "empty":
            self.save_data.make_save_file(os.path.join(self.main_dir, "save", str(slot) + ".dat"),
                                          self.battle.all_story_profiles[player])

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
