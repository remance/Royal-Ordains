from pygame import Vector2, Surface, SRCALPHA
from pygame.transform import smoothscale

from engine.uimenu.uimenu import UIMenu


class UIGrand(UIMenu):
    def __init__(self, player_cursor_interact=True, has_containers=False):
        """
        Parent class for all battle menu user interface
        """
        from engine.grand.grand import Grand
        UIMenu.__init__(self, player_cursor_interact=player_cursor_interact, has_containers=has_containers)
        self.grand = Grand.grand
        self.cursor = Grand.cursor  # use battle cursor for battle ui


class YesNo(UIGrand):
    def __init__(self, images):
        UIGrand.__init__(self)
        self._layer = 5
        self.yes_image = images["yes"]
        self.no_image = images["no"]

        self.yes_zoom_animation_timer = 0
        self.no_zoom_animation_timer = 0

        self.image = Surface((self.yes_image.get_width() * 2.5, self.yes_image.get_height() * 1.5), SRCALPHA)
        self.base_image = self.image.copy()

        self.pos = Vector2(self.screen_size[0] / 2, 400 * self.screen_scale[1])
        yes_image_rect = self.yes_image.get_rect(midleft=(0, self.image.get_height() / 2))
        no_image_rect = self.no_image.get_rect(midright=(self.image.get_width(), self.image.get_height() / 2))
        self.image.blit(self.yes_image, yes_image_rect)
        self.image.blit(self.no_image, no_image_rect)
        self.base_image2 = self.image.copy()
        self.selected = None

        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt):
        yes_image_rect = self.yes_image.get_rect(midleft=(0, self.image.get_height() / 2))
        no_image_rect = self.no_image.get_rect(midright=(self.image.get_width(),
                                                         self.image.get_height() / 2))
        cursor_pos = (self.cursor.pos[0] - self.rect.topleft[0],
                      self.cursor.pos[1] - self.rect.topleft[1])
        if yes_image_rect.collidepoint(cursor_pos):
            if self.event_press:
                self.selected = "yes"
                return
            else:
                self.image = self.base_image.copy()
                self.no_zoom_animation_timer = 0
                if not self.yes_zoom_animation_timer:
                    self.yes_zoom_animation_timer = 0.01
                    yes_zoom_animation_timer = 1.01
                else:
                    self.yes_zoom_animation_timer += self.grand.true_dt / 5
                    yes_zoom_animation_timer = 1 + self.yes_zoom_animation_timer
                    if self.yes_zoom_animation_timer > 0.2:
                        yes_zoom_animation_timer = 1.2 - (self.yes_zoom_animation_timer - 0.2)
                        if self.yes_zoom_animation_timer > 0.4:
                            self.yes_zoom_animation_timer = 0

                yes_image = smoothscale(self.yes_image, (self.yes_image.get_width() * yes_zoom_animation_timer,
                                                         self.yes_image.get_height() * yes_zoom_animation_timer))
                yes_image_rect = yes_image.get_rect(midleft=(0, self.image.get_height() / 2))
                self.image.blit(yes_image, yes_image_rect)
                self.image.blit(self.no_image, no_image_rect)

        elif no_image_rect.collidepoint(cursor_pos):
            if self.event_press:
                self.selected = "no"
                return
            else:
                self.image = self.base_image.copy()
                self.yes_zoom_animation_timer = 0
                if not self.no_zoom_animation_timer:
                    self.no_zoom_animation_timer = 0.01
                    no_zoom_animation_timer = 1.01
                else:
                    self.no_zoom_animation_timer += self.grand.true_dt / 5
                    no_zoom_animation_timer = 1 + self.no_zoom_animation_timer
                    if self.no_zoom_animation_timer > 0.2:
                        no_zoom_animation_timer = 1.2 - (self.no_zoom_animation_timer - 0.2)
                        if self.no_zoom_animation_timer > 0.4:
                            self.no_zoom_animation_timer = 0

                no_image = smoothscale(self.no_image, (self.no_image.get_width() * no_zoom_animation_timer,
                                                       self.no_image.get_height() * no_zoom_animation_timer))
                no_image_rect = no_image.get_rect(midright=(self.image.get_width(), self.image.get_height() / 2))
                self.image.blit(no_image, no_image_rect)
                self.image.blit(self.yes_image, yes_image_rect)

        elif self.no_zoom_animation_timer or self.yes_zoom_animation_timer:
            self.no_zoom_animation_timer = 0
            self.yes_zoom_animation_timer = 0
            self.image = self.base_image2

# class PlayerGrandInteract(UIGrand):
#     def __init__(self):
#         self._layer = 9999999999999999999
#         UIBattle.__init__(self, player_cursor_interact=False)
#         self.battle_camera = self.battle.camera
#         self.selection_start_pos = Vector2()
#         self.current_pos = Vector2()
#         self.line_size = int(10 * self.screen_scale[0])
#         self.inner_line_size = int(20 * self.screen_scale[0])
#         if self.line_size < 1:
#             self.line_size = 1
#         self.image = None
#         self.rect = None
#         self.current_strategy_base_range = None
#         self.current_strategy_base_activate_range = None
#         self.current_strategy_range = None
#         self.current_strategy_activate_range = None
#         self.strategy_line_top = 500 * self.screen_scale[1]
#         self.strategy_line_bottom = 2160 * self.screen_scale[1]
#         self.strategy_line_width = int(20 * self.screen_scale[0])
#         self.strategy_line_inner_width = int(self.strategy_line_width / 2)
#         self.strategy_line_center = 900 * self.screen_scale[1]
#         self.show_strategy_activate_line = False
#
#     def reset(self):
#         self.current_pos = None
#         self.selection_start_pos = None
#         self.rect = None

# def update(self):
#     self.event_press = False
#     self.event_hold = False  # some UI differentiates between press release or holding, if not just use event
#     self.event_alt_press = False
#     self.event_alt_hold = True
#     self.show_strategy_activate_line = False
#     if self.battle.player_team:
#         if not self.cursor.mouse_over:
#             if self.cursor.is_alt_select_just_up:  # put alt (right) click first to prioritise it
#                 self.event_alt_press = True
#                 self.cursor.is_alt_select_just_up = False  # reset select button to prevent overlap interaction
#             elif self.cursor.is_alt_select_down:
#                 self.event_alt_hold = True
#                 self.cursor.is_alt_select_just_down = False  # reset select button to prevent overlap interaction
#             elif self.cursor.is_select_just_up:
#                 self.event_press = True
#                 self.cursor.is_select_just_up = False  # reset select button to prevent overlap interaction
#             elif self.cursor.is_select_down:
#                 self.event_hold = True
#                 self.cursor.is_select_just_down = False  # reset select button to prevent overlap interaction
#             else:  # no mouse activity
#                 if self.battle.player_selected_strategy:
#                     # draw activation line
#                     commander = self.battle.team_commander[self.battle.player_team]
#                     line_start = (commander.pos[0] - self.current_strategy_activate_range) - (
#                             self.battle.shown_camera_pos[0] - self.battle_camera.camera_w_center)
#                     line_end = (commander.pos[0] + self.current_strategy_activate_range) - (
#                             self.battle.shown_camera_pos[0] - self.battle_camera.camera_w_center)
#                     if line_start > 0:
#                         draw.line(self.battle.camera.image, (80, 120, 200),
#                                   (line_start, self.strategy_line_top),
#                                   (line_start, self.strategy_line_bottom), width=self.strategy_line_width)
#                         draw.line(self.battle.camera.image, (20, 70, 50),
#                                   (line_start, self.strategy_line_top),
#                                   (line_start, self.strategy_line_bottom), width=self.strategy_line_inner_width)
#                     if line_end > 0:
#                         draw.line(self.battle.camera.image, (80, 120, 200),
#                                   (line_end, self.strategy_line_top),
#                                   (line_end, self.strategy_line_bottom), width=self.strategy_line_width)
#                         draw.line(self.battle.camera.image, (20, 70, 50),
#                                   (line_end, self.strategy_line_top),
#                                   (line_end, self.strategy_line_bottom), width=self.strategy_line_inner_width)
#
#                     if not self.current_strategy_base_activate_range or \
#                             (abs(commander.base_pos[0] - self.battle.base_cursor_pos[0]) <
#                             self.current_strategy_base_activate_range):
#                         self.show_strategy_activate_line = True
#
#                         # draw strategy range if player cursor is within activation range, mean strategy can be used
#                         # or strategy has no activation range, which mean activate only from commander
#                         if not self.current_strategy_base_activate_range:
#                             pos_to_use = commander.pos[0]
#                         else:
#                             pos_to_use = self.battle.cursor_pos[0]
#                         line_start = (pos_to_use - self.current_strategy_range) - (
#                                 self.battle.shown_camera_pos[0] - self.battle_camera.camera_w_center)
#                         line_end = (pos_to_use + self.current_strategy_range) - (
#                                 self.battle.shown_camera_pos[0] - self.battle_camera.camera_w_center)
#                         if line_start > 0:
#                             draw.line(self.battle.camera.image, (120, 180, 80),
#                                       (line_start, self.strategy_line_top),
#                                       (line_start, self.strategy_line_bottom), width=self.strategy_line_width)
#                             draw.line(self.battle.camera.image, (70, 20, 50),
#                                       (line_start, self.strategy_line_top),
#                                       (line_start, self.strategy_line_bottom), width=self.strategy_line_inner_width)
#                         if line_end > 0:
#                             draw.line(self.battle.camera.image, (120, 180, 80),
#                                       (line_start, self.strategy_line_center),
#                                       (line_end, self.strategy_line_center), width=self.strategy_line_width)
#
#                             draw.line(self.battle.camera.image, (120, 180, 80),
#                                       (line_end, self.strategy_line_top),
#                                       (line_end, self.strategy_line_bottom), width=self.strategy_line_width)
#                             draw.line(self.battle.camera.image, (70, 20, 50),
#                                       (line_end, self.strategy_line_top),
#                                       (line_end, self.strategy_line_bottom), width=self.strategy_line_inner_width)
#
#         if not self.event_hold and not self.event_press:
#             if self.selection_start_pos:  # release hold while band exist
#                 rect_list = list(set([character for index, character in enumerate(self.battle.all_team_leader[self.battle.player_team]) if
#                                       index in self.rect.collidelistall([
#                                           character.rect for
#                                           character in self.battle.all_team_leader[self.battle.player_team] if character.is_controllable])]
#                                      + [indicator.character for index, indicator in
#                                         enumerate(self.battle.player_leader_indicators) if index in
#                                         self.rect.collidelistall([indicator.rect for indicator in
#                                                                        self.battle.player_leader_indicators])]))
#                 if self.battle.shift_press:
#                     self.battle.player_selected_leaders += rect_list
#                     self.battle.player_selected_leaders = list(set(self.battle.player_selected_leaders))
#                 elif self.battle.ctrl_press:
#                     for character in rect_list:
#                         if character in self.battle.player_selected_leaders:
#                             self.battle.player_selected_leaders.remove(character)
#                 else:
#                     self.battle.player_selected_leaders = rect_list
#                 self.reset()
#
#             if self.event_alt_press:  # right click order selected leader to do something
#                 if self.battle.player_selected_strategy:
#                     # has strategy selected, prioritise activate strategy for this input
#                     if self.battle.activate_strategy(self.battle.player_team, self.battle.player_selected_strategy[0],
#                                                      self.battle.player_selected_strategy[1],
#                                                      self.battle.base_cursor_pos[0]):
#                         # successfully activate strategy
#                         self.battle.player_selected_strategy = None
#                 else:
#                     if self.battle.player_selected_leaders:
#                         for leader in self.battle.player_selected_leaders:
#                             if self.battle.alt_press:  # order to move and attack enemy in range along the way
#                                 leader.issue_commander_order(("attack", self.battle.base_cursor_pos[0]))
#                             else:  # order to move to area, no attack at all until reach
#                                 leader.issue_commander_order(("move", self.battle.base_cursor_pos[0]))
#                     if self.battle.command_ui.selected_air_group_indexes:
#                         self.battle.call_in_air_group(1, self.battle.command_ui.selected_air_group_indexes,
#                                                       self.battle.base_cursor_pos[0])
#                         self.battle.command_ui.selected_air_group_indexes = []
#         else:  # holding left click, manipulate band
#             if self.event_press and self.battle.player_selected_strategy:
#                 # deactivate strategy when there is one selected
#                 self.battle.player_selected_strategy = None
#
#             self.current_pos = self.cursor.pos
#             if not self.selection_start_pos:
#                 self.selection_start_pos = self.current_pos
#             else:
#                 x1, y1 = self.selection_start_pos
#                 x2, y2 = self.current_pos
#                 # Calculate the top-left and dimensions of the selection rectangle
#                 left = min(x1, x2)
#                 top = min(y1, y2)
#                 if self.current_pos != self.selection_start_pos:
#                     width = abs(x1 - x2)
#                     height = abs(y1 - y2)
#                     selection_rect = Rect(left, top, width, height)
#                     self.rect = Rect(left - self.battle.camera_center_x + self.battle.camera_pos[0],
#                                      top, width, height)  # rect for collision unit selection check
#                     draw.rect(self.battle_camera.image, (0, 0, 0), selection_rect, self.inner_line_size)
#                     draw.rect(self.battle_camera.image, (255, 255, 255), selection_rect, self.line_size)
#                 else:
#                     self.rect = Rect(left - self.battle.camera_center_x + self.battle.camera_pos[0],
#                                      top, 1, 1)  # rect for collision unit selection check
