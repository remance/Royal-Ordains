def reset_sprite(self):
    self.image = self.current_animation_direction["sprite"]
    offset = self.current_animation_direction["offset"]
    self.offset_pos = self.pos
    if offset:
        self.offset_pos = self.pos - (offset[0], offset[1])
    self.rect = self.image.get_rect(midbottom=self.offset_pos)


def battle_reset_sprite(self):
    # grid check does not check pass existing stage
    reset_sprite(self)
    grid_left = int(self.rect.topleft[0] / self.collision_grid_width)
    if grid_left < 0:
        grid_left = 0
    grid_right = int(self.rect.topright[0] / self.collision_grid_width) + 1
    if grid_right > self.last_grid:
        grid_right = self.last_grid
    grid_range = range(grid_left, grid_right)
    if self.grid_range != grid_range:
        no_longer_in_grid = set(grid_range).difference(self.grid_range)
        for team, team_grid in self.all_team_enemy_collision_grids.items():
            if team != self.team:
                for grid in no_longer_in_grid:  # remove from no longer in grid
                    team_grid[grid].remove(self)
                if not self.invincible:
                    for grid in grid_range:
                        if grid not in self.grid_range:
                            team_grid[grid].add(self)
        self.grid_range = grid_range

    self.mask = self.current_animation_direction["mask"]
