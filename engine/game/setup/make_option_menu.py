from pygame.transform import flip

from engine.uimenu.uimenu import MenuButton, TickBox, OptionMenuText, SliderMenu, ValueBox, \
    ControllerIcon, KeybindIcon, MenuImageButton
from engine.utils.data_loading import load_image, load_images, make_bar_list


def make_option_menu(button_image_list, config, keybind):
    """
    This method create UI in option menu and keybinding menu
    """
    # Create option menu button and icon
    from engine.game.game import Game
    data_dir = Game.data_dir
    localisation = Game.localisation
    resolution_list = Game.resolution_list
    screen_scale = Game.screen_scale
    screen_rect = Game.screen_rect
    font_size = int(32 * screen_scale[1])

    back_button = MenuButton(button_image_list, (screen_rect.width / 3, screen_rect.height / 1.2),
                             key_name="back_button")
    keybind_button = MenuButton(button_image_list, (screen_rect.width / 2, screen_rect.height / 1.2),
                                key_name="option_menu_keybind")
    default_button = MenuButton(button_image_list, (screen_rect.width / 1.5, screen_rect.height / 1.2),
                                key_name="option_menu_default")

    option_menu_image = load_images(data_dir, screen_scale=screen_scale,
                                    subfolder=("ui", "option_ui"))

    fullscreen_box = TickBox((screen_rect.width / 3, screen_rect.height / 6.5),
                             option_menu_image["untick"], option_menu_image["tick"], "fullscreen")
    fps_box = TickBox((screen_rect.width / 3, screen_rect.height / 10),
                      option_menu_image["untick"], option_menu_image["tick"], "fps")
    easy_text_box = TickBox((screen_rect.width / 1.5, screen_rect.height / 10),
                            option_menu_image["untick"], option_menu_image["tick"], "easytext")

    if int(config["full_screen"]) == 1:
        fullscreen_box.change_tick(True)
    if int(config["fps"]) == 1:
        fps_box.change_tick(True)
    if int(config["easy_text"]) == 1:
        easy_text_box.change_tick(True)

    fps_text = OptionMenuText(
        (fps_box.pos[0] - (fps_box.pos[0] / 5), fps_box.pos[1]),
        localisation.grab_text(key=("ui", "option_fps",)), font_size)
    fullscreen_text = OptionMenuText(
        (fullscreen_box.pos[0] - (fullscreen_box.pos[0] / 5), fullscreen_box.pos[1]),
        localisation.grab_text(key=("ui", "option_full_screen",)), font_size)
    easy_text = OptionMenuText((easy_text_box.pos[0] - (easy_text_box.pos[0] / 10), easy_text_box.pos[1]),
                               localisation.grab_text(key=("ui", "option_easy_text",)), font_size)

    # Volume change scroll bar
    option_menu_slider_images = load_images(data_dir, screen_scale=screen_scale,
                                            subfolder=("ui", "option_ui", "slider"))
    scroller_images = (option_menu_slider_images["scroller_box"], option_menu_slider_images["scroller"])
    scroll_button_images = (
        option_menu_slider_images["scroll_button_normal"], option_menu_slider_images["scroll_button_click"])
    volume_slider = {"master": SliderMenu(scroller_images, scroll_button_images,
                                          (screen_rect.width / 2, screen_rect.height / 4),
                                          float(config["master_volume"])),
                     "music": SliderMenu(scroller_images, scroll_button_images,
                                         (screen_rect.width / 2, screen_rect.height / 3),
                                         float(config["music_volume"])),
                     "voice": SliderMenu(scroller_images, scroll_button_images,
                                         (screen_rect.width / 2, screen_rect.height / 2.4),
                                         float(config["voice_volume"])),
                     "effect": SliderMenu(scroller_images, scroll_button_images,
                                          (screen_rect.width / 2, screen_rect.height / 2),
                                          float(config["effect_volume"])),
                     }
    value_box = {key: ValueBox(option_menu_slider_images["value"],
                               (volume_slider[key].rect.topright[0] * 1.1, volume_slider[key].rect.center[1]),
                               volume_slider[key].value, int(26 * screen_scale[1])) for key in volume_slider}

    volume_texts = {key: OptionMenuText((volume_slider[key].pos[0] - (volume_slider[key].pos[0] / 4.5),
                                         volume_slider[key].pos[1]),
                                        localisation.grab_text(key=("ui", "option_" + key + "_volume",)),
                                        font_size) for key in volume_slider}

    # Resolution changing bar that fold out the list when clicked
    image = load_image(data_dir, screen_scale, "drop_normal.jpg", ("ui", "mainmenu_ui"))
    image2 = image
    image3 = load_image(data_dir, screen_scale, "drop_click.jpg", ("ui", "mainmenu_ui"))
    button_image_list = [image, image2, image3]
    resolution_drop = MenuButton(button_image_list, (screen_rect.width / 2, screen_rect.height / 1.8),
                                 key_name=str(screen_rect.width) + " x " + str(screen_rect.height),
                                 font_size=int(30 * screen_scale[1]))

    resolution_bar = make_bar_list(data_dir, screen_scale, resolution_list, resolution_drop)

    resolution_text = OptionMenuText((resolution_drop.pos[0] - (resolution_drop.pos[0] / 4.5),
                                      resolution_drop.pos[1]),
                                     localisation.grab_text(key=("ui", "option_display_resolution",)),
                                     font_size)

    keybind_text = {"Weak": OptionMenuText((screen_rect.width / 4, screen_rect.height / 5),
                                           localisation.grab_text(
                                               key=("ui", "keybind_weak_attack",)), font_size),
                    "Strong": OptionMenuText((screen_rect.width / 4, screen_rect.height / 3.5),
                                             localisation.grab_text(
                                                 key=("ui", "keybind_strong_attack",)), font_size),
                    "Guard": OptionMenuText((screen_rect.width / 4, screen_rect.height / 2.5),
                                            localisation.grab_text(key=("ui", "keybind_guard",)), font_size),
                    "Special": OptionMenuText((screen_rect.width / 4, screen_rect.height / 2),
                                              localisation.grab_text(key=("ui", "keybind_special",)), font_size),
                    "Left": OptionMenuText((screen_rect.width / 4, screen_rect.height / 1.7),
                                           localisation.grab_text(key=("ui", "keybind_move_left",)), font_size),
                    "Right": OptionMenuText((screen_rect.width / 4, screen_rect.height / 1.5),
                                            localisation.grab_text(key=("ui", "keybind_move_right",)), font_size),
                    "Up": OptionMenuText((screen_rect.width / 2, screen_rect.height / 5),
                                         localisation.grab_text(key=("ui", "keybind_move_up",)), font_size),
                    "Down": OptionMenuText((screen_rect.width / 2, screen_rect.height / 3.5),
                                           localisation.grab_text(key=("ui", "keybind_move_down",)), font_size),
                    "Menu/Cancel": OptionMenuText((screen_rect.width / 2, screen_rect.height / 2.5),
                                                  localisation.grab_text(key=("ui", "keybind_menu",)), font_size),
                    "Order Menu": OptionMenuText((screen_rect.width / 2, screen_rect.height / 2),
                                                 localisation.grab_text(key=("ui", "keybind_order_menu",)), font_size),
                    "Inventory Menu": OptionMenuText((screen_rect.width / 2, screen_rect.height / 1.7),
                                                     localisation.grab_text(key=("ui", "keybind_inventory_menu",)), font_size)
                    }

    control_type = "keyboard"  # make default keyboard for now, get changed later when player enter keybind menu

    keybind = keybind[control_type]

    control_images = load_images(data_dir, screen_scale=screen_scale, subfolder=("ui", "option_ui"))
    control_switch = ControllerIcon((screen_rect.width / 2, screen_rect.height * 0.1),
                                    control_images, control_type)

    control_player_next = MenuImageButton((screen_rect.width / 1.7, screen_rect.height * 0.1),
                                          control_images["change"])
    control_player_back = MenuImageButton((screen_rect.width / 2.5, screen_rect.height * 0.1),
                                          flip(control_images["change"], True, False))

    keybind_icon = {"Weak": KeybindIcon((screen_rect.width / 3, screen_rect.height / 5),
                                        font_size, control_type, keybind["Weak"]),
                    "Strong": KeybindIcon((screen_rect.width / 3, screen_rect.height / 3.5),
                                          font_size, control_type,
                                          keybind["Strong"]),
                    "Guard": KeybindIcon((screen_rect.width / 3, screen_rect.height / 2.5), font_size,
                                         control_type, keybind["Guard"]),
                    "Special": KeybindIcon((screen_rect.width / 3, screen_rect.height / 2), font_size,
                                           control_type, keybind["Special"]),
                    "Left": KeybindIcon((screen_rect.width / 3, screen_rect.height / 1.7), font_size,
                                        control_type, keybind["Left"]),
                    "Right": KeybindIcon((screen_rect.width / 3, screen_rect.height / 1.5), font_size,
                                         control_type, keybind["Right"]),
                    "Up": KeybindIcon((screen_rect.width / 1.7, screen_rect.height / 5), font_size,
                                      control_type, keybind["Up"]),
                    "Down": KeybindIcon((screen_rect.width / 1.7, screen_rect.height / 3.5), font_size,
                                        control_type, keybind["Down"]),
                    "Menu/Cancel": KeybindIcon((screen_rect.width / 1.7, screen_rect.height / 2.5), font_size,
                                               control_type, keybind["Menu/Cancel"]),
                    "Order Menu": KeybindIcon((screen_rect.width / 1.7, screen_rect.height / 2), font_size,
                                              control_type, keybind["Order Menu"]),
                    "Inventory Menu": KeybindIcon((screen_rect.width / 1.7, screen_rect.height / 1.7), font_size,
                                                  control_type, keybind["Inventory Menu"])}

    return {"back_button": back_button, "keybind_button": keybind_button,
            "default_button": default_button, "resolution_drop": resolution_drop,
            "resolution_bar": resolution_bar, "resolution_text": resolution_text, "volume_sliders": volume_slider,
            "value_boxes": value_box, "volume_texts": volume_texts, "fullscreen_box": fullscreen_box,
            "fullscreen_text": fullscreen_text, "fps_box": fps_box,
            "fps_text": fps_text, "keybind_text": keybind_text, "keybind_icon": keybind_icon,
            "control_switch": control_switch, "control_player_next": control_player_next,
            "control_player_back": control_player_back, "easy_text_box": easy_text_box, "easy_text": easy_text}
