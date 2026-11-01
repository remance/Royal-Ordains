from random import uniform, choice

from engine.uibattle.uibattle import CharacterSpeechBox


def ai_speak(self, event):
    CharacterSpeechBox(self, choice(self.ai_speak_list[event]))
    self.battle.ai_battle_speak_timer = uniform(10, 60)
