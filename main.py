from edge import Edge
from edge import Vertex


edges = []
vertices = []



def sort_children(vertices,buckets):
    for v in vertices:
        low = v.lowpoint
        buckets[low].append(v)
    for b in buckets:
        for v in b:
            if v.parent != None:
                v.node_in_parent_list = v.parent.sortedDFSchildren.append(v)


def euler_test(edges,vert_id):
    return len(vert_id) * 3 - 6 >= len(edges)


def dfs_graph(edges,vertices,vertex:Vertex,dfi_counter):
    vertex.set_lowpoint(dfi_counter)
    vertex.leastAncestor = float('inf')
    for e in edges:
        if e.vertex_a == vertex.id:
            neighbour_id = e.vertex_b

        elif e.vertex_b == vertex.id:
            neighbour_id = e.vertex_a

        else:
            continue

        neighbour = [v for v in vertices if v.id == neighbour_id]
        if len(neighbour) == 0:
            e.add_to_tree()
            newVertex = Vertex(neighbour_id)
            dfi_counter += 1
            newVertex.set_vertex_dfi(dfi_counter)
            vertex.add_child(newVertex)
            newVertex.set_parent(vertex)
            vertices.append(newVertex)
            dfi_counter = dfs_graph(edges,vertices,newVertex,dfi_counter)
            vertex.lowpoint = min(vertex.lowpoint, newVertex.lowpoint)
        else:
            neighbour_v = neighbour[0]
            if vertex.parent is None or neighbour_id != vertex.parent.id:
                if neighbour_v.dfi < vertex.dfi:
                    neighbour_v.back_edges_list.append(e)
                    vertex.leastAncestor = min(vertex.leastAncestor, neighbour_v.dfi)
                    vertex.lowpoint = min(vertex.lowpoint, neighbour_v.dfi)

    return dfi_counter


file_name = "test.txt"
vert_id =[]
with open(file_name,"r") as f:
    for line in f:
        line = line.split()
        e = Edge(line[0],line[1],line[2],float(line[3]))
        edges.append(e)
        if e.vertex_a not in vert_id:
            vert_id.append(e.vertex_a)
        if e.vertex_b not in vert_id:
            vert_id.append(e.vertex_b)
f.close()

if not euler_test(edges,vert_id):
    print("Didnt pass Euler's test - not planar")
    exit()
root = Vertex(edges[0].vertex_a)
dfi_counter = 0
root.set_vertex_dfi(dfi_counter)
vertices.append(root)
dfs_graph(edges,vertices,root,dfi_counter)

buckets = [[] for _ in range(len(vertices))]
print(len(buckets))

sort_children(vertices,buckets)
#for i in vertices:
    # print(i.id,i.dfi,i.lowpoint,i.leastAncestor)
    # for e in i.back_edges_list:
    #     print(e.name, " ", end="")
    # print()
    # print("im vertex ",i.id)
    # for c in i.sortedDFSchildren:
    #     print(c.id,end=' ')
    # print()
# for e in edges:
#     print(e.name, e.is_in_tree)


