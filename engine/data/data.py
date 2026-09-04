class GameData:
    def __init__(self):
        from engine.game.game import Game
        self.game = Game.game
        self.main_dir = Game.main_dir
        self.data_dir = Game.data_dir
        self.font_dir = Game.font_dir
        self.localisation = Game.localisation
        self.screen_scale = Game.screen_scale
        self.screen_scale_width = Game.screen_scale_width
        self.screen_scale_height = Game.screen_scale_height
