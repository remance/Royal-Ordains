def sort_dot_army_occupation(self, base_pos):
    self.dots_army_occupation[base_pos].sort(key=lambda x: x.power, reverse=True)
