def common_process(self):
    """process that should be run in most battle state"""
    if self.sound_effect_queue:
        for key, value in self.sound_effect_queue.items():  # play each sound effect initiate in this loop
            self.play_sound_effect(key, value)
        self.sound_effect_queue = {}

    self.drama_process()
