from engine.constants import Default_Showcase_Character_POS


def menu_lorebook_beast(self):
    if self.lorebook_back_button.event_press or self.esc_press:  # back to start_set menu
        self.remove_from_ui_updater(self.lorebook_menu_uis)
        self.back_mainmenu()

    elif self.lorebook_showcase_animation_list_box.adapter.last_click:
        animation = self.lorebook_showcase_animation_list_box.adapter.last_click
        animation_name = self.lorebook_showcase_animation_list_box.adapter.actual_list[animation[1]]
        move_exist = False
        if animation[0] == "click":
            self.lorebook_showcase_character.interrupt_animation = True
            self.lorebook_showcase_character.command_action = {}
            if animation_name in self.sprite_data.character_animation_data[self.lorebook_showcase_character.char_id]:
                if animation_name in self.character_list[self.lorebook_showcase_character.char_id]["Move"]:
                    # animation is action move, display move stat, assuming that main and sub characters have no shared move
                    move_exist = True
                    self.lorebook_character_moveset_showcase.change_moveset(self.lorebook_showcase_character.char_id,
                                                                            animation_name)
                self.lorebook_showcase_character.command_action = {"name": animation_name, "repeat": True,
                                                                   "target": (self.lorebook_showcase_character.base_pos[0] + 500,
                                                                              Default_Showcase_Character_POS[1])}

            for sub_character in self.lorebook_showcase_character.sub_characters:
                sub_character.interrupt_animation = True
                sub_character.command_action = {}
                if animation_name in self.sprite_data.character_animation_data[sub_character.char_id]:
                    if animation_name in self.character_list[sub_character.char_id]["Move"]:
                        # animation is action move, display move stat
                        move_exist = True
                        self.lorebook_character_moveset_showcase.change_moveset(sub_character.char_id, animation_name)
                    sub_character.command_action = {"name": animation_name, "repeat": True,
                                                    "target": (sub_character.base_pos[0] + 500,
                                                               Default_Showcase_Character_POS[1])}
        if not move_exist:
            self.lorebook_character_moveset_showcase.change_moveset(None, None)
        self.lorebook_showcase_animation_list_box.adapter.last_click = ()
    # elif self.mission_setup_start_button.event_press:
    #
    #     self.remove_from_ui_updater(self.mission_menu_uis)
    #     self.back_mainmenu()
    #
    #     self.grand.run_grand()
