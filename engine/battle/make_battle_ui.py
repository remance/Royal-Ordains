from engine.uibattle.uibattle import WheelUI, PlayerPortrait, TrainingHelper


def make_battle_ui(self, battle_ui_images):
    player_portraits = {1: PlayerPortrait(battle_ui_images["health_bar"],
                                          battle_ui_images["resource_bar"], battle_ui_images["guard_bar"], 1,
                                          (250 * self.screen_scale[0], 60 * self.screen_scale[1])),
                        2: PlayerPortrait(battle_ui_images["health_bar"],
                                          battle_ui_images["resource_bar"], battle_ui_images["guard_bar"], 2,
                                          (650 * self.screen_scale[0], 60 * self.screen_scale[1])),
                        3: PlayerPortrait(battle_ui_images["health_bar"],
                                          battle_ui_images["resource_bar"], battle_ui_images["guard_bar"], 3,
                                          (1250 * self.screen_scale[0], 60 * self.screen_scale[1])),
                        4: PlayerPortrait(battle_ui_images["health_bar"],
                                          battle_ui_images["resource_bar"], battle_ui_images["guard_bar"], 4,
                                          (1650 * self.screen_scale[0], 60 * self.screen_scale[1]))}

    player_wheel_uis = {key: WheelUI(battle_ui_images, key, player_portraits[key].rect.midbottom) for key in
                        range(1, 5)}

    player_trainings = {key: TrainingHelper(battle_ui_images, key,
                                            player_portraits[key].rect.bottomleft) for key in range(1, 5)}

    return {"player_wheel_uis": player_wheel_uis, "player_portraits": player_portraits,
            "player_trainings": player_trainings}
