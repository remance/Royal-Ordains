from engine.constants import Route_Travel_Modifier


def issue_move_command(self, target_destination, direct=False):
    travelling = self.travelling
    if not travelling or travelling["type"] != "retreat":
        # cannot issue new move command while in retreat
        old_destination = None
        if travelling:
            old_destination = travelling["destination"]
        if (old_destination != target_destination or (not travelling and self.current_region != target_destination) or
                self.travel_how != direct):
            # issue new move command to move to different target region or use different mean
            route_list = self.grand.route_list
            new_travel_route_id = []
            command_type = "move"

            if travelling:
                # check if army still at settlement pos, which mean it has not yet start travelling
                if self.base_pos == route_list[travelling["id_routes"][0]]["Dots"][0]:
                    # still at starting point of travelling, remove current travel
                    self.travelling = {}
                    travelling = self.travelling

            if self.current_region != target_destination:
                if (self.current_region, target_destination) in self.pathfinding_array:
                    if direct:
                        new_travel_route_id = list(self.direct_routing_array[(self.current_region, target_destination)])
                    else:
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

                    if current_route_id not in new_travel_route_id and current_route_id[::-1] not in new_travel_route_id:
                        if self.current_region == current_route_id[1]:  # finish travel
                            new_travel_route_id.insert(0, current_route_id)
                        else:  # revert back
                            new_travel_route_id.insert(0, current_route_id[::-1])

            else:  # click at current region while travelling out
                # travelling already, must check if current path must be added to the new route so army can
                # use the current route to travel back
                if travelling:
                    if target_destination == travelling["id_routes"][0][0]:
                        # revert travel direction back to where it heading out from
                        new_travel_route_id = [travelling["id_routes"][0][::-1]]
                    else:
                        new_travel_route_id = [travelling["id_routes"][0]]

            if new_travel_route_id:
                # create dots to travel based on new travel route list
                dot_routes = []
                for index, item in enumerate(new_travel_route_id):
                    dots = list(route_list[item]["Dots"])
                    dot_routes.append(dots)
                if self.base_pos in dot_routes[0]:  # already travelling along the path, remove already travelled dots
                    first_route = dot_routes[0]
                    dot_routes[0] = first_route[first_route.index(self.base_pos):]
                    if len(dot_routes[0]) <= 1:
                        dot_routes.pop(0)
                    if not dot_routes:  # turn out no route to move
                        return
                    # print(travelling["dot_routes"][0])

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
        self.travel_how = direct


# old 'progress': 1, 'destination': 'test5', 'id_routes': [('test7', 'test8'), ('test8', 'test5')], 'dot_routes': [[(1754, 847), (1763, 831)], [(1763, 831), (1749, 829), (1736, 821), (1721, 811), (1705, 803), (1690, 796), (1671, 789), (1654, 782), (1630, 788)]], 'difficulties': [2, 1], 'remain_phase_require': [[2, 1, 2, 1], [2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1]]}
# test8 test9 (1754, 847) [('test7', 'test8'), ('test8', 'test9')] [[(1670, 900), (1688, 893), (1701, 884), (1714, 876), (1728, 866), (1744, 857), (1754, 847), (1763, 831)], [(1763, 831), (1763, 854), (1762, 870), (1761, 886), (1758, 905), (1753, 918), (1749, 930), (1745, 975)]]

# old 'destination': 'test9', 'id_routes': [('test7', 'test8'), ('test8', 'test9')], 'dot_routes': [[(1763, 854), (1762, 870), (1761, 886), (1758, 905), (1753, 918), (1749, 930), (1745, 975)]], 'difficulties': [1], 'remain_phase_require': [[1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1]]}
# test8 test5 (1763, 854) [('test7', 'test8'), ('test8', 'test5')] [[(1670, 900), (1688, 893), (1701, 884), (1714, 876), (1728, 866), (1744, 857), (1754, 847), (1763, 831)], [(1763, 831), (1749, 829), (1736, 821), (1721, 811), (1705, 803), (1690, 796), (1671, 789), (1654, 782), (1630, 788)]]
