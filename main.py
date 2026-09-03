import tkinter as tk
from edge import Edge, Vertex
from planarity_testing import PlanarityTester
from layout import assign_positions, compute_internal_positions_parallel
from graph_vis import GraphVisualizer
import sys
import time


if __name__=="__main__":
    start = time.time()

    edges = []
    vertices = {}
    file_name = sys.argv[1] if len(sys.argv) > 1 else "test.txt"
    max_workers = int(sys.argv[2]) if len(sys.argv) > 2 else 4

    with open(file_name,"r") as f:
        for line in f:
            line = line.split()
            e = Edge(line[0],line[1],line[2],float(line[3]))
            edges.append(e)
    f.close()
    for e in edges:
        vertices[e.vertex_a_id] = Vertex(e.vertex_a_id)
        vertices[e.vertex_b_id] = Vertex(e.vertex_b_id)


    pt = PlanarityTester(vertices,edges)
    print("Graph is planar - ", pt.is_planar())
    if pt.is_planar():
        positions = compute_internal_positions_parallel(vertices, edges, workers=max_workers)
        assign_positions(vertices, positions)
        end = time.time()
        print(end - start)

        root = tk.Tk()

        app = GraphVisualizer(root, vertices, edges)
        root.mainloop()



