def drama_process(self):
    # Drama text function
    if not self.drama_timer and self.drama_text.queue:  # Start timer and draw if there is event queue
        # add to ui and realtime ui updater, so it shows when both running and pause
        self.realtime_ui_updater.add(self.drama_text)
        self.add_ui_updater(self.drama_text)
        self.drama_text.process_queue()
        self.drama_timer = 0.1
    elif self.drama_timer:
        self.drama_text.play_animation()
        self.drama_timer += self.ui_dt
        if self.drama_timer > 5:  # drama popup last for 5 seconds
            self.drama_timer = 0
            self.realtime_ui_updater.remove(self.drama_text)
            self.remove_ui_updater(self.drama_text)
