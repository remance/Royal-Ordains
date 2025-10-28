def back_mainmenu(self):
    self.menu_state = "main_menu"
    self.add_ui_updater(*self.main_menu_buttons)
    self.remove_ui_updater(self.hide_background)
