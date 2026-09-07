from edge import Segment


class PlanarityTester:
    def __init__(self, vertices, edges):
        self.vertices = vertices
        self.edges = edges

    def is_planar(self):
        return self.check_planarity()

    def check_planarity(self):
        adjacency = {}
        for e in self.edges:
            u, v = e.vertex_a_id, e.vertex_b_id
            adjacency.setdefault(u, set()).add(v)
            adjacency.setdefault(v, set()).add(u)

        visited = set()
        components = []
        for vertex in self.vertices:
            if vertex not in visited:
                comp = set()
                queue = [vertex]
                visited.add(vertex)
                while queue:
                    curr = queue.pop(0)
                    comp.add(curr)
                    for next_vert in adjacency.get(curr, set()):
                        if next_vert not in visited:
                            visited.add(next_vert)
                            queue.append(next_vert)
                components.append(comp)

        for comp in components:
            if not self.test_component_planarity(comp, adjacency):
                return False
        return True

    def test_component_planarity(self, comp_vertices, global_adj):
        comp_adj = {}
        for vrtx in comp_vertices:
            comp_adj[vrtx] = set(global_adj.get(vrtx, set()))
        self.remove_one_neigbour_vertices(comp_adj)
        if not comp_adj:
            return True

        E_all = set()
        for vrtx_a in comp_adj:
            for vrtx_b in comp_adj[vrtx_a]:
                E_all.add(frozenset([vrtx_a, vrtx_b]))

        if len(E_all) > 3 * len(comp_adj) - 6 and len(comp_adj) >= 3:
            return False

        parent, visited, cycle = {}, {}, []

        self.make_cycle(list(comp_adj.keys())[0], comp_adj, visited, parent, cycle)
        if not cycle:
            return True

        faces = [list(cycle), list(reversed(cycle))]
        E_embedded = set()
        for i in range(len(cycle)):
            E_embedded.add(frozenset([cycle[i], cycle[(i + 1) % len(cycle)]]))
        V_embedded = set(cycle)

        while len(E_embedded) < len(E_all):
            segments = self.find_segments(E_all, E_embedded, V_embedded, comp_adj)

            for seg in segments:
                seg.allowed_faces = []
                for face in faces:
                    if seg.attachments.issubset(set(face)):
                        seg.allowed_faces.append(face)

            if any(len(seg.allowed_faces) == 0 for seg in segments):
                return False

            chosen_segment = next((seg for seg in segments if len(seg.allowed_faces) == 1), segments[0])
            chosen_face = chosen_segment.allowed_faces[0]
            faces.remove(chosen_face)

            path_vertices = self.find_path_in_segment(chosen_segment, V_embedded)
            self.embed_segment(path_vertices, chosen_face, faces, E_embedded, V_embedded)

        return True

    def remove_one_neigbour_vertices(self, comp_adj):
        while True:
            one_neigh_vertices = []
            for v, neighs in comp_adj.items():
                if len(neighs) <= 1:
                    one_neigh_vertices.append(v)
            if not one_neigh_vertices:
                break
            for v in one_neigh_vertices:
                for nxt in comp_adj.get(v, set()):
                    comp_adj[nxt].discard(v)
                comp_adj.pop(v, None)

    def make_cycle(self, curr, comp_adj, visited, parent, cycle, p=None):
        visited[curr] = 1
        for nxt in comp_adj[curr]:
            if nxt == p:
                continue
            if visited.get(nxt, 0) == 1:
                c = [nxt, curr]
                node = curr
                while node != nxt:
                    node = parent[node]
                    c.append(node)
                cycle.extend(c[:-1])
                return True
            elif visited.get(nxt, 0) == 0:
                parent[nxt] = curr
                if self.make_cycle(nxt, comp_adj, visited, parent, cycle, curr):
                    return True
        visited[curr] = 2
        return False

    def find_segments(self, E_all, E_embedded, V_embedded, comp_adj):
        E_remaining = E_all - E_embedded
        segments = []
        visited_edges = set()
        for edge in E_remaining:
            if edge in visited_edges:
                continue

            vert_a, vert_b = list(edge)
            if vert_a in V_embedded and vert_b in V_embedded:
                segments.append(Segment({edge}, {vert_a, vert_b}))
                visited_edges.add(edge)
            else:
                seg_edges = {edge}
                seg_attachments = set()
                queue = []

                if vert_a not in V_embedded:
                    queue.append(vert_a)
                else:
                    seg_attachments.add(vert_a)
                if vert_b not in V_embedded:
                    queue.append(vert_b)
                else:
                    seg_attachments.add(vert_b)
                visited_edges.add(edge)
                visited_vertices = set(queue)
                while queue:
                    current_vert = queue.pop(0)
                    for next_vert in comp_adj[current_vert]:
                        current_edge = frozenset([current_vert, next_vert])
                        if current_edge in E_remaining:
                            if current_edge not in seg_edges:
                                seg_edges.add(current_edge)
                                visited_edges.add(current_edge)
                            if next_vert in V_embedded:
                                seg_attachments.add(next_vert)
                            elif next_vert not in visited_vertices:
                                visited_vertices.add(next_vert)
                                queue.append(next_vert)
                segments.append(Segment(seg_edges, seg_attachments))
        return segments

    def find_path_in_segment(self, seg, V_embedded):
        local_adj = {}
        for edge in seg.edges:
            vert_a, vert_b = list(edge)
            local_adj.setdefault(vert_a, set()).add(vert_b)
            local_adj.setdefault(vert_b, set()).add(vert_a)

        attachment = list(seg.attachments)[0]
        queue = [[attachment]]
        path_visited = {attachment}

        while queue:
            current_path = queue.pop(0)
            current_vertex = current_path[-1]

            for next_vertex in local_adj.get(current_vertex, []):
                if next_vertex in seg.attachments and next_vertex != attachment:
                    return current_path + [next_vertex]

                if next_vertex not in path_visited and next_vertex not in V_embedded:
                    path_visited.add(next_vertex)
                    queue.append(current_path + [next_vertex])

        return None

    def embed_segment(self, path_vertices, chosen_face, faces, E_embedded, V_embedded):
        vertex_a = path_vertices[0]
        vertex_b = path_vertices[-1]
        id_a = chosen_face.index(vertex_a)
        id_b = chosen_face.index(vertex_b)

        if id_a > id_b:
            vertex_a, vertex_b = vertex_b, vertex_a
            path_vertices = list(reversed(path_vertices))
            id_a, id_b = chosen_face.index(vertex_a), chosen_face.index(vertex_b)

        part1 = chosen_face[id_a: id_b + 1]
        part2 = chosen_face[id_b:] + chosen_face[:id_a + 1]
        faces.append(part1 + list(reversed(path_vertices[1:-1])))
        faces.append(part2 + path_vertices[1:-1])

        for i in range(len(path_vertices) - 1):
            E_embedded.add(frozenset([path_vertices[i], path_vertices[i + 1]]))
        V_embedded.update(path_vertices)
