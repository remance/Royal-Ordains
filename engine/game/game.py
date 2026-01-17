import ast
import configparser
import os.path
import sys
from copy import deepcopy

import pygame
from pygame import sprite, display, mouse
from pygame.font import Font
from pygame.locals import *
from pygame.mixer import Sound, Channel

from engine.army.army import Army
from engine.battle.battle import Battle
from engine.battleobject.battleobject import StageObject
from engine.character.character import Character, BattleCharacter
from engine.constants import *
from engine.data.datalocalisation import Localisation
from engine.data.datamap import MapData
from engine.data.datasave import SaveData
from engine.data.datasound import SoundData
from engine.data.datasprite import SpriteData
from engine.data.datastat import CharacterData
from engine.effect.effect import Effect
from engine.game.activate_input_popup import activate_input_popup
from engine.game.assign_key import assign_key
from engine.game.back_mainmenu import back_mainmenu
from engine.game.change_keybind import change_keybind
from engine.game.change_pause_update import change_pause_update
from engine.game.change_sound_volume import change_sound_volume
from engine.game.convert_army_to_deployable import convert_army_to_deployable
from engine.game.create_config import create_config
from engine.game.get_keybind_button_name import get_keybind_button_name
from engine.game.load_grand_campaign import load_grand_campaign
from engine.game.loading_screen import loading_screen
from engine.game.make_input_box import make_input_box
from engine.game.make_lorebook import make_lorebook
from engine.game.make_option_menu import make_option_menu
from engine.game.menu_custom_preset import menu_custom_preset
from engine.game.menu_custom_setup import menu_custom_setup
from engine.game.menu_grand_setup import menu_grand_setup
from engine.game.menu_keybind import menu_keybind
from engine.game.menu_main import menu_main
from engine.game.menu_mission_setup import menu_mission_setup
from engine.game.menu_option import menu_option
from engine.game.start_battle import start_battle
from engine.grandobject.grandobject import GrandObject
from engine.lorebook.lorebook import Lorebook, lorebook_process
from engine.menuobject.menuobject import MenuActor, MenuRotate, StaticImage
from engine.uibattle.uibattle import (Profiler, FPSCount, CharacterSpeechBox)
from engine.uimenu.uimenu import (OptionMenuText, SliderMenu, MenuCursor, BoxUI, BrownMenuButton, MenuButton,
                                  TextPopup, CustomTeamSetupUI, FactionSelector, CustomPresetArmySetupUI, GrandMiniMap,
                                  GrandFactionDetail, GrandFactionShowCase,
                                  CharacterSelector, CustomPresetTitle, ListUI, CustomPresetListAdapter,
                                  GenericListAdapter)
from engine.updater.updater import ReversedLayeredUpdates
from engine.utils.data_loading import load_image, load_images, csv_read

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

    game_version = "0.2.3.6"

    # import from game
    activate_input_popup = activate_input_popup
    assign_key = assign_key
    back_mainmenu = back_mainmenu
    change_keybind = change_keybind
    change_pause_update = change_pause_update
    change_sound_volume = change_sound_volume
    convert_army_to_deployable = convert_army_to_deployable
    create_config = create_config
    get_keybind_button_name = get_keybind_button_name
    load_grand_campaign = load_grand_campaign
    loading_screen = loading_screen
    make_input_box = make_input_box
    make_lorebook = make_lorebook
    make_option_menu = make_option_menu
    menu_custom_preset = menu_custom_preset
    menu_custom_setup = menu_custom_setup
    menu_grand_setup = menu_grand_setup
    menu_mission_setup = menu_mission_setup
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

        self.campaign = None
        self.menu_state = "main_menu"

        # Read config file
        config = configparser.ConfigParser()  # initiate config reader
        try:
            config.read_file(open(self.config_path))  # read config file
        except FileNotFoundError:  # Create config file if not found with the default
            config = self.create_config()

        try:
            self.config = config
            self.show_fps = int(self.config["USER"]["fps"])
            self.use_simple_text = int(self.config["USER"]["easy_text"])
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
            self.use_simple_text = int(self.config["USER"]["easy_text"])
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
        self.before_save_preset_army_setup = deepcopy(self.save_data.custom_army_preset_save)

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
        self.loading_screen_lore_font = Font(self.ui_font["main_button"], int(60 * self.screen_scale[1]))

        self.generic_ui_font = Font(self.ui_font["main_button"], int(30 * self.screen_scale[1]))
        self.fps_counter_font = Font(self.ui_font["main_button"], int(40 * self.screen_scale[1]))
        self.large_text_font = Font(self.ui_font["main_button"], int(50 * self.screen_scale[1]))
        self.battle_timer_font = Font(self.ui_font["main_button"], int(54 * self.screen_scale[1]))
        self.screen_fade_font = Font(self.ui_font["manuscript_font"], int(100 * self.screen_scale[1]))
        self.character_indicator_font = Font(self.ui_font["manuscript_font"], int(50 * self.screen_scale[1]))
        self.damage_number_font = Font(self.ui_font["manuscript_font"], int(46 * self.screen_scale[1]))
        self.critical_damage_number_font = Font(self.ui_font["manuscript_font2"], int(76 * self.screen_scale[1]))
        self.character_name_talk_prompt_font = Font(self.ui_font["talk_font"], int(40 * self.screen_scale[1]))
        self.drama_font = Font(self.ui_font["manuscript_font"], int(90 * self.screen_scale[1]))
        self.preset_name_font = Font(self.ui_font["main_button"], int(60 * self.screen_scale[1]))
        self.note_font = Font(self.ui_font["main_button"], int(24 * self.screen_scale[1]))
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

        # Assign containers
        OptionMenuText.containers = self.menu_icon
        SliderMenu.containers = self.menu_slider

        StaticImage.containers = self.ui_updater, self.ui_drawer
        MenuRotate.containers = self.ui_updater, self.ui_drawer
        MenuActor.containers = self.ui_updater, self.ui_drawer

        # SubsectionName.containers = self.ui_updater, self.ui_drawer, self.battle_ui_updater, self.battle_ui_drawer

        # Load sound effect
        self.sound_data = SoundData()
        self.sound_effect_pool = self.sound_data.sound_effect_pool
        self.music_pool = self.sound_data.music_pool
        self.ambient_pool = self.sound_data.ambient_pool
        self.weather_ambient_pool = self.sound_data.weather_ambient_pool
        
        # Music player
        pygame.mixer.set_num_channels(1000)
        self.music = Channel(0)
        self.music.set_volume(self.play_music_volume)
        self.current_ambient = None
        self.ambient = Channel(1)
        self.ambient.set_volume(self.play_effect_volume)
        self.weather_ambient = Channel(2)
        self.weather_ambient.set_volume(self.play_effect_volume)
        self.button_sound = Channel(3)
        self.button_sound.set_volume(self.play_effect_volume)
        self.music.play(Sound(self.music_pool["Menu"]), loops=-1)

        self.game_intro(False)  # run intro

        # Load game localisation data
        self.localisation = Localisation()
        Game.localisation = self.localisation

        # Create game cursor, make sure it is the first object in ui to be created, so it is always update first
        Game.cursor = MenuCursor(load_images(self.data_dir, subfolder=("ui", "cursor_menu")))  # no need to scale cursor
        self.add_to_ui_updater(self.cursor)

        # Battle related data
        self.character_data = CharacterData()
        self.map_data = MapData()

        self.preset_map_data = self.map_data.preset_map_data

        if self.show_dmg_number:
            BattleCharacter.show_dmg_number = True
        Army.character_list = self.character_data.character_list
        Character.character_data = self.character_data
        Character.status_list = self.character_data.status_list
        Character.status_apply_funcs = self.character_data.status_apply_funcs
        Character.effect_list = self.character_data.effect_list

        Effect.effect_list = self.character_data.effect_list

        self.sprite_data = SpriteData(self.character_data.character_list, self.character_indicator_font)
        self.character_animation_data = self.sprite_data.character_animation_data  # character animation data pool
        self.character_portraits = self.sprite_data.character_portraits
        self.stage_object_animation_pool = self.sprite_data.stage_object_animation_pool
        self.grand_object_animation_pool = self.sprite_data.grand_object_animation_pool
        self.effect_animation_pool = self.sprite_data.effect_animation_pool  # effect sprite animation pool

        Effect.effect_animation_pool = self.effect_animation_pool
        StageObject.stage_object_animation_pool = self.stage_object_animation_pool
        GrandObject.grand_object_animation_pool = self.grand_object_animation_pool

        # Load UI images
        self.weather_icon_images = load_images(self.data_dir, screen_scale=self.screen_scale,
                                               subfolder=("ui", "weather_ui"), key_file_name_readable=True)
        self.option_menu_images = load_images(self.data_dir, screen_scale=self.screen_scale,
                                              subfolder=("ui", "option_ui"))
        image = load_image(self.data_dir, self.screen_scale, "drop_normal.png", ("ui", "mainmenu_ui"))
        image2 = load_image(self.data_dir, self.screen_scale, "drop_click.png", ("ui", "mainmenu_ui"))
        self.drop_button_lists = (image, image2, image2)

        text_button_image = load_image(self.data_dir, self.screen_scale, "text_normal.png", ("ui", "mainmenu_ui"))
        text_button_image2 = load_image(self.data_dir, self.screen_scale, "text_click.png", ("ui", "mainmenu_ui"))
        self.text_button_image_list = (text_button_image, text_button_image2, text_button_image2)

        # Main menu interface
        self.fps_count = FPSCount(self)  # FPS number counter
        if self.show_fps:
            self.add_to_ui_updater(self.fps_count)
        if self.use_simple_text:
            CharacterSpeechBox.simple_font = True

        BrownMenuButton.button_frame = load_image(self.game.data_dir, (1, 1),
                                                  "new_button.png", ("ui", "mainmenu_ui"))
        main_menu_buttons_box = BoxUI((0, -8),
                                      (self.screen_width, 200 * self.screen_scale[1]), parent=self.screen)

        self.grand_button = BrownMenuButton((.15, 0.5), (-0.6, -1.5), key_name="main_menu_start_game",
                                            parent=main_menu_buttons_box)
        self.mission_button = BrownMenuButton((.15, 0.5), (-0.2, -1.5), key_name="main_menu_start_mission",
                                              parent=main_menu_buttons_box)
        self.test_battle_button = BrownMenuButton((.15, 0.5), (0.2, -1.5), key_name="main_menu_test_battle",
                                                  parent=main_menu_buttons_box)
        self.custom_battle_button = BrownMenuButton((.15, 0.5), (0.6, -1.5), key_name="main_menu_custom_game",
                                                    parent=main_menu_buttons_box)
        self.option_button = BrownMenuButton((.15, 0.5), (-0.25, 0), key_name="game_option",
                                             parent=main_menu_buttons_box)
        self.quit_button = BrownMenuButton((.15, 0.5), (0.25, 0), key_name="game_quit",
                                           parent=main_menu_buttons_box)

        self.main_menu_buttons = (
        self.grand_button, self.mission_button, self.test_battle_button, self.custom_battle_button,
        self.option_button, self.quit_button)

        self.text_popup = TextPopup(font_size=50, layer=10000)
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

        # Custom battle select menu button
        self.custom_team1_player = "player"
        self.custom_team2_player = "computer"
        self.custom_team_army = {index: [Army(None, [], [], [], []) for _ in range(5)] for index in (1, 2)}

        self.selected_custom_map_battle = Default_Selected_Map_Custom_Battle
        self.team1_supply_limit_custom_battle = Default_Supply_limit_Custom_Battle
        self.team2_supply_limit_custom_battle = Default_Supply_limit_Custom_Battle
        self.team1_gold_limit_custom_battle = Default_Gold_limit_Custom_Battle
        self.team2_gold_limit_custom_battle = Default_Gold_limit_Custom_Battle
        self.selected_weather_custom_battle = Default_Weather_Custom_Battle
        self.selected_weather_strength_custom_battle = Default_Weather_Strength_Custom_Battle

        self.setup_back_button = BrownMenuButton((.15, 0.5), (0.6, 0),
                                                 key_name="back_button", parent=main_menu_buttons_box)

        self.custom_battle_setup_start_battle_button = BrownMenuButton((.15, 0.5), (-0.6, 0), key_name="start_button",
                                                                       parent=main_menu_buttons_box)
        self.custom_battle_preset_button = BrownMenuButton((.15, 0.5), (0, 0), key_name="custom_preset_button",
                                                           parent=main_menu_buttons_box)

        self.custom_battle_multi_purposes_list = ListUI(pivot=(-0.15, 0.14), origin=(-1, -1), size=(0.2, 0.35),
                                                        items=GenericListAdapter(()),
                                                        parent=self.screen, item_size=10, layer=10000)

        self.custom_battle_map_button = MenuButton(
            self.drop_button_lists, (self.screen_rect.width * 0.3, self.screen_rect.height * 0.05),
            key_name="map_" + self.selected_custom_map_battle, font_size=52, layer=151)
        self.custom_map_list = ("map_Custom1", "map_Custom2", "map_Custom3", "map_Custom4", "map_Custom5")
        self.custom_map_bar = ListUI(pivot=(-0.55, -0.85), origin=(-1, -1), size=(0.15, 0.25),
                                     items=GenericListAdapter(
                                         [(-0, self.localisation.grab_text(("ui", item))) for item in
                                          self.custom_map_list]),
                                     parent=self.screen, item_size=8, layer=10000)

        self.custom_battle_weather_strength_button = MenuButton(
            self.drop_button_lists, (self.screen_rect.width * 0.5, self.screen_rect.height * 0.05),
            key_name="weather_strength_" + str(self.selected_weather_strength_custom_battle), font_size=52, layer=151)
        self.custom_weather_strength_list = ("weather_strength_0", "weather_strength_1", "weather_strength_2")
        self.custom_weather_strength_bar = ListUI(pivot=(-0.15, -0.85), origin=(-1, -1), size=(0.15, 0.25),
                                                  items=GenericListAdapter(
                                                      [(0, self.localisation.grab_text(("ui", item))) for item in
                                                       self.custom_weather_strength_list]),
                                                  parent=self.screen, item_size=8, layer=10000)

        self.custom_battle_weather_type_button = MenuButton(
            self.drop_button_lists, (self.screen_rect.width * 0.7, self.screen_rect.height * 0.05),
            key_name="weather_" + str(self.selected_weather_custom_battle), font_size=52, layer=151)
        self.custom_weather_list = tuple(self.map_data.weather_data.keys())
        self.custom_weather_bar = ListUI(pivot=(0.25, -0.85), origin=(-1, -1), size=(0.15, 0.25),
                                         items=GenericListAdapter([(
                                             0, self.localisation.grab_text(("ui", "weather_" + str(item)))) for item in
                                             self.custom_weather_list]),
                                         parent=self.screen, item_size=8, layer=10000)

        self.custom_battle_team1_supply_button = MenuButton(
            self.text_button_image_list, (self.screen_rect.width * 0.15, self.screen_rect.height * 0.1),
            key_name=("Supply Limit:", self.team1_supply_limit_custom_battle), font_size=52, layer=151)
        self.custom_battle_team2_supply_button = MenuButton(
            self.text_button_image_list, (self.screen_rect.width * 0.65, self.screen_rect.height * 0.1),
            key_name=("Supply Limit:", self.team2_supply_limit_custom_battle), font_size=52, layer=151)

        self.custom_battle_team1_gold_button = MenuButton(
            self.text_button_image_list, (self.screen_rect.width * 0.35, self.screen_rect.height * 0.1),
            key_name=("Gold Limit:", self.team1_gold_limit_custom_battle), font_size=52, layer=151)
        self.custom_battle_team2_gold_button = MenuButton(
            self.text_button_image_list, (self.screen_rect.width * 0.85, self.screen_rect.height * 0.1),
            key_name=("Gold Limit:", self.team2_gold_limit_custom_battle), font_size=52, layer=151)

        self.player_image = {"player": load_image(self.game.data_dir, self.screen_scale,
                                                  "player.png", ("ui", "mainmenu_ui")),
                             "computer": load_image(self.game.data_dir, self.screen_scale,
                                                    "computer.png", ("ui", "mainmenu_ui"))}
        self.custom_battle_team1_setup = CustomTeamSetupUI(1, (self.screen_width * 0.25, self.screen_height * 0.435))
        self.custom_battle_team2_setup = CustomTeamSetupUI(2, (self.screen_width * 0.75, self.screen_height * 0.435))

        self.custom_faction_list = ["Random", "All"]
        self.custom_faction_list += [key for key in self.game.sprite_data.faction_coas if
                                     key not in self.custom_faction_list]
        self.custom_team_army_buttons = {1: [], 2: []}
        self.custom_team_army_button_bars = {1: [], 2: []}
        self.last_shown_custom_army = None
        y_pos = (0.27, 0.37, 0.48, 0.58, 0.68)
        y_pivot = (-0.43, -0.23, -0.01, 0.18, 0.385)
        team_x_pos = {1: self.screen_rect.width * 0.22, 2: self.screen_rect.width * 0.72}
        team_y_pivot = {1: -0.7, 2: 0.3}
        for team in (1, 2):
            for index in range(0, 5):
                self.custom_team_army_buttons[team].append(MenuButton(
                    self.drop_button_lists, (team_x_pos[team], self.screen_rect.height * y_pos[index]),
                    font_size=52, layer=9000))
                self.custom_team_army_button_bars[team].append(ListUI(pivot=(team_y_pivot[team], y_pivot[index]),
                                                                      origin=(-1, -1), size=(0.15, 0.25),
                                                                      items=GenericListAdapter([]),
                                                                      parent=self.screen, item_size=8, layer=10000))

        self.custom_faction_selector_popup = FactionSelector(1200,
                                                             (self.screen_width / 2, 0), layer=10000,
                                                             is_popup=True)
        self.custom_army_info_popup = CustomPresetArmySetupUI((self.screen_width * 0.5, self.screen_height * 0.5),
                                                              False, layer=100000)
        self.custom_army_title_popup = CustomPresetTitle((self.custom_army_info_popup.image.get_width(),
                                                          80 * self.screen_scale[1]),
                                                         (self.screen_rect.width / 2,
                                                          self.custom_army_info_popup.rect.midtop[1]))
        self.custom_battle_menu_uis = (self.setup_back_button, self.custom_battle_preset_button,
                                       self.custom_battle_setup_start_battle_button,
                                       self.custom_battle_weather_type_button,
                                       self.custom_battle_weather_strength_button,
                                       self.custom_battle_map_button, self.custom_battle_team1_setup,
                                       self.custom_battle_team2_setup,
                                       self.custom_battle_team1_supply_button,
                                       self.custom_battle_team2_supply_button,
                                       self.custom_battle_team1_gold_button,
                                       self.custom_battle_team2_gold_button)

        self.all_custom_battle_bars = (
                    [self.custom_map_bar, self.custom_weather_strength_bar, self.custom_weather_bar] +
                    self.custom_team_army_button_bars[1] + self.custom_team_army_button_bars[2])

        self.custom_battle_menu_uis_remove = tuple(list(self.custom_battle_menu_uis) + [
            self.custom_faction_selector_popup, self.custom_army_info_popup, self.custom_army_title_popup] +
                                                   self.custom_team_army_buttons[1] + self.custom_team_army_buttons[2] +
                                                   list(self.all_custom_battle_bars))

        # preset army setup for custom battle ui
        self.preset_back_button = BrownMenuButton((.15, 0.5), (0.3, 0),
                                                  key_name="back_button", parent=main_menu_buttons_box)
        self.preset_save_button = BrownMenuButton((.15, 0.5), (-0.3, 0), key_name="save_button",
                                                  parent=main_menu_buttons_box)

        self.custom_preset_army_setup = CustomPresetArmySetupUI((self.screen_width * 0.4, self.screen_height * 0.2),
                                                                True)
        self.custom_preset_army_title = CustomPresetTitle((self.game.screen_width * 0.8, 80 * self.screen_scale[1]),
                                                          (self.screen_rect.width / 2,
                                                           self.custom_preset_army_setup.rect.midtop[1]))
        self.custom_character_selector = CharacterSelector((self.screen_width * 0.78, self.screen_height * 0.2))
        self.custom_preset_list_box = ListUI(pivot=(-0.9, -0.6), origin=(-1, -1), size=(0.15, 0.5),
                                             items=CustomPresetListAdapter(),
                                             parent=self.screen, item_size=20)
        self.faction_selector = FactionSelector(3800, (self.screen_width / 2, 0), army_create=True)

        self.custom_preset_menu_uis = (self.preset_back_button, self.preset_save_button, self.custom_preset_list_box,
                                       self.faction_selector, self.custom_preset_army_setup,
                                       self.custom_character_selector,
                                       self.custom_preset_army_title)

        # mission select menu button
        self.mission_setup_start_button = BrownMenuButton((.15, 0.5), (-0.6, 0), key_name="start_button",
                                                          parent=main_menu_buttons_box)
        self.mission_menu_uis = (self.mission_setup_start_button, self.setup_back_button,)

        # Grand strategy select menu button
        self.load_grand_button = BrownMenuButton((.15, 0.5), (0, 0), key_name="main_menu_load_game",
                                                 parent=main_menu_buttons_box)
        self.grand_setup_start_button = BrownMenuButton((.15, 0.5), (-0.6, 0), key_name="start_button",
                                                        parent=main_menu_buttons_box)
        self.grand_mini_map = GrandMiniMap(self.faction_selector.rect.midbottom, (2000, 1000), "setup")
        self.grand_faction_detail = GrandFactionDetail()

        self.faction_showcase_banners = load_images(self.data_dir, screen_scale=self.screen_scale,
                                                    subfolder=("ui", "faction_ui", "banner"),
                                                    key_file_name_readable=True)
        self.grand_faction_showcase = GrandFactionShowCase(self.faction_showcase_banners)
        self.grand_menu_uis = (self.setup_back_button, self.load_grand_button, self.grand_mini_map,
                               self.grand_faction_detail, self.grand_faction_showcase,
                               self.grand_setup_start_button, self.faction_selector)

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
        # self.grand = Grand(self)

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
        self.dt = 0
        self.input_delay = 0
        self.text_delay = 0
        self.add_to_ui_updater(self.main_menu_buttons)

        self.menu_state_methods = {"main_menu": self.menu_main, "custom": self.menu_custom_setup,
                                   "grand": self.menu_grand_setup,
                                   "mission": self.menu_mission_setup,
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

    def add_to_ui_updater(self, *args):
        self.ui_updater.add(*args)
        self.ui_drawer.add(*args)

    def remove_from_ui_updater(self, *args):
        self.ui_updater.remove(*args)
        self.ui_drawer.remove(*args)

    def setup_profiler(self):
        self.profiler = Profiler()
        self.profiler.enable()
        self.battle.outer_ui_updater.add(self.profiler)

    def run_game(self):
        while True:
            # Get user input
            self.remove_from_ui_updater(self.text_popup)
            self.dt = self.clock.get_time() / 1000  # dt before game_speed
            if self.input_delay:
                self.input_delay -= self.dt
                if self.input_delay < 0:
                    self.input_delay = 0
            self.cursor.scroll_down = False
            self.cursor.scroll_up = False
            self.esc_press = False

            self.player_key_press = {key: False for key in self.player_key_press}
            self.player_key_hold = {key: False for key in self.player_key_hold}

            key_press = pygame.key.get_pressed()

            if not self.music.get_busy():  # play menu song when not playing anything
                self.music.play(Sound(self.music_pool["Menu"]), loops=-1)

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
                            self.text_delay = 0.15
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

                    elif self.input_popup[1] == "new_preset":
                        if self.input_box.text and "custom_" + self.input_box.text not in self.before_save_preset_army_setup:
                            if self.custom_preset_army_setup.selected_faction not in self.before_save_preset_army_setup:
                                self.before_save_preset_army_setup[self.custom_preset_army_setup.selected_faction] = {}
                            save_preset = deepcopy(self.custom_preset_army_setup.army_preset)
                            save_preset["Name"] = self.input_box.text
                            self.before_save_preset_army_setup[self.custom_preset_army_setup.selected_faction][
                                "custom_" + self.input_box.text] = save_preset
                            self.custom_preset_army_setup.army_preset = self.before_save_preset_army_setup[
                                self.custom_preset_army_setup.selected_faction]["custom_" + self.input_box.text]

                            self.custom_preset_list_box.adapter.__init__()
                            self.custom_preset_army_title.change_text(self.input_box.text,
                                                                      self.custom_preset_army_setup.total_gold_cost)
                            self.custom_preset_army_setup.change_portrait_selection(None, None)

                        else:
                            done = False
                            self.activate_input_popup(("confirm_input", "exist_name"),
                                                      self.localisation.grab_text(("ui", "name_in_use_warn")),
                                                      self.game.inform_popup_uis)

                    elif "remove_preset" in self.input_popup[1]:
                        self.before_save_preset_army_setup[self.custom_preset_army_setup.selected_faction].pop(
                            self.input_popup[1][1])
                        if self.input_popup[1][1] == self.custom_preset_army_setup.current_preset:
                            self.custom_preset_army_setup.current_preset = ""
                            self.custom_preset_army_title.change_text("", self.custom_preset_army_setup.total_gold_cost)
                        self.custom_preset_list_box.adapter.__init__()

                    elif self.input_popup[1] == "custom_gold":
                        if self.input_box.text.isdigit():
                            if self.input_popup[2] == 1:
                                self.team1_gold_limit_custom_battle = int(self.input_box.text)
                                self.custom_battle_team1_gold_button.change_state(
                                    ("Gold Limit:", self.team1_gold_limit_custom_battle))
                                self.custom_battle_team1_setup.change_cost(0, self.custom_team_army[1][0].cost)
                            else:
                                self.team2_gold_limit_custom_battle = int(self.input_box.text)
                                self.custom_battle_team2_gold_button.change_state(
                                    ("Gold Limit:", self.team2_gold_limit_custom_battle))
                                self.custom_battle_team2_setup.change_cost(0, self.custom_team_army[2][0].cost)

                    elif self.input_popup[1] == "custom_supply":
                        if self.input_box.text.isdigit():
                            if self.input_popup[2] == 1:
                                self.team1_supply_limit_custom_battle = int(self.input_box.text)
                                self.custom_battle_team1_supply_button.change_state(
                                    ("Supply Limit:", self.team1_supply_limit_custom_battle))
                            else:
                                self.team2_supply_limit_custom_battle = int(self.input_box.text)
                                self.custom_battle_team2_supply_button.change_state(
                                    ("Supply Limit:", self.team2_supply_limit_custom_battle))

                    elif self.input_popup[1] == "quit":
                        pygame.time.wait(1000)
                        pygame.quit()
                        sys.exit()

                    if done:
                        self.change_pause_update(False)
                        self.input_box.render_text("")
                        self.input_popup = None
                        self.remove_from_ui_updater(self.all_input_popup_uis)

                elif self.input_cancel_button.event_press or self.input_close_button.event_press or self.esc_press:
                    self.change_pause_update(False)
                    self.input_box.render_text("")
                    self.input_popup = None
                    self.remove_from_ui_updater(self.all_input_popup_uis)

                elif self.input_popup[0] == "text_input":
                    if not self.text_delay:
                        if key_press[self.input_box.hold_key]:
                            self.input_box.player_input(None, key_press)
                            self.text_delay = 0.15
                    else:
                        self.text_delay -= self.dt
                        if self.text_delay < 0:
                            self.text_delay = 0

            else:
                self.menu_state_methods[self.menu_state]()

            self.ui_drawer.draw(self.screen)
            display.update()
            self.clock.tick(1000)
