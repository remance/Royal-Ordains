import gc

from pygame.mixer import music


def start_battle(self, chapter, mission, stage, players=None):
    # self.error_log.write("\n Map: " + str(self.map_selected) + "\n")
    self.loading_screen("start")

    music.unload()
    music.set_endevent(self.SONG_END)
    self.battle.prepare_new_stage(chapter, mission, stage, players)
    next_stage = self.battle.run_game()
    music.unload()
    music.set_endevent(self.SONG_END)
    music.load(self.music_list[0])
    music.play(-1)
    gc.collect()  # collect no longer used object in previous battle from memory

    if next_stage:
        if stage + 1 in self.preset_map_data[chapter][mission]:  # has next stage
            self.start_battle(chapter, mission, stage + 1, players=players)
        else:  # start next mission
            self.start_battle(chapter, mission + 1, 1, players=players)

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
