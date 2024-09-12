from random import uniform, choice

from engine.uibattle.uibattle import CharacterSpeechBox


def follower_talk(self, event):
    CharacterSpeechBox(self, choice(self.follower_speak[event]))
    self.battle.follower_talk_timer = uniform(10, 60)
