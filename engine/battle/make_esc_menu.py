from engine.uibattle.uibattle import EscButton, CharacterBaseInterface
from engine.uimenu.uimenu import SliderMenu, ValueBox, OptionMenuText, ListUI, ListAdapter


def make_esc_menu(self):
    """create Esc menu related objects"""
    font_size = int(32 * self.screen_scale[1])

    player1_char_base_interface = CharacterBaseInterface((self.screen_width / 8, self.screen_height / 2.4),
                                                         self.game.char_selector_images["Profile"])
    player2_char_base_interface = CharacterBaseInterface((self.screen_width / 2.7, self.screen_height / 2.4),
                                                         self.game.char_selector_images["Profile"])
    player3_char_base_interface = CharacterBaseInterface((self.screen_width / 1.6, self.screen_height / 2.4),
                                                         self.game.char_selector_images["Profile"])
    player4_char_base_interface = CharacterBaseInterface((self.screen_width / 1.15, self.screen_height / 2.4),
                                                         self.game.char_selector_images["Profile"])
    player_char_base_interfaces = {1: player1_char_base_interface, 2: player2_char_base_interface,
                                   3: player3_char_base_interface, 4: player4_char_base_interface}

    # Create ESC Menu box and buttons
    esc_button_text_size = int(22 * self.screen_scale[1])

    battle_menu_button = [
        EscButton(self.game.button_images,
                  (self.screen_rect.center[0] / 7, self.screen_rect.height - (20 * self.screen_scale[1])),
                  text="Resume", text_size=esc_button_text_size),
        EscButton(self.game.button_images,
                  (self.screen_rect.center[0] / 2.55, self.screen_rect.height - (20 * self.screen_scale[1])),
                  text="Encyclopedia", text_size=esc_button_text_size),
        EscButton(self.game.button_images,
                  (self.screen_rect.center[0] / 1.55, self.screen_rect.height - (20 * self.screen_scale[1])),
                  text="Dialogue Log", text_size=esc_button_text_size),
        EscButton(self.game.button_images,
                  (self.screen_rect.center[0], self.screen_rect.height - (20 * self.screen_scale[1])),
                  text="Option", text_size=esc_button_text_size),
        EscButton(self.game.button_images,
                  (self.screen_rect.center[0] * 1.35, self.screen_rect.height - (20 * self.screen_scale[1])),
                  text="End Battle", text_size=esc_button_text_size),
        EscButton(self.game.button_images,
                  (self.screen_rect.center[0] * 1.6, self.screen_rect.height - (20 * self.screen_scale[1])),
                  text="Main Menu", text_size=esc_button_text_size),
        EscButton(self.game.button_images,
                  (self.screen_rect.center[0] * 1.85, self.screen_rect.height - (20 * self.screen_scale[1])),
                  text="Desktop", text_size=esc_button_text_size)]

    dialogue_box = ListUI(pivot=(-0.9, -0.9), origin=(-1, -1), size=(.9, .8),
                          items=ListAdapter(["None"]), parent=self.screen, item_size=10)

    esc_dialogue_button = EscButton(self.game.button_images,
                                    (self.screen_rect.center[0], self.screen_rect.center[1] * 1.8),
                                    text="Close", text_size=esc_button_text_size)

    # Create option menu
    esc_option_menu_button = EscButton(self.game.button_images,
                                       (self.screen_rect.center[0], self.screen_rect.center[1] * 1.3),
                                       text="Confirm", text_size=esc_button_text_size)

    # Volume change scroll bar

    scroller_images = (self.game.option_menu_images["scroller_box"], self.game.option_menu_images["scroller"])
    scroll_button_images = (
    self.game.option_menu_images["scroll_button_normal"], self.game.option_menu_images["scroll_button_click"])
    volume_slider = {"master": SliderMenu(scroller_images, scroll_button_images,
                                          (self.screen_rect.width / 2, self.screen_rect.height / 4),
                                          self.master_volume),
                     "music": SliderMenu(scroller_images, scroll_button_images,
                                         (self.screen_rect.width / 2, self.screen_rect.height / 3),
                                         self.music_volume),
                     "voice": SliderMenu(scroller_images, scroll_button_images,
                                         (self.screen_rect.width / 2, self.screen_rect.height / 2.4),
                                         self.voice_volume),
                     "effect": SliderMenu(scroller_images, scroll_button_images,
                                          (self.screen_rect.width / 2, self.screen_rect.height / 2),
                                          self.effect_volume)}

    value_box = {key: ValueBox(self.game.option_menu_images["value"],
                               (volume_slider[key].rect.topright[0] * 1.1, volume_slider[key].rect.center[1]),
                               volume_slider[key].value, int(26 * self.screen_scale[1])) for key in volume_slider}

    volume_texts = {key: OptionMenuText((volume_slider[key].pos[0] - (volume_slider[key].pos[0] / 4.5),
                                         volume_slider[key].pos[1]),
                                        self.localisation.grab_text(key=("ui", "option_" + key + "_volume",)),
                                        font_size) for key in volume_slider}

    return {"battle_menu_button": battle_menu_button,
            "esc_option_menu_button": esc_option_menu_button,
            "esc_slider_menu": volume_slider, "esc_value_boxes": value_box, "volume_texts": volume_texts,
            "player_char_base_interfaces": player_char_base_interfaces, "dialogue_box": dialogue_box,
            "esc_dialogue_button": esc_dialogue_button}
