from engine.utils.common import clean_object


def erase(self):
    """Character erase entirely from game"""
    self.battle_camera_drawer.remove(self)

    self.battle.battle_character_updater.remove(self)
    self.battle.all_battle_characters.remove(self)
    clean_object(self)
    self.alive = False  # keep alive attribute to false in case it remain in enemy check of other characters
