from pygame import Surface, SRCALPHA
from pygame.transform import smoothscale, flip

from engine.uimenu.uimenu import UIMenu
from engine.utils.sprite_altering import apply_sprite_colour
from engine.utils.text_making import text_render_with_bg, make_long_text, minimise_number_text


class UIGrand(UIMenu):
    def __init__(self, player_cursor_interact=False, has_containers=False):
        """
        Parent class for all grand menu user interface that exist inside of grand camera,
        typically player cannot directly interact with them
        """
        from engine.grand.grand import Grand
        UIMenu.__init__(self, player_cursor_interact=player_cursor_interact, has_containers=has_containers)
        self.grand = Grand.grand
        self.grand_camera_ui_drawer = self.grand.grand_camera_ui_drawer
        self.camera = self.grand.camera

    def check_draw(self):
        grand_camera_ui_drawer = self.grand_camera_ui_drawer
        if self.rect.colliderect(self.camera.rect):
            if self not in grand_camera_ui_drawer:
                grand_camera_ui_drawer.add(self)
        elif self in grand_camera_ui_drawer:
            grand_camera_ui_drawer.remove(self)


class DotInfoBanner(UIGrand):
    base_image = Surface((1, 1))  # need to be at size 1,1 here so armydot can check_draw position before reset
    cache_banner_team = {}

    def __init__(self, base_pos, pos):
        self._layer = 5
        UIGrand.__init__(self, has_containers=True, player_cursor_interact=False)
        self.font = self.game.medium_generic_ui_font
        self.base_pos = base_pos
        self.dots_army_occupation = self.grand.dots_army_occupation

        if not self.cache_banner_team:  # create banner cache
            end = self.grand.grand_ui_images["region_banner_end"]
            body = self.grand.grand_ui_images["region_banner_body"]
            self.cache_banner_team["neutral"] = (end, body, flip(self.grand.grand_ui_images["region_banner_end"],
                                                                 True, False))
            # player banner
            coloured_end = apply_sprite_colour(end, (50, 50, 180))
            self.cache_banner_team["player"] = (coloured_end,
                                                apply_sprite_colour(body, (50, 50, 180)),
                                                flip(coloured_end, True, False))
            # enemy banner
            coloured_end = apply_sprite_colour(end, (180, 50, 50))
            self.cache_banner_team["enemy"] = (coloured_end,
                                               apply_sprite_colour(body, (180, 50, 50)),
                                               flip(coloured_end, True, False))
            # ally banner
            coloured_end = apply_sprite_colour(end, (50, 180, 50))
            self.cache_banner_team["ally"] = (coloured_end,
                                              apply_sprite_colour(body, (50, 180, 50)),
                                              flip(coloured_end, True, False))
        self.previous_state_value_list = {}
        self.pos = pos
        self.image = self.base_image
        self.rect = self.image.get_rect(midtop=pos)

    def make_text_image(self, team, text):
        banner = self.cache_banner_team[team]
        if type(text) is str:
            text_image = text_render_with_bg(text, self.font)
        else:
            text_image = make_long_text(text, self.font,
                                        with_texture=(None, ((30, 30, 30), (255, 255, 255), 2)))
        banner_left = banner[0]
        banner_right = banner[2]
        banner_body = smoothscale(banner[1], (text_image.get_width(), banner[1].get_height()))
        banner_body_width = banner_body.get_width()
        banner_body_height = banner_body.get_height()
        banner_body.blit(text_image, text_image.get_rect(center=(banner_body_width / 2, banner_body_height / 2)))
        self.image = Surface(((banner_left.get_width() * 2) + banner_body_width,
                              banner_body_height), SRCALPHA)
        left_rect = banner_left.get_rect()
        self.image.blit(banner_left, left_rect)
        self.image.blit(banner_body, banner_body.get_rect(topleft=left_rect.topright))
        self.image.blit(banner_right, banner_right.get_rect(topright=(self.image.get_width(), 0)))

    def update(self, dt):
        self.check_draw()


class DotNameBannerSettlement(DotInfoBanner):
    def __init__(self, base_pos, pos, region):
        DotInfoBanner.__init__(self, base_pos, pos)
        self.region = region
        self.reset(self.grand.current_campaign_state["region"][region]["control"])

    def reset(self, faction_owner):
        team = "neutral"
        if faction_owner == self.grand.player_faction:
            team = "player"
        elif self.grand.player_faction:
            if faction_owner in self.grand.current_campaign_state["faction"][self.grand.player_faction]["alliance"]:
                team = "ally"
            elif faction_owner != "free":
                team = "enemy"

        self.make_text_image(team, self.grab_text(("region", self.region, "Name")))
        self.rect = self.image.get_rect(midtop=self.pos)


class DotInfoBannerSettlement(DotInfoBanner):
    def __init__(self, base_pos, pos, region):
        DotInfoBanner.__init__(self, base_pos, pos)
        self.name_image = None
        self.income_image = None
        self.previous_income = ()
        self.owner = None
        self.region = region
        self.reset(self.grand.current_campaign_state["region"][region]["control"])

    def check_draw(self):
        if self.owner == self.grand.player_faction and self.rect.colliderect(self.camera.rect):
            if self not in self.grand_camera_ui_drawer:
                self.grand_camera_ui_drawer.add(self)
        else:
            if self in self.grand_camera_ui_drawer:
                self.grand_camera_ui_drawer.remove(self)

    def reset(self, faction_owner):
        self.owner = faction_owner
        if faction_owner == self.grand.player_faction:
            income_state = self.grand.current_campaign_state["region"][self.region]["income"].copy()
            if self.previous_income != income_state:
                self.previous_income = income_state
                text = [minimise_number_text(income_state["gold_income"]), self.grand_ui_images["gold"], "/",
                        minimise_number_text(income_state["supply_income"]), self.grand_ui_images["supply"], "/"]
                if income_state["happiness"] > 0:
                    text.append(self.grand_ui_images["happiness"])
                else:
                    text.append(self.grand_ui_images["anger"])
                self.make_text_image("player", text)

            self.rect = self.image.get_rect(midbottom=self.pos)


class DotInfoBannerArmy(DotInfoBanner):
    def __init__(self, base_pos, pos):
        DotInfoBanner.__init__(self, base_pos, pos)

    def reset(self, state_value_list):
        if "battle" in state_value_list:
            text = ((minimise_number_text(state_value_list[0][0]), self.grand_ui_images["number"]), "/",
                    state_value_list[0][1] + "%", self.grand_ui_images["supply"], "VS",
                    minimise_number_text(state_value_list[1][0]), self.grand_ui_images["number"], "/",
                    state_value_list[1][1] + "%", self.grand_ui_images["supply"])
            team = state_value_list[2]
        else:
            team = state_value_list[2]
            text = (minimise_number_text(state_value_list[0]), self.grand_ui_images["number"], "/",
                    state_value_list[1] + "%",
                    self.grand_ui_images["supply"])
        self.make_text_image(team, text)
        self.rect = self.image.get_rect(midtop=self.pos)

    def check_draw(self, active):
        grand_camera_ui_drawer = self.grand_camera_ui_drawer
        if active and self.rect.colliderect(self.camera.rect):
            player_faction = self.grand.player_faction
            if self.base_pos in self.grand.current_campaign_state["battle"]["dot"]:  # battle going on
                state_value_list = [[0, "100"], [0, "100"], "neutral", "battle"]
                for team, team_value in self.grand.current_campaign_state["battle"]["auto"][self.base_pos].items():
                    total_supply = 0
                    total_supply_usage = 0
                    team_index = team - 1
                    for army in team_value.values():
                        if player_faction and state_value_list[2] not in ("player", "ally"):
                            if army.belong_to_player_faction:
                                state_value_list[2] = "player"
                            elif army.faction in self.grand.current_campaign_state["faction"][player_faction]["alliance"]:
                                state_value_list[2] = "ally"
                            else:
                                state_value_list[2] = "enemy"
                        state_value_list[team_index][0] += army.total_number
                    if total_supply_usage:
                        state_value_list[team_index][1] = str(int(total_supply / total_supply_usage * 100))

            else:
                state_value_list = [0, "100", "neutral"]
                total_supply = 0
                total_supply_usage = 0
                for army in self.dots_army_occupation[self.base_pos]:
                    state_value_list[0] += army.total_number
                    total_supply += army.supply
                    total_supply_usage += army.total_supply_usage
                    if player_faction and state_value_list[2] not in ("player", "ally"):
                        if army.belong_to_player_faction:
                            state_value_list[2] = "player"
                        elif army.faction in self.grand.current_campaign_state["faction"][player_faction]["alliance"]:
                            state_value_list[2] = "ally"
                        else:
                            state_value_list[2] = "enemy"

                if total_supply_usage:
                    state_value_list[1] = str(int(total_supply / total_supply_usage * 100))

                if state_value_list != self.previous_state_value_list:
                    self.previous_state_value_list = state_value_list
                    self.reset(state_value_list)

            if self not in grand_camera_ui_drawer:
                grand_camera_ui_drawer.add(self)
        elif self in grand_camera_ui_drawer:
            grand_camera_ui_drawer.remove(self)

    def update(self, dt):
        active = False
        if (self.base_pos in self.grand.current_campaign_state["battle"]["dot"] or
                self.dots_army_occupation[self.base_pos]):
            active = True

        self.check_draw(active)
