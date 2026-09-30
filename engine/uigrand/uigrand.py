from pygame import Surface, SRCALPHA
from pygame.transform import smoothscale, flip

from engine.uimenu.uimenu import UIMenu
from engine.utils.sprite_altering import apply_sprite_colour
from engine.utils.text_making import text_render_with_bg, minimise_number_text


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
    banner_team_cache = {}

    def __init__(self, base_pos, pos):
        self._layer = 5
        UIGrand.__init__(self, has_containers=True, player_cursor_interact=False)
        self.font = self.game.medium_generic_ui_font
        self.base_pos = base_pos
        self.dots_army_occupation = self.grand.dots_army_occupation

        if not self.banner_team_cache:  # create banner cache
            end = self.grand.grand_ui_images["region_banner_end"]
            body = self.grand.grand_ui_images["region_banner_body"]
            self.banner_team_cache["neutral"] = (end, body, flip(self.grand.grand_ui_images["region_banner_end"],
                                                                 True, False))
            coloured_end = apply_sprite_colour(end, (100, 100, 220))
            self.banner_team_cache["player"] = (coloured_end,
                                                apply_sprite_colour(body, (100, 100, 220)),
                                                flip(coloured_end, True, False))
            coloured_end = apply_sprite_colour(end, (220, 100, 100))
            self.banner_team_cache["enemy"] = (coloured_end,
                                                 apply_sprite_colour(body, (220, 100, 100)),
                                                 flip(coloured_end, True, False))
        self.previous_state_value_list = {}
        self.pos = pos
        self.image = self.base_image
        self.rect = self.image.get_rect(midtop=pos)

    def make_text_image(self, team, text):
        banner = self.banner_team_cache[team]
        text_image = text_render_with_bg(text, self.font)
        banner_body = smoothscale(banner[1], (text_image.get_width(), banner[1].get_height()))
        banner_body_width = banner_body.get_width()
        banner_body_height = banner_body.get_height()
        banner_body.blit(text_image, text_image.get_rect(center=(banner_body_width / 2,
                                                                 banner_body_height / 2)))
        self.image = Surface(((banner[0].get_width() * 2) + banner_body_width,
                              banner_body_height), SRCALPHA)
        left_rect = banner[0].get_rect(topleft=(0, 0))
        self.image.blit(banner[0], left_rect)
        self.image.blit(banner_body, banner_body.get_rect(topleft=left_rect.topright))
        self.image.blit(banner[2], banner[2].get_rect(topright=(self.image.get_width(), 0)))

    def update(self, dt):
        self.check_draw()


class DotNameBannerSettlement(DotInfoBanner):
    def __init__(self, base_pos, pos, region):
        DotInfoBanner.__init__(self, base_pos, pos)
        self.region = region
        self.reset(self.grand.current_campaign_state["region"]["control"][region])

    def reset(self, faction_owner):
        team = "neutral"
        if faction_owner == self.grand.player_faction:
            team = "player"
        elif self.grand.player_faction and faction_owner != "free":
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
        self.reset(self.grand.current_campaign_state["region"]["control"][region])

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
            income_state = self.grand.current_campaign_state["region"]["income"][self.region].copy()
            if self.previous_income != income_state:
                self.previous_income = income_state
                self.make_text_image("player",
                                     "G:" + minimise_number_text(income_state["gold_income"]) + ", " +
                                     "S:" + minimise_number_text(income_state["supply_income"]) + ", " +
                                     "H:" + minimise_number_text(income_state["happiness"]))

            self.rect = self.image.get_rect(midbottom=self.pos)



class DotInfoBannerArmy(DotInfoBanner):
    def __init__(self, base_pos, pos):
        DotInfoBanner.__init__(self, base_pos, pos)

    def reset(self, state_value_list):
        if "battle" in state_value_list:
            text = " VS "
            team = "player"
        else:
            if state_value_list["player"][0]:
                text = (minimise_number_text(state_value_list["player"][0]) + "/" +
                        minimise_number_text(
                            state_value_list["player"][1] / state_value_list["player"][2] * 100) + "%")
                team = "player"
            elif state_value_list["enemy"][0]:
                text = (minimise_number_text(state_value_list["enemy"][0]) + "/" +
                        minimise_number_text(
                            state_value_list["enemy"][1] / state_value_list["enemy"][2] * 100) + "%")
                team = "enemy"
            else:
                # neutral only shown when no player or enemy army in this dot
                text = (minimise_number_text(state_value_list["neutral"][0]) + "/" +
                        minimise_number_text(
                            state_value_list["neutral"][1] / state_value_list["neutral"][2] * 100) + "%")
                team = "neutral"

        self.make_text_image(team, text)
        self.rect = self.image.get_rect(midtop=self.pos)

    def check_draw(self, active):
        grand_camera_ui_drawer = self.grand_camera_ui_drawer
        if active and self.rect.colliderect(self.camera.rect):
            if self.base_pos in self.grand.current_campaign_state["battle"]["dot"]:  # battle going on
                state_value_list = ([0, 0, 0], [0, 0, 0])
                for army in self.grand.current_campaign_state["battle"]["auto"][self.base_pos][""].values():
                    if army.faction == self.grand.player_faction:
                        state_value_list[0][0] += army.total_number
                        state_value_list["player"][1] += army.max_supply
                        state_value_list["player"][2] += army.total_supply_usage
                    elif self.grand.player_faction and army.faction != "free":
                        state_value_list["enemy"][0] += army.total_number
                        state_value_list["enemy"][1] += army.max_supply
                        state_value_list["enemy"][2] += army.total_supply_usage
                    else:
                        state_value_list["neutral"][0] += army.total_number
                        state_value_list["neutral"][1] += army.max_supply
                        state_value_list["neutral"][2] += army.total_supply_usage
            else:
                state_value_list = {"player": [0, 0, 0], "enemy": [0, 0, 0], "neutral": [0, 0, 0]}
                for army in self.dots_army_occupation[self.base_pos]:
                    if army.faction == self.grand.player_faction:
                        state_value_list["player"][0] += army.total_number
                        state_value_list["player"][1] += army.max_supply
                        state_value_list["player"][2] += army.total_supply_usage
                    elif self.grand.player_faction and army.faction != "free":
                        state_value_list["enemy"][0] += army.total_number
                        state_value_list["enemy"][1] += army.max_supply
                        state_value_list["enemy"][2] += army.total_supply_usage
                    else:
                        state_value_list["neutral"][0] += army.total_number
                        state_value_list["neutral"][1] += army.max_supply
                        state_value_list["neutral"][2] += army.total_supply_usage
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
