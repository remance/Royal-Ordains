from engine.utils.common import edit_config


def escmenu_process(self, esc_press: bool):
    """
    User interaction processing for ESC menu during battle
    :param self: Battle object
    :param esc_press: esc button
    :return: special command that process in battle loop
    """
    self.remove_ui_updater(self.text_popup)
    command = None
    if esc_press and self.battle_menu.mode == "menu":  # in menu or option
        back_to_battle_state(self)

    elif self.battle_menu.mode == "menu":  # esc menu
        # Player can interact with UI during this state like mouse over to show information or scrolling event log
        # if self.players:
        #     if self.portrait_rect.collidepoint(self.cursor.pos):
        #         if self.cursor.is_alt_select_just_up:
        #             popout_encyclopedia(self, self.lorebook.leader_section,
        #                                 self.lorebook.leader_id_reindex[self.players.troop_id])
        #         else:
        #             self.text_popup.popup(self.cursor.rect,
        #                                   (self.localisation.grab_text(("leader", self.players.troop_id))[
        #                                        "Name"],
        #                                    self.localisation.grab_text(("leader", self.players.troop_id))[
        #                                        "Description"]),
        #                                   width_text_wrapper=500 * self.screen_scale[0])
        #             self.add_ui_updater(self.text_popup)
        #
        #     elif self.weapon_ui.mouse_over and self.players:
        #         mouse_pos_inside_weapon_ui = (self.cursor.pos[0] - self.weapon_ui.rect.topleft[0],
        #                                       self.cursor.pos[1] - self.weapon_ui.rect.topleft[1])
        #         if self.weapon_ui.prim_main_weapon_box_rect.collidepoint(mouse_pos_inside_weapon_ui):
        #             weapon = self.players.primary_main_weapon[0]
        #             if self.players.equipped_weapon == 1:
        #                 weapon = self.players.secondary_main_weapon[0]
        #             if self.cursor.is_alt_select_just_up:
        #                 popout_encyclopedia(self, self.lorebook.equipment_section, weapon)
        #             else:
        #                 self.text_popup.popup(self.cursor.rect,
        #                                       (self.localisation.grab_text(("weapon", weapon))["Name"],
        #                                        self.localisation.grab_text(("weapon", weapon))["Description"]),
        #                                       width_text_wrapper=500 * self.screen_scale[0])
        #                 self.add_ui_updater(self.text_popup)
        #         elif self.weapon_ui.prim_sub_weapon_box_rect.collidepoint(mouse_pos_inside_weapon_ui):
        #             weapon = self.players.primary_sub_weapon[0]
        #             if self.players.equipped_weapon == 1:
        #                 weapon = self.players.secondary_sub_weapon[0]
        #             if self.cursor.is_alt_select_just_up:
        #                 popout_encyclopedia(self, self.lorebook.equipment_section, weapon)
        #             else:
        #                 self.text_popup.popup(self.cursor.rect,
        #                                       (self.localisation.grab_text(("weapon", weapon))["Name"],
        #                                        self.localisation.grab_text(("weapon", weapon))["Description"]),
        #                                       width_text_wrapper=500 * self.screen_scale[0])
        #                 self.add_ui_updater(self.text_popup)
        #         elif self.weapon_ui.sec_main_weapon_box_rect.collidepoint(mouse_pos_inside_weapon_ui):
        #             weapon = self.players.secondary_main_weapon[0]
        #             if self.players.equipped_weapon == 1:
        #                 weapon = self.players.primary_main_weapon[0]
        #             if self.cursor.is_alt_select_just_up:
        #                 popout_encyclopedia(self, self.lorebook.equipment_section, weapon)
        #             else:
        #                 self.text_popup.popup(self.cursor.rect,
        #                                       (self.localisation.grab_text(("weapon", weapon))["Name"],
        #                                        self.localisation.grab_text(("weapon", weapon))["Description"]),
        #                                       width_text_wrapper=500 * self.screen_scale[0])
        #                 self.add_ui_updater(self.text_popup)
        #         elif self.weapon_ui.sec_sub_weapon_box_rect.collidepoint(mouse_pos_inside_weapon_ui):
        #             weapon = self.players.secondary_sub_weapon[0]
        #             if self.players.equipped_weapon == 1:
        #                 weapon = self.players.primary_sub_weapon[0]
        #             if self.cursor.is_alt_select_just_up:
        #                 popout_encyclopedia(self, self.lorebook.equipment_section, weapon)
        #             else:
        #                 self.text_popup.popup(self.cursor.rect,
        #                                       (self.localisation.grab_text(("weapon", weapon))["Name"],
        #                                        self.localisation.grab_text(("weapon", weapon))["Description"]),
        #                                       width_text_wrapper=500 * self.screen_scale[0])
        #                 self.add_ui_updater(self.text_popup)

        for button in self.battle_menu_button:
            if button.event_press:
                if button.text == "Resume":  # resume battle
                    back_to_battle_state(self)

                elif button.text == "Encyclopedia":  # open lorebook
                    self.battle_menu.change_mode("lorebook")  # change to enclycopedia mode
                    self.add_ui_updater(self.lorebook_stuff)  # add sprite related to lorebook
                    self.lorebook.change_section(0, self.lore_name_list, self.subsection_name,
                                                 self.tag_filter_name,
                                                 self.lore_name_list.scroll, self.filter_tag_list,
                                                 self.filter_tag_list.scroll)
                    self.remove_ui_updater(self.battle_menu, self.battle_menu_button, self.esc_slider_menu.values(),
                                           self.esc_value_boxes.values(),
                                           self.esc_option_text.values())  # remove menu sprite

                elif button.text == "Option":  # open option menu
                    self.battle_menu.change_mode("option")  # change to option menu mode
                    self.remove_ui_updater(self.battle_menu_button)  # remove start_set esc menu button
                    self.add_ui_updater(self.esc_option_menu_button, self.esc_slider_menu.values(),
                                        self.esc_value_boxes.values(), self.esc_option_text.values())

                elif button.text == "End Battle":  # back to start_set menu
                    self.exit_battle()
                    command = "end_battle"

                elif button.text == "Desktop":  # quit self
                    self.activate_input_popup(("confirm_input", "quit"), "Quit Game?", self.confirm_ui_popup)
                break  # found clicked button, break loop
            else:
                button.image = button.images[0]

    elif self.battle_menu.mode == "lorebook":  # esc menu
        command = self.lorebook_process(esc_press)
        if command == "exit":
            self.battle_menu.change_mode("menu")  # go back to start_set esc menu
            self.add_ui_updater(self.battle_menu, self.battle_menu_button)  # add start_set esc menu buttons back

    elif self.battle_menu.mode == "option":  # option menu
        for key, value in self.esc_slider_menu.items():
            if value.event:  # press on slider bar
                value.player_input(self.esc_value_boxes[key])  # update slider button based on mouse value
                edit_config("USER", key + "_volume", value.value, self.config_path,
                            self.config)
                self.game.change_sound_volume()

        if self.esc_option_menu_button.event_press or esc_press:  # confirm or esc, close option menu
            self.battle_menu.change_mode("menu")  # go back to start_set esc menu
            self.remove_ui_updater(self.esc_option_menu_button, self.esc_slider_menu.values(),
                                   self.esc_value_boxes.values(),
                                   self.esc_option_text.values())  # remove option menu sprite
            self.add_ui_updater(self.battle_menu_button)  # add start_set esc menu buttons back

    return command


def back_to_battle_state(self):
    self.remove_ui_updater(self.battle_menu, self.battle_menu_button, self.esc_option_menu_button,
                           self.esc_slider_menu.values(),
                           self.esc_value_boxes.values(), self.esc_option_text.values(), self.cursor)
    self.realtime_ui_updater.add(self.player1_battle_cursor)
    self.game_state = "battle"


def popout_encyclopedia(self, section, subsection):
    self.battle_menu.change_mode("lorebook")  # change to enclycopedia mode
    self.add_ui_updater(self.lorebook_stuff)  # add sprite related to lorebook
    self.lorebook.change_section(section, self.lore_name_list,
                                 self.subsection_name, self.tag_filter_name,
                                 self.lore_name_list.scroll, self.filter_tag_list,
                                 self.filter_tag_list.scroll)
    self.lorebook.change_subsection(subsection)
    self.remove_ui_updater(self.battle_menu, self.battle_menu_button, self.esc_slider_menu.values(),
                           self.esc_value_boxes.values(), self.esc_option_text.values())  # remove menu sprite
