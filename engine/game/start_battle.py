import gc

from pygame.mixer import music


def start_battle(self, mission):
    # self.error_log.write("\n Map: " + str(self.map_selected) + "\n")
    self.loading_screen("start")

    music.stop()

    self.battle.prepare_new_stage(mission, {})
    result = self.battle.run_game()  # run next scene
    self.battle.exit_battle()  # run exit battle for previous one

    music.play()
    gc.collect()  # collect no longer used object in previous battle from memory

    # Finish battle, check for next one
    self.battle.change_game_state("battle")  # reset battle game state when end

    # save_profile = self.save_data.save_profile
    # print(save_profile)

    # save_profile["playtime"] += self.battle.play_time
    # save_profile["total kills"] += sum(self.battle.player_kill.values())
    # save_profile["total damages"] += sum(self.battle.player_damage.values())
    # for player, value in self.battle.player_kill.items():  # check for update for all active players to update state
    #     character = self.game.player_char_select[player]["character"]
    #     if character not in save_profile["kills"]:
    #         save_profile["kills"][character] = 0
    #     save_profile["kills"][character] += value

    # self.save_data.make_save_file(path_join(self.main_dir, "save", "game.dat"),
    #                               save_profile)

    # for memory leak checking
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
