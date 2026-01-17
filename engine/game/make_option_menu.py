from engine.uimenu.uimenu import BrownMenuButton, TickBox, OptionMenuText, SliderMenu, ValueBox, \
    MenuButton, KeybindIcon, ListUI, GenericListAdapter


def make_option_menu(self, main_menu_buttons_box):
    """
    This method create UI in option menu and keybinding menu
    """
    # Create option menu button and icon
    config = self.config["USER"]
    keybind = self.player_key_bind_list
    font_size = int(64 * self.screen_scale[1])

    back_button = BrownMenuButton((.15, 0.5), (0.6, 0), key_name="back_button",
                                  parent=main_menu_buttons_box)
    keybind_button = BrownMenuButton((.15, 0.5), (0, 0), key_name="option_menu_keybind",
                                     parent=main_menu_buttons_box)
    default_button = BrownMenuButton((.15, 0.5), (-0.6, 0), key_name="option_menu_default",
                                     parent=main_menu_buttons_box)

    fullscreen_box = TickBox((self.screen_rect.width / 3, self.screen_rect.height / 6.5),
                             self.option_menu_images["untick"], self.option_menu_images["tick"], "fullscreen")
    fps_box = TickBox((self.screen_rect.width / 3, self.screen_rect.height / 10),
                      self.option_menu_images["untick"], self.option_menu_images["tick"], "fps")
    easy_text_box = TickBox((self.screen_rect.width * 0.6, self.screen_rect.height / 10),
                            self.option_menu_images["untick"], self.option_menu_images["tick"], "easytext")
    show_dmg_box = TickBox((self.screen_rect.width * 0.6, self.screen_rect.height / 6.5),
                           self.option_menu_images["untick"], self.option_menu_images["tick"], "showdmg")

    if int(config["full_screen"]) == 1:
        fullscreen_box.change_tick(True)
    if int(config["fps"]) == 1:
        fps_box.change_tick(True)
    if int(config["easy_text"]) == 1:
        easy_text_box.change_tick(True)
    if int(config["show_dmg_number"]) == 1:
        show_dmg_box.change_tick(True)

    fps_text = OptionMenuText(
        (fps_box.pos[0] - (fps_box.pos[0] / 5), fps_box.pos[1]),
        self.localisation.grab_text(key=("ui", "option_fps",)), font_size)
    fullscreen_text = OptionMenuText(
        (fullscreen_box.pos[0] - (fullscreen_box.pos[0] / 5), fullscreen_box.pos[1]),
        self.localisation.grab_text(key=("ui", "option_full_screen",)), font_size)
    easy_text = OptionMenuText((easy_text_box.pos[0] - (easy_text_box.pos[0] / 10), easy_text_box.pos[1]),
                               self.localisation.grab_text(key=("ui", "option_easy_text",)), font_size)
    show_dmg_text = OptionMenuText((show_dmg_box.pos[0] - (show_dmg_box.pos[0] / 10), show_dmg_box.pos[1]),
                                   self.localisation.grab_text(key=("ui", "option_show_dmg_text",)), font_size)

    # Volume change scroll bar
    scroller_images = (self.option_menu_images["scroller_box"], self.option_menu_images["scroller"])
    scroll_button_images = (
        self.option_menu_images["scroll_button_normal"], self.option_menu_images["scroll_button_click"])
    volume_slider = {"master": SliderMenu(scroller_images, scroll_button_images,
                                          (self.screen_rect.width / 2, self.screen_rect.height / 4),
                                          float(config["master_volume"])),
                     "music": SliderMenu(scroller_images, scroll_button_images,
                                         (self.screen_rect.width / 2, self.screen_rect.height / 3),
                                         float(config["music_volume"])),
                     "voice": SliderMenu(scroller_images, scroll_button_images,
                                         (self.screen_rect.width / 2, self.screen_rect.height / 2.4),
                                         float(config["voice_volume"])),
                     "effect": SliderMenu(scroller_images, scroll_button_images,
                                          (self.screen_rect.width / 2, self.screen_rect.height / 2),
                                          float(config["effect_volume"])),
                     }
    value_box = {key: ValueBox(self.option_menu_images["value"],
                               (volume_slider[key].rect.topright[0] * 1.1, volume_slider[key].rect.center[1]),
                               volume_slider[key].value, int(52 * self.screen_scale[1])) for key in volume_slider}

    volume_texts = {key: OptionMenuText((volume_slider[key].pos[0] - (volume_slider[key].pos[0] / 4.5),
                                         volume_slider[key].pos[1]),
                                        self.localisation.grab_text(key=("ui", "option_" + key + "_volume",)),
                                        font_size) for key in volume_slider}

    # Resolution changing bar that fold out the list when clicked

    resolution_drop = MenuButton(self.drop_button_lists, (self.screen_rect.width / 2, self.screen_rect.height / 1.8),
                                 key_name=str(self.screen_rect.width) + " x " + str(self.screen_rect.height), layer=151)

    resolution_bar = ListUI(pivot=(-0.15, 0.14), origin=(-1, -1), size=(0.15, 0.25),
                            items=GenericListAdapter([(0, item) for item in self.resolution_list]),
                            parent=self.screen, item_size=8, layer=1000)

    resolution_text = OptionMenuText((resolution_drop.pos[0] - (resolution_drop.pos[0] / 4.5),
                                      resolution_drop.pos[1]),
                                     self.localisation.grab_text(key=("ui", "option_display_resolution",)),
                                     font_size)

    keybind_text = {"Confirm": OptionMenuText((self.screen_rect.width / 6, self.screen_rect.height * 0.1),
                                              self.localisation.grab_text(
                                                  key=("ui", "keybind_confirm")), font_size),
                    "Menu/Cancel": OptionMenuText((self.screen_rect.width / 6, self.screen_rect.height * 0.17),
                                                  self.localisation.grab_text(
                                                      key=("ui", "keybind_menu")), font_size),
                    "Up": OptionMenuText((self.screen_rect.width / 6, self.screen_rect.height * 0.24),
                                         self.localisation.grab_text(key=("ui", "keybind_move_up")), font_size),
                    "Down": OptionMenuText((self.screen_rect.width / 6, self.screen_rect.height * 0.31),
                                           self.localisation.grab_text(key=("ui", "keybind_move_down")), font_size),
                    "Left": OptionMenuText((self.screen_rect.width / 6, self.screen_rect.height * 0.38),
                                           self.localisation.grab_text(key=("ui", "keybind_move_left")), font_size),
                    "Right": OptionMenuText((self.screen_rect.width / 6, self.screen_rect.height * 0.45),
                                            self.localisation.grab_text(key=("ui", "keybind_move_right")), font_size),
                    "Call Leader 1": OptionMenuText((self.screen_rect.width / 6, self.screen_rect.height * 0.52),
                                                    self.localisation.grab_text(key=("ui", "keybind_call_leader1")),
                                                    font_size),
                    "Call Leader 2": OptionMenuText((self.screen_rect.width / 6, self.screen_rect.height * 0.59),
                                                    self.localisation.grab_text(key=("ui", "keybind_call_leader2")),
                                                    font_size),
                    "Call Leader 3": OptionMenuText((self.screen_rect.width / 6, self.screen_rect.height * 0.66),
                                                    self.localisation.grab_text(key=("ui", "keybind_call_leader3")),
                                                    font_size),
                    "Call Troop 1": OptionMenuText((self.screen_rect.width / 2.1, self.screen_rect.height * 0.1),
                                                   self.localisation.grab_text(key=("ui", "keybind_call_troop1")),
                                                   font_size),
                    "Call Troop 2": OptionMenuText((self.screen_rect.width / 2.1, self.screen_rect.height * 0.17),
                                                   self.localisation.grab_text(key=("ui", "keybind_call_troop2")),
                                                   font_size),
                    "Call Troop 3": OptionMenuText((self.screen_rect.width / 2.1, self.screen_rect.height * 0.24),
                                                   self.localisation.grab_text(key=("ui", "keybind_call_troop3")),
                                                   font_size),
                    "Call Troop 4": OptionMenuText((self.screen_rect.width / 2.1, self.screen_rect.height * 0.31),
                                                   self.localisation.grab_text(key=("ui", "keybind_call_troop4")),
                                                   font_size),
                    "Call Troop 5": OptionMenuText((self.screen_rect.width / 2.1, self.screen_rect.height * 0.38),
                                                   self.localisation.grab_text(key=("ui", "keybind_call_troop5")),
                                                   font_size),
                    "Call Air 1": OptionMenuText((self.screen_rect.width / 2.1, self.screen_rect.height * 0.45),
                                                 self.localisation.grab_text(key=("ui", "keybind_call_air1")),
                                                 font_size),
                    "Call Air 2": OptionMenuText((self.screen_rect.width / 2.1, self.screen_rect.height * 0.52),
                                                 self.localisation.grab_text(key=("ui", "keybind_call_air2")),
                                                 font_size),
                    "Call Air 3": OptionMenuText((self.screen_rect.width / 2.1, self.screen_rect.height * 0.59),
                                                 self.localisation.grab_text(key=("ui", "keybind_call_air3")),
                                                 font_size),
                    "Call Air 4": OptionMenuText((self.screen_rect.width / 2.1, self.screen_rect.height * 0.66),
                                                 self.localisation.grab_text(key=("ui", "keybind_call_air4")),
                                                 font_size),
                    "Call Air 5": OptionMenuText((self.screen_rect.width / 2.1, self.screen_rect.height * 0.73),
                                                 self.localisation.grab_text(key=("ui", "keybind_call_air5")),
                                                 font_size),
                    "Strategy 1": OptionMenuText((self.screen_rect.width / 1.2, self.screen_rect.height * 0.1),
                                                 self.localisation.grab_text(key=("ui", "keybind_select_strategy1")),
                                                 font_size),
                    "Strategy 2": OptionMenuText((self.screen_rect.width / 1.2, self.screen_rect.height * 0.17),
                                                 self.localisation.grab_text(key=("ui", "keybind_select_strategy2")),
                                                 font_size),
                    "Strategy 3": OptionMenuText((self.screen_rect.width / 1.2, self.screen_rect.height * 0.24),
                                                 self.localisation.grab_text(key=("ui", "keybind_select_strategy3")),
                                                 font_size),
                    "Strategy 4": OptionMenuText((self.screen_rect.width / 1.2, self.screen_rect.height * 0.31),
                                                 self.localisation.grab_text(key=("ui", "keybind_select_strategy4")),
                                                 font_size),
                    "Strategy 5": OptionMenuText((self.screen_rect.width / 1.2, self.screen_rect.height * 0.38),
                                                 self.localisation.grab_text(key=("ui", "keybind_select_strategy5")),
                                                 font_size),
                    }

    keybind_icon = {"Confirm": KeybindIcon((self.screen_rect.width / 4, keybind_text["Confirm"].rect.centery),
                                           font_size, keybind["Confirm"]),
                    "Menu/Cancel": KeybindIcon((self.screen_rect.width / 4, keybind_text["Menu/Cancel"].rect.centery),
                                               font_size, keybind["Menu/Cancel"]),
                    "Up": KeybindIcon((self.screen_rect.width / 4, keybind_text["Up"].rect.centery), font_size,
                                      keybind["Up"]),
                    "Down": KeybindIcon((self.screen_rect.width / 4, keybind_text["Down"].rect.centery), font_size,
                                        keybind["Down"]),
                    "Left": KeybindIcon((self.screen_rect.width / 4, keybind_text["Left"].rect.centery), font_size,
                                        keybind["Left"]),
                    "Right": KeybindIcon((self.screen_rect.width / 4, keybind_text["Right"].rect.centery), font_size,
                                         keybind["Right"]),
                    "Call Leader 1": KeybindIcon((self.screen_rect.width / 4,
                                                  keybind_text["Call Leader 1"].rect.centery), font_size,
                                                 keybind["Call Leader 1"]),
                    "Call Leader 2": KeybindIcon((self.screen_rect.width / 4,
                                                  keybind_text["Call Leader 2"].rect.centery), font_size,
                                                 keybind["Call Leader 2"]),
                    "Call Leader 3": KeybindIcon((self.screen_rect.width / 4,
                                                  keybind_text["Call Leader 3"].rect.centery), font_size,
                                                 keybind["Call Leader 3"]),
                    "Call Troop 1": KeybindIcon(
                        (self.screen_rect.width / 1.8, keybind_text["Call Troop 1"].rect.centery), font_size,
                        keybind["Call Troop 1"]),
                    "Call Troop 2": KeybindIcon(
                        (self.screen_rect.width / 1.8, keybind_text["Call Troop 2"].rect.centery),
                        font_size, keybind["Call Troop 2"]),
                    "Call Troop 3": KeybindIcon(
                        (self.screen_rect.width / 1.8, keybind_text["Call Troop 3"].rect.centery),
                        font_size,
                        keybind["Call Troop 3"]),
                    "Call Troop 4": KeybindIcon(
                        (self.screen_rect.width / 1.8, keybind_text["Call Troop 4"].rect.centery),
                        font_size,
                        keybind["Call Troop 4"]),
                    "Call Troop 5": KeybindIcon(
                        (self.screen_rect.width / 1.8, keybind_text["Call Troop 5"].rect.centery),
                        font_size,
                        keybind["Call Troop 5"]),
                    "Call Air 1": KeybindIcon((self.screen_rect.width / 1.8, keybind_text["Call Air 1"].rect.centery),
                                              font_size,
                                              keybind["Call Air 1"]),
                    "Call Air 2": KeybindIcon((self.screen_rect.width / 1.8, keybind_text["Call Air 2"].rect.centery),
                                              font_size, keybind["Call Air 2"]),
                    "Call Air 3": KeybindIcon((self.screen_rect.width / 1.8, keybind_text["Call Air 3"].rect.centery),
                                              font_size,
                                              keybind["Call Air 3"]),
                    "Call Air 4": KeybindIcon((self.screen_rect.width / 1.8, keybind_text["Call Air 4"].rect.centery),
                                              font_size,
                                              keybind["Call Air 4"]),
                    "Call Air 5": KeybindIcon((self.screen_rect.width / 1.8, keybind_text["Call Air 5"].rect.centery),
                                              font_size,
                                              keybind["Call Air 5"]),
                    "Strategy 1": KeybindIcon((self.screen_rect.width / 1.1, keybind_text["Strategy 1"].rect.centery),
                                              font_size, keybind["Strategy 1"]),
                    "Strategy 2": KeybindIcon((self.screen_rect.width / 1.1, keybind_text["Strategy 2"].rect.centery),
                                              font_size, keybind["Strategy 2"]),
                    "Strategy 3": KeybindIcon((self.screen_rect.width / 1.1, keybind_text["Strategy 3"].rect.centery),
                                              font_size, keybind["Strategy 3"]),
                    "Strategy 4": KeybindIcon((self.screen_rect.width / 1.1, keybind_text["Strategy 4"].rect.centery),
                                              font_size, keybind["Strategy 4"]),
                    "Strategy 5": KeybindIcon((self.screen_rect.width / 1.1, keybind_text["Strategy 5"].rect.centery),
                                              font_size, keybind["Strategy 5"]),
                    }

    return {"back_button": back_button, "keybind_button": keybind_button,
            "default_button": default_button, "resolution_drop": resolution_drop,
            "resolution_bar": resolution_bar, "resolution_text": resolution_text, "volume_sliders": volume_slider,
            "value_boxes": value_box, "volume_texts": volume_texts, "fullscreen_box": fullscreen_box,
            "fullscreen_text": fullscreen_text, "fps_box": fps_box,
            "fps_text": fps_text, "keybind_text": keybind_text, "keybind_icon": keybind_icon,
            "easy_text_box": easy_text_box, "easy_text": easy_text, "show_dmg_box": show_dmg_box,
            "show_dmg_text": show_dmg_text}
