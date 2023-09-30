from engine.uibattle.uibattle import TimeUI, Timer, WheelUI, PlayerPortrait


def make_battle_ui(battle_ui_image):
    from engine.game.game import Game
    from engine.battle.battle import Battle
    screen_scale = Game.screen_scale
    battle_camera_size = Battle.battle_camera_size
    time_ui = TimeUI((Game.screen_rect.width, 0))
    time_number = Timer(time_ui.rect.midtop)  # time number on time ui

    # Right top bar ui that show rough information of selected battalions
    wheel_ui = WheelUI(battle_ui_image["wheel"], battle_ui_image["wheel_selected"],
                       (battle_camera_size[0] / 2, battle_camera_size[1] / 2))

    player_1_portrait = PlayerPortrait(battle_ui_image["player1"], battle_ui_image["health_bar"],
                                       battle_ui_image["resource_bar"], battle_ui_image["guard_bar"],
                                       (250 * screen_scale[0], 120 * screen_scale[1]))

    player_2_portrait = PlayerPortrait(battle_ui_image["player1"], battle_ui_image["health_bar"],
                                       battle_ui_image["resource_bar"], battle_ui_image["guard_bar"],
                                       (600 * screen_scale[0], 120 * screen_scale[1]))

    return {"time_ui": time_ui, "time_number": time_number, "wheel_ui": wheel_ui,
            "player_1_portrait": player_1_portrait, "player_2_portrait": player_2_portrait}
