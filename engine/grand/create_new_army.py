from engine.army.army import Army
from engine.grandactor.grandactor import GrandActor


def create_new_army(self, faction_army_value, army, index="new", sort=True):
    """Create new army that did not exist before"""
    if index == "new":
        faction_army_value.append(None)
        index = -1
    army_faction = army["Faction"]
    faction_army_value[index] = Army(army["ID"], army_faction,
                                     self.character_list[army["Commander"]]["Culture"],
                                     army["Commander"],
                                     [army["Leader 1"], army["Leader 2"], army["Leader 3"]],
                                     [army["Troop 1"], army["Troop 2"], army["Troop 3"],
                                      army["Troop 4"], army["Troop 5"]],
                                     [army["Air 1"], army["Air 2"], army["Air 3"],
                                      army["Air 4"], army["Air 5"]],
                                     [army["Retinue 1"], army["Retinue 2"], army["Retinue 3"]],
                                     supply=army["Supply"], max_supply=army["Max Supply"],
                                     current_region=army["Region"], travelling=army["Route"])

    GrandActor(faction_army_value[index].commander_id, faction_army_value[index],
               army_faction)

    if sort and army_faction == self.player_faction:  # update player ui
        self.sort_player_army_list()
