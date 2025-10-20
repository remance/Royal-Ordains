from operator import itemgetter
from functools import lru_cache

from engine.constants import Default_Screen_Width, Collision_Grid_Per_Scene

grid_width = Default_Screen_Width / Collision_Grid_Per_Scene


@lru_cache(maxsize=2000)
def find_grid_range(base_pos_x, max_enemy_range_check, last_grid):
    grid_left = int((base_pos_x - max_enemy_range_check) / grid_width)
    if grid_left < 0:
        grid_left = 0
    grid_right = int((base_pos_x + max_enemy_range_check) / grid_width) + 1
    if grid_right > last_grid:
        grid_right = last_grid
    return range(grid_left, grid_right)


def get_near_enemy(self, near_enemy):
    self.near_enemy = sorted({key: abs(key.base_pos.distance_to(self.base_pos) - key.sprite_width) for key in near_enemy}.items(),
                             key=itemgetter(1))  # sort the closest enemy
    if self.near_enemy:
        self.nearest_enemy = self.near_enemy[0][0]
        self.nearest_enemy_distance = self.near_enemy[0][1]
        self.nearest_enemy_pos = self.nearest_enemy.base_pos
    self.near_enemy = [key for key in self.near_enemy if key[1] <= self.ai_max_effect_range]


def ai_prepare(self):
    """find distance of enemies and allies within range"""
    follower_ai_prepare(self)

    self.nearest_ally = None
    self.nearest_ally_distance = None
    self.near_ally = sorted({key: key.base_pos.distance_to(self.base_pos) for key in self.ally_list}.items(),
                            key=itemgetter(1))  # sort the closest friend
    if self.near_ally:
        self.nearest_ally = self.near_ally[0][0]
        self.nearest_ally_distance = self.near_ally[0][1]
    self.near_ally = [key for key in self.near_ally if key[1] <= self.ai_max_effect_range]


def follower_ai_prepare(self):
    """find distance of enemies within range"""
    self.nearest_enemy = None
    self.nearest_enemy_distance = None
    self.nearest_enemy_pos = None
    grid_range = find_grid_range(self.base_pos[0], self.max_enemy_range_check, self.last_grid)
    near_enemy = [enemy for grid in grid_range for enemy in self.ground_enemy_collision_grids[grid] if
                  not enemy.invisible and not enemy.no_target]
    self.get_near_enemy(near_enemy)


def sub_character_ai_prepare(self):
    """Use distance of enemies and allies within range from the main character"""
    self.nearest_enemy = self.main_character.nearest_enemy
    self.nearest_enemy_distance = self.main_character.nearest_enemy_distance
    self.nearest_enemy_pos = self.main_character.nearest_enemy_pos
    self.nearest_ally = self.main_character.nearest_ally
    self.nearest_ally_distance = self.main_character.nearest_ally_distance
    self.near_enemy = self.main_character.near_enemy
    self.near_ally = self.main_character.near_ally  # sort the closest friend


def interceptor_ai_prepare(self):
    """Check only for air enemy"""
    self.nearest_enemy = None
    self.nearest_enemy_distance = None
    self.nearest_enemy_pos = None
    grid_range = find_grid_range(self.base_pos[0], self.max_enemy_range_check, self.last_grid)
    near_enemy = [enemy for grid in grid_range for enemy in self.air_enemy_collision_grids[grid] if
                  not enemy.invisible and not enemy.no_target]
    self.get_near_enemy(near_enemy)


def bomber_ai_prepare(self):
    """Check only for ground enemy"""
    self.nearest_enemy = None
    self.nearest_enemy_distance = None
    self.nearest_enemy_pos = None
    grid_range = find_grid_range(self.base_pos[0], self.max_enemy_range_check, self.last_grid)
    near_enemy = [enemy for grid in grid_range for enemy in self.ground_enemy_collision_grids[grid] if
                  not enemy.invisible and not enemy.no_target]
    self.get_near_enemy(near_enemy)


def fighter_ai_prepare(self):
    """Check for both ground and air enemy"""
    self.nearest_enemy = None
    self.nearest_enemy_distance = None
    self.nearest_enemy_pos = None
    grid_range = find_grid_range(self.base_pos[0], self.max_enemy_range_check, self.last_grid)
    near_enemy = [enemy for grid_list in (self.ground_enemy_collision_grids, self.air_enemy_collision_grids) for grid
                  in grid_range for enemy in grid_list[grid] if not enemy.invisible and not enemy.no_target]
    self.get_near_enemy(near_enemy)
