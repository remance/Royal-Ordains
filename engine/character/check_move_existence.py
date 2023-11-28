def check_move_existence(self):
    """find next moveset that can continue from previous one first if exist, interrupt animation with found"""
    if self.continue_moveset:  # continue from previous move
        if self.stoppable_frame:
            for move in self.continue_moveset:
                if tuple(self.moveset_command_key_input[-len(move):]) == move:
                    self.interrupt_animation = True
                    self.current_moveset = self.continue_moveset[move]
                    if "Next Move" in self.continue_moveset[move]:
                        self.continue_moveset = self.continue_moveset[move]["Next Move"]
                    else:
                        self.continue_moveset = None
                    return True

    # not continue move or not found with new input
    if "run" in self.current_action and ((self.slide_attack and "weak" in self.current_action) or
                                         (self.tackle_attack and "strong" in self.current_action)):  # run moveset
        move_name = "Slide"
        if self.moveset_command_key_input[-1] == "Strong":
            move_name = "Tackle"
        self.current_moveset = self.moveset[self.position][move_name]
    else:
        for move in self.moveset[self.position]:
            if tuple(self.moveset_command_key_input[-len(move):]) == move:
                self.current_moveset = self.moveset[self.position][move]
                if "Next Move" in self.current_moveset:  # check for next move combo
                    self.continue_moveset = self.current_moveset["Next Move"]
                return True
    return False
