import webbrowser

browser = webbrowser.get()


def menu_main(self):
    if self.custom_battle_button.event:
        self.menu_state = "custom"
        self.remove_ui_updater(self.mainmenu_button, self.main_menu_actor)
        self.add_ui_updater(self.custom_battle_menu_buttons)
        pass

    elif self.test_battle_button.event:
        team_stat = {0: {"strategy_resource": 0, "start_pos": -1, "air_group": [], "retinue": (),
                         "strategy": [], "strategy_cooldown": {},
                         "unit": {
                             "controllable": [],
                             "uncontrollable": [{"Castle_cat_shield_crossbow": {
                                 "Followers": [{"Castle_cat_shield_crossbow": 10}],
                                 "Start Health": 1, "Start Resource": 1}}],
                             "reinforcement": {}}},
                     1: {"strategy_resource": 0, "start_pos": 0, "air_group": [], "retinue": ("Test", "Test", "Test2", "Test2"),
                         "strategy": [], "strategy_cooldown": {},
                         "unit": {
                             "controllable": [
                                 {"Leader_bigta": {"Followers": [{"Small_rabbit_spear": 20},
                                                     {"Small_rabbit_sling": 20},
                                                     {"Small_rabbit_spear": 20}],
                                       "Start Health": 1, "Start Resource": 1}},
                     {"Leader_iri": {"Followers": [{"Small_rabbit_spear": 20},
                                                   {"Small_rabbit_spear": 20},
                                                   {"Small_rabbit_spear": 20}],
                                     "Start Health": 1, "Start Resource": 1}}],
                             "uncontrollable": [],
                             "air": [{"Castle_human_air_flying_monk": 10}, {"Small_eagle_air_stone": 10}],
                             "reinforcement": {"controllable": [{"Small_rabbit_leader_hero": {"Followers": [
                     {"Small_rabbit_snail_cav": 10},
                     {"Small_rabbit_snail_cav": 10},
                     {"Small_rabbit_snail_cav": 10}],
                     "Start Health": 1, "Start Resource": 1}}], "air": [{"Small_eagle_air_stone": 10}]}}},
         2: {"strategy_resource": 100, "start_pos": -0.5, "air_group": [],
             "retinue": (), "strategy": [], "strategy_cooldown": {},
             "unit": {
                 "controllable": [{"Leader_tulia": {"Followers": [{"Small_rabbit_spear": 20},
                                                                  {"Small_rabbit_spear": 20},
                                                                  {"Small_rabbit_spear": 20}],
                                                    "Start Health": 1, "Start Resource": 1}}],
                 "uncontrollable": [{"Small_rabbit_tower": {"Followers": [{"Small_rabbit_spear": 20},
                                                                          {"Small_rabbit_spear": 20},
                                                                          {"Small_rabbit_spear": 20}],
                                                            "Start Health": 1, "Start Resource": 1}},
                                    {"Small_rabbit_tower": {"Followers": [],
                                                            "Start Health": 1, "Start Resource": 1}}],
                 "air": [{"Castle_cat_air_rocket_bomb": 5}, {"Castle_cat_air_rocket_bomb": 5}],
                 "reinforcement": {"controllable": [], "air": []}}}}

        self.start_battle("test", team_stat, ai_retreat=False)

    # if self.start_game_button.event:  # start new game
    #     self.menu_state = "char"
    #     self.play_map_type = "preset"
    #     self.background = self.background_image["char_background"]
    #     for interface in self.player_char_interfaces.values():
    #         interface.remake()
    #     self.remove_ui_updater(self.mainmenu_button, self.main_menu_actor)
    #     self.add_ui_updater(self.char_menu_buttons)
    #
    # elif self.load_game_button.event:  # load save
    #     self.start_battle(self.mission_selected)

    elif self.option_button.event:  # change main menu to option menu
        self.menu_state = "option"
        self.remove_ui_updater(self.mainmenu_button)

        self.add_ui_updater(self.option_menu_button, self.option_menu_sliders.values(), self.value_boxes.values(),
                            self.option_text_list, self.hide_background)

    elif self.quit_button.event or self.esc_press:  # open quit game confirmation input
        self.activate_input_popup(("confirm_input", "quit"), "Quit Game?", self.confirm_ui_popup)
