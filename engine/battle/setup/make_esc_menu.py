from engine.uibattle.uibattle import EscButton, CharacterBaseInterface
from engine.uimenu.uimenu import SliderMenu, ValueBox, OptionMenuText
from engine.utils.data_loading import load_images


def make_esc_menu(char_selector_images, button_images, option_menu_images,
                  master_volume, music_volume, voice_volume, effect_volume):
    """create Esc menu related objects"""
    from engine.game.game import Game
    screen_scale = Game.screen_scale
    screen_rect = Game.screen_rect
    screen_width = screen_rect.width
    screen_height = screen_rect.height
    localisation = Game.localisation
    font_size = int(32 * screen_scale[1])

    player1_char_base_interface = CharacterBaseInterface((screen_width / 8, screen_height / 2.4),
                                                         char_selector_images["Profile"])
    player2_char_base_interface = CharacterBaseInterface((screen_width / 2.7, screen_height / 2.4),
                                                         char_selector_images["Profile"])
    player3_char_base_interface = CharacterBaseInterface((screen_width / 1.6, screen_height / 2.4),
                                                         char_selector_images["Profile"])
    player4_char_base_interface = CharacterBaseInterface((screen_width / 1.15, screen_height / 2.4),
                                                         char_selector_images["Profile"])
    player_char_base_interfaces = {1: player1_char_base_interface, 2: player2_char_base_interface,
                                   3: player3_char_base_interface, 4: player4_char_base_interface}

    # Create ESC Menu box and buttons
    esc_button_text_size = int(22 * screen_scale[1])

    battle_menu_button = [
        EscButton(button_images, (screen_rect.center[0] / 4.5, screen_rect.height - (20 * screen_scale[1])),
                  text="Resume", text_size=esc_button_text_size),
        EscButton(button_images, (screen_rect.center[0] / 1.9, screen_rect.height - (20 * screen_scale[1])),
                  text="Encyclopedia", text_size=esc_button_text_size),
        EscButton(button_images, (screen_rect.center[0] / 1.2, screen_rect.height - (20 * screen_scale[1])),
                  text="Option", text_size=esc_button_text_size),
        EscButton(button_images, (screen_rect.center[0] * 1.2, screen_rect.height - (20 * screen_scale[1])),
                  text="End Battle", text_size=esc_button_text_size),
        EscButton(button_images, (screen_rect.center[0] * 1.5, screen_rect.height - (20 * screen_scale[1])),
                  text="Main Menu", text_size=esc_button_text_size),
        EscButton(button_images, (screen_rect.center[0] * 1.8, screen_rect.height - (20 * screen_scale[1])),
                  text="Desktop", text_size=esc_button_text_size)]

    # Create option menu
    esc_option_menu_button = EscButton(button_images, (screen_rect.center[0], screen_rect.center[1] * 1.3),
                                       text="Confirm", text_size=esc_button_text_size)

    # Volume change scroll bar

    scroller_images = (option_menu_images["scroller_box"], option_menu_images["scroller"])
    scroll_button_images = (option_menu_images["scroll_button_normal"], option_menu_images["scroll_button_click"])
    volume_slider = {"master": SliderMenu(scroller_images, scroll_button_images,
                                          (screen_rect.width / 2, screen_rect.height / 4),
                                          master_volume),
                     "music": SliderMenu(scroller_images, scroll_button_images,
                                         (screen_rect.width / 2, screen_rect.height / 3),
                                         music_volume),
                     "voice": SliderMenu(scroller_images, scroll_button_images,
                                         (screen_rect.width / 2, screen_rect.height / 2.4),
                                         voice_volume),
                     "effect": SliderMenu(scroller_images, scroll_button_images,
                                          (screen_rect.width / 2, screen_rect.height / 2),
                                          effect_volume)}

    value_box = {key: ValueBox(option_menu_images["value"],
                               (volume_slider[key].rect.topright[0] * 1.1, volume_slider[key].rect.center[1]),
                               volume_slider[key].value, int(26 * screen_scale[1])) for key in volume_slider}

    volume_texts = {key: OptionMenuText((volume_slider[key].pos[0] - (volume_slider[key].pos[0] / 4.5),
                                         volume_slider[key].pos[1]),
                                        localisation.grab_text(key=("ui", "option_" + key + "_volume",)),
                                        font_size) for key in volume_slider}

    return {"battle_menu_button": battle_menu_button,
            "esc_option_menu_button": esc_option_menu_button,
            "esc_slider_menu": volume_slider, "esc_value_boxes": value_box, "volume_texts": volume_texts,
            "player_char_base_interfaces": player_char_base_interfaces}
