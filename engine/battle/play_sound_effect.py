from pygame.mixer import Sound, find_channel


def play_sound_effect(self, sound, effect_volume, shake=False):
    sound_effect = find_channel()
    if sound_effect:
        sound_effect.set_volume(effect_volume[0], effect_volume[1])
        sound_effect.play(Sound(sound))
    if shake:
        self.screen_shake_value += shake
