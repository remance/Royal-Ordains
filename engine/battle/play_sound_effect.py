from pygame.mixer import find_channel


def play_sound_effect(self, sound, effect_volume):
    sound_effect_channel = find_channel()
    if sound_effect_channel:
        sound_effect_channel.set_volume(effect_volume[0], effect_volume[1])
        sound_effect_channel.play(sound)
