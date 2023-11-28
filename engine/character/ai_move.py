from random import choice, randint

from pygame import Vector2

follow_distance = 100
stay_formation_distance = 1


def stationary_ai(self, dt):
    pass


def helper_ai(self, dt):
    if self.battle.player_1_battle_cursor.pos != self.old_cursor_pos and \
            self.battle.decision_select not in self.battle.realtime_ui_updater:
        self.old_cursor_pos = Vector2(self.battle.player_1_battle_cursor.pos)
        self.ai_movement_timer = 0.1
        self.command_pos = self.battle.base_cursor_pos

    elif self.ai_movement_timer >= 2 or not self.ai_movement_timer:
        self.ai_movement_timer = 0
        self.command_pos = Vector2(self.battle.camera_pos[0], 140 * self.screen_scale[1])
        # print(self.battle.camera_pos, self.base_pos, self.ai_movement_timer)

    if self.pos.distance_to(self.command_pos) > 50:
        if self.pos.distance_to(self.command_pos) > 50:
            if abs(self.pos[0] - self.command_pos[0]) > 40:
                self.x_momentum = self.command_pos[0] - self.pos[0]
            if abs(self.pos[1] - self.command_pos[1]) > 40:
                self.y_momentum = self.pos[1] - self.command_pos[1]

            if not self.current_action and not self.command_action:
                if self.pos.distance_to(self.command_pos) > 300:
                    self.command_action = self.run_command_action | {"x_momentum": True}
                else:
                    self.command_action = self.walk_command_action
        else:
            self.base_pos = self.command_pos.copy()
            self.pos = Vector2((self.base_pos[0] * self.screen_scale[0],
                                self.base_pos[1] * self.screen_scale[1]))

            for part in self.body_parts.values():
                part.re_rect()
    else:
        self.x_momentum = 0
        self.y_momentum = 0


def common_ai(self, dt):
    if self.ai_movement_timer > self.end_ai_movment_timer:
        self.ai_movement_timer = 0
    if not self.current_action and not self.command_action and not self.ai_movement_timer:
        # if not self.nearest_enemy or self.nearest_enemy[1] > self.max_attack_range:
        # walk randomly when not attack
        if not self.leader:
            self.ai_movement_timer = 0.1
            self.x_momentum = randint(1, 50) * self.walk_speed / 20 * choice((-1, 1))
            self.command_action = self.walk_command_action | {"x_momentum": self.x_momentum}
        else:
            leader_distance = self.base_pos.distance_to(self.leader.base_pos)
            if leader_distance < 400:  # not too far from leader, walk randomly
                self.ai_movement_timer = 0.1
                self.x_momentum = randint(1, 50) * self.walk_speed / 20 * choice((-1, 1))
                self.command_action = self.walk_command_action | {"x_momentum": self.x_momentum}
            else:  # catch up with leader
                self.x_momentum = ((self.leader.base_pos[0] - self.base_pos[0]) / 10) + randint(-30, 30)
                self.command_action = self.walk_command_action | {"x_momentum": self.x_momentum}


def common_boss_ai(self, dt):
    if self.ai_movement_timer > 3:
        self.ai_movement_timer = 0
    if not self.current_action and not self.command_action and not self.ai_movement_timer:
        # if not self.nearest_enemy or self.nearest_enemy[1] > self.max_attack_range:
        # walk randomly when not attack
        if not self.leader:
            self.ai_movement_timer = 0.1
            self.x_momentum = self.walk_speed * choice((-1, 1))
            self.command_action = self.walk_command_action | {"x_momentum": self.x_momentum}
        else:
            leader_distance = self.base_pos.distance_to(self.leader.base_pos)
            if leader_distance < 400:  # not too far from leader, walk randomly
                self.ai_movement_timer = 0.1
                self.x_momentum = self.walk_speed * choice((-1, 1))
                self.command_action = self.walk_command_action | {"x_momentum": self.x_momentum}
            else:  # catch up with leader
                self.x_momentum = ((self.leader.base_pos[0] - self.base_pos[0]) / 10) + randint(-30, 30)
                self.command_action = self.walk_command_action | {"x_momentum": self.x_momentum}


def pursue_range_ai(self, dt):
    if not self.current_action and not self.command_action:
        if self.nearest_enemy:
            if self.nearest_enemy[1] > self.ai_max_attack_range:
                # run to enemy within attack range
                angle = self.set_rotate(self.nearest_enemy[0].base_pos)
                if angle > 0:
                    self.x_momentum = self.run_speed / 20
                else:
                    self.x_momentum = -self.run_speed / 20
                self.command_action = self.run_command_action


def pursue_melee_ai(self, dt):
    if not self.current_action and not self.command_action:
        if self.nearest_enemy:
            if self.nearest_enemy[1] > self.base_body_mass:
                # run to enemy
                angle = self.set_rotate(self.nearest_enemy[0].base_pos)
                if angle > 0:
                    self.x_momentum = self.run_speed / 20
                else:
                    self.x_momentum = -self.run_speed / 20
                self.command_action = self.walk_command_action


def sentry_ai(self, dt):
    if not self.current_action and not self.command_action:
        if self.nearest_enemy:
            if self.nearest_enemy[1] > self.ai_max_attack_range and self.base_pos.distance_to(
                    self.assign_pos) > follow_distance:
                # no enemy nearby, run to assigned pos
                angle = self.set_rotate(self.assign_pos)
                if angle > 0:
                    self.x_momentum = self.run_speed / 20
                else:
                    self.x_momentum = -self.run_speed / 20
                self.command_action = self.run_command_action


ai_move_dict = {"default": stationary_ai, "helper": helper_ai, "common_melee": common_ai, "common_range": common_ai,
                "pursue_melee": common_ai, "pursue_range": pursue_range_ai, "sentry": sentry_ai,
                "trap": stationary_ai, "bigta": common_boss_ai, "guard_melee": common_ai}
