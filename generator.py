import networkx as nx

G = nx.grid_2d_graph(100, 100)

print(f"Liczba węzłów: {G.number_of_nodes()}")
print(f"Liczba krawędzi: {G.number_of_edges()}")
print(f"Czy graf jest planarny? {nx.check_planarity(G)[0]}\n")
with open("graf_planarny_1000.txt", "w") as f:
    for i, (u, v) in enumerate(G.edges(), start=1):
        # Zamiana współrzędnych (x,y) na pojedyncze identyfikatory węzłów
        u_id = u[0] * 100 + u[1] + 1
        v_id = v[0] * 100 + v[1] + 1
        f.write(f"e{i} {u_id} {v_id} 1\n")

print(
    "Zapisano 1000 krawędzi do pliku 'graf_planarny_1000.txt' w formacie 'eX wierzcholek1 wierzcholek2'"
)