from engine.utils.common import clean_object


def erase(self):
    """Character erase entirely from game"""
    self.battle_camera.remove(self)

    for speech in self.battle.speech_boxes:
        if speech.character == self:  # kill any current speech
            speech.kill()
    self.battle.character_updater.remove(self)
    self.battle.all_characters.remove(self)
    clean_object(self)
    self.alive = False  # keep alive attribute to false in case it remain in enemy check of other characters
