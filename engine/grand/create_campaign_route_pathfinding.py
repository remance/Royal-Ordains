from engine.constants import Route_Travel_Modifier


def create_campaign_route_pathfinding(self):
    pathfinding_dict = self.current_campaign_state["pathfinding"]
    direct_route_dict = self.current_campaign_state["direct_routing"]
    region_number = len(self.region_list)
    route_matrix = [[0] * region_number for _ in range(region_number)]
    route_vertex_data = [""] * region_number

    for index, region in enumerate(self.region_list):
        route_vertex_data[index] = region

    region_key_index = list(self.region_list.keys())
    for route, route_data in self.route_list.items():
        route_0_index = region_key_index.index(route[0])
        route_1_index = region_key_index.index(route[1])
        weight = len(route_data["Dots"]) * Route_Travel_Modifier[route_data["Type"]]
        route_matrix[route_0_index][route_1_index] = weight
        route_matrix[route_1_index][route_0_index] = weight  # For undirected graph

    inf = float('inf')
    n = len(route_matrix)

    # create shortest route for all possible start to destination in the campaign using dijkstra
    for start_route in range(len(region_key_index)):
        for end_route in range(len(region_key_index)):
            start_route_id = region_key_index[start_route]
            end_route_id = region_key_index[end_route]
            if start_route != end_route and (end_route_id, start_route_id) not in pathfinding_dict:
                # no need to search for reversed direction
                dist = [inf] * n
                dist[start_route] = route_matrix[start_route][start_route]  # 0

                sp_vertex = [False] * n
                parent = [-1] * n

                path = [{}] * n

                for count in range(n - 1):
                    minix = inf
                    u = 0

                    for v in range(len(sp_vertex)):
                        if sp_vertex[v] is False and dist[v] <= minix:
                            minix = dist[v]
                            u = v

                    sp_vertex[u] = True
                    for v in range(n):
                        if (not (sp_vertex[v]) and route_matrix[u][v] != 0 and
                                dist[u] + route_matrix[u][v] < dist[v]):
                            parent[v] = u
                            dist[v] = dist[u] + route_matrix[u][v]

                for i in range(n):
                    j = i
                    s = []
                    while parent[j] != -1:
                        s.append(j)
                        j = parent[j]
                    s.append(start_route)
                    path[i] = s[::-1]
                if end_route >= 0:
                    pathfinding_dict[(start_route_id, end_route_id)] = [region_key_index[item] for item in
                                                                        path[end_route]]
                else:
                    pathfinding_dict[(start_route_id, end_route_id)] = [region_key_index[item] for item in path]

                pathfinding_dict[(end_route_id, start_route_id)] = pathfinding_dict[(start_route_id, end_route_id)][
                                                                   ::-1]

    # create direct route for all possible start to destination in the campaign using dijkstra
    for route, route_data in self.route_list.items():
        route_0_index = region_key_index.index(route[0])
        route_1_index = region_key_index.index(route[1])
        route_matrix[route_0_index][route_1_index] = 1
        route_matrix[route_1_index][route_0_index] = 1

    for start_route in range(len(region_key_index)):
        for end_route in range(len(region_key_index)):
            start_route_id = region_key_index[start_route]
            end_route_id = region_key_index[end_route]
            if start_route != end_route and (end_route_id, start_route_id) not in direct_route_dict:
                # no need to search for reversed direction
                dist = [inf] * n
                dist[start_route] = route_matrix[start_route][start_route]  # 0

                sp_vertex = [False] * n
                parent = [-1] * n

                path = [{}] * n

                for count in range(n - 1):
                    minix = inf
                    u = 0

                    for v in range(len(sp_vertex)):
                        if sp_vertex[v] is False and dist[v] <= minix:
                            minix = dist[v]
                            u = v

                    sp_vertex[u] = True
                    for v in range(n):
                        if (not (sp_vertex[v]) and route_matrix[u][v] != 0 and
                                dist[u] + route_matrix[u][v] < dist[v]):
                            parent[v] = u
                            dist[v] = dist[u] + route_matrix[u][v]

                for i in range(n):
                    j = i
                    s = []
                    while parent[j] != -1:
                        s.append(j)
                        j = parent[j]
                    s.append(start_route)
                    path[i] = s[::-1]
                if end_route >= 0:
                    direct_route_dict[(start_route_id, end_route_id)] = [region_key_index[item] for item in
                                                                        path[end_route]]
                else:
                    direct_route_dict[(start_route_id, end_route_id)] = [region_key_index[item] for item in path]
                direct_route_dict[(end_route_id, start_route_id)] = direct_route_dict[(start_route_id, end_route_id)][
                                                                   ::-1]