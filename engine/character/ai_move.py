from random import choice, randint, uniform

from pygame import Vector2

follow_distance = 100
stay_formation_distance = 1


def stationary_ai(self):
    pass


def cinematic_ai(self):
    pass


def observer_ai(self):
    """Keep facing target"""
    if self.target.base_pos[0] >= self.base_pos[0]:
        self.new_angle = -90
    else:
        self.new_angle = 90


def helper_ai(self):
    """Movement AI for fairy helper, follow around cursor"""
    if self.battle.main_player_battle_cursor.pos != self.old_cursor_pos and \
            self.battle.decision_select not in self.battle.realtime_ui_updater:
        self.old_cursor_pos = Vector2(self.battle.main_player_battle_cursor.pos)
        self.ai_movement_timer = 3
        self.command_pos = self.battle.base_cursor_pos

    elif not self.ai_movement_timer:
        # go back to middle top of screen when idle
        self.command_pos = Vector2(self.battle.camera_pos[0], 140 * self.screen_scale[1])

    new_distance = self.pos.distance_to(self.command_pos)
    if new_distance > 50:
        if abs(self.pos[0] - self.command_pos[0]) > 40:
            self.x_momentum = self.command_pos[0] - self.pos[0]
        if abs(self.pos[1] - self.command_pos[1]) > 40:
            self.y_momentum = self.pos[1] - self.command_pos[1]
        if not self.current_action and not self.command_action:
            if new_distance > 300:
                self.command_action = self.run_command_action | {"x_momentum": True}
            else:
                self.command_action = self.walk_command_action
    else:
        self.x_momentum = 0
        self.y_momentum = 0


def common_ai(self):
    if not self.current_action and not self.command_action and not self.ai_movement_timer:
        # if not self.nearest_enemy or self.nearest_enemy[1] > self.max_attack_range:
        # walk randomly when not attack or inside stage lock
        self.ai_movement_timer = uniform(0.1, 3)
        self.x_momentum = uniform(0.1, 1.5) * self.walk_speed * choice((-1, 1))
        if (self.x_momentum < 0 and abs(self.base_pos[0] - self.battle.base_stage_start) < 50) or \
                (self.x_momentum > 0 and abs(self.base_pos[0] - self.battle.base_stage_end) < 50):
            # too close to corner move other way to avoid stuck
            self.x_momentum *= -1
        self.command_action = self.walk_command_action | {"x_momentum": True}


def move_city_ai(self):
    if not self.current_action and not self.command_action and not self.ai_movement_timer:
        # if not self.nearest_enemy or self.nearest_enemy[1] > self.max_attack_range:
        # walk randomly when not attack or inside stage lock
        self.ai_movement_timer = uniform(0.1, 5)
        self.x_momentum = uniform(0.1, 10) * self.city_walk_speed * choice((-1, 1))
        if (self.x_momentum < 0 and abs(self.base_pos[0] - self.battle.base_stage_start) < 50) or \
                (self.x_momentum > 0 and abs(self.base_pos[0] - self.battle.base_stage_end) < 50):
            # too close to corner move other way to avoid stuck
            self.x_momentum *= -1
        self.command_action = self.walk_command_action | {"x_momentum": True}


def follower_ai(self):
    if not self.current_action and not self.command_action and not self.ai_movement_timer:
        # if not self.nearest_enemy or self.nearest_enemy[1] > self.max_attack_range:
        # walk randomly when not attack or inside stage lock
        if (not self.leader or not self.leader.alive) or self.follow_command == "Free":  # random movement
            self.ai_movement_timer = uniform(0.1, 3)
            self.x_momentum = uniform(1, 50) * self.walk_speed / 20 * choice((-1, 1))
            self.command_action = self.walk_command_action | {"x_momentum": True}
        else:  # check for leader pos for follow
            if self.follow_command == "Follow":
                leader_distance = self.base_pos.distance_to(self.leader.base_pos)
                if leader_distance < 400:  # not too far from leader, walk randomly
                    self.ai_movement_timer = uniform(0.1, 3)
                    self.x_momentum = uniform(1, 50) * self.walk_speed / 20 * choice((-1, 1))
                    self.command_action = self.walk_command_action
                else:  # catch up with leader
                    self.x_momentum = ((self.leader.base_pos[0] - self.base_pos[0]) / 2) + uniform(-30, 30)
                    self.command_action = self.walk_command_action
            elif self.follow_command == "Attack":
                if self.nearest_enemy and self.nearest_enemy_distance > self.ai_max_attack_range:
                    self.x_momentum = ((self.nearest_enemy.base_pos[0] - self.base_pos[0]) / 2) + uniform(-30, 30)
                    self.command_action = self.walk_command_action


def pursue_ai(self):
    if not self.current_action and not self.command_action:
        if self.nearest_enemy:
            if self.nearest_enemy_distance > self.ai_max_attack_range:
                # run to enemy within attack range
                angle = self.set_rotate(self.nearest_enemy.base_pos)
                if angle > 0:
                    self.x_momentum = self.run_speed / 20
                else:
                    self.x_momentum = -self.run_speed / 20
                self.command_action = self.walk_command_action


def sentry_ai(self):
    if not self.current_action and not self.command_action:
        if self.nearest_enemy:
            if self.nearest_enemy_distance > self.ai_max_attack_range and self.base_pos.distance_to(
                    self.assign_pos) > follow_distance:
                # no enemy nearby, run to assigned pos
                angle = self.set_rotate(self.assign_pos)
                if angle > 0:
                    self.x_momentum = self.run_speed / 20
                else:
                    self.x_momentum = -self.run_speed / 20
                self.command_action = self.run_command_action


ai_move_dict = {"default": stationary_ai, "helper": helper_ai, "common": common_ai, "common_leader": common_ai,
                "pursue": pursue_ai, "sentry": sentry_ai, "follower": follower_ai,
                "trap": stationary_ai, "guard_melee": common_ai, "boss_cheer": observer_ai,
                "move_city_ai": move_city_ai}
