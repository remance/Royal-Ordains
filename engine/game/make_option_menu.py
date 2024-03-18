from pygame.transform import flip

from engine.uimenu.uimenu import MenuButton, TickBox, OptionMenuText, SliderMenu, ValueBox, \
    ControllerIcon, KeybindIcon, MenuImageButton
from engine.utils.data_loading import load_image, make_bar_list


def make_option_menu(self, button_image_list):
    """
    This method create UI in option menu and keybinding menu
    """
    # Create option menu button and icon
    config = self.config["USER"]
    keybind = self.player_key_bind_list[1]
    font_size = int(32 * self.screen_scale[1])

    back_button = MenuButton(button_image_list, (self.screen_rect.width / 3, self.screen_rect.height / 1.2),
                             key_name="back_button")
    keybind_button = MenuButton(button_image_list, (self.screen_rect.width / 2, self.screen_rect.height / 1.2),
                                key_name="option_menu_keybind")
    default_button = MenuButton(button_image_list, (self.screen_rect.width / 1.5, self.screen_rect.height / 1.2),
                                key_name="option_menu_default")

    fullscreen_box = TickBox((self.screen_rect.width / 3, self.screen_rect.height / 6.5),
                             self.option_menu_images["untick"], self.option_menu_images["tick"], "fullscreen")
    fps_box = TickBox((self.screen_rect.width / 3, self.screen_rect.height / 10),
                      self.option_menu_images["untick"], self.option_menu_images["tick"], "fps")
    easy_text_box = TickBox((self.screen_rect.width / 1.5, self.screen_rect.height / 10),
                            self.option_menu_images["untick"], self.option_menu_images["tick"], "easytext")

    if int(config["full_screen"]) == 1:
        fullscreen_box.change_tick(True)
    if int(config["fps"]) == 1:
        fps_box.change_tick(True)
    if int(config["easy_text"]) == 1:
        easy_text_box.change_tick(True)

    fps_text = OptionMenuText(
        (fps_box.pos[0] - (fps_box.pos[0] / 5), fps_box.pos[1]),
        self.localisation.grab_text(key=("ui", "option_fps",)), font_size)
    fullscreen_text = OptionMenuText(
        (fullscreen_box.pos[0] - (fullscreen_box.pos[0] / 5), fullscreen_box.pos[1]),
        self.localisation.grab_text(key=("ui", "option_full_screen",)), font_size)
    easy_text = OptionMenuText((easy_text_box.pos[0] - (easy_text_box.pos[0] / 10), easy_text_box.pos[1]),
                               self.localisation.grab_text(key=("ui", "option_easy_text",)), font_size)

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
                               volume_slider[key].value, int(26 * self.screen_scale[1])) for key in volume_slider}

    volume_texts = {key: OptionMenuText((volume_slider[key].pos[0] - (volume_slider[key].pos[0] / 4.5),
                                         volume_slider[key].pos[1]),
                                        self.localisation.grab_text(key=("ui", "option_" + key + "_volume",)),
                                        font_size) for key in volume_slider}

    # Resolution changing bar that fold out the list when clicked
    image = load_image(self.data_dir, self.screen_scale, "drop_normal.jpg", ("ui", "mainmenu_ui"))
    image2 = image
    image3 = load_image(self.data_dir, self.screen_scale, "drop_click.jpg", ("ui", "mainmenu_ui"))
    button_image_list = [image, image2, image3]
    resolution_drop = MenuButton(button_image_list, (self.screen_rect.width / 2, self.screen_rect.height / 1.8),
                                 key_name=str(self.screen_rect.width) + " x " + str(self.screen_rect.height),
                                 font_size=int(30 * self.screen_scale[1]))

    resolution_bar = make_bar_list(self.data_dir, self.screen_scale, self.resolution_list, resolution_drop)

    resolution_text = OptionMenuText((resolution_drop.pos[0] - (resolution_drop.pos[0] / 4.5),
                                      resolution_drop.pos[1]),
                                     self.localisation.grab_text(key=("ui", "option_display_resolution",)),
                                     font_size)

    keybind_text = {"Weak": OptionMenuText((self.screen_rect.width / 4, self.screen_rect.height / 5),
                                           self.localisation.grab_text(
                                               key=("ui", "keybind_weak_attack",)), font_size,
                                           button_image=self.battle_ui_images["button_weak"]),
                    "Strong": OptionMenuText((self.screen_rect.width / 4, self.screen_rect.height / 3.5),
                                             self.localisation.grab_text(
                                                 key=("ui", "keybind_strong_attack",)), font_size,
                                             button_image=self.battle_ui_images["button_strong"]),
                    "Guard": OptionMenuText((self.screen_rect.width / 4, self.screen_rect.height / 2.5),
                                            self.localisation.grab_text(key=("ui", "keybind_guard",)), font_size,
                                            button_image=self.battle_ui_images["button_guard"]),
                    "Special": OptionMenuText((self.screen_rect.width / 4, self.screen_rect.height / 2),
                                              self.localisation.grab_text(key=("ui", "keybind_special",)), font_size,
                                              button_image=self.battle_ui_images["button_special"]),
                    "Left": OptionMenuText((self.screen_rect.width / 4, self.screen_rect.height / 1.7),
                                           self.localisation.grab_text(key=("ui", "keybind_move_left",)), font_size,
                                           button_image=self.battle_ui_images["button_left"]),
                    "Right": OptionMenuText((self.screen_rect.width / 4, self.screen_rect.height / 1.5),
                                            self.localisation.grab_text(key=("ui", "keybind_move_right",)), font_size,
                                            button_image=self.battle_ui_images["button_right"]),
                    "Up": OptionMenuText((self.screen_rect.width / 1.5, self.screen_rect.height / 5),
                                         self.localisation.grab_text(key=("ui", "keybind_move_up",)), font_size,
                                         button_image=self.battle_ui_images["button_up"]),
                    "Down": OptionMenuText((self.screen_rect.width / 1.5, self.screen_rect.height / 3.5),
                                           self.localisation.grab_text(key=("ui", "keybind_move_down",)), font_size,
                                           button_image=self.battle_ui_images["button_down"]),
                    "Menu/Cancel": OptionMenuText((self.screen_rect.width / 1.5, self.screen_rect.height / 2.5),
                                                  self.localisation.grab_text(key=("ui", "keybind_menu",)), font_size,
                                                  button_image=self.battle_ui_images["button_menu"]),
                    "Order Menu": OptionMenuText((self.screen_rect.width / 1.5, self.screen_rect.height / 2),
                                                 self.localisation.grab_text(key=("ui", "keybind_order_menu",)),
                                                 font_size,
                                                 button_image=self.battle_ui_images["button_order"]),
                    "Inventory Menu": OptionMenuText((self.screen_rect.width / 1.5, self.screen_rect.height / 1.7),
                                                     self.localisation.grab_text(key=("ui", "keybind_inventory_menu",)),
                                                     font_size, button_image=self.battle_ui_images["button_inventory"])
                    }

    control_type = "keyboard"  # make default keyboard for now, get changed later when player enter keybind menu

    keybind = keybind[control_type]

    control_switch = ControllerIcon((self.screen_rect.width / 2, self.screen_rect.height * 0.1),
                                    self.option_menu_images, control_type)

    control_player_next = MenuImageButton((self.screen_rect.width / 1.7, self.screen_rect.height * 0.1),
                                          self.option_menu_images["change"])
    control_player_back = MenuImageButton((self.screen_rect.width / 2.5, self.screen_rect.height * 0.1),
                                          flip(self.option_menu_images["change"], True, False))

    keybind_icon = {"Weak": KeybindIcon((self.screen_rect.width / 3, self.screen_rect.height / 5),
                                        font_size, control_type, keybind["Weak"]),
                    "Strong": KeybindIcon((self.screen_rect.width / 3, self.screen_rect.height / 3.5),
                                          font_size, control_type,
                                          keybind["Strong"]),
                    "Guard": KeybindIcon((self.screen_rect.width / 3, self.screen_rect.height / 2.5), font_size,
                                         control_type, keybind["Guard"]),
                    "Special": KeybindIcon((self.screen_rect.width / 3, self.screen_rect.height / 2), font_size,
                                           control_type, keybind["Special"]),
                    "Left": KeybindIcon((self.screen_rect.width / 3, self.screen_rect.height / 1.7), font_size,
                                        control_type, keybind["Left"]),
                    "Right": KeybindIcon((self.screen_rect.width / 3, self.screen_rect.height / 1.5), font_size,
                                         control_type, keybind["Right"]),
                    "Up": KeybindIcon((self.screen_rect.width / 1.3, self.screen_rect.height / 5), font_size,
                                      control_type, keybind["Up"]),
                    "Down": KeybindIcon((self.screen_rect.width / 1.3, self.screen_rect.height / 3.5), font_size,
                                        control_type, keybind["Down"]),
                    "Menu/Cancel": KeybindIcon((self.screen_rect.width / 1.3, self.screen_rect.height / 2.5), font_size,
                                               control_type, keybind["Menu/Cancel"]),
                    "Order Menu": KeybindIcon((self.screen_rect.width / 1.3, self.screen_rect.height / 2), font_size,
                                              control_type, keybind["Order Menu"]),
                    "Inventory Menu": KeybindIcon((self.screen_rect.width / 1.3, self.screen_rect.height / 1.7),
                                                  font_size,
                                                  control_type, keybind["Inventory Menu"])}

    return {"back_button": back_button, "keybind_button": keybind_button,
            "default_button": default_button, "resolution_drop": resolution_drop,
            "resolution_bar": resolution_bar, "resolution_text": resolution_text, "volume_sliders": volume_slider,
            "value_boxes": value_box, "volume_texts": volume_texts, "fullscreen_box": fullscreen_box,
            "fullscreen_text": fullscreen_text, "fps_box": fps_box,
            "fps_text": fps_text, "keybind_text": keybind_text, "keybind_icon": keybind_icon,
            "control_switch": control_switch, "control_player_next": control_player_next,
            "control_player_back": control_player_back, "easy_text_box": easy_text_box, "easy_text": easy_text}
