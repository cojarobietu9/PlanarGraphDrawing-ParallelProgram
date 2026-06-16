import tkinter as tk

class GraphVisualizer:

    def __init__(self, root, vertices, edges, width=800, height=600, multipler = 250):
        self.root = root
        self.root.title("Wizualizator Grafu")
        self.vertices = vertices
        self.edges = edges
        self.width = width
        self.height = height
        self.multiplier = multipler

        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="white")
        self.canvas.pack()

        self._draw_edges()
        self._draw_vertices()

    def _draw_edges(self):
        for e in self.edges:
            start_v = self.vertices.get(e.vertex_a_id)
            end_v = self.vertices.get(e.vertex_b_id)

            if start_v and end_v:
                x1, y1 = start_v.x*self.multiplier, start_v.y*self.multiplier
                x2, y2 = end_v.x*self.multiplier, end_v.y*self.multiplier
                # self.canvas.create_line(x1, y1, x2, y2, fill="black", width=2)
                self.canvas.create_line(self.width / 2 - x1, self.height / 2 - y1, self.width / 2 - x2,
                                        self.height / 2 - y2, fill="black", width=2)
            else:
                print(f"Ostrzeżenie: Krawędź między nieistniejącymi wierzchołkami: {start_v} - {end_v}")

    def _draw_vertices(self):

        radius = 10

        for v_id, v_data in self.vertices.items():
            x, y = v_data.x*self.multiplier, v_data.y*self.multiplier
            label = str(v_id)

            self.canvas.create_oval(self.width/2- (x - radius), self.height/2 - (y - radius), self.width/2 - (x + radius), self.height/2 - (y + radius), fill="lightblue", outline="black", width=2)

            self.canvas.create_text(self.width/2 - x, self.height/2 - y, text=label, font=("Arial", 12, "bold"), fill="black")