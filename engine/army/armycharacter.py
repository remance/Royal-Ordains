import uuid


class ArmyCharacter:
    character_list = None
    grand = None

    def __init__(self, char_id):
        self.char_id = char_id
        self.game_id = str(uuid.uuid1())
