from engine.army.armycharacter import ArmyCharacter

from engine.constants import Custom_Default_Faction


def menu_main(self):
    if self.custom_battle_button.event_press:
        self.menu_state = "custom"
        self.background = self.background_image["empty_background"]
        for index in range(0, 4):
            self.custom_battle_team1_setup.change_faction(None, index)
            self.custom_battle_team2_setup.change_faction(None, index)
        self.remove_from_ui_updater(self.main_menu_buttons, self.main_menu_actor)
        self.add_to_ui_updater(self.custom_battle_menu_uis)

    elif self.mission_button.event_press:
        self.menu_state = "mission"
        self.background = self.background_image["empty_background"]
        self.remove_from_ui_updater(self.main_menu_buttons, self.main_menu_actor)
        self.add_to_ui_updater(self.mission_menu_uis)

    elif self.grand_button.event_press:
        self.menu_state = "grand"
        self.load_grand_campaign("main")
        self.faction_selector.change_faction(Custom_Default_Faction)
        self.background = self.background_image["empty_background"]
        self.remove_from_ui_updater(self.main_menu_buttons, self.main_menu_actor)
        self.add_to_ui_updater(self.grand_menu_uis)

    elif self.test_battle_button.event_press:
        self.custom_team_army[1][0].__init__(ArmyCharacter("Leader_bigta"),
                                             ["Small_rabbit_leader_knight", "Leader_iri"],
                                             ["Small_rabbit_spear", "Small_rabbit_sling", "Small_rabbit_sling"],
                                             ["Castle_human_air_flying_monk", "Small_eagle_air_stone"],
                                             ["Mage_earth", "Test", "Test2"], supply=1000)
        self.custom_team_army[1][1].__init__(ArmyCharacter("Leader_adaqua"),
                                             ["Small_rabbit_leader_knight", "Small_rabbit_leader_knight"],
                                             ["Small_rabbit_sling", "Small_rabbit_snail_cav", "Small_rabbit_hound_cav"],
                                             ["Castle_human_air_flying_monk", "Small_eagle_air_stone"],
                                             ["Test", "Test2"], supply=500)
        self.custom_team_army[2][0].__init__(ArmyCharacter("Leader_tulia"),
                                             ["Small_rabbit_leader_banner", "Castle_human_leader_mage"],
                                             ["Small_rabbit_spear", "Small_snail_sword"],
                                             ["Castle_cat_air_rocket_bomb", "Castle_cat_air_rocket_bomb"],
                                             ["Mage_earth", "Test2", "Test"], supply=1000)
        self.custom_team_army[2][1].__init__(ArmyCharacter("Small_rabbit_leader_hero"),
                                             ["Small_rabbit_leader_knight", "Leader_amgarn", "Leader_vraesier", ],
                                             ["Small_rabbit_sling", "Castle_cat_shield_crossbow", "Doll_candle_spear",
                                              "Castle_human_militia_bow"],
                                             ["Small_eagle_air_stone", "Castle_human_air_flying_monk",
                                              "Small_eagle_air_stone", "Castle_human_air_flying_monk"],
                                             ["Test", "Test"], supply=700)

        for army in self.custom_team_army[1][2:]:
            army.__init__(None, [], [], [], [])
        for army in self.custom_team_army[2][2:]:
            army.__init__(None, [], [], [], [])

        team_stat = {0: {"strategy_resource": 0, "start_pos": 0.5, "air_group": [], "retinue": (),
                         "strategy": [], "strategy_cooldown": {},
                         "main_army": None,
                         "reinforcement_army": []},
                     1: {"strategy_resource": 0, "start_pos": 0, "air_group": [], "retinue": (),
                         "strategy": [], "strategy_cooldown": {},
                         "main_army": self.custom_team_army[1][0],
                         "reinforcement_army": self.custom_team_army[1][1:2]},
                     2: {"strategy_resource": 0, "start_pos": 1, "air_group": [],
                         "retinue": (), "strategy": [], "strategy_cooldown": {},
                         "main_army": self.custom_team_army[2][0],
                         "reinforcement_army": self.custom_team_army[2][1:2]}}

        self.start_battle("main", "Test", team_stat, 2)

    elif self.option_button.event_press:  # change main menu to option menu
        self.menu_state = "option"
        self.remove_from_ui_updater(self.main_menu_buttons, self.main_menu_actor)
        self.background = self.background_image["empty_background"]
        self.add_to_ui_updater(self.option_menu_buttons, self.option_menu_sliders.values(), self.value_boxes.values(),
                               self.option_text_list)

    elif self.quit_button.event_press or self.esc_press:  # open quit game confirmation input
        self.activate_input_popup(("confirm_input", "quit"), "Quit Game?", self.confirm_popup_uis)
