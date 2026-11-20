@property
def character_to_dict(self) -> dict:
    return {"game_id": self.game_id, "health": self.health,
            "resource": self.resource, "status_duration": self.status_duration,
            "moveset_cooldown": self.moveset_cooldown, "Max commander_order": self.commander_order,
            "base_pos": self.base_pos, "active": self.active,
            }


@property
def sub_character_to_dict(self) -> dict:
    return character_to_dict(self) | {"main_character_game_id": self.main_character.game_id}
