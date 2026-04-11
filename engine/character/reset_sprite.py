from engine.constants import Collision_Grid_Y_Per_Scene

max_grid_y_range = tuple(range(Collision_Grid_Y_Per_Scene + 1))


def reset_sprite(self):
    self.image = self.current_animation_direction["sprite"]
    offset = self.current_animation_direction["offset"]
    offset_pos = self.pos
    if offset:
        offset_pos = self.pos - offset
    self.rect = self.image.get_rect(midbottom=offset_pos)


def battle_reset_sprite(self):
    # grid check does not check pass existing stage
    reset_sprite(self)
    rect = self.rect
    grid_left = int(rect.topleft[0] / self.collision_grid_width)
    if grid_left < 0:
        grid_left = 0
    grid_right = int(rect.topright[0] / self.collision_grid_width) + 1
    if grid_right > self.last_grid:
        grid_right = self.last_grid
    grid_range_x = set(range(grid_left, grid_right))

    grid_top = int(rect.topleft[1] / self.collision_grid_height)
    grid_bottom = int(rect.bottomleft[1] / self.collision_grid_height) + 1
    if grid_top < Collision_Grid_Y_Per_Scene:
        if grid_bottom > Collision_Grid_Y_Per_Scene:
            grid_bottom = Collision_Grid_Y_Per_Scene
        if grid_top < 0:
            grid_top = 0
    else:  # character that somehow exists lower than bottom of the screen, ignored for collision
        grid_top = 0
        grid_bottom = 0
    grid_range_y = set(range(grid_top, grid_bottom))

    if self.grid_range_x != grid_range_x or self.grid_range_y != grid_range_y:
        no_longer_in_grid_x = grid_range_x.difference(self.grid_range_x)
        for team, team_grid in self.all_team_enemy_collision_grids.items():
            if team != self.team:
                for grid_x in no_longer_in_grid_x:  # remove from no longer in grid
                    for grid_y in max_grid_y_range:
                        team_grid[grid_y][grid_x].remove(self)
                    team_grid[-1][grid_x].remove(self)
                if not self.invincible and grid_range_y:
                    # skip invincible character and those with sprite outside of screen
                    for grid_x in grid_range_x:
                        if grid_x not in self.grid_range_x:
                            for grid_y in grid_range_y:
                                team_grid[grid_y][grid_x].add(self)
                            team_grid[-1][grid_x].add(self)
        self.grid_range_x = grid_range_x
        self.grid_range_y = grid_range_y
    self.mask = self.current_animation_direction["mask"]
