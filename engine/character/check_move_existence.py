def check_move_existence(self):
    """find next moveset that can continue from previous one first if exist, interrupt animation with found"""
    if self.continue_moveset:  # continue from previous move
        if self.stoppable_frame:
            for move in self.continue_moveset:
                if tuple(self.moveset_command_key_input[-len(move):]) == move:
                    self.interrupt_animation = True
                    self.command_moveset = self.continue_moveset[move]
                    if "Next Move" in self.continue_moveset[move]:
                        self.continue_moveset = self.continue_moveset[move]["Next Move"]
                    else:
                        self.continue_moveset = None
                    return True

    # not continue move or not found with new input
    if self.position in self.moveset:
        for move in self.moveset[self.position]:
            if tuple(self.moveset_command_key_input[-len(move):]) == move:
                self.command_moveset = self.moveset[self.position][move]
                return True
    return False


def nayedien_check_move_existence(self):
    if self.continue_moveset:  # continue from previous move
        if self.stoppable_frame:
            for move in self.continue_moveset:
                if tuple(self.moveset_command_key_input[-len(move):]) == move:
                    self.interrupt_animation = True
                    self.command_moveset = self.continue_moveset[move]
                    if "Next Move" in self.continue_moveset[move]:  # find more next move if any
                        self.continue_moveset = self.continue_moveset[move]["Next Move"]
                    else:
                        self.continue_moveset = None
                    return True

    # not continue move or not found with new input
    if self.position in self.moveset:
        if self.special_combat_state and self.moveset_command_key_input[-1] in ("Weak", "Strong"):
            next_move = self.moveset[self.position][("Weak",)]
            for run in range(self.special_combat_state - 1):  # find next stage until reach current
                next_move = next_move["Next Move"][("Weak",)]
            if self.moveset_command_key_input[-1] == "Strong" and ("Strong",) in next_move["Next Move"]:
                # first strong attack can skip weak parent move
                self.command_moveset = next_move["Next Move"][("Strong",)]
                return True
            elif self.moveset_command_key_input[-1] == "Weak" and ("Weak",) in next_move["Next Move"]:
                # continue from weak of current state instead of new one
                self.command_moveset = next_move["Next Move"][("Weak",)]
                return True
        else:
            for move in self.moveset[self.position]:
                if tuple(self.moveset_command_key_input[-len(move):]) == move:
                    self.command_moveset = self.moveset[self.position][move]
                    return True
    return False


def training_moveset_existence_check(self):
    old_moveset = None
    if self.continue_moveset and self.stoppable_frame:
        old_moveset = self.current_moveset
    found_move = self.battle_check_move_existence()
    if self.player_control and found_move:
        move = [self.command_moveset, 5, old_moveset]
        self.battle.player_trainings[int(self.game_id[1])].combo_input.append(move)
    return found_move
