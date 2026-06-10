from dcll import DCLL
class Edge:
    def __init__(self,name,vertex_a,vertex_b,weight):
        self.name = name
        self.vertex_a = vertex_a
        self.vertex_b = vertex_b
        self.weight = weight
        self.is_in_tree = False
        self.sign = 1


    def add_to_tree(self):
        self.is_in_tree = True
class Vertex:
    def __init__(self,id):
        self.id = id
        self.neighbors = []
        self.parent = None
        self.children = []
        self.dfi = 0
        self.lowpoint=None
        self.leastAncestor = float('inf')
        self.back_edges_list = []
        self.sortedDFSchildren = DCLL()
        self.node_in_parent_list = None
        self.left_link = {}
        self.right_link = {}

    def set_vertex_dfi(self,dfi):
        self.dfi = dfi
    def set_lowpoint(self,lowpoint):
        self.lowpoint = lowpoint
    def add_neighbor(self,neighbor):
        self.neighbors.append(neighbor)
    def set_parent(self,parent):
        self.parent = parent
    def add_child(self,child):
        self.children.append(child)
