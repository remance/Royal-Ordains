from engine.uibattle.uibattle import WheelUI, PlayerPortrait


def make_battle_ui(battle_ui_image):
    from engine.game.game import Game
    screen_scale = Game.screen_scale

    player_1_portrait = PlayerPortrait(battle_ui_image["health_bar"],
                                       battle_ui_image["resource_bar"], battle_ui_image["guard_bar"],
                                       (250 * screen_scale[0], 60 * screen_scale[1]))

    player_2_portrait = PlayerPortrait(battle_ui_image["health_bar"],
                                       battle_ui_image["resource_bar"], battle_ui_image["guard_bar"],
                                       (650 * screen_scale[0], 60 * screen_scale[1]))

    player_3_portrait = PlayerPortrait(battle_ui_image["health_bar"],
                                       battle_ui_image["resource_bar"], battle_ui_image["guard_bar"],
                                       (1250 * screen_scale[0], 60 * screen_scale[1]))

    player_4_portrait = PlayerPortrait(battle_ui_image["health_bar"],
                                       battle_ui_image["resource_bar"], battle_ui_image["guard_bar"],
                                       (1650 * screen_scale[0], 60 * screen_scale[1]))

    player_1_wheel_ui = WheelUI(battle_ui_image, 1, player_1_portrait.rect.midbottom)
    player_2_wheel_ui = WheelUI(battle_ui_image, 2, player_2_portrait.rect.midbottom)
    player_3_wheel_ui = WheelUI(battle_ui_image, 3, player_3_portrait.rect.midbottom)
    player_4_wheel_ui = WheelUI(battle_ui_image, 4, player_4_portrait.rect.midbottom)

    return {"player_1_wheel_ui": player_1_wheel_ui, "player_2_wheel_ui": player_2_wheel_ui,
            "player_3_wheel_ui": player_3_wheel_ui, "player_4_wheel_ui": player_4_wheel_ui,
            "player_1_portrait": player_1_portrait, "player_2_portrait": player_2_portrait,
            "player_3_portrait": player_3_portrait, "player_4_portrait": player_4_portrait}
