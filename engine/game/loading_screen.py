import pygame


def loading_screen(self, state):
    if state == "start":
        self.screen.blit(self.loading, (0, 0))  # blit loading screen
    elif state == "end":
        self.cursor.change_image("normal")
    else:
        loading = self.loading.copy()
        text_surface = self.loading_screen_lore_font.render(state, True, (255, 255, 255))
        text_rect = text_surface.get_rect(bottomleft=(0, self.screen.get_height()))
        loading.blit(text_surface, text_rect)

        self.loading_lore_text_popup.popup(("bottomleft", (text_rect.topleft[0],
                                                           text_rect.topleft[1] - (40 * self.screen_scale[1]))),
                                           self.loading_lore_text, width_text_wrapper=1600 * self.screen_scale[0],
                                           bg_colour=(0, 0, 0), font_colour=(255, 255, 255))
        loading.blit(self.loading_lore_text_popup.image, self.loading_lore_text_popup.rect)
        self.screen.blit(loading, (0, 0))
    pygame.display.flip()
