import glob
import os

from pygame.mixer import Sound

from engine.data.datastat import GameData
from engine.utils.data_loading import filename_convert_readable as fcv


class SoundData(GameData):
    def __init__(self):
        GameData.__init__(self)

        # load sound effect
        self.sound_effect_pool = {}
        dir_path = os.path.join(self.data_dir, "sound", "effect")
        for file in os.listdir(dir_path):
            if file.endswith(".ogg"):  # read ogg file only
                file_name = file.split(".")[0]
                if file_name[-1].isdigit() and file_name[-2] == "_":  # variation for same sound effect
                    file_name = file_name[:-2]

                file_name = fcv(file_name)

                if file_name not in self.sound_effect_pool:
                    self.sound_effect_pool[file_name] = [os.path.join(dir_path, file)]
                else:
                    self.sound_effect_pool[file_name].append(os.path.join(dir_path, file))

        for file_name in self.sound_effect_pool:  # convert to tuple with pygame Sound object inside
            self.sound_effect_pool[file_name] = tuple([Sound(item) for item in self.sound_effect_pool[file_name]])

        # load music
        self.music_pool = glob.glob(os.path.join(self.data_dir, "sound", "music", "*.ogg"))
        self.music_pool = {item.split("\\")[-1].replace(".ogg", ""): item for
                           item in self.music_pool}
        # self.music_pool = {item.split("\\")[-1].replace(".ogg", ""): Sound(item) for
        #                    item in self.music_pool}
