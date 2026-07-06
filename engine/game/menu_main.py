from engine.constants import Custom_Default_Culture


def menu_main(self):
    if self.custom_battle_button.event_press:
        self.menu_state = "custom"
        self.background = self.background_image["empty_background"]
        for index in range(0, 4):
            self.custom_battle_team_setup[1].change_faction(None, index)
            self.custom_battle_team_setup[2].change_faction(None, index)
        self.remove_from_ui_menu_updater(self.main_menu_buttons, self.main_menu_actor)
        self.add_to_ui_menu_updater(self.custom_battle_menu_uis)

    # elif self.mission_button.event_press:
    #     self.menu_state = "mission"
    #     self.background = self.background_image["empty_background"]
    #     self.remove_from_ui_updater(self.main_menu_buttons, self.main_menu_actor)
    #     self.add_to_ui_updater(self.mission_menu_uis)

    elif self.lorebook_button.event_press:
        self.menu_state = "beast"
        self.custom_preset_faction_selector.change_faction(Custom_Default_Culture)
        self.background = self.background_image["empty_background"]

        self.sprite_data.load_character_animation((self.lorebook_showcase_character.char_id,))
        animation_list = list(
            self.sprite_data.character_animation_data[self.lorebook_showcase_character.char_id].keys())
        for character in self.character_list[self.lorebook_showcase_character.char_id]["Sub Characters"]:
            for anim in self.game.sprite_data.character_animation_data[character[0]]:
                if anim not in animation_list:
                    animation_list.append(anim)
        animation_list = sorted(animation_list)
        self.lorebook_showcase_animation_list_box.adapter.__init__(
            [[0, key] for key in animation_list if key != "Default"])
        self.lorebook_character_description_showcase.change_character(self.lorebook_showcase_character.char_id)
        self.lorebook_character_moveset_showcase.change_moveset(self.lorebook_showcase_character.char_id, None)

        self.lorebook_showcase_character_selector.add(self.lorebook_faction_selector.selected_faction, None)
        self.remove_from_ui_menu_updater(self.main_menu_buttons, self.main_menu_actor)
        self.add_to_ui_menu_updater(self.lorebook_menu_uis)

    elif self.grand_button.event_press:
        self.menu_state = "grand"
        self.load_grand_campaign("main")
        self.custom_preset_faction_selector.change_faction(self.map_data.default_grand_faction)
        self.background = self.background_image["empty_background"]
        self.remove_from_ui_menu_updater(self.main_menu_buttons, self.main_menu_actor)
        self.add_to_ui_menu_updater(self.grand_menu_uis)

    elif self.test_battle_button.event_press:
        # self.custom_team_army[1][0].__init__("", "small", "small", "leader_bigta",
        #                                      [],
        #                                      [],
        #                                      [],
        #                                      ["mage_earth", "test", "test2"], supply=1000)
        # self.custom_team_army[2][0].__init__("", "castle", "castle", "leader_buikuuh",
        #                                      [],
        #                                      [],
        #                                      [],
        #                                      ["mage_earth", "test2", "test"], supply=1000)

        self.custom_team_army[1][0].__init__("", "small", "small", "leader_bigta",
                                             ["leader_doll_princess", ],
                                             [],
                                             [],
                                             ["small_rabbit_leader_shaman"], supply=10000)
        self.custom_team_army[1][1].__init__("", "small", "small", "leader_adaqua",
                                             ["small_rabbit_leader_knight", "small_rabbit_leader_knight"],
                                             ["small_rabbit_sling", ],
                                             ["castle_human_air_flying_monk", "small_eagle_air_stone"],
                                             ["small_rabbit_leader_shaman"], supply=500)
        self.custom_team_army[2][0].__init__("", "castle", "castle", "leader_buikuuh",
                                             ["leader_adaqua", ],
                                             [],
                                             [],
                                             ["small_rabbit_leader_shaman"], supply=10000)
        self.custom_team_army[2][1].__init__("", "castle", "castle", "",
                                             [],
                                             [],
                                             [],
                                             [], supply=700)

        for army in self.custom_team_army[1][2:]:
            army.__init__("", "", "", None, [], [], [], [])
        for army in self.custom_team_army[2][2:]:
            army.__init__("", "", "", None, [], [], [], [])

        stage_stat = {}
        team_state = {
            0: {"faction": "free", "culture": "free", "strategy_resource": 0, "start_pos": 0.5, "air_group": [],
                "active_retinue": (),
                "strategy": [], "strategy_cooldown": {},
                "main_army": None,
                "reinforcement_army": []},
            1: {"faction": self.custom_team_army[1][0].faction,
                "culture": self.custom_team_army[1][0].culture,
                "strategy_resource": 0, "start_pos": 0, "air_group": [], "active_retinue": (),
                "strategy": [], "strategy_cooldown": {},
                "main_army": self.custom_team_army[1][0],
                "reinforcement_army": self.custom_team_army[1][1:2]},
            2: {"faction": self.custom_team_army[2][0].faction,
                "culture": self.custom_team_army[2][0].culture,
                "strategy_resource": 0, "start_pos": 1, "air_group": [],
                "active_retinue": (), "strategy": [], "strategy_cooldown": {},
                "main_army": self.custom_team_army[2][0],
                "reinforcement_army": self.custom_team_army[2][1:2]}}

        self.start_battle(None, "main", "test", team_state, 1, self.grab_text(("ui", "info_text_custom_battle")),
                          setup_battle=True)

    elif self.option_button.event_press:  # change main menu to option menu
        self.menu_state = "option"
        self.remove_from_ui_menu_updater(self.main_menu_buttons, self.main_menu_actor)
        self.background = self.background_image["empty_background"]
        self.add_to_ui_menu_updater(self.option_menu_buttons, self.option_menu_sliders.values(),
                                    self.value_boxes.values(),
                                    self.option_text_list)

    elif self.quit_button.event_press or self.esc_press:  # open quit game confirmation input
        self.activate_input_popup(("confirm_input", "quit"), self.grab_text(("ui", "input_quit_game")),
                                  self.confirm_popup_uis)
