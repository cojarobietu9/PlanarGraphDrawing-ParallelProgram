import tkinter as tk
from edge import Edge, Vertex
from planarity_testing import PlanarityTester
from layout import assign_positions, compute_internal_positions_parallel
from graph_vis import GraphVisualizer
import sys

edges = []
vertices = {}

file_name = sys.argv[1] if len(sys.argv) > 1 else "test.txt"
max_workers = int(sys.argv[2]) if len(sys.argv) > 2 else 32
vert_id =[]
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
if pt.is_planar():
    positions = compute_internal_positions_parallel(vertices, edges, workers=max_workers)
    assign_positions(vertices, positions)
    for v in vertices:
        vertex=vertices.get(v)
        role = "boundary" if vertex.is_boundary else "internal"
        #print(f"{vertex.id}: ({vertex.x:.6f}, {vertex.y:.6f}) [{role}]")

root = tk.Tk()

app = GraphVisualizer(root, vertices, edges)
root.mainloop()

print("Graph is planar - ",pt.is_planar())
