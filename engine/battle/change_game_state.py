from types import MethodType


def change_game_state(self, new_state):
    self.game_state = new_state
    self.state_process = MethodType(self.process_list[new_state], self)
    if new_state != "battle":
        self.player_character_select_band.reset()  # reset rubberband select ui
