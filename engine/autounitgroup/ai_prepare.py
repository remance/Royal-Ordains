from operator import itemgetter

from engine.utils.common import empty_method


def base_ai_prepare(self):
    """No need to create grid range for auto unit since number of unit in battle should be low enough"""
    self.nearest_enemy = None
    self.nearest_enemy_distance = None
    self.nearest_enemy_pos = None
    self.furthest_enemy = None
    self.furthest_enemy_distance = None
    self.furthest_enemy_pos = None
    self.nearest_ally = None
    self.nearest_ally_pos = None
    self.nearest_ally_distance = None


def ground_ai_prepare(self):
    """find distance of enemies and allies within range"""
    base_ai_prepare(self)
    near_enemy = [enemy for enemy in self.all_ground_enemy if not enemy.invisible and not enemy.no_target]
    self.get_near_enemy(near_enemy)

    if self.ai_ally_max_effect_range:
        base_pos = self.base_pos
        ai_ally_max_effect_range = self.ai_ally_max_effect_range
        self.near_ally = sorted({key: key.base_pos.distance_to(base_pos) for key in self.ally_list}.items(),
                                key=itemgetter(1))  # sort the closest friend
        self.near_ally = [key for key in self.near_ally if key[1] <= ai_ally_max_effect_range and key[0] is not self]
        if self.near_ally:
            self.nearest_ally = self.near_ally[0][0]
            self.nearest_ally_pos = self.near_ally[0][0].base_pos
            self.nearest_ally_distance = self.near_ally[0][1]


def sub_character_ai_prepare(self):
    """Use distance of enemies and allies within range from the main character"""
    if self.main_character:
        main_character = self.main_character
        self.nearest_enemy = main_character.nearest_enemy
        self.nearest_enemy_distance = main_character.nearest_enemy_distance
        self.nearest_enemy_pos = main_character.nearest_enemy_pos
        self.nearest_ally = main_character.nearest_ally
        self.nearest_ally_pos = main_character.nearest_ally_pos
        self.nearest_ally_distance = main_character.nearest_ally_distance
        self.near_enemy = main_character.near_enemy
        self.near_ally = main_character.near_ally  # sort the closest friend
        self.furthest_enemy = main_character.furthest_enemy
        self.furthest_enemy_distance = main_character.furthest_enemy_distance
        self.furthest_enemy_pos = main_character.furthest_enemy_pos


def interceptor_ai_prepare(self):
    """Check only for air enemy"""
    base_ai_prepare(self)
    near_enemy = [enemy for enemy in self.all_air_enemy if not enemy.invisible and not enemy.no_target]
    self.get_near_enemy(near_enemy)


def bomber_ai_prepare(self):
    """Check only for ground enemy"""
    base_ai_prepare(self)
    near_enemy = [enemy for enemy in self.all_ground_enemy if not enemy.invisible and not enemy.no_target]
    self.get_near_enemy(near_enemy)


def fighter_ai_prepare(self):
    """Check for both ground and air enemy"""
    base_ai_prepare(self)
    near_enemy = ([enemy for enemy in self.all_ground_enemy if not enemy.invisible and not enemy.no_target] +
                  [enemy for enemy in self.all_air_enemy if not enemy.invisible and not enemy.no_target])
    self.get_near_enemy(near_enemy)


auto_ai_prepare_dict = {"default": empty_method, "melee": ground_ai_prepare, "range": ground_ai_prepare,
                        "mix": ground_ai_prepare, "flank": ground_ai_prepare, "nice": ground_ai_prepare,
                        "curious": ground_ai_prepare, "territorial": ground_ai_prepare, "trap": ground_ai_prepare,
                        "interceptor": interceptor_ai_prepare, "fighter": fighter_ai_prepare,
                        "bomber": bomber_ai_prepare, "sub": sub_character_ai_prepare}