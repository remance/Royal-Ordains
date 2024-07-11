from random import uniform, choice

from engine.uibattle.uibattle import CharacterSpeechBox


def follower_talk(self, event):
    CharacterSpeechBox(self, choice(self.follower_speak[event]), add_log=False)
    self.battle.follower_talk_timer = uniform(10, 60)
