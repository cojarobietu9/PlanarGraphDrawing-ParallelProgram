class PlanarityTester:
    def __init__(self, vertices, edges):
        self.vertices = vertices
        self.edges = edges

    def is_planar(self):

        return self.check_planarity_robust()

    def check_planarity_robust(self):
        adj = {}
        for e in self.edges:
            u, v = e.vertex_a_id, e.vertex_b_id
            adj.setdefault(u, set()).add(v)
            adj.setdefault(v, set()).add(u)

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
                    for next in adj.get(curr, set()):
                        if next not in visited:
                            visited.add(next)
                            queue.append(next)
                components.append(comp)

        for comp in components:
            if not self.test_component_planarity(comp, adj):
                return False
        return True

    def test_component_planarity(self, comp_nodes, global_adj):
        core_adj = {v: set(global_adj.get(v, set())) for v in comp_nodes}

        # jeżeli w lokalnej kopii listy sąsiedztwa - core_adj - mamy wierzchołki stopnia <= 1 (czyli mają <= 1 krawędź),
        # usuwamy je - one nie wpływają na planarność
        while True:
            to_remove = [v for v, neighs in core_adj.items() if len(neighs) <= 1]
            if not to_remove:
                break
            for v in to_remove:
                for nxt in core_adj[v]:
                    core_adj[nxt].discard(v)
                del core_adj[v]

        # brak segmentów do sprawdzenia - graf planarny. To jest na wszelki wypadek
        if not core_adj:
            return True

        # sprawdzanie liczby wszystkich krawędzi opartych o core_adj testem Eulera
        E_all = set()
        for u in core_adj:
            for v in core_adj[u]:
                E_all.add(frozenset([u, v]))

        if len(E_all) > 3 * len(core_adj) - 6 and len(core_adj) >= 3:
            return False

        parent, visited, cycle = {}, {}, []

        # dfs-podobny algorytm wyszukujący podgraf 2-spójny.
        # na pewno możliwe, dzięki temu że wcześniej usunęliśmy wierzchołki o stopniu <=1 - każdy ma co najmniej 2 połączenia
        def make_cycle(curr, p=None):
            visited[curr] = 1
            for nxt in core_adj[curr]:
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
                    if make_cycle(nxt, curr):
                        return True
            visited[curr] = 2
            return False

        make_cycle(list(core_adj.keys())[0])
        # na wszelki wypadek
        if not cycle:
            return True

        # zbiory krawędzi i wierzchołków, które są już osadzone w grafie bo są częścią podgrafu cyklicznego cycle
        # ergo -> V_embedded = wierzchołki kontaktowe / połączeniowe
        faces = [list(cycle), list(reversed(cycle))]
        E_embedded = set(frozenset([cycle[i], cycle[(i + 1) % len(cycle)]]) for i in range(len(cycle)))
        V_embedded = set(cycle)

        # dopóty dopóki mamy jeszcze krawędzie do sprawdzania
        while len(E_embedded) < len(E_all):
            E_remaining = E_all - E_embedded  # nifty operation
            segments = []
            visited_edges = set()

            # główna pętla tworząca segmenty (ergo fragmenty)
            for edge in E_remaining:
                # jeżeli byliśmy w krawędzi i jeszcze nie skończył się algorytm, to znaczy że na pewno jest OK - do skipnięcia
                if edge in visited_edges:
                    continue
                u, v = list(edge)

                # !! tworzenie fragmentów
                # V_embedded to krawędzie kontaktowe. Jeżeli oba wierzchołki są ma jeden wierzchołek krawędziowy (połączeniowe),
                # drugi nie krawędziowy => dodajemy do fragmentu
                if u in V_embedded and v in V_embedded:
                    segments.append({'edges': {edge}, 'attachments': {u, v}})
                    visited_edges.add(edge)

                # jeżeli co najmniej jedna nie jest - tworzy możliwy rozwinięty "blob", "zbiór", "zwał jak zwał"
                else:
                    seg_edges = {edge}  # krawędzie fragmentu
                    seg_attachments = set()  # wierzchołki połączeniowe segmentu
                    queue = []

                    # jeżeli u lub v jest już w embedded, jest on połączeniem fragmentu (seg_attachments)
                    # jeżeli nie, dodajemy go do kolejki sprawdzania
                    for vertex in (u, v):
                        if vertex not in V_embedded:
                            queue.append(vertex)
                        else:
                            seg_attachments.add(vertex)

                    visited_edges.add(edge)
                    visited_nodes = set(queue)

                    while queue:
                        curr = queue.pop(0)
                        for nxt in core_adj[curr]:
                            curr_edge = frozenset([curr, nxt])
                            # patrzymy na krawędzie sąsiedzkie wierzchołka curr, które są dostępne i nie należą do segmentu / fragmentu.
                            # Idziemy po kolei po krawędziach, jeżeli można (alfa-krawędź)
                            # Dodajemy je do segmentów.
                            if curr_edge in E_remaining:
                                if curr_edge not in seg_edges:
                                    seg_edges.add(curr_edge)
                                    visited_edges.add(curr_edge)
                                if nxt in V_embedded:
                                    seg_attachments.add(nxt)
                                elif nxt not in visited_nodes:
                                    # następny nie jest końcem alfa-krawędzi => dodajemy do queue, sprawdzamy go następnie
                                    visited_nodes.add(nxt)
                                    queue.append(nxt)
                    segments.append({'edges': seg_edges, 'attachments': seg_attachments})

            # !! koniec tworzenia segmentów / fragmentów

            # sprawdzamy, czy segmenty mają ściany do których możemy połączyć
            for seg in segments:
                seg['allowed_faces'] = [idx for idx, f in enumerate(faces) if seg['attachments'].issubset(set(f))]

            # nie mają => na pewno nie planarny
            if any(len(seg['allowed_faces']) == 0 for seg in segments):
                return False

            # arbitralnie wybieramy pierwszy segment do dołączenia do ściany, do której możemy je połączyć.
            # Po tej operacji będzie w E_embedded i V_embedded
            chosen_seg = next((seg for seg in segments if len(seg['allowed_faces']) == 1), segments[0])
            face_idx = chosen_seg['allowed_faces'][0]
            chosen_face = faces.pop(face_idx)

            local_adj = {}
            for edge in chosen_seg['edges']:
                x, y = list(edge)
                local_adj.setdefault(x, set()).add(y)
                local_adj.setdefault(y, set()).add(x)

            u = list(chosen_seg['attachments'])[0]
            queue, path_visited, path_verts = [[u]], {u}, None

            # ! ważne
            # przechodzimy przez wierzchołki po sąsiednich krawędziach, w wybranym segmencie (maksymalnie raz),
            # żeby stworzyć alfa-krawędź którą podłączymy do embeddu
            # tutaj jest mini-bfs
            while queue:
                curr_path = queue.pop(0)
                curr_node = curr_path[-1]
                for nxt in local_adj.get(curr_node, []):
                    if nxt in chosen_seg['attachments'] and nxt != u:
                        path_verts = curr_path + [nxt]
                        break
                    if nxt not in path_visited and nxt not in V_embedded:
                        path_visited.add(nxt)
                        queue.append(curr_path + [nxt])
                if path_verts:
                    break

            v = path_verts[-1]
            idx_u, idx_v = chosen_face.index(u), chosen_face.index(v)
            if idx_u > idx_v:
                u, v, path_verts = v, u, list(reversed(path_verts))
                idx_u, idx_v = chosen_face.index(u), chosen_face.index(v)

            part1 = chosen_face[idx_u: idx_v + 1]
            part2 = chosen_face[idx_v:] + chosen_face[:idx_u + 1]

            faces.append(part1 + list(reversed(path_verts[1:-1])))
            faces.append(part2 + path_verts[1:-1])

            for i in range(len(path_verts) - 1):
                E_embedded.add(frozenset([path_verts[i], path_verts[i + 1]]))
            V_embedded.update(path_verts)

        return True

