from random import uniform


def enter_stage(self, animation_data_pool):
    """run once when stage start or character just get created"""
    from engine.character.character import BodyPart

    # Grab only animation sprite that the character can use
    self.animation_data_pool = animation_data_pool[self.char_id]
    self.animation_pool = animation_data_pool[self.char_id]
    exist_part = []  # list to remove unused body parts from loop entirely
    for animation in self.animation_pool.values():
        for frame in animation["r_side"]:
            for part, data in frame.items():
                if data and part not in exist_part:
                    exist_part.append(part)

    self.body_parts = {key: value for key, value in self.body_parts.items() if key in exist_part}
    self.body_parts = {
        key: BodyPart(self, key) if not any(ext in key for ext in ("weapon",)) else BodyPart(self, key,
                                                                                             can_hurt=False)
        for key, value in self.body_parts.items()}

    # adjust layer
    if self.player_control:  # player character get priority in sprite showing
        self.base_layer = int(self.layer_id * self.body_size * 1000000000)
    else:
        if self.invincible:  # invincible character has lower layer priority
            self.base_layer = int(self.layer_id * self.body_size * 1000)
        else:
            self.base_layer = int(self.layer_id * self.body_size * 1000000)
    self.dead_layer = self.base_layer * 10000
    for part in self.body_parts.values():
        part.owner_layer = self.base_layer
        part.dead_layer = self.dead_layer

    # Add character to list
    self.battle.all_team_character[self.team].add(self)
    if not self.invincible:  # not add to list if can't take damage
        for team in self.battle.all_team_enemy:
            if team != self.team:
                self.battle.all_team_enemy[team].add(self)
                if self.team != 0:  # team 0 is not part of condition check:
                    self.battle.all_team_enemy_check[team].add(self)
                for part in self.body_parts.values():
                    self.battle.all_team_enemy_part[team].add(part)

    if not self.battle.city_mode:
        self.near_enemy = sorted({key: key.base_pos.distance_to(self.base_pos) for key in
                                  self.enemy_list}.items(), key=lambda item: item[1])  # sort the closest enemy
        self.near_ally = sorted(
            {key: key.base_pos.distance_to(self.base_pos) for key in self.ally_list}.items(),
            key=lambda item: item[1])  # sort the closest friend
        if self.near_enemy:
            self.nearest_enemy = self.near_enemy[0][0]
            self.nearest_enemy_distance = self.near_enemy[0][1]
        if self.near_ally:
            self.nearest_ally = self.near_ally[0][0]
            self.nearest_ally_distance = self.near_ally[0][1]

        self.moveset_view = {key: tuple(value.items()) for key, value in self.moveset.items()}

        if "arrive" in self.arrive_condition:  # start with arrive animation
            self.combat_state = "Combat"
            if self.nearest_enemy:
                self.x_momentum = self.nearest_enemy.base_pos[0] - self.base_pos[0]
            else:
                self.x_momentum = uniform(-1000, 1000)
            self.current_action = self.arrive_command_action
            if "fly" in self.arrive_condition:
                self.current_action = self.arrive_fly_command_action

    if self.base_pos[1] < self.ground_pos:  # start in air position
        self.position = "Air"

    self.pick_animation()
