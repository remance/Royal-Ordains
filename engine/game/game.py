import ast
import configparser
import os.path
import sys
import types

import pygame
from pygame import sprite, display, mouse, Surface
from pygame.font import Font
from pygame.locals import *
from pygame.mixer import music

from engine.army.army import Army, GarrisonArmy
from engine.battle.battle import Battle
from engine.character.character import Character, BattleCharacter
from engine.data.datalocalisation import Localisation
from engine.data.datamap import BattleMapData
from engine.data.datasave import SaveData
from engine.data.datasound import SoundData
from engine.data.datasprite import SpriteData
from engine.data.datastat import CharacterData
from engine.effect.effect import Effect, DamageEffect
from engine.lorebook.lorebook import Lorebook, lorebook_process
from engine.menubackground.menubackground import MenuActor, MenuRotate, StaticImage
from engine.stageobject.stageobject import StageObject
from engine.uibattle.uibattle import (Profiler, FPSCount, DamageNumber, CharacterSpeechBox,
                                      CharacterGeneralIndicator, CharacterCommandIndicator)
from engine.uimenu.uimenu import (OptionMenuText, SliderMenu, MenuCursor, BoxUI, BrownMenuButton,
                                  TextPopup, PresetSelectInterface, FactionSelector, CustomArmySetupUI,
                                  CharacterSelector, MapTitle, ListUI, CustomPresetListAdapter)
from engine.updater.updater import ReversedLayeredUpdates
from engine.utils.common import cutscene_update
from engine.utils.data_loading import load_image, load_images, csv_read, load_base_button
from engine.weather.weather import MatterSprite

from engine.game.activate_input_popup import activate_input_popup
from engine.game.assign_key import assign_key
from engine.game.back_mainmenu import back_mainmenu
from engine.game.change_keybind import change_keybind
from engine.game.change_pause_update import change_pause_update
from engine.game.change_sound_volume import change_sound_volume
from engine.game.create_config import create_config
from engine.game.get_keybind_button_name import get_keybind_button_name
from engine.game.loading_screen import loading_screen
from engine.game.make_input_box import make_input_box
from engine.game.make_lorebook import make_lorebook
from engine.game.make_option_menu import make_option_menu
from engine.game.menu_custom_preset import menu_custom_preset
from engine.game.menu_custom_setup import menu_custom_setup
from engine.game.menu_keybind import menu_keybind
from engine.game.menu_main import menu_main
from engine.game.menu_option import menu_option
from engine.game.start_battle import start_battle

from engine.constants import *

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

    screen_rect = None
    screen_scale = (1, 1)
    screen_size = ()

    game_version = "0.2.3.2"

    # import from game
    activate_input_popup = activate_input_popup
    assign_key = assign_key
    back_mainmenu = back_mainmenu
    change_keybind = change_keybind
    change_pause_update = change_pause_update
    change_sound_volume = change_sound_volume
    create_config = create_config
    get_keybind_button_name = get_keybind_button_name
    loading_screen = loading_screen
    make_input_box = make_input_box
    make_lorebook = make_lorebook
    make_option_menu = make_option_menu
    menu_custom_preset = menu_custom_preset
    menu_custom_setup = menu_custom_setup
    menu_keybind = menu_keybind
    menu_main = menu_main
    menu_option = menu_option
    start_battle = start_battle

    lorebook_process = lorebook_process
    resolution_list = ("3840 x 2160", "3200 x 1800", "2560 x 1440", "1920 x 1080", "1600 x 900", "1360 x 768",
                       "1280 x 720", "1024 x 576", "960 x 540", "854 x 480")

    def __init__(self, main_dir, error_log):
        Game.game = self
        Game.main_dir = main_dir
        Game.data_dir = os.path.join(self.main_dir, "data")
        Game.font_dir = os.path.join(self.data_dir, "font")

        self.config_path = os.path.join(self.main_dir, "configuration.ini")

        pygame.mixer.pre_init(44100, -16, 1000, 4096)
        pygame.init()  # Initialize pygame

        pygame.event.set_allowed((QUIT, KEYDOWN, KEYUP, MOUSEBUTTONUP, MOUSEBUTTONDOWN))

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
            self.use_easy_text = int(self.config["USER"]["easy_text"])
            self.show_dmg_number = int(self.config["USER"]["show_dmg_number"])
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
            self.player_key_bind_list = ast.literal_eval(self.config["USER"]["keybind"])
            if self.game_version != self.config["VERSION"]["ver"]:  # remake config as game version change
                raise KeyError  # cause KeyError to reset config file
        except (KeyError, TypeError, NameError) as b:  # config error will make the game recreate config with default
            self.error_log.write(str(b))
            config = self.create_config()
            self.config = config
            self.show_fps = int(self.config["USER"]["fps"])
            self.use_easy_text = int(self.config["USER"]["easy_text"])
            self.show_dmg_number = int(self.config["USER"]["show_dmg_number"])
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
            self.player_key_bind_list = ast.literal_eval(self.config["USER"]["keybind"])

        self.corner_screen_width = self.screen_width - 1
        self.corner_screen_height = self.screen_height - 1

        self.default_player_key_bind_list = ast.literal_eval(self.config["DEFAULT"]["keybind"])

        Game.language = self.language

        # Set the display mode
        # game default screen size is 3840 x 2160, other resolution get scaled from there
        Game.screen_scale = (self.screen_width / Default_Screen_Width, self.screen_height / Default_Screen_Height)
        Game.screen_size = (self.screen_width, self.screen_height)

        self.window_style = 0
        if self.full_screen == 1:
            self.window_style = pygame.FULLSCREEN | SCALED

        self.screen = display.set_mode(self.screen_size, DOUBLEBUF | self.window_style)

        Game.screen_rect = self.screen.get_rect()

        Character.screen_scale = self.screen_scale
        Effect.screen_scale = self.screen_scale
        StageObject.screen_scale = self.screen_scale

        self.clock = pygame.time.Clock()  # set get clock

        self.save_data = SaveData()

        self.loading = load_image(self.data_dir, self.screen_scale, "loading.png", ("ui", "mainmenu_ui"))
        self.loading = pygame.transform.scale(self.loading, self.screen_rect.size)

        self.player_key_bind = self.player_key_bind_list
        self.player_key_bind_name = {value: key for key, value in self.player_key_bind.items()}
        self.player_key_press = {key: False for key in self.player_key_bind}
        self.player_key_hold = {key: False for key in self.player_key_bind}  # key that consider holding
        self.player_key_bind_button_name = self.get_keybind_button_name()

        Game.ui_font = csv_read(self.data_dir, "ui_font.csv", ("ui",), header_key=True)
        for item in Game.ui_font:  # add ttf file extension for font data reading.
            Game.ui_font[item] = os.path.join(self.font_dir, Game.ui_font[item]["Font"] + ".ttf")
        Game.font_texture = load_images(self.data_dir, screen_scale=self.screen_scale,
                                        subfolder=("font", "texture"), as_pillow_image=True)

        # ui font
        self.loading_screen_lore_font = pygame.font.Font(self.ui_font["main_button"], int(60 * self.screen_scale[1]))

        self.generic_ui_font = Font(self.ui_font["main_button"], int(30 * self.screen_scale[1]))
        self.fps_counter_font = Font(self.ui_font["main_button"], int(40 * self.screen_scale[1]))
        self.battle_timer_font = Font(self.ui_font["main_button"], int(60 * self.screen_scale[1]))
        self.screen_fade_font = Font(self.ui_font["manuscript_font"], int(100 * self.screen_scale[1]))
        self.character_indicator_font = Font(self.ui_font["manuscript_font"], int(50 * self.screen_scale[1]))
        self.damage_number_font = Font(self.ui_font["manuscript_font"], int(46 * self.screen_scale[1]))
        self.critical_damage_number_font = Font(self.ui_font["manuscript_font2"], int(76 * self.screen_scale[1]))
        self.character_name_talk_prompt_font = Font(self.ui_font["talk_font"], int(40 * self.screen_scale[1]))
        self.drama_font = Font(self.ui_font["manuscript_font"], int(90 * self.screen_scale[1]))
        self.profiler_font = Font(self.ui_font["main_button"], 16)

        self.list_font1 = Font(self.ui_font["text_paragraph"], int(40 * Game.screen_scale[1]))
        self.list_font2 = Font(self.ui_font["text_paragraph"], int(32 * Game.screen_scale[1]))
        self.list_font3 = Font(self.ui_font["text_paragraph"], int(24 * Game.screen_scale[1]))

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

        # ui list group
        self.subsection_name = sprite.Group()  # subsection name objects group for item list
        self.tag_filter_name = sprite.Group()  # tag filter objects group in lorebook blit on filter_name_list

        # battle object group
        self.battle_camera_object_drawer = sprite.LayeredUpdates()
        self.battle_camera_ui_drawer = sprite.LayeredUpdates()  # this is drawer for ui in battle, does not move alonge with camera
        self.battle_ui_updater = ReversedLayeredUpdates()  # this is updater and drawer for ui, all image pos should be based on the screen
        self.battle_ui_drawer = sprite.LayeredUpdates()

        self.character_updater = ReversedLayeredUpdates()  # updater for character objects,
        # higher layer characters got update first for the purpose of blit culling check
        self.character_updater.cutscene_update = types.MethodType(cutscene_update, self.character_updater)
        # for battle UI stuff that need to be updated in real time like drama and weather objects, also used as drawer
        self.battle_outer_ui_updater = sprite.Group()
        self.effect_updater = sprite.Group()  # updater for effect objects (e.g. range attack sprite)
        self.effect_updater.cutscene_update = types.MethodType(cutscene_update, self.effect_updater)

        self.all_characters = sprite.Group()  # group for all character objects for cleaning
        self.stage_objects = sprite.Group()  # group for all scene objects for event delete check
        self.player_general_indicators = sprite.Group()  # group for select check of all indicator of player general

        self.button_uis = sprite.Group()  # ui button group in battle

        self.speech_boxes = sprite.Group()
        self.ui_boxes = sprite.Group()

        self.slider_menus = sprite.Group()  # volume slider in esc option menu

        self.weather_matters = sprite.Group()  # sprite of weather effect group such as rain sprite

        # Assign containers
        OptionMenuText.containers = self.menu_icon
        SliderMenu.containers = self.menu_slider, self.slider_menus

        StaticImage.containers = self.ui_updater, self.ui_drawer
        MenuRotate.containers = self.ui_updater, self.ui_drawer
        MenuActor.containers = self.ui_updater, self.ui_drawer

        # SubsectionName.containers = self.ui_updater, self.ui_drawer, self.battle_ui_updater, self.battle_ui_drawer

        # battle containers
        CharacterSpeechBox.containers = self.effect_updater, self.battle_camera_ui_drawer, self.speech_boxes
        CharacterGeneralIndicator.containers = self.effect_updater, self.battle_camera_ui_drawer
        CharacterCommandIndicator.containers = self.effect_updater
        DamageNumber.containers = self.effect_updater, self.battle_camera_ui_drawer
        Effect.containers = self.effect_updater
        StageObject.containers = self.effect_updater, self.stage_objects
        DamageEffect.containers = self.effect_updater
        MatterSprite.containers = self.weather_matters, self.battle_outer_ui_updater

        Character.containers = self.character_updater, self.all_characters

        self.game_intro(False)  # run intro

        # Load game localisation data
        self.localisation = Localisation()
        Game.localisation = self.localisation

        # Create game cursor, make sure it is the first object in ui to be created, so it is always update first
        Game.cursor = MenuCursor(load_images(self.data_dir, subfolder=("ui", "cursor_menu")))  # no need to scale cursor
        self.add_ui_updater(self.cursor)

        # Battle related data
        self.character_data = CharacterData()
        self.battle_map_data = BattleMapData()
        self.sound_data = SoundData()

        self.preset_map_data = self.battle_map_data.preset_map_data

        if self.show_dmg_number:
            BattleCharacter.show_dmg_number = True
        Army.character_list = self.character_data.character_list
        Character.character_data = self.character_data
        Character.status_list = self.character_data.status_list
        Character.status_apply_funcs = self.character_data.status_apply_funcs
        Character.effect_list = self.character_data.effect_list

        Effect.effect_list = self.character_data.effect_list

        self.sprite_data = SpriteData()
        self.character_animation_data = self.sprite_data.character_animation_data  # character animation data pool
        self.character_portraits = self.sprite_data.character_portraits
        self.stage_object_animation_pool = self.sprite_data.stage_object_animation_pool
        self.effect_animation_pool = self.sprite_data.effect_animation_pool  # effect sprite animation pool

        Effect.effect_animation_pool = self.effect_animation_pool
        StageObject.stage_object_animation_pool = self.stage_object_animation_pool

        # Load sound effect
        self.sound_effect_pool = self.sound_data.sound_effect_pool
        self.music_pool = self.sound_data.music_pool
        self.ambient_pool = self.sound_data.ambient_pool
        self.weather_ambient_pool = self.sound_data.weather_ambient_pool

        # Music player
        pygame.mixer.set_num_channels(1000)
        music.load(self.music_pool["Menu"])
        music.set_volume(self.play_music_volume)

        # Load UI images
        self.battle_ui_images = load_images(self.data_dir, screen_scale=self.screen_scale,
                                            subfolder=("ui", "battle_ui"))
        self.weather_icon_images = load_images(self.data_dir, screen_scale=self.screen_scale,
                                               subfolder=("ui", "weather_ui"), key_file_name_readable=True)
        self.option_menu_images = load_images(self.data_dir, screen_scale=self.screen_scale,
                                              subfolder=("ui", "option_ui"))
        # Main menu interface
        self.fps_count = FPSCount(self)  # FPS number counter
        if self.show_fps:
            self.add_ui_updater(self.fps_count)
        if self.use_easy_text:
            CharacterSpeechBox.simple_font = True

        BrownMenuButton.button_frame = load_image(self.game.data_dir, (1, 1),
                                                  "new_button.png", ("ui", "mainmenu_ui"))
        main_menu_buttons_box = BoxUI((0, -12),
                                      (self.screen_width, 100 * self.screen_scale[1]), parent=self.screen)

        self.test_battle_button = BrownMenuButton((.15, 1), (-0.7, 0), key_name="main_menu_test_battle",
                                                  parent=main_menu_buttons_box)
        self.custom_battle_button = BrownMenuButton((.15, 1), (-0.25, 0), key_name="main_menu_custom_game",
                                                    parent=main_menu_buttons_box)
        self.option_button = BrownMenuButton((.15, 1), (0.25, 0), key_name="game_option",
                                             parent=main_menu_buttons_box)
        self.quit_button = BrownMenuButton((.15, 1), (0.7, 0), key_name="game_quit",
                                           parent=main_menu_buttons_box)

        self.main_menu_buttons = (self.custom_battle_button, self.test_battle_button,
                                  self.option_button, self.quit_button)

        # self.start_game_button = BrownMenuButton((-2.4, 1), key_name="main_menu_start_game",
        #                                          parent=main_menu_buttons_box)
        # self.load_game_button = BrownMenuButton((-1.2, 1), key_name="main_menu_load_game",
        #                                          parent=main_menu_buttons_box)
        # self.custom_battle_button = BrownMenuButton((-1.2, 1), key_name="main_menu_custom_game",
        #                                          parent=main_menu_buttons_box)
        # self.lore_button = BrownMenuButton((0, 1), key_name="game_lorebook",
        #                                          parent=main_menu_buttons_box)
        # self.option_button = BrownMenuButton((1.2, 1), key_name="game_option", parent=main_menu_buttons_box)
        # self.quit_button = BrownMenuButton((2.4, 1), key_name="game_quit", parent=main_menu_buttons_box)
        #
        # self.mainmenu_button = (self.start_game_button, self.load_game_button, self.custom_battle_button,
        #                         self.lore_button, self.option_button, self.quit_button)

        self.text_popup = TextPopup(font_size=50)
        self.loading_lore_text_popup = TextPopup(font_size=70)
        self.loading_lore_text = ""

        # Option menu button
        option_menu_dict = self.make_option_menu(main_menu_buttons_box)
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
        self.easy_text_box = option_menu_dict["easy_text_box"]
        self.easy_text = option_menu_dict["easy_text"]
        self.show_dmg_box = option_menu_dict["show_dmg_box"]
        self.show_dmg_text = option_menu_dict["show_dmg_text"]

        self.option_text_list = tuple(
            [self.resolution_text, self.fullscreen_text, self.fps_text, self.easy_text, self.show_dmg_text] +
            [value for value in self.volume_texts.values()])
        self.option_menu_buttons = (
            self.back_button, self.default_button, self.keybind_button, self.resolution_drop,
            self.fullscreen_box, self.fps_box, self.easy_text_box, self.show_dmg_box)

        # Grand strategy select menu button
        self.setup_back_button = BrownMenuButton((.15, 1), (-0.6, 0),
                                                 key_name="back_button", parent=main_menu_buttons_box)
        self.grand_setup_confirm_battle_button = BrownMenuButton((.15, 1), (0.6, 0), key_name="start_button",
                                                                 parent=main_menu_buttons_box)
        self.grand_menu_uis = (self.setup_back_button,
                               self.grand_setup_confirm_battle_button)

        # Custom battle select menu button
        self.custom_battle_setup_start_battle_button = BrownMenuButton((.15, 1), (0.6, 0), key_name="start_button",
                                                                       parent=main_menu_buttons_box)
        self.custom_battle_preset_button = BrownMenuButton((.15, 1), (0, 0), key_name="custom_preset_button",
                                                           parent=main_menu_buttons_box)


        # self.char_interface_text_popup = {index: TextPopup() for index in range(1, 3)}

        # self.player_char_interfaces = {index: CharacterInterface((self.player_char_selectors[index].rect.topleft[0],
        #                                                           self.player_char_selectors[index].rect.topleft[1] -
        #                                                           (60 * self.screen_scale[1])),
        #                                                          index, self.char_interface_text_popup[index]) for index
        #                                in range(1, 3)}

        self.custom_battle_menu_uis = (self.setup_back_button, self.custom_battle_preset_button,
                                       self.custom_battle_setup_start_battle_button)

        self.custom_team1_army = Army({}, [], [])
        self.custom_team2_army = Army({}, [], [])
        self.custom_team1_reinforcement_army = Army({}, [], [])
        self.custom_team2_reinforcement_army = Army({}, [], [])
        self.custom_team0_garrison_army = GarrisonArmy({}, [], [])
        self.custom_team1_garrison_army = GarrisonArmy({}, [], [])
        self.custom_team2_garrison_army = GarrisonArmy({}, [], [])

        self.preset_back_button = BrownMenuButton((.15, 1), (-0.2, 0),
                                                  key_name="back_button", parent=main_menu_buttons_box)
        self.preset_save_button = BrownMenuButton((.15, 1), (0.2, 0), key_name="save_button",
                                                  parent=main_menu_buttons_box)
        self.preset_clear_button = BrownMenuButton((.15, 1), (0.2, 0), key_name="clear_button",
                                                  parent=main_menu_buttons_box)
        self.preset_revert_all_button = BrownMenuButton((.15, 1), (0.2, 0), key_name="revert_all_button",
                                                  parent=main_menu_buttons_box)
        self.custom_preset_list_box = ListUI(pivot=(-0.9, -0.6), origin=(-1, -1), size=(0.15, 0.5),
                                             items=CustomPresetListAdapter(),
                                             parent=self.screen, item_size=20)
        self.custom_army_setup = CustomArmySetupUI((self.screen_width * 0.4, self.screen_height * 0.2))
        self.custom_character_selector = CharacterSelector((self.screen_width * 0.78, self.screen_height * 0.2))
        self.faction_selector = FactionSelector((self.screen_width / 2, self.screen_height * 0.05))
        self.custom_preset_menu_uis = (self.preset_back_button, self.preset_save_button, self.custom_preset_list_box,
                                       self.faction_selector, self.custom_army_setup, self.custom_character_selector)

        self.before_save_preset_army_setup = {}

        # Battle map select menu button
        self.map_title = MapTitle((self.screen_rect.width / 2, 0))

        # self.map_preview = MapPreview(self.preset_map_list_box.rect.topright)

        # UIScroll(self.unit_selector, self.unit_selector.rect.topright)  # scroll bar for character pick


        # User input popup ui
        input_ui_dict = self.make_input_box()
        self.input_ui = input_ui_dict["input_ui"]
        self.input_ok_button = input_ui_dict["input_ok_button"]
        self.input_close_button = input_ui_dict["input_close_button"]
        self.input_cancel_button = input_ui_dict["input_cancel_button"]
        self.input_box = input_ui_dict["input_box"]
        self.static_input_box = input_ui_dict["static_input_box"]
        self.input_popup_uis = (self.input_ok_button, self.input_cancel_button, self.input_ui, self.input_box)
        self.confirm_popup_uis = (self.input_ok_button, self.input_cancel_button, self.input_ui)
        self.inform_popup_uis = (self.input_close_button, self.input_ui, self.static_input_box)
        self.all_input_popup_uis = (self.input_ok_button, self.input_cancel_button, self.input_close_button,
                                    self.input_ui, self.input_box, self.static_input_box)

        # Encyclopedia interface
        # Lorebook.history_lore = self.localisation.create_lore_data("history")
        # Lorebook.character_lore = self.localisation.create_lore_data("character")

        Lorebook.character_data = self.character_data

        # self.lorebook, self.lore_name_list, self.filter_tag_list, self.lore_buttons = self.make_lorebook()
        #
        # self.lorebook_stuff = (self.lorebook, self.lore_name_list, self.filter_tag_list,
        #                        self.lore_name_list.scroll, self.filter_tag_list.scroll, self.lore_buttons.values())

        self.custom_battle_setting = {"map": "", "weather": 1, "fund": {1: 10000, 2: 10000}, "event": None,
                                      "team": {1: {"faction": "Small", "units": {}},
                                               2: {"faction": "Small", "units": {}}}}

        self.battle = Battle(self)

        Game.battle = self.battle
        Character.battle = self.battle
        Effect.battle = self.battle
        StageObject.battle = self.battle

        # Background image
        self.background_image = load_images(self.data_dir, screen_scale=self.screen_scale,
                                            subfolder=("ui", "mainmenu_ui", "background"))
        self.background = self.background_image["background"]
        self.o2 = MenuRotate((1530 * self.screen_scale[0], 564 * self.screen_scale[1]),
                             self.background_image["o2_1"], 10, 1, rotate_left=False)
        self.o2_actor = MenuActor((1530 * self.screen_scale[0], 570 * self.screen_scale[1]),
                                  [self.background_image[item] for item in self.background_image if
                                   "o2_1_actor" in item], 0,
                                  animation_frame_play_time=0.15)
        self.a4_actor = MenuActor((2320 * self.screen_scale[0], 650 * self.screen_scale[1]),
                                  [self.background_image[item] for item in self.background_image if
                                   "a4_1_actor" in item], 0,
                                  animation_frame_play_time=0.15)
        self.y3_actor = MenuActor((1920 * self.screen_scale[0], 400 * self.screen_scale[1]),
                                  [self.background_image[item] for item in self.background_image if
                                   "y3_1_actor" in item], 0,
                                  animation_frame_play_time=0.15)
        self.l5_actor = MenuActor((2676 * self.screen_scale[0], 520 * self.screen_scale[1]),
                                  [self.background_image[item] for item in self.background_image if
                                   "l5_1_actor" in item], 0,
                                  animation_frame_play_time=0.15)

        self.main_menu_actor = (self.o2, self.o2_actor, self.a4_actor, self.y3_actor, self.l5_actor)

        hide_bg = Surface((self.screen_width, self.screen_height), SRCALPHA)
        hide_bg.fill((0, 0, 0, 200))
        self.hide_background = StaticImage((self.screen_width / 2, self.screen_height / 2), 3, hide_bg)
        self.remove_ui_updater(self.hide_background)

        self.dt = 0
        self.text_delay = 0
        self.add_ui_updater(self.main_menu_buttons)

        self.menu_state = "main_menu"
        self.menu_state_methods = {"main_menu": self.menu_main, "custom": self.menu_custom_setup,
                                   "preset": self.menu_custom_preset, "option": self.menu_option,
                                   "keybind": self.menu_keybind}

        self.input_popup = None  # popup for text input state

        self.loading_screen("end")

        self.run_game()

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
        self.battle.battle_outer_ui_updater.add(self.profiler)

    def run_game(self):
        while True:
            # Get user input
            self.remove_ui_updater(self.text_popup)
            self.dt = self.clock.get_time() / 1000  # dt before game_speed
            self.cursor.scroll_down = False
            self.cursor.scroll_up = False
            self.esc_press = False

            self.player_key_press = {key: False for key in self.player_key_press}
            self.player_key_hold = {key: False for key in self.player_key_hold}

            key_press = pygame.key.get_pressed()

            if not music.get_busy():  # replay menu song when not playing anything
                music.play()

            for key in self.player_key_press:
                if type(self.player_key_bind[key]) is int and key_press[self.player_key_bind[key]]:
                    self.player_key_hold[key] = True

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 4:  # Mouse scroll down
                        self.cursor.scroll_up = True
                    elif event.button == 5:  # Mouse scroll up
                        self.cursor.scroll_down = True

                elif event.type == pygame.KEYDOWN:
                    event_key_press = event.key

                    if self.input_popup:  # event update to input box

                        if event.key == pygame.K_ESCAPE:
                            self.esc_press = True

                        elif self.input_popup[0] == "keybind_input":
                            self.assign_key(event.key)

                        elif self.input_popup[0] == "text_input":
                            self.input_box.player_input(event, key_press)
                            self.text_delay = 0.1
                    else:
                        if event_key_press in self.player_key_bind_name:  # check for key press
                            self.player_key_press[self.player_key_bind_name[event_key_press]] = True

                        if event.key == pygame.K_ESCAPE:
                            self.esc_press = True

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
                        old_key = self.player_key_bind[self.input_popup[1][1]]

                        self.player_key_bind[self.input_popup[1][1]] = self.player_key_bind[self.input_popup[1][2]]
                        self.player_key_bind[self.input_popup[1][2]] = old_key
                        self.config["USER"]["keybind"] = str(self.player_key_bind_list)
                        self.change_keybind()

                    elif self.input_popup[1] == "quit":
                        pygame.time.wait(1000)
                        pygame.quit()
                        sys.exit()

                    if done:
                        self.change_pause_update(False)
                        self.input_box.render_text("")
                        self.input_popup = None
                        self.remove_ui_updater(self.all_input_popup_uis)

                elif self.input_cancel_button.event_press or self.input_close_button.event_press or self.esc_press:
                    self.change_pause_update(False)
                    self.input_box.render_text("")
                    self.input_popup = None
                    self.remove_ui_updater(self.all_input_popup_uis)

                elif self.input_popup[0] == "text_input":
                    if not self.text_delay:
                        if key_press[self.input_box.hold_key]:
                            self.input_box.player_input(None, key_press)
                            self.text_delay = 0.1
                    else:
                        self.text_delay -= self.dt
                        if self.text_delay < 0:
                            self.text_delay = 0

            else:
                self.menu_state_methods[self.menu_state]()

            self.ui_drawer.draw(self.screen)
            display.update()
            self.clock.tick(1000)

