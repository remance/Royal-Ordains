from pygame import draw


def draw_route(self):
    camera_left_bound = self.camera.camera_left_bound
    camera_top_bound = self.camera.camera_top_bound
    map_shown_to_base_scale_width = self.map_shown_to_base_scale_width
    map_shown_to_base_scale_height = self.map_shown_to_base_scale_height

    lines_to_draws = []
    screen_rect = self.screen_rect
    if self.player_selected_army:
        for army in self.player_selected_army:
            # draw line movement for selected player armies that are travelling
            if "travel" in army.activity:
                this_army_line = []
                for route in army.activity["dot_routes"]:
                    for index, dot in enumerate(route[:-1]):
                        # skip drawing for line that are not in screen
                        start_dot = ((dot[0] * map_shown_to_base_scale_width) - camera_left_bound,
                                     (dot[1] * map_shown_to_base_scale_height) - camera_top_bound)
                        end_dot = ((route[index + 1][0] * map_shown_to_base_scale_width) - camera_left_bound,
                                   (route[index + 1][1] * map_shown_to_base_scale_height) - camera_top_bound)

                        if screen_rect.clipline(start_dot, end_dot):
                            # skip last dot since it already got checked in second last
                            if not index:  # add only first dot for starting point
                                this_army_line.append(start_dot)
                            this_army_line.append(end_dot)
                        else:  # line break, reset list
                            lines_to_draws.append(this_army_line)
                            this_army_line = []
                if this_army_line and this_army_line not in lines_to_draws:
                    lines_to_draws.append(this_army_line)

        camera_image = self.camera.image
        army_move_line_width = self.army_move_line_width
        army_move_inner_line_width = self.army_move_inner_line_width
        for line_to_draw in lines_to_draws:
            if len(line_to_draw) > 1:
                draw.lines(camera_image, (0, 0, 0), False, line_to_draw, army_move_line_width)
                draw.lines(camera_image, (255, 255, 255), False, line_to_draw, army_move_inner_line_width)
