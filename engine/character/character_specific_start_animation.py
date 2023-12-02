def nayedien_start(self, *args):
    if "moveset" in self.current_action:
        if self.current_moveset and "Weak" in self.current_moveset["Buttons"]:  # weak move increase combat state
            self.special_combat_state = int(self.current_moveset["Move"][-1])
    elif self.current_action:  # any action that is not in moveset will reset special combat state
        self.special_combat_state = 0


animation_start_dict = {"Nayedien": nayedien_start}
