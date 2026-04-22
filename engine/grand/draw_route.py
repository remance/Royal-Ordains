from pygame import draw


def draw_route(self):
    camera_left_bound = self.camera.camera_left_bound
    camera_right_bound = self.camera.camera_right_bound
    camera_top_bound = self.camera.camera_top_bound
    camera_bottom_bound = self.camera.camera_bottom_bound
    # print(camera_left_bound, camera_top_bound, camera_right_bound, camera_bottom_bound)
    # print(self.route_dot_draw_array)
    for x in self.route_dot_draw_array:
        if camera_left_bound < x < camera_right_bound:
            for y in self.route_dot_draw_array[x]:
                if camera_top_bound < y < camera_bottom_bound:
                    dot_image = self.route_dot_draw_array[x][y]
                    self.camera.image.blit(dot_image, dot_image.get_rect(center=(x - camera_left_bound, y - camera_top_bound)))
                elif y > camera_bottom_bound:
                    break
        elif x > camera_right_bound:
            break

    for army in self.player_selected_army:
        # draw arrow movement for selected player armies that are travelling
        if army.travelling:
            pass
