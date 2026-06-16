class Edge:
    def __init__(self, name, vertex_a_id, vertex_b_id, weight=1.0):
        self.name = name
        self.vertex_a_id = vertex_a_id
        self.vertex_b_id = vertex_b_id
        self.vertex_a = None
        self.vertex_b = None
        self.weight = weight



class Vertex:
    def __init__(self, id_val):
        self.id = id_val
        self.x = 0.0
        self.y = 0.0
        self.is_boundary = False
