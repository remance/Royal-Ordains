from engine.army.general import General


def menu_main(self):
    if self.custom_battle_button.event:
        self.menu_state = "custom"
        self.background = self.background_image["empty_background"]
        self.remove_ui_updater(self.main_menu_buttons, self.main_menu_actor)
        self.add_ui_updater(self.custom_battle_menu_buttons)
        pass

    elif self.test_battle_button.event:
        self.custom_team0_garrison_army.__init__({General("Castle_cat_shield_crossbow"): [{"Castle_cat_shield_crossbow": 10}]},
                                                 [], [])
        self.custom_team1_army.__init__({General("Leader_bigta"): [{"Small_rabbit_spear": 20},
                                                                   {"Small_rabbit_sling": 20},
                                                                   {"Small_rabbit_spear": 20}],
                                        General("Leader_iri"): [{"Small_rabbit_spear": 20},
                                                                 {"Small_rabbit_spear": 20},
                                                                 {"Small_rabbit_spear": 20}]},
                                        [{"Castle_human_air_flying_monk": 10}, {"Small_eagle_air_stone": 10}],
                                        ["Test", "Test", "Test2", "Test2"]
                                        )
        self.custom_team2_army.__init__({General("Leader_tulia"): [{"Small_rabbit_spear": 20},
                                                           {"Small_rabbit_spear": 20},
                                                           {"Small_rabbit_spear": 20}]},
                                        [{"Castle_cat_air_rocket_bomb": 5}, {"Castle_cat_air_rocket_bomb": 5}],
                                        [])
        self.custom_team1_reinforcement_army.__init__({General("Small_rabbit_leader_hero"):
                                                            [{"Small_rabbit_snail_cav": 10},
                                                             {"Small_rabbit_snail_cav": 10},
                                                             {"Small_rabbit_snail_cav": 10}]},
                                                      [{"Small_eagle_air_stone": 10}], [])
        self.custom_team2_reinforcement_army.__init__({}, [], [])
        self.custom_team1_garrison_army.__init__({}, [], [])
        self.custom_team2_garrison_army.__init__({General("Small_rabbit_tower"):
                                                       [{"Small_rabbit_spear": 20},
                                                        {"Small_rabbit_spear": 20},
                                                        {"Small_rabbit_spear": 20}],
                                                  General("Small_rabbit_tower"): {}}, [], [])

        team_stat = {0: {"strategy_resource": 0, "start_pos": 1, "air_group": [], "retinue": (),
                         "strategy": [], "strategy_cooldown": {},
                         "main_army": None, "garrison_army": self.custom_team0_garrison_army,
                         "reinforcement_army": []},
                     1: {"strategy_resource": 0, "start_pos": 0, "air_group": [], "retinue": (),
                         "strategy": [], "strategy_cooldown": {},
                         "main_army": self.custom_team1_army, "garrison_army": self.custom_team1_garrison_army,
                         "reinforcement_army": [self.custom_team1_reinforcement_army]},
                     2: {"strategy_resource": 100, "start_pos": 0.5, "air_group": [],
                         "retinue": (), "strategy": [], "strategy_cooldown": {},
                         "main_army": self.custom_team2_army,
                         "garrison_army": self.custom_team2_garrison_army,
                         "reinforcement_army": [self.custom_team2_reinforcement_army]}}

        self.start_battle("test", team_stat, ai_retreat=False)

    # elif self.load_game_button.event:  # load save
    #     self.start_battle(self.mission_selected)

    elif self.option_button.event:  # change main menu to option menu
        self.menu_state = "option"
        self.remove_ui_updater(self.main_menu_buttons)

        self.add_ui_updater(self.option_menu_buttons, self.option_menu_sliders.values(), self.value_boxes.values(),
                            self.option_text_list, self.hide_background)

    elif self.quit_button.event or self.esc_press:  # open quit game confirmation input
        self.activate_input_popup(("confirm_input", "quit"), "Quit Game?", self.confirm_popup_uis)
