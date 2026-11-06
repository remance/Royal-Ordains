from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.battle.battle import Battle


def state_result_process(self: Battle):
    # update battle scene first here
    camera = self.camera
    self.scene.update()
    camera.update(self.battle_camera_object_drawer)

    camera.update(self.battle_camera_ui_drawer)
    self.outer_ui_updater.update(self.true_dt)

    camera.out_update(self.outer_ui_drawer)
    self.ui_menu_updater.update(self.true_dt)
    self.ui_menu_drawer.draw(self.screen)  # draw the UI

    if self.out_of_battle_result_button.event_press or self.esc_press:
        self.remove_from_outer_ui_menu_updater(self.out_of_battle_result_button, self.battle_result_ui)
        self.back_to_battle_state()
        self.battle_helper_ui.battle_end("normal")
        return True
