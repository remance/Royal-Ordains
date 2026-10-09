from random import randint

import pygame


def loading_screen(self, state):
    if state == "start":
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.loading_text,  # blit loading text
                         self.loading_text.get_rect(bottomright=(self.screen_width, self.screen_height)))
    elif state == "end":
        self.cursor.change_image("normal")
    else:
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.loading_text,  # blit loading text
                         self.loading_text.get_rect(bottomright=(self.screen_width, self.screen_height)))
        text_surface = self.loading_screen_lore_font.render(state, True, (255, 255, 255))
        text_rect = text_surface.get_rect(bottomleft=(0, self.screen.get_height()))
        self.screen.blit(text_surface, text_rect)
        loading_lore_text = self.grab_text(
            ("load", randint(0, len(self.localisation.text[self.language]["load"]) - 1), "Text"))
        self.loading_lore_text_popup.popup(("bottomleft", (text_rect.topleft[0],
                                                           text_rect.topleft[1] - (40 * self.screen_scale[1]))),
                                           loading_lore_text, width_text_wrapper=1600 * self.screen_scale[0],
                                           bg_colour=(0, 0, 0), font_colour=(255, 255, 255))
        self.screen.blit(self.loading_lore_text_popup.image, self.loading_lore_text_popup.rect)
    pygame.display.flip()
