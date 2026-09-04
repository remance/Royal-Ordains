from engine.grandarmyactor.grandarmyactor import GrandArmyActor

from engine.utils.common import clean_object


def change_active_commander_actor(self, new_commander_char_id):
    self.commander_id = new_commander_char_id

    # change commander actor
    self.commander_actor.change_team_state()

