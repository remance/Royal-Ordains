import uuid


class General:
    character_list = None

    def __init__(self, char_id):
        self.char_id = char_id
        self.game_id = str(uuid.uuid1())
        self.start_health = 1
