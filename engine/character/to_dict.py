@property
def character_to_dict(self) -> dict:
    return {"ID": self.game_id, "team": self.team,
            "Commander": self.commander_id, "army_followers": self.army_followers,
            "Supply": self.supply, "Max Supply": self.max_supply, "custom_preset_id": self.custom_preset_id,
            "grand_state": {"activity": self.activity, "enable_resupply": self.enable_resupply,
                            "enable_assemble": self.enable_assemble, "base_pos": self.base_pos,
                            "current_region": self.current_region, },
            }


@property
def battle_character_to_dict(self) -> dict:
    character_to_dict(self)
    return {
            }


@property
def air_character_to_dict(self) -> dict:
    return {
            }


@property
def sub_character_to_dict(self) -> dict:
    return {"ID": self.game_id, "faction": self.faction, "team": self.team,
            "Commander": self.commander_id, "army_followers": self.army_followers,
            "Supply": self.supply, "Max Supply": self.max_supply, "custom_preset_id": self.custom_preset_id,
            "grand_state": {"activity": self.activity, "enable_resupply": self.enable_resupply,
                            "enable_assemble": self.enable_assemble, "base_pos": self.base_pos,
                            "current_region": self.current_region, },
            }