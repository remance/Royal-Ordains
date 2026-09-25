from engine.army.army import Army
from engine.grandarmyactor.grandarmyactor import GrandArmyActor


def create_new_army(self, faction_army_value, army, index="new", sort=True, no_assemble=False):
    """Create new army that did not exist before"""
    if index == "new":
        faction_army_value.append(None)
        index = -1
    army_faction = army["Faction"]
    if no_assemble:  # deploy from starting new campaign data, no assembling required
        army_followers = {"leader": [[], [], []],
                          "troop": [[], [], [],
                                    [], []],
                          "air": [[], [], [],
                                  [], []],
                          "retinue": [[], [], []]}
        for header in ("Leader 1", "Leader 2", "Leader 3", "Troop 1", "Troop 2", "Troop 3", "Troop 4",
                       "Troop 5", "Air 1", "Air 2", "Air 3", "Air 4", "Air 5", "Retinue 1", "Retinue 2", "Retinue 3"):
            follower_type = header.split(" ")[0].lower()
            follower_index = int(header.split(" ")[1]) - 1
            character = army[header]
            if character:
                army_followers[follower_type][follower_index] = [character, True]
        assembling = {}
    else:  # deploy from existing army (saved game loading) or reserve (saved preset)
        army_followers = army["army_followers"]
        assembling = army["assembling"]
    faction_army_value[index] = Army(army["ID"], army_faction,
                                     self.character_list[army["Commander"]]["Culture"],
                                     army["Commander"], army_followers,
                                     supply=army["Supply"], max_supply=army["Max Supply"],
                                     current_region=army["Region"], travelling=army["Route"],
                                     assembling_followers=assembling)

    GrandArmyActor(faction_army_value[index], army_faction)

    if sort and army_faction == self.player_faction:  # update player ui
        self.sort_player_army_list()
