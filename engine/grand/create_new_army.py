from engine.grandarmyactor.grandarmyactor import GrandArmyActor

from engine.army.army import Army


def create_new_army(self, faction_army_value, army, index="new", sort=True, no_assemble=False):
    """Create new army that did not exist before"""
    if index == "new":
        faction_army_value.append(None)
        index = -1
    army_faction = army["Faction"]
    if no_assemble:  # deploy from starting new campaign data
        leader_group = {army["Leader 1"]: 0, army["Leader 2"]: 0, army["Leader 3"]: 0}
        ground_group = {army["Troop 1"]: 0, army["Troop 2"]: 0, army["Troop 3"]: 0, army["Troop 4"]: 0,
                        army["Troop 5"]: 0}
        air_group = {army["Air 1"]: 0, army["Air 2"]: 0, army["Air 3"]: 0, army["Air 4"]: 0, army["Air 5"]: 0}
        retinue = {army["Retinue 1"]: 0, army["Retinue 2"]: 0, army["Retinue 3"]: 0}
    else:  # deploy from existing army (saved game loading) or converted reserve data (saved preset)
        leader_group = army["leader_group"]
        ground_group = army["ground_group"]
        air_group = army["air_group"]
        retinue = army["retinue"]
    faction_army_value[index] = Army(army["ID"], army_faction,
                                     self.character_list[army["Commander"]]["Culture"],
                                     army["Commander"], leader_group, ground_group, air_group, retinue,
                                     supply=army["Supply"], max_supply=army["Max Supply"],
                                     current_region=army["Region"], travelling=army["Route"])

    GrandArmyActor(faction_army_value[index], army_faction)

    if sort and army_faction == self.player_faction:  # update player ui
        self.sort_player_army_list()
