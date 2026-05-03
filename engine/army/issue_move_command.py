from engine.constants import Route_Travel_Modifier


def issue_move_command(self, target_destination):
    travelling = self.travelling
    if not travelling or travelling["type"] != "retreat":
        # cannot issue new move command while in retreat
        old_destination = None
        if travelling:
            old_destination = travelling["destination"]
        if old_destination != target_destination or (not travelling and self.current_region != target_destination):
            # cannot issue new move command to move to current region
            route_list = self.grand.route_list

            command_type = "move"

            if travelling:
                # check if army still at settlement pos, which mean it has not yet start travelling
                if self.base_pos == route_list[travelling["id_routes"][0]]["Dots"][0]:
                    # still at starting point of travelling, remove current travel
                    self.travelling = {}
                    travelling = self.travelling

            if self.current_region != target_destination:
                if (self.current_region, target_destination) in self.pathfinding_array:
                    new_travel_route_id = list(self.pathfinding_array[(self.current_region, target_destination)])
                else:  # somehow destination region has no path to reach, end function
                    return

                # recreate list of ids into ids pair for each route to pass
                new_travel_route_id = [(item, new_travel_route_id[index + 1]) if
                                       (item, new_travel_route_id[index + 1]) in route_list else
                                       (new_travel_route_id[index + 1], item) for
                                       index, item in enumerate(new_travel_route_id) if
                                       index + 1 < len(new_travel_route_id)]

                if travelling:
                    # travelling already, must check if current path must be added to the new route so army can
                    # leave the current route
                    current_route_id = travelling["id_routes"][0]
                    if current_route_id not in new_travel_route_id and current_route_id[
                                                                       ::-1] not in new_travel_route_id:
                        new_travel_route_id.insert(0, current_route_id)

            else:  # click at current region while travelling out
                # travelling already, must check if current path must be added to the new route so army can
                # use the current route to travel back
                if travelling:
                    new_travel_route_id = [travelling["id_routes"][0][::-1]]

            # create dots to travel based on new travel route list
            dot_routes = []
            for index, item in enumerate(new_travel_route_id):
                dots = list(route_list[item]["Dots"])
                dot_routes.append(dots)

            if self.base_pos in dot_routes[0]:  # already travelling along the path, remove already travelled dots
                first_route = dot_routes[0]
                dot_routes[0] = first_route[first_route.index(self.base_pos):]

            if self.assembling:  # cancel assembling when move for any reason  TODO add event inform this cancel
                self.assembling = {}

            if self in self.grand.current_campaign_state["battle"]["armies"]:
                command_type = "retreat"

            route_difficulties = [Route_Travel_Modifier[route_list[new_travel_route_id[index]]["Type"]] for
                                  index, dots in enumerate(dot_routes)]
            travelling = {"type": command_type, "progress": 0, "destination": target_destination,
                          "id_routes": new_travel_route_id,
                          "dot_routes": dot_routes, "difficulties": route_difficulties,
                          "remain_phase_require": [len(dots) * route_difficulties for index, dots in
                                                   enumerate(dot_routes)]}

            self.travelling = travelling

            if self.grand.player_faction == self.faction:
                self.grand.player_army_list_ui.reset_card(self)
