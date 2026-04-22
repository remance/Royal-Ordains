from engine.grandactor.grandactor import GrandActor
from engine.utils.common import clean_object


def change_active_commander_actor(self, new_commander_char_id):
    self.commander_id = new_commander_char_id

    # remove previous actor
    self.grand.grand_actor_updater.remove(self.commander_actor.grand_faction_actor_circle)
    self.grand.grand_camera_object_drawer.remove(self.commander_actor.grand_faction_actor_circle)
    clean_object(self.commander_actor.grand_faction_actor_circle)

    self.grand.grand_actor_updater.remove(self.commander_actor)
    self.grand.grand_camera_object_drawer.remove(self.commander_actor)
    clean_object(self.commander_actor)

    self.commander_actor = GrandActor(self.commander_id, self, self.faction)
