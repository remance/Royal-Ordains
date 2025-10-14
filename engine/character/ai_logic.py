def ai_logic(self, dt):
    if self.ai_timer:
        self.ai_timer -= dt
        if self.ai_timer < 0:
            self.ai_timer = 0
    if self.ai_movement_timer:
        self.ai_movement_timer -= dt
        if self.ai_movement_timer < 0:
            self.ai_movement_timer = 0
    if not self.broken and "broken" not in self.commander_order:
        self.ai_combat()
        self.ai_move()
    else:
        self.ai_retreat()
