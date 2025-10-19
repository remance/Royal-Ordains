def menu_char(self):
    if self.char_back_button.event or self.esc_press:  # back to start_set menu
        self.player_char_select = {1: {"character": None, "followers": None}, 2: {"character": None, "followers": None}}
        for player, selector in self.player_char_selectors.items():
            selector.change_mode("empty")
            self.player_char_interfaces[player].change_mode("empty")
        self.background = self.background_image["background"]
        self.add_ui_updater(self.main_menu_actor)
        self.remove_ui_updater(self.char_menu_buttons, self.player_char_selectors.values(),
                               self.player_char_interfaces.values(),
                               self.char_interface_text_popup.values())
        self.back_mainmenu()

    elif self.start_battle_button.event:
        all_ready = True
        if len([player for player in self.player_char_selectors.values() if player.mode == "empty"]) == 2:  # all empty
            all_ready = False
        else:
            for player, item in self.player_char_select.items():
                if self.player_char_selectors[player].mode not in ("ready", "empty"):
                    all_ready = False  # some not ready
                    break
        self.mission_selected = "0"
        if all_ready and self.mission_selected:
            self.battle.main_player = 1
            if self.player_char_selectors[1].mode == "empty":
                self.battle.main_player = 2

            self.start_battle(self.mission_selected)

    else:
        for key_list in (self.player_key_press, self.player_key_hold):
            for player in key_list:
                for key_press, pressed in key_list[player].items():
                    if pressed:
                        selector = self.player_char_selectors[player]
                        interface = self.player_char_interfaces[player]
                        if not interface.input_delay:
                            if selector.mode != "ready":
                                if key_press == "Left":
                                    if interface.mode in ("character", "followers"):
                                        interface.current_select -= 1
                                        interface.change_portrait_list()

                                elif key_press == "Right":
                                    if interface.mode in ("character", "followers"):
                                        interface.current_select += 1
                                        interface.change_portrait_list()

                                elif key_press == "Down":
                                    if interface.mode in ("character", "followers"):
                                        interface.current_select += 4
                                        interface.change_portrait_list()

                                elif key_press == "Up":
                                    if interface.mode in ("character", "followers"):
                                        interface.current_select -= 4
                                        interface.change_portrait_list()

                                elif key_press == "Weak":  # confirm
                                    if interface.mode == "empty":
                                        interface.change_mode("character")

                                    elif interface.mode == "character":
                                        self.remove_ui_updater(interface.text_popup)
                                        self.player_char_select[player]["character"] = interface.character_list[
                                            interface.current_select]
                                        interface.change_mode("followers")

                                    elif interface.mode == "followers":  # follower to ready
                                        self.remove_ui_updater(interface.text_popup)
                                        self.player_char_select[player]["followers"] = interface.followers_list[
                                            interface.current_select]
                                        selector.change_mode("ready", delay=False)

                                elif key_press == "Guard":  # add/remove favourite
                                    interface.input_delay = 0.2
                                    if interface.mode == "character":
                                        interface.add_remove_text_popup()
                                        interface.text_popup.popup(interface.rect.topleft,
                                                                   (interface.grab_text(
                                                                       ("ui", "keybind_confirm")) + " " +
                                                                    interface.grab_text(("ui", "Button")) + " (" +
                                                                    interface.game.player_key_bind_button_name[
                                                                        interface.player]["Special"] +
                                                                    "): " + interface.grab_text(
                                                                       ("ui", "select_character")),
                                                                    interface.grab_text(
                                                                        ("ui", "keybind_strong_attack")) + " " +
                                                                    interface.grab_text(("ui", "Button")) + " (" +
                                                                    interface.game.player_key_bind_button_name[
                                                                        interface.player]["Strong"] +
                                                                    "): " + interface.grab_text(
                                                                        ("ui", "remove_player")),
                                                                    interface.grab_text(
                                                                        ("ui", "keybind_special")) + " " +
                                                                    interface.grab_text(("ui", "Button")) + " (" +
                                                                    interface.game.player_key_bind_button_name[
                                                                        interface.player][
                                                                        "Special"] +
                                                                    "): " + interface.grab_text(
                                                                        ("ui", "set_favourite")),
                                                                    interface.grab_text(
                                                                        ("ui", "keybind_inventory_menu")) + " " +
                                                                    interface.grab_text(("ui", "Button")) + " (" +
                                                                    interface.game.player_key_bind_button_name[
                                                                        interface.player][
                                                                        "Inventory Menu"] +
                                                                    "): " + interface.grab_text(
                                                                        ("ui", "toggle_description"))
                                                                    ),
                                                                   width_text_wrapper=500 * self.screen_scale[0])
                                    elif interface.mode == "followers":
                                        interface.add_remove_text_popup()
                                        interface.text_popup.popup(interface.rect.topleft,
                                                                   (interface.grab_text(
                                                                       ("ui", "keybind_confirm")) + " " +
                                                                    interface.grab_text(("ui", "Button")) + " (" +
                                                                    interface.game.player_key_bind_button_name[
                                                                        interface.player]["Special"] +
                                                                    "): " + interface.grab_text(
                                                                       ("ui", "select_follower")),
                                                                    interface.grab_text(
                                                                        ("ui", "keybind_strong_attack")) + " " +
                                                                    interface.grab_text(("ui", "Button")) + " (" +
                                                                    interface.game.player_key_bind_button_name[
                                                                        interface.player]["Strong"] +
                                                                    "): " + interface.grab_text(
                                                                        ("ui", "back_character")),
                                                                    interface.grab_text(
                                                                        ("ui", "keybind_special")) + " " +
                                                                    interface.grab_text(("ui", "Button")) + " (" +
                                                                    interface.game.player_key_bind_button_name[
                                                                        interface.player][
                                                                        "Special"] +
                                                                    "): " + interface.grab_text(
                                                                        ("ui", "set_favourite")),
                                                                    interface.grab_text(
                                                                        ("ui", "keybind_inventory_menu")) + " " +
                                                                    interface.grab_text(("ui", "Button")) + " (" +
                                                                    interface.game.player_key_bind_button_name[
                                                                        interface.player][
                                                                        "Inventory Menu"] +
                                                                    "): " + interface.grab_text(
                                                                        ("ui", "toggle_description"))),
                                                                   width_text_wrapper=500 * self.screen_scale[0])
                                    elif interface.mode == "empty":
                                        interface.add_remove_text_popup()
                                        interface.text_popup.popup(interface.rect.topleft,
                                                                   (interface.grab_text(
                                                                       ("ui", "keybind_confirm")) + " " +
                                                                    interface.grab_text(("ui", "Button")) + " (" +
                                                                    interface.game.player_key_bind_button_name[
                                                                        interface.player][
                                                                        "Special"] +
                                                                    "): " + interface.grab_text(("ui", "add_player"))),
                                                                   width_text_wrapper=500 * self.screen_scale[0])
                                elif key_press == "Inventory Menu":
                                    interface.input_delay = 0.2
                                    if interface.mode == "character":
                                        interface.add_remove_text_popup()
                                        character = interface.character_list[interface.current_select]
                                        interface.text_popup.popup(interface.rect.topleft,
                                                                   (interface.grab_text(
                                                                       ("character", character, "Name")) +
                                                                    ": " + interface.grab_text(
                                                                       ("character", character, "True Name")),
                                                                    " ",
                                                                    interface.grab_text(
                                                                        ("character", character, "Description"))),
                                                                   width_text_wrapper=500 * self.screen_scale[0])
                                    elif interface.mode == "followers":
                                        interface.add_remove_text_popup()
                                        followers = interface.followers_list[interface.current_select]
                                        interface.text_popup.popup(interface.rect.topleft,
                                                                   (interface.grab_text(
                                                                       ("followers", followers, "Name")),
                                                                    " ",
                                                                    interface.grab_text(
                                                                        ("followers", followers, "Description"))),
                                                                   width_text_wrapper=500 * self.screen_scale[0])
                                elif key_press == "Special":  # add/remove favourite
                                    interface.input_delay = 0.2
                                    if interface.mode == "character":
                                        if interface.character_list[interface.current_select] in \
                                                self.save_data.save_profile["favourite"][interface.player][
                                                    interface.mode]:
                                            self.save_data.save_profile["favourite"][interface.player][
                                                interface.mode].remove(
                                                interface.character_list[interface.current_select])
                                        else:
                                            self.save_data.save_profile["favourite"][interface.player][
                                                interface.mode].append(
                                                interface.character_list[interface.current_select])
                                    elif interface.mode == "followers":
                                        if interface.follower_list[interface.current_select] in \
                                                self.save_data.save_profile["favourite"][interface.player][
                                                    interface.mode]:
                                            self.save_data.save_profile["favourite"][interface.player][
                                                interface.mode].remove(
                                                interface.follower_list[interface.current_select])
                                        else:
                                            self.save_data.save_profile["favourite"][interface.player][
                                                interface.mode].append(
                                                interface.follower_list[interface.current_select])

                            if key_press == "Strong":  # cancel, go back to previous state
                                if selector.mode == "ready":
                                    interface.change_mode("followers")
                                    selector.change_mode("empty")
                                    self.player_char_select[player]["followers"] = None

                                elif interface.mode == "character":
                                    interface.change_mode("empty")
                                    self.remove_ui_updater(interface.text_popup)

                                elif interface.mode == "followers":
                                    self.player_char_select[player]["character"] = None
                                    self.remove_ui_updater(interface.text_popup)
                                    interface.change_mode("character")
