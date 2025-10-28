from engine.uimenu.uimenu import BoxUI, BrownMenuButton, InputBox


def make_input_box(self):
    """Input box popup"""
    input_ui = BoxUI((0, 0.5), (self.screen_rect.width / 2, self.screen_rect.height / 2), parent=self.screen,
                     layer=10000)  # user text input ui box popup
    input_button_box = BoxUI((-1, -7), (input_ui.rect[2], input_ui.rect[3] * 0.15), parent=input_ui.image,
                             layer=10000)   # user text input ui box popup
    input_ok_button = BrownMenuButton((.25, 1), (0.65, 0), key_name="confirm_button", parent=input_button_box)
    input_close_button = BrownMenuButton((.25, 1), (0, 0), key_name="close_button", parent=input_button_box)
    input_cancel_button = BrownMenuButton((.25, 1), (-0.65, 0), key_name="cancel_button", parent=input_button_box)

    input_box = InputBox(input_ui.rect.center, input_ui.image.get_width(), layer=10001)  # user text input box

    return {"input_ui": input_ui, "input_ok_button": input_ok_button, "input_close_button": input_close_button,
            "input_cancel_button": input_cancel_button, "input_box": input_box}
