from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.grand.grand import Grand

from engine.uimenu.uimenu import BrownMenuButton, BoxUI, SliderMenu, ValueBox, OptionMenuText


def make_esc_menu(self: Grand):
    """create Esc menu related objects"""
    font_size = int(64 * self.screen_scale[1])

    # Create ESC Menu box and buttons
    main_menu_buttons_box = BoxUI((0, 0.5),
                                  (self.screen_width / 5, self.screen_height / 2), parent=self.screen)
    grand_menu_button = {
        "resume": BrownMenuButton((1, .15), (0, -0.8), key_name="button_resume", parent=main_menu_buttons_box),
        "save": BrownMenuButton((1, .15), (0, -0.4), key_name="button_save", parent=main_menu_buttons_box),
        "option": BrownMenuButton((1, .15), (0, 0), key_name="button_game_option", parent=main_menu_buttons_box),
        "end": BrownMenuButton((1, .15), (0, 0.4), key_name="button_end_grand", parent=main_menu_buttons_box),
        "quit": BrownMenuButton((1, .15), (0, 0.8), key_name="button_game_quit", parent=main_menu_buttons_box)}

    # Create option menu
    esc_option_menu_button = BrownMenuButton((1, .15), (0, 0.9),
                                             key_name="button_confirm", parent=main_menu_buttons_box)

    # Volume change scroll bar
    scroller_images = (self.game.option_menu_images["scroller_box"], self.game.option_menu_images["scroller"])
    scroll_button_images = (
        self.game.option_menu_images["scroll_button_normal"], self.game.option_menu_images["scroll_button_click"])
    volume_sliders = {"master": SliderMenu(scroller_images, scroll_button_images,
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

    value_boxes = {key: ValueBox(self.game.option_menu_images["value"],
                                 (volume_sliders[key].rect.topright[0] * 1.1, volume_sliders[key].rect.center[1]),
                                 volume_sliders[key].value, self.game.large_generic_ui_font) for key in volume_sliders}
    for key, value in volume_sliders.items():
        value.value_box = value_boxes[key]

    volume_texts = {key: OptionMenuText((volume_sliders[key].pos[0] - (volume_sliders[key].pos[0] / 4.5),
                                         volume_sliders[key].pos[1]),
                                        self.grab_text(key=("ui", "option_" + key + "_volume",)),
                                        font_size) for key in volume_sliders}

    return {"grand_menu_button": grand_menu_button,
            "esc_option_menu_button": esc_option_menu_button,
            "esc_slider_menu": volume_sliders, "esc_value_boxes": value_boxes, "volume_texts": volume_texts}
