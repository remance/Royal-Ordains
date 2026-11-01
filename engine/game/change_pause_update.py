def change_pause_update(self, pause, except_list=()):
    for item in self.ui_menu_updater:
        if item not in except_list:
            item.pause = pause
