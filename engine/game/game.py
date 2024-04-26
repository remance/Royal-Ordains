import ast
import configparser
import os.path
import sys
import types
from math import sin, cos, radians

import pygame
from pygame import sprite, Vector2, JOYDEVICEADDED, JOYDEVICEREMOVED, display, mouse
from pygame.locals import *
from pygame.mixer import music

from engine.battle.battle import Battle
from engine.character.character import Character, BodyPart
from engine.data.datalocalisation import Localisation
from engine.data.datamap import BattleMapData
from engine.data.datasave import SaveData
from engine.data.datasound import SoundData
from engine.data.datasprite import AnimationData
from engine.data.datastat import CharacterData
from engine.drop.drop import Drop
from engine.effect.effect import Effect, DamageEffect
from engine.lorebook.lorebook import Lorebook, SubsectionName, lorebook_process
from engine.menubackground.menubackground import MenuActor, MenuRotate, StaticImage
from engine.stageobject.stageobject import StageObject
from engine.uibattle.uibattle import Profiler, FPSCount, DamageNumber, CharacterSpeechBox, \
    CharacterIndicator, WheelUI
from engine.uimenu.uimenu import OptionMenuText, SliderMenu, MenuCursor, BoxUI, BrownMenuButton, \
    URLIconLink, MenuButton, TextPopup, MapTitle, CharacterInterface, CharacterProfileBox, \
    NameTextBox
from engine.updater.updater import ReversedLayeredUpdates
from engine.utils.common import edit_config, cutscene_update
from engine.utils.data_loading import load_image, load_images, csv_read, load_base_button
from engine.utils.text_making import number_to_minus_or_plus
from engine.weather.weather import MatterSprite, SpecialWeatherEffect

game_name = "Royal Ordains"  # Game name that will appear as game name at the windows bar


class Game:
    game = None
    battle = None
    main_dir = None
    data_dir = None
    font_dir = None
    ui_font = None
    font_texture = None
    language = None
    localisation = None
    cursor = None
    ui_updater = None
    ui_drawer = None
    battle_camera = None

    player_list = (1, 2, 3, 4)

    screen_rect = None
    screen_scale = (1, 1)
    screen_size = ()

    game_version = "0.2"
    joystick_bind_name = {"XBox": {0: "A", 1: "B", 2: "X", 3: "Y", 4: "-", 5: "Home", 6: "+", 7: "Start", 8: None,
                                   9: None, 10: None, 11: "D-Up", 12: "D-Down", 13: "D-Left", 14: "D-Right",
                                   15: "Capture", "axis-0": "L. Stick Left", "axis+0": "L. Stick R.",
                                   "axis-1": "L. Stick U.", "axis+1": "L. Stick D.",
                                   "axis-2": "R. Stick Left", "axis+2": "R. Stick R.",
                                   "axis-3": "R. Stick U.", "axis+3": "R. Stick D.",
                                   "hat-0": "L. Arrow", "hat+0": "R. Arrow",
                                   "hat-1": "D. Arrow", "hat+1": "U. Arrow"},
                          "Other": {0: "1", 1: "2", 2: "3", 3: "4", 4: "L1", 5: "R1", 6: "L2", 7: "R2", 8: "Select",
                                    9: "Start", 10: "L. Stick", 11: "R. Stick", 12: None, 13: None, 14: None, 15: None,
                                    "axis-0": "L. Stick L.", "axis+0": "L. Stick R.",
                                    "axis-1": "L. Stick U.", "axis+1": "L. Stick D.",
                                    "axis-2": "R. Stick Left", "axis+2": "R. Stick R.",
                                    "axis-3": "R. Stick U.", "axis+3": "R. Stick D.",
                                    "hat-0": "L. Arrow", "hat+0": "R. Arrow",
                                    "hat-1": "D. Arrow", "hat+1": "U. Arrow"},
                          "DualSense Wireless Controller":  # ps5 joystick
                              {0: "Cross", 1: "Circle", 2: "Square", 3: "Triangle", 4: "Share", 5: "PS", 6: "Options",
                               7: "L. Stick",
                               8: "R. Stick", 9: "L1", 10: "R1", 11: "D-Up", 12: "D-Down", 13: "D-Left", 14: "D-R.",
                               15: "T-Pad", "axis-0": "L. Stick L.", "axis+0": "L. Stick R.",
                               "axis-1": "L. Stick U.", "axis+1": "L. Stick D.",
                               "axis-2": "R. Stick Left", "axis+2": "R. Stick R.",
                               "axis-3": "R. Stick U.", "axis+3": "R. Stick D.",
                               "axis+4": "L2", "axis+5": "R2",
                               "hat-0": "L. Arrow", "hat+0": "R. Arrow",
                               "hat-1": "D. Arrow", "hat+1": "U. Arrow"}}

    # import from game
    from engine.game.activate_input_popup import activate_input_popup
    activate_input_popup = activate_input_popup

    from engine.game.add_joystick import add_joystick
    add_joystick = add_joystick

    from engine.game.assign_key import assign_key
    assign_key = assign_key

    from engine.game.back_mainmenu import back_mainmenu
    back_mainmenu = back_mainmenu

    from engine.game.change_keybind import change_keybind
    change_keybind = change_keybind

    from engine.game.change_pause_update import change_pause_update
    change_pause_update = change_pause_update

    from engine.game.change_sound_volume import change_sound_volume
    change_sound_volume = change_sound_volume

    from engine.game.create_config import create_config
    create_config = create_config

    from engine.game.generate_custom_equipment import generate_custom_equipment
    generate_custom_equipment = generate_custom_equipment

    from engine.game.get_keybind_button_name import get_keybind_button_name
    get_keybind_button_name = get_keybind_button_name

    from engine.game.loading_screen import loading_screen
    loading_screen = loading_screen

    from engine.game.make_character_interfaces import make_character_interfaces
    make_character_interfaces = make_character_interfaces

    from engine.game.make_input_box import make_input_box
    make_input_box = make_input_box

    from engine.game.make_lorebook import make_lorebook
    make_lorebook = make_lorebook

    from engine.game.make_option_menu import make_option_menu
    make_option_menu = make_option_menu

    from engine.game.menu_char import menu_char
    menu_char = menu_char

    from engine.game.menu_keybind import menu_keybind
    menu_keybind = menu_keybind

    from engine.game.menu_main import menu_main
    menu_main = menu_main

    from engine.game.menu_option import menu_option
    menu_option = menu_option

    from engine.game.start_battle import start_battle
    start_battle = start_battle

    from engine.game.update_profile_slots import update_profile_slots
    update_profile_slots = update_profile_slots

    from engine.game.write_all_player_save import write_all_player_save
    write_all_player_save = write_all_player_save

    lorebook_process = lorebook_process

    resolution_list = ("3200 x 1800", "2560 x 1440", "1920 x 1080", "1600 x 900", "1360 x 768",
                       "1280 x 720", "1024 x 576", "960 x 540", "854 x 480")

    def __init__(self, main_dir, error_log):
        Game.game = self
        Game.main_dir = main_dir
        Game.data_dir = os.path.join(self.main_dir, "data")
        Game.font_dir = os.path.join(self.data_dir, "font")

        self.config_path = os.path.join(self.main_dir, "configuration.ini")

        pygame.init()  # Initialize pygame

        mouse.set_visible(False)  # set mouse as not visible, use in-game mouse sprite

        self.error_log = error_log
        self.error_log.write("Game Version: " + self.game_version)

        # Read config file
        config = configparser.ConfigParser()  # initiate config reader
        try:
            config.read_file(open(self.config_path))  # read config file
        except FileNotFoundError:  # Create config file if not found with the default
            config = self.create_config()

        try:
            self.config = config
            self.show_fps = int(self.config["USER"]["fps"])
            self.easy_text = int(self.config["USER"]["easy_text"])
            self.screen_width = int(self.config["USER"]["screen_width"])
            self.screen_height = int(self.config["USER"]["screen_height"])
            self.full_screen = int(self.config["USER"]["full_screen"])
            self.master_volume = float(self.config["USER"]["master_volume"])
            self.music_volume = float(self.config["USER"]["music_volume"])
            self.play_music_volume = self.master_volume * self.music_volume / 10000  # convert volume into percentage
            self.effect_volume = float(self.config["USER"]["effect_volume"])
            self.play_effect_volume = self.master_volume * self.effect_volume / 10000
            self.voice_volume = float(self.config["USER"]["voice_volume"])
            self.play_voice_volume = self.master_volume * self.voice_volume / 10000
            self.language = str(self.config["USER"]["language"])
            self.player_key_bind_list = {player: ast.literal_eval(self.config["USER"]["keybind player " + str(player)])
                                         for player in self.player_list}
            self.player_key_control = {player: self.config["USER"]["control player " + str(player)] for player in
                                       self.player_list}
            if self.game_version != self.config["VERSION"]["ver"]:  # remake config as game version change
                raise KeyError  # cause KeyError to reset config file
        except (KeyError, TypeError, NameError) as b:  # config error will make the game recreate config with default
            self.error_log.write(str(b))
            config = self.create_config()
            self.config = config
            self.show_fps = int(self.config["USER"]["fps"])
            self.easy_text = int(self.config["USER"]["easy_text"])
            self.screen_width = int(self.config["USER"]["screen_width"])
            self.screen_height = int(self.config["USER"]["screen_height"])
            self.full_screen = int(self.config["USER"]["full_screen"])
            self.master_volume = float(self.config["USER"]["master_volume"])
            self.music_volume = float(self.config["USER"]["music_volume"])
            self.play_music_volume = self.master_volume * self.music_volume / 10000
            self.effect_volume = float(self.config["USER"]["effect_volume"])
            self.play_effect_volume = self.master_volume * self.effect_volume / 10000
            self.voice_volume = float(self.config["USER"]["voice_volume"])
            self.play_voice_volume = self.master_volume * self.voice_volume / 10000
            self.language = str(self.config["USER"]["language"])
            self.player_key_bind_list = {player: ast.literal_eval(self.config["USER"]["keybind player " + str(player)])
                                         for player in self.player_list}
            self.player_key_control = {player: self.config["USER"]["control player " + str(player)] for player in
                                       self.player_list}

        self.corner_screen_width = self.screen_width - 1
        self.corner_screen_height = self.screen_height - 1

        self.default_player_key_bind_list = {
            player: ast.literal_eval(self.config["DEFAULT"]["keybind player " + str(player)])
            for player in self.player_list}

        Game.language = self.language

        # Set the display mode
        # game default screen size is 1920 x 1080, other resolution get scaled from there
        Game.screen_scale = (self.screen_width / 1920, self.screen_height / 1080)
        Game.screen_size = (self.screen_width, self.screen_height)

        self.window_style = 0
        if self.full_screen == 1:
            self.window_style = pygame.FULLSCREEN
        self.screen = display.set_mode(self.screen_size, self.window_style)
        Game.screen_rect = self.screen.get_rect()

        Character.screen_scale = self.screen_scale
        Effect.screen_scale = self.screen_scale
        StageObject.screen_scale = self.screen_scale

        self.clock = pygame.time.Clock()  # set get clock

        self.save_data = SaveData()

        self.loading = load_image(self.data_dir, self.screen_scale, "loading.png", ("ui", "mainmenu_ui"))
        self.loading = pygame.transform.scale(self.loading, self.screen_rect.size)

        self.joysticks = {}
        self.joystick_name = {}
        self.player_joystick = {}  # always check link with joystick_player when change code
        self.joystick_player = {}

        self.player_key_control = {player: self.config["USER"]["control player " + str(player)] for player in
                                   self.player_list}
        self.player_key_bind = {player: self.game.player_key_bind_list[player][self.player_key_control[player]] for
                                player in self.player_list}
        self.player_key_bind_name = {player: {value: key for key, value in self.player_key_bind[player].items()} for
                                     player in self.player_list}
        self.player_key_press = {player: {key: False for key in self.player_key_bind[player]} for player in
                                 self.player_list}
        self.player_key_hold = {player: {key: False for key in self.player_key_bind[player]} for player in
                                self.player_list}  # key that consider holding
        self.player_key_bind_button_name = self.get_keybind_button_name()

        Game.ui_font = csv_read(self.data_dir, "ui_font.csv", ("ui",), header_key=True)
        for item in Game.ui_font:  # add ttf file extension for font data reading.
            Game.ui_font[item] = os.path.join(self.font_dir, Game.ui_font[item]["Font"] + ".ttf")
        Game.font_texture = load_images(self.data_dir, screen_scale=self.screen_scale,
                                        subfolder=("font", "texture"), as_pillow_image=True)

        # Decorate game icon window
        # icon = load_image(self.data_dir, "sword.jpg")
        # icon = pygame.transform.scale(icon, (32, 32))
        # display.set_icon(icon)

        # Initialise groups
        Game.ui_updater = ReversedLayeredUpdates()  # main drawer for ui in main menu
        Game.ui_drawer = sprite.LayeredUpdates()

        # game start menu group
        self.menu_icon = sprite.Group()  # mostly for option icon like volume or screen resolution
        self.menu_slider = sprite.Group()

        # lorebook group
        self.subsection_name = sprite.Group()  # subsection name objects group in lorebook blit on lore_name_list
        self.tag_filter_name = sprite.Group()  # tag filter objects group in lorebook blit on filter_name_list

        # battle object group
        Game.battle_camera = sprite.LayeredUpdates()  # layer drawer battle camera, all image pos should be based on the map not screen
        self.battle_ui_updater = ReversedLayeredUpdates()  # this is updater and drawer for ui, all image pos should be based on the screen
        self.battle_ui_drawer = sprite.LayeredUpdates()
        self.battle_cursor_drawer = sprite.LayeredUpdates()

        self.character_updater = sprite.Group()  # updater for character objects
        self.character_updater.cutscene_update = types.MethodType(cutscene_update, self.character_updater)
        self.realtime_ui_updater = sprite.Group()  # for UI stuff that need to be updated in real time like drama and weather objects, also used as drawer
        self.effect_updater = sprite.Group()  # updater for effect objects (e.g. range attack sprite)
        self.effect_updater.cutscene_update = types.MethodType(cutscene_update, self.effect_updater)

        self.all_chars = sprite.Group()  # group to keep all character objects for cleaning
        self.all_damage_effects = sprite.Group()  # group to keep all damage objects for collision check

        self.button_ui = sprite.Group()  # ui button group in battle

        self.speech_boxes = sprite.Group()
        self.ui_boxes = sprite.Group()

        self.slider_menu = sprite.Group()  # volume slider in esc option menu

        self.weather_matters = sprite.Group()  # sprite of weather effect group such as rain sprite
        self.weather_effect = sprite.Group()  # sprite of special weather effect group such as fog that cover whole screen

        # Assign containers
        OptionMenuText.containers = self.menu_icon
        SliderMenu.containers = self.menu_slider, self.slider_menu

        MenuRotate.containers = self.ui_updater, self.ui_drawer
        MenuActor.containers = self.ui_updater, self.ui_drawer

        SubsectionName.containers = self.ui_updater, self.ui_drawer, self.battle_ui_updater, self.battle_ui_drawer

        # battle containers
        CharacterSpeechBox.containers = self.effect_updater, self.battle_camera, self.speech_boxes
        CharacterIndicator.containers = self.effect_updater, self.battle_camera
        Drop.containers = self.effect_updater, self.battle_camera
        DamageNumber.containers = self.effect_updater, self.battle_camera
        BodyPart.containers = self.effect_updater, self.battle_camera
        Effect.containers = self.effect_updater, self.battle_camera
        StageObject.containers = self.effect_updater, self.battle_camera
        DamageEffect.containers = self.all_damage_effects, self.effect_updater, self.battle_camera

        MenuCursor.containers = self.ui_updater, self.ui_drawer

        MatterSprite.containers = self.weather_matters, self.realtime_ui_updater
        SpecialWeatherEffect.containers = self.weather_effect, self.battle_ui_updater, self.battle_ui_drawer

        Character.containers = self.character_updater, self.all_chars

        self.game_intro(False)  # run intro

        # Load game localisation data
        self.localisation = Localisation()
        Game.localisation = self.localisation

        # Create game cursor, make sure it is the first object in ui to be created, so it is always update first
        cursor_images = load_images(self.data_dir, subfolder=("ui", "cursor_menu"))  # no need to scale cursor
        self.cursor = MenuCursor(cursor_images)
        Game.cursor = self.cursor

        # Battle related data
        self.character_data = CharacterData()
        self.battle_map_data = BattleMapData()
        self.sound_data = SoundData()

        self.preset_map_folder = self.battle_map_data.preset_map_folder
        self.preset_map_data = self.battle_map_data.preset_map_data
        self.choice_stage_reward = self.battle_map_data.choice_stage_reward
        self.stage_reward = self.battle_map_data.stage_reward

        Character.character_data = self.character_data
        Character.status_list = self.character_data.status_list
        Character.effect_list = self.character_data.effect_list

        Drop.drop_item_list = self.character_data.drop_item_list

        Effect.effect_list = self.character_data.effect_list

        self.animation_data = AnimationData()
        self.character_animation_data = self.animation_data.character_animation_data  # animation data pool
        self.body_sprite_pool = self.animation_data.body_sprite_pool  # body sprite pool
        self.stage_object_animation_pool = self.animation_data.stage_object_animation_pool
        self.effect_animation_pool = self.animation_data.effect_animation_pool  # effect sprite animation pool

        BodyPart.body_sprite_pool = self.body_sprite_pool
        Drop.item_sprite_pool = self.body_sprite_pool["Item"]["special"]
        Effect.effect_animation_pool = self.effect_animation_pool
        WheelUI.item_sprite_pool = self.body_sprite_pool["Item"]["special"]
        CharacterInterface.item_sprite_pool = self.body_sprite_pool["Item"]["special"]
        StageObject.stage_object_animation_pool = self.stage_object_animation_pool

        # Load sound effect
        self.sound_effect_pool = self.sound_data.sound_effect_pool
        self.music_pool = self.sound_data.music_pool

        # Music player
        pygame.mixer.set_num_channels(1000)
        music.load(self.music_pool["menu"])
        music.set_volume(self.play_music_volume)

        # Load UI images
        self.battle_ui_images = load_images(self.data_dir, screen_scale=self.screen_scale,
                                            subfolder=("ui", "battle_ui"))
        self.char_selector_images = load_images(self.data_dir, screen_scale=self.screen_scale,
                                                subfolder=("ui", "char_ui"), key_file_name_readable=True)
        self.button_images = load_images(self.data_dir, screen_scale=self.screen_scale,
                                         subfolder=("ui", "battlemenu_ui", "button"))
        self.option_menu_images = load_images(self.data_dir, screen_scale=self.screen_scale,
                                              subfolder=("ui", "option_ui"))
        # Main menu interface
        self.fps_count = FPSCount(self)  # FPS number counter
        if self.show_fps:
            self.add_ui_updater(self.fps_count)
        if self.easy_text:
            CharacterSpeechBox.simple_font = True

        base_button_image_list = load_base_button(self.data_dir, self.screen_scale)

        main_menu_buttons_box = BoxUI((400, 500), parent=self.screen)

        f = 0.68
        self.start_game_button = BrownMenuButton((0, -0.6 * f), key_name="main_menu_start_game",
                                                 parent=main_menu_buttons_box)
        self.lore_button = BrownMenuButton((0, -0.2 * f), key_name="main_menu_lorebook", parent=main_menu_buttons_box)
        self.option_button = BrownMenuButton((0, 0.2 * f), key_name="game_option", parent=main_menu_buttons_box)
        self.quit_button = BrownMenuButton((0, 0.6 * f), key_name="game_quit", parent=main_menu_buttons_box)

        main_menu_button_images = load_images(self.data_dir, screen_scale=self.screen_scale,
                                              subfolder=("ui", "mainmenu_ui"))

        self.discord_button = URLIconLink(main_menu_button_images["discord"], (self.screen_width, 0),
                                          "https://discord.gg/q7yxz4netf")
        self.youtube_button = URLIconLink(main_menu_button_images["youtube"], self.discord_button.rect.topleft,
                                          "https://www.youtube.com/channel/UCgapwWog3mYhkEKIGW8VZtw")
        self.github_button = URLIconLink(main_menu_button_images["github"], self.youtube_button.rect.topleft,
                                         "https://github.com/remance/Royal-Ordains")

        self.mainmenu_button = (self.start_game_button, self.lore_button, self.option_button, self.quit_button,
                                self.discord_button, self.youtube_button)

        # Battle map select menu button
        self.map_title = MapTitle((self.screen_rect.width / 2, 0))

        # self.map_preview = MapPreview(self.preset_map_list_box.rect.topright)

        # UIScroll(self.unit_selector, self.unit_selector.rect.topright)  # scroll bar for character pick

        bottom_height = self.screen_rect.height - base_button_image_list[0].get_height()
        self.select_button = MenuButton(base_button_image_list,
                                        (self.screen_rect.width - base_button_image_list[0].get_width(), bottom_height),
                                        key_name="select_button")

        # Option menu button
        option_menu_dict = self.make_option_menu(base_button_image_list)
        self.back_button = option_menu_dict["back_button"]
        self.keybind_button = option_menu_dict["keybind_button"]
        self.default_button = option_menu_dict["default_button"]
        self.resolution_drop = option_menu_dict["resolution_drop"]
        self.resolution_bar = option_menu_dict["resolution_bar"]
        self.resolution_text = option_menu_dict["resolution_text"]
        self.option_menu_sliders = option_menu_dict["volume_sliders"]
        self.value_boxes = option_menu_dict["value_boxes"]
        self.volume_texts = option_menu_dict["volume_texts"]
        self.fullscreen_box = option_menu_dict["fullscreen_box"]
        self.fullscreen_text = option_menu_dict["fullscreen_text"]
        self.fps_box = option_menu_dict["fps_box"]
        self.fps_text = option_menu_dict["fps_text"]
        self.keybind_text = option_menu_dict["keybind_text"]
        self.keybind_icon = option_menu_dict["keybind_icon"]
        self.control_switch = option_menu_dict["control_switch"]
        self.control_player_next = option_menu_dict["control_player_next"]
        self.control_player_back = option_menu_dict["control_player_back"]
        self.easy_text_box = option_menu_dict["easy_text_box"]
        self.easy_text = option_menu_dict["easy_text"]

        self.option_text_list = tuple(
            [self.resolution_text, self.fullscreen_text, self.fps_text, self.easy_text] +
            [value for value in self.volume_texts.values()])
        self.option_menu_button = (
            self.back_button, self.default_button, self.keybind_button, self.resolution_drop,
            self.fullscreen_box, self.fps_box, self.easy_text_box)

        # Character select menu button
        self.start_button = MenuButton(base_button_image_list,
                                       (self.screen_rect.width / 1.5, self.screen_rect.height / 1.05),
                                       key_name="start_button")
        self.char_back_button = MenuButton(base_button_image_list,
                                           (self.screen_rect.width / 4, self.screen_rect.height / 1.05),
                                           key_name="back_button")

        self.char_interface_text_popup = {index: TextPopup() for index in range(1, 5)}

        self.player_char_selectors, self.player_char_interfaces = self.make_character_interfaces()
        self.char_menu_buttons = (self.player_char_selectors[1], self.player_char_selectors[2],
                                  self.player_char_selectors[3], self.player_char_selectors[4],
                                  self.char_back_button, self.start_button)
        CharacterProfileBox.image = self.char_selector_images["Charsheet"]
        self.char_profile_boxes = {
            key + 1: {key2 + 1: CharacterProfileBox((self.player_char_selectors[key + 1].rect.topleft[0],
                                                     self.player_char_selectors[key + 1].rect.topleft[1] +
                                                     (key2 * (210 * self.screen_scale[1])))) for
                      key2 in range(4)} for key in range(4)}
        self.char_profile_page_text = {key + 1: NameTextBox((self.player_char_selectors[1].image.get_width() / 1.5,
                                                             42 * self.screen_scale[1]),
                                                            (self.player_char_selectors[key + 1].rect.center[0],
                                                             self.player_char_selectors[key + 1].rect.midbottom[1] -
                                                             42 * self.screen_scale[1]),
                                                            "1/2", text_size=36 * self.screen_scale[1],
                                                            center_text=True) for key in range(4)}
        self.profile_page = {1: 0, 2: 0, 3: 0, 4: 0}
        self.profile_index = {1: 1, 2: 1, 3: 1, 4: 1}

        # User input popup ui
        input_ui_dict = self.make_input_box(base_button_image_list)
        self.input_ui = input_ui_dict["input_ui"]
        self.input_ok_button = input_ui_dict["input_ok_button"]
        self.input_close_button = input_ui_dict["input_close_button"]
        self.input_cancel_button = input_ui_dict["input_cancel_button"]
        self.input_box = input_ui_dict["input_box"]
        self.input_ui_popup = (self.input_ok_button, self.input_cancel_button, self.input_ui, self.input_box)
        self.confirm_ui_popup = (self.input_ok_button, self.input_cancel_button, self.input_ui)
        self.inform_ui_popup = (self.input_close_button, self.input_ui, self.input_box)
        self.all_input_ui_popup = (self.input_ok_button, self.input_cancel_button, self.input_close_button,
                                   self.input_ui, self.input_box)

        # Encyclopedia interface
        Lorebook.history_lore = self.localisation.create_lore_data("history")
        Lorebook.character_lore = self.localisation.create_lore_data("character")
        Lorebook.item_lore = self.localisation.create_lore_data("item")
        Lorebook.status_lore = self.localisation.create_lore_data("status")

        Lorebook.character_data = self.character_data

        self.lorebook, self.lore_name_list, self.filter_tag_list, self.lore_buttons = self.make_lorebook()

        self.lorebook_stuff = (self.lorebook, self.lore_name_list, self.filter_tag_list,
                               self.lore_name_list.scroll, self.filter_tag_list.scroll, self.lore_buttons.values())

        self.battle = Battle(self)

        Game.battle = self.battle
        Character.battle = self.battle
        Drop.battle = self.battle
        BodyPart.battle = self.battle
        Effect.battle = self.battle
        StageObject.battle = self.battle

        # Background image
        self.background_image = load_images(self.data_dir, screen_scale=self.screen_scale,
                                            subfolder=("ui", "mainmenu_ui", "background"))
        self.background = self.background_image["background"]

        self.atlas = MenuRotate((self.screen_width / 2, self.screen_height / 2), self.background_image["atlas"], 5)
        self.hide_background = StaticImage((self.screen_width / 2, self.screen_height / 2),
                                           self.background_image["hide"])

        # Starting script
        for event in pygame.event.get():
            if event.type == JOYDEVICEADDED:  # search for joystick plugin before game start
                self.add_joystick(event)

        for player in self.player_key_control:
            # search for joystick player with no joystick to revert control to keyboard
            if self.player_key_control[player] == "joystick" and player not in self.player_joystick:
                self.config["USER"]["control player " + str(player)] = "keyboard"
                self.change_keybind()

        self.player_char_select = {1: None, 2: None, 3: None, 4: None}

        self.dt = 0
        self.text_delay = 0
        self.url_delay = 0
        self.add_ui_updater(self.mainmenu_button)

        self.menu_state = "main_menu"
        self.input_popup = None  # popup for text input state

        self.loading_screen("end")

        self.run()

    def game_intro(self, intro):
        timer = 0
        while intro:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    intro = False
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            display.update()
            self.clock.tick(1000)
            timer += 1
            if timer == 1000:
                intro = False

        self.loading_screen("start")

        display.set_caption(game_name)  # set the self name on program border/tab

    def add_ui_updater(self, *args):
        self.ui_updater.add(*args)
        self.ui_drawer.add(*args)

    def remove_ui_updater(self, *args):
        self.ui_updater.remove(*args)
        self.ui_drawer.remove(*args)

    def setup_profiler(self):
        self.profiler = Profiler()
        self.profiler.enable()
        self.battle.realtime_ui_updater.add(self.profiler)

    def run(self):
        while True:
            # Get user input
            self.dt = self.clock.get_time() / 1000  # dt before game_speed
            self.cursor.scroll_down = False
            self.cursor.scroll_up = False
            esc_press = False

            self.player_key_press = {key: dict.fromkeys(self.player_key_press[key], False) for key in
                                     self.player_key_press}
            self.player_key_hold = {key: dict.fromkeys(self.player_key_hold[key], False) for key in
                                    self.player_key_hold}

            key_press = pygame.key.get_pressed()

            if not music.get_busy():  # replay menu song when not playing anything
                music.play()

            if self.url_delay:
                self.url_delay -= self.dt
                if self.url_delay < 0:
                    self.url_delay = 0

            for player, key_set in self.player_key_press.items():
                if self.player_key_control[player] == "keyboard":
                    for key in key_set:  # check for key holding
                        if type(self.player_key_bind[player][key]) == int and key_press[
                            self.player_key_bind[player][key]]:
                            self.player_key_hold[player][key] = True
                else:
                    player_key_bind_name = self.player_key_bind_name[player]
                    for joystick_id, joystick in self.joysticks.items():
                        if self.player_joystick[player] == joystick_id:
                            for i in range(joystick.get_numaxes()):
                                if joystick.get_axis(i) > 0.5 or joystick.get_axis(i) < -0.5:
                                    if i in (2, 3) and player == 1:  # right axis only for cursor (player 1 only)
                                        vec = Vector2(joystick.get_axis(2), joystick.get_axis(3))
                                        radius, angle = vec.as_polar()
                                        adjusted_angle = (angle + 90) % 360
                                        new_pos = Vector2(
                                            self.cursor.pos[0] + (self.dt * 1000 * sin(radians(adjusted_angle))),
                                            self.cursor.pos[1] - (self.dt * 1000 * cos(radians(adjusted_angle))))
                                        if new_pos[0] < 0:
                                            new_pos[0] = 0
                                        elif new_pos[0] > self.corner_screen_width:
                                            new_pos[0] = self.corner_screen_width
                                        if new_pos[1] < 0:
                                            new_pos[1] = 0
                                        elif new_pos[1] > self.corner_screen_height:
                                            new_pos[1] = self.corner_screen_height
                                        mouse.set_pos(new_pos)
                                    else:
                                        axis_name = "axis" + number_to_minus_or_plus(joystick.get_axis(i)) + str(i)
                                        if axis_name in player_key_bind_name:
                                            self.player_key_hold[player][player_key_bind_name[axis_name]] = True
                                            self.player_key_press[player][player_key_bind_name[axis_name]] = True

                            for i in range(joystick.get_numbuttons()):
                                if joystick.get_button(i) and i in player_key_bind_name:
                                    self.player_key_hold[player][player_key_bind_name[i]] = True

                            for i in range(joystick.get_numhats()):
                                if joystick.get_hat(i)[0] > 0.1 or joystick.get_hat(i)[0] < -0.1:
                                    hat_name = "hat" + number_to_minus_or_plus(joystick.get_hat(i)[0]) + str(0)
                                    if hat_name in self.player_key_bind_name:
                                        self.player_key_hold[player][player_key_bind_name[hat_name]] = True
                                if joystick.get_hat(i)[1] > 0.1 or joystick.get_hat(i)[1] < -0.1:
                                    hat_name = "hat" + number_to_minus_or_plus(joystick.get_hat(i)[1]) + str(1)
                                    if hat_name in self.player_key_bind_name:
                                        self.player_key_hold[player][player_key_bind_name[hat_name]] = True

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 4:  # Mouse scroll down
                        self.cursor.scroll_up = True
                    elif event.button == 5:  # Mouse scroll up
                        self.cursor.scroll_down = True

                elif event.type == pygame.JOYBUTTONUP:
                    joystick = event.instance_id
                    if self.input_popup:
                        if self.config["USER"]["control player " + str(self.control_switch.player)] == "joystick" and \
                                self.input_popup[0] == "keybind_input" and \
                                self.player_joystick[self.control_switch.player] == joystick:
                            # check for button press
                            self.assign_key(event.button)
                    else:
                        if joystick in self.joystick_player:
                            player = self.joystick_player[joystick]
                            if self.player_key_control[player] == "joystick" and \
                                    event.button in self.player_key_bind_name[player]:  # check for key press
                                self.player_key_press[player][self.player_key_bind_name[player][event.button]] = True

                elif event.type == pygame.KEYDOWN:
                    event_key_press = event.key
                    if self.input_popup:  # event update to input box

                        if event.key == pygame.K_ESCAPE:
                            esc_press = True

                        elif self.input_popup[0] == "keybind_input" and \
                                self.config["USER"]["control player " + str(self.control_switch.player)] == "keyboard":
                            self.assign_key(event.key)

                        elif self.input_popup[0] == "text_input":
                            self.input_box.player_input(event, key_press)
                            self.text_delay = 0.1
                    else:
                        for player in self.player_key_control:
                            if self.player_key_control[player] == "keyboard" and \
                                    event_key_press in self.player_key_bind_name[player]:  # check for key press
                                self.player_key_press[player][self.player_key_bind_name[player][event_key_press]] = True

                        if event.key == pygame.K_ESCAPE:
                            esc_press = True

                elif event.type == JOYDEVICEADDED:
                    # Player add new joystick by plug in
                    self.add_joystick(event)

                elif event.type == JOYDEVICEREMOVED:
                    # Player unplug joystick
                    del self.joysticks[event.instance_id]
                    del self.joystick_name[event.instance_id]
                    for key, value in self.player_joystick.copy().items():
                        if value == event.instance_id:
                            self.player_joystick.pop(key)
                            self.joystick_player.pop(value)

                            if self.menu_state == "keybind" and self.control_switch.player == key:
                                # remove joystick when in keybind menu with joystick setting
                                self.player_key_bind[key] = self.player_key_bind_list[key]["keyboard"]
                                self.config["USER"]["control player " + str(key)] = "keyboard"
                                self.control_switch.change_control("keyboard", key)
                                self.player_key_control[key] = self.config["USER"][
                                    "control player " + str(key)]
                                edit_config("USER", "control player " + str(key),
                                            self.config["USER"]["control player " + str(key)],
                                            self.config_path, self.config)

                                for key2, value2 in self.keybind_icon.items():
                                    value2.change_key(self.config["USER"]["control player " + str(key)],
                                                      self.player_key_bind_list[key][self.config["USER"][
                                                          "control player " + str(key)]][key2], None)

                                self.player_key_bind_name = {player: {value: key for key, value in
                                                                      self.player_key_bind[player].items()}
                                                             for player in self.player_list}
                                self.player_key_bind_button_name = self.get_keybind_button_name()

                            break

                    self.player_key_bind_name = {
                        player: {value: key for key, value in self.player_key_bind[player].items()} for
                        player in self.player_list}
                    self.player_key_bind_button_name = self.get_keybind_button_name()

                elif event.type == QUIT:
                    pygame.quit()
                    sys.exit()

            self.ui_updater.update()

            # Reset screen
            self.screen.blit(self.background, (0, 0))  # blit background over instead of clear() to reset screen

            if self.input_popup:  # currently, have input text pop up on screen, stop everything else until done
                if self.input_ok_button.event_press or key_press[pygame.K_RETURN] or key_press[pygame.K_KP_ENTER]:
                    done = True
                    if "replace key" in self.input_popup[1]:  # swap between 2 keys
                        player = self.control_switch.player
                        old_key = self.player_key_bind[player][self.input_popup[1][1]]

                        self.player_key_bind[player][self.input_popup[1][1]] = self.player_key_bind[player][
                            self.input_popup[1][2]]
                        self.player_key_bind[player][self.input_popup[1][2]] = old_key
                        self.config["USER"]["keybind player " + str(player)] = str(self.player_key_bind_list[player])
                        self.change_keybind()

                    elif self.input_popup[1] == "delete profile":
                        self.save_data.save_profile["character"].pop(self.input_popup[2])
                        self.save_data.remove_save_file(
                            os.path.join(self.main_dir, "save", str(self.input_popup[2]) + ".dat"))
                        for player2 in self.profile_page:
                            self.update_profile_slots(player2)

                    elif self.input_popup[1] == "quit":
                        pygame.time.wait(1000)
                        pygame.quit()
                        sys.exit()

                    if done:
                        self.change_pause_update(False)
                        self.input_box.text_start("")
                        self.input_popup = None
                        self.remove_ui_updater(self.all_input_ui_popup)

                elif self.input_cancel_button.event_press or self.input_close_button.event_press or esc_press:
                    self.change_pause_update(False)
                    self.input_box.text_start("")
                    self.input_popup = None
                    self.remove_ui_updater(self.all_input_ui_popup)

                elif self.input_popup[0] == "text_input":
                    if self.text_delay == 0:
                        if key_press[self.input_box.hold_key]:
                            self.input_box.player_input(None, key_press)
                            self.text_delay = 0.1
                    else:
                        self.text_delay += self.dt
                        if self.text_delay >= 0.3:
                            self.text_delay = 0

                else:
                    if self.player_key_control[self.control_switch.player] == "joystick" and \
                            self.input_popup[0] == "keybind_input":  # check for joystick hat and axis keybind
                        for joystick_id, joystick in self.joysticks.items():
                            if self.player_joystick[self.control_switch.player] == joystick_id:
                                for i in range(joystick.get_numaxes()):
                                    if i < 4:
                                        if joystick.get_axis(i) > 0.5 or joystick.get_axis(i) < -0.5:
                                            if i not in (2, 3):  # prevent right axis from being assigned
                                                axis_name = "axis" + number_to_minus_or_plus(
                                                    joystick.get_axis(i)) + str(i)
                                                self.assign_key(axis_name)
                                    else:  # axis from other type of joystick (ps5 axis 4 and 5 is L2 and R2) which -1 mean not press
                                        if joystick.get_axis(i) > 0.5:  # check only positive
                                            axis_name = "axis" + number_to_minus_or_plus(joystick.get_axis(i)) + str(i)
                                            self.assign_key(axis_name)

                                for i in range(joystick.get_numhats()):
                                    if joystick.get_hat(i)[0] > 0.1 or joystick.get_hat(i)[0] < -0.1:
                                        hat_name = "hat" + number_to_minus_or_plus(joystick.get_hat(i)[0]) + str(0)
                                        self.assign_key(hat_name)
                                    elif joystick.get_hat(i)[1] > 0.1 or joystick.get_hat(i)[1] < -0.1:
                                        hat_name = "hat" + number_to_minus_or_plus(joystick.get_hat(i)[1]) + str(1)
                                        self.assign_key(hat_name)

            elif not self.input_popup:
                if self.menu_state == "main_menu":
                    self.menu_main(esc_press)

                elif self.menu_state == "char":
                    self.menu_char(esc_press)

                elif self.menu_state == "option":
                    self.menu_option(esc_press)

                elif self.menu_state == "keybind":
                    self.menu_keybind(esc_press)

                elif self.menu_state == "lorebook":
                    command = self.lorebook_process(esc_press)
                    if esc_press or command == "exit":
                        self.menu_state = "main_menu"  # change menu back to default 0

            self.ui_drawer.draw(self.screen)
            display.update()
            self.clock.tick(300)
