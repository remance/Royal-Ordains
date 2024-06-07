from random import randint, uniform
from pygame import Vector2

from engine.drop.drop import Drop
from engine.uibattle.uibattle import DamageNumber
from engine.effect.effect import Effect


def check_new_animation(self, done):
    from engine.character.character import BattleAICharacter

    # Pick new action and animation, either when animation finish or get interrupt,
    # low level action got replace with more important one, finish playing, skill animation and its effect end
    if (self.interrupt_animation and "uninterruptible" not in self.current_action) or \
            (((not self.current_action or "low level" in self.current_action) and
              self.command_action) or done):
        # finish current action
        if done:
            if self.current_moveset:
                if self.current_moveset["Status"]:  # moveset apply status effect
                    for effect in self.current_moveset["Status"]:
                        self.apply_status(self, effect)
                        for ally in self.near_ally:
                            if ally[1] <= self.current_moveset["Range"]:  # apply status based on range
                                ally[0].apply_status(self, effect)
                            else:
                                break

                if "helper" in self.current_moveset["Property"]:
                    for key, value in self.current_moveset["Property"].items():
                        if key == "helper drop item":
                            self.battle.helper.interrupt_animation = True
                            self.battle.helper.command_action = {"name": "special",
                                                                 "drop": value}
                        # elif key == "helper use item":
                        #     self.battle.helper.interrupt_animation = True
                        #     self.battle.helper.command_action = {"name": "special",
                        #                                          "drop": value, "player": self.game_id[-1]}
            if "item" in self.current_action:  # action use equipped item
                item_stat = self.character_data.equip_item_list[self.current_action["item"]]
                if item_stat["Health"]:
                    self.health += item_stat["Health"]
                    if self.health > self.base_health:
                        self.health = self.base_health
                    DamageNumber(str(int(item_stat["Health"])),
                                 (self.pos[0], (self.pos[1] - self.sprite_height * 3.5)), False, "health")
                if item_stat["Resource"]:
                    self.resource += item_stat["Resource"] * self.item_effect_modifier
                    if self.resource > self.base_resource:
                        self.resource = self.base_resource
                    DamageNumber(str(int(item_stat["Resource"])),
                                 (self.pos[0], (self.pos[1] - self.sprite_height * 2)), False, "resource")
                if item_stat["Status"]:
                    for effect in item_stat["Status"]:
                        self.apply_status(self, effect)

                if item_stat["Property"]:
                    if "weather" in item_stat["Property"]:  # item that change weather
                        self.current_weather.__init__(item_stat["Property"]["weather"], randint(0, 359), randint(0, 3),
                                                      self.weather_data)
                    for spawn_type in ("chaos summon", "chaos invasion", "summon"):
                        if spawn_type in item_stat["Property"]:
                            team = self.team
                            if "chaos" in spawn_type:  # chaos summon enemy with neutral team
                                team = 5
                            for spawn, chance in item_stat["Property"][spawn_type].items():
                                spawn_name = spawn
                                if "+" in spawn_name:  # + indicate number of possible drop
                                    spawn_num = int(spawn_name.split("+")[1])
                                    spawn_name = spawn_name.split("+")[0]
                                    for _ in range(spawn_num):
                                        self.battle.last_char_id += 1  # id continue from last chars
                                        if chance >= uniform(0, 100):
                                            if "invasion" in spawn_type:
                                                start_pos = (self.base_pos[0] + uniform(-2000, 2000),
                                                             self.base_pos[1])
                                            else:
                                                start_pos = (self.base_pos[0] + uniform(-200, 200),
                                                             self.base_pos[1])
                                            BattleAICharacter(self.battle.last_char_id, self.battle.last_char_id,
                                                              self.character_data.character_list[spawn_name] |
                                                              {"ID": spawn_name,
                                                               "Sprite Ver": self.sprite_ver, "Angle": self.angle,
                                                               "Team": team, "POS": start_pos,
                                                               "Arrive Condition": ()})
                                            Effect(None, ("Movement", "Summon", start_pos[0],
                                                          start_pos[1], -self.angle, 1, 0, 1), 0)
                                else:
                                    if chance >= uniform(0, 100):
                                        self.battle.last_char_id += 1  # id continue from last chars
                                        if "invasion" in spawn_type:
                                            start_pos = (self.base_pos[0] + uniform(-2000, 2000),
                                                         self.base_pos[1])
                                        else:
                                            start_pos = (self.base_pos[0] + uniform(-200, 200),
                                                         self.base_pos[1])
                                        BattleAICharacter(self.battle.last_char_id, self.battle.last_char_id,
                                                          self.character_data.character_list[spawn_name] |
                                                          {"ID": spawn_name,
                                                           "Sprite Ver": self.sprite_ver, "Angle": self.angle,
                                                           "Team": team, "POS": start_pos,
                                                           "Arrive Condition": ()})

                for ally in self.near_ally:
                    if ally[1] <= item_stat["Range"]:  # apply status based on range
                        if item_stat["Health"]:
                            ally[0].health += item_stat["Health"]
                            if ally[0].health > ally[0].base_health:
                                ally[0].health = ally[0].base_health
                            DamageNumber(str(int(item_stat["Health"])),
                                         (ally[0].pos[0], ally[0].pos[1] - ally[0].sprite_height * 3.5), False, "health")
                        if item_stat["Resource"]:
                            ally[0].resource += item_stat["Resource"] * ally[0].item_effect_modifier
                            if ally[0].resource > ally[0].base_resource:
                                ally[0].resource = ally[0].base_resource
                            DamageNumber(str(int(item_stat["Resource"])),
                                         (ally[0].pos[0], ally[0].pos[1] - ally[0].sprite_height * 2), False, "resource")
                        if item_stat["Status"]:
                            for effect in item_stat["Status"]:
                                ally[0].apply_status(self, effect)
                    else:
                        break
                for enemy in self.near_enemy:
                    if enemy[1] <= item_stat["Range"]:  # apply status based on range
                        if item_stat["Enemy Status"]:
                            for effect in item_stat["Enemy Status"]:
                                enemy[0].apply_status(self, effect)
                    else:
                        break

                if not self.free_first_item_use or (self.item_free_use_chance and uniform(1, 10) > 7):
                    self.item_usage[self.current_action["item"]] -= 1
                    if self.player_control:  # subtract from in storage
                        self.battle.all_story_profiles[int(self.game_id[-1])]["storage"][self.current_action["item"]] -= 1
                elif self.free_first_item_use:
                    self.free_first_item_use = False

            if "drop" in self.current_action:
                Drop(Vector2(self.base_pos), self.current_action["drop"], self.team)

        # Reset action check
        if "next action" in self.current_action and (not self.interrupt_animation or not self.command_action) and \
                (not self.current_moveset or "no auto next" not in self.current_moveset["Property"]):
            # play next action from current first instead of command if not finish by interruption
            self.current_action = self.current_action["next action"]
        elif ("remove momentum when done" not in self.current_action and
              (("x_momentum" in self.current_action and self.x_momentum) or
               ("y_momentum" in self.current_action and self.y_momentum))) and not self.interrupt_animation:
            # action that require movement to run out first before continue to next action
            pass  # pass not getting new action
        elif "arrive" in self.current_action and "Arrive2" in self.skill[self.position]:
            # has arrival (Arrive2) skill to use after finish arriving
            self.moveset_command_key_input = self.skill[self.position]["Arrive2"]["Buttons"]
            self.check_move_existence()
            self.current_action = self.attack_command_actions["Special"] | self.command_moveset["Property"]

        elif "run" in self.current_action and not self.command_action:  # stop running, halt
            self.current_action = self.halt_command_action
            if self.angle == -90:
                self.x_momentum = self.walk_speed
            else:
                self.x_momentum = -self.walk_speed
        elif "halt" in self.current_action:  # already halting
            self.x_momentum = 0
            self.current_action = self.command_action  # continue next action when animation finish
            self.command_action = {}
        else:
            self.current_action = self.command_action  # continue next action when animation finish
            self.command_action = {}

        if self.command_moveset:  # assign next moveset to current
            self.current_moveset = self.command_moveset
            self.command_moveset = {}
            self.continue_moveset = None
            if "Next Move" in self.current_moveset:  # check for next move combo
                self.continue_moveset = self.current_moveset["Next Move"]

        self.specific_animation_done(done)
        # reset animation playing related value
        self.stoppable_frame = False
        self.hit_enemy = False
        self.interrupt_animation = False
        self.release_timer = 0  # reset any release timer

        self.show_frame = 0
        self.frame_timer = 0
        self.move_speed = 0

        # check for new position before picking new animation
        if "couch" in self.current_action:
            self.position = "Couch"
        elif "air" in self.current_action:
            self.position = "Air"
            self.y_momentum = self.jump_power
            if self.x_momentum:  # increase y momentum a bit when has x momentum so jump not too short
                self.y_momentum *= 1.3
        elif "stand" in self.current_action:
            self.position = "Stand"

        self.pick_animation()

        # new action property
        if "freeze" in self.current_action:
            self.freeze_timer = self.current_action["freeze"]

        if "x_momentum" in self.current_action and not isinstance(self.current_action["x_momentum"], bool):
            # action with specific x_momentum from data like attack action that move player, not for AI move
            if self.angle != 90:
                self.x_momentum = self.current_action["x_momentum"]
            else:
                self.x_momentum = -self.current_action["x_momentum"]
        if "y_momentum" in self.current_action and not isinstance(self.current_action["y_momentum"], bool):
            self.y_momentum = self.current_action["y_momentum"]
