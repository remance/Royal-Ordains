def drama_process(self):
    # Drama text function
    if not self.drama_timer and self.drama_text.queue:  # Start timer and draw if there is event queue
        # add to ui and realtime ui updater, so it shows when both running and pause
        self.add_to_outer_ui_menu_updater(self.drama_text)
        self.drama_text.process_queue()
        self.drama_timer = 0.1
    elif self.drama_timer:
        self.drama_text.play_animation()
        self.drama_timer += self.true_dt
        if self.drama_timer > self.drama_text.timer:
            self.drama_timer = 0
            self.remove_from_outer_ui_menu_updater(self.drama_text)
