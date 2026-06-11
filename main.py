from edge import Edge
from edge import Vertex


edges = []
vertices = []
parent_block = {}
block_root = {}

def find_block(b_id):
    if b_id not in parent_block or parent_block[b_id] == b_id:
        return b_id
    parent_block[b_id] = find_block(parent_block[b_id])
    return parent_block[b_id]

def get_actual_key(vertex, b_id):
    if b_id in vertex.left_link:
        return b_id
    target_block = find_block(b_id)
    for k in vertex.left_link:
        if find_block(k) == target_block:
            return k
    return b_id


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


def dfs_graph(edges,vertex:Vertex,dfi_counter):
    global vertices
    vertex.set_lowpoint(dfi_counter)
    vertex.leastAncestor = float('inf')
    for e in edges:
        if e.vertex_a_id == vertex.id:
            e.setVertA(vertex)
            neighbour_id = e.vertex_b_id
        elif e.vertex_b_id == vertex.id:
            e.setVertB(vertex)
            neighbour_id = e.vertex_a_id
        else:
            continue

        neighbourl = [v for v in vertices if v.id == neighbour_id]
        if len(neighbourl) == 0:
            e.add_to_tree()
            newVertex = Vertex(neighbour_id)
            dfi_counter += 1
            newVertex.set_vertex_dfi(dfi_counter)
            vertex.add_child(newVertex)
            newVertex.set_parent(vertex)
            vertices.append(newVertex)
            dfi_counter = dfs_graph(edges,newVertex,dfi_counter)
            vertex.lowpoint = min(vertex.lowpoint, newVertex.lowpoint)
        else:
            neighbour_v = neighbourl[0]
            if vertex.parent is None or neighbour_v.id != vertex.parent.id:
                if neighbour_v.dfi < vertex.dfi:
                    neighbour_v.back_edges_list.append(e)
                    vertex.leastAncestor = min(vertex.leastAncestor, neighbour_v.dfi)
                    vertex.lowpoint = min(vertex.lowpoint, neighbour_v.dfi)

    return dfi_counter


def walkup(vertex, ancestor):
    vertex.backedgeFlag = ancestor

    curr = vertex
    while curr != ancestor:
        if curr.visited_walkup == ancestor.id:
            break
        curr.visited_walkup = ancestor.id
        curr.pertinent = True

        if curr.parent is None:
            break

        b_id = find_block(curr.id)
        r = block_root.get(b_id, curr.parent)

        for direction in [0, 1]:
            temp = curr
            came_from = None
            while temp != r and temp is not None:
                if temp.visited_walkup == ancestor.id:
                    break
                temp.visited_walkup = ancestor.id
                temp.pertinent = True

                key = get_actual_key(temp, b_id)
                if came_from is None:
                    next_node = temp.left_link.get(key) if direction == 0 else temp.right_link.get(key)
                else:
                    next_node = temp.right_link.get(key) if temp.left_link.get(
                        key) == came_from else temp.left_link.get(key)
                came_from = temp
                temp = next_node

        if r != ancestor:
            if b_id not in r.pertinentRoots:
                if curr.lowpoint < ancestor.dfi:
                    r.pertinentRoots.append(b_id)
                else:
                    r.pertinentRoots.insert(0, b_id)
        curr = r


def is_active_or_pertinent(vertex, v):
    if vertex is None:
        return False
    if vertex.pertinent:
        return True
    if vertex.backedgeFlag == v:
        return True
    if vertex.pertinentRoots:
        return True
    return False

def walkdown(vertex):
    v = vertex
    curr_node = v.sortedDFSchildren.head
    if curr_node is None:
        return

    children = []
    for _ in range(v.sortedDFSchildren.count):
        children.append(curr_node.data)
        curr_node = curr_node.next

    for child in children:
        b_id = find_block(child.id)
        if b_id not in v.pertinentRoots and not child.pertinent:
            continue

        merge_stack = []

        for v_out in [0, 1]:
            key_v = get_actual_key(v, b_id)
            w = v.left_link.get(key_v) if (1 ^ v_out) == 0 else v.right_link.get(key_v)
            win = v
            current_b_id = b_id

            visited_states = set()

            while w != v and w is not None:
                state = (w.id, current_b_id)
                if state in visited_states:
                    break
                visited_states.add(state)

                if w.backedgeFlag == v:
                    while merge_stack:
                        MergeBiconnectedComponent(merge_stack, v)
                    EmbedBackEdge(v, v_out, w, win, current_b_id)
                    w.backedgeFlag = None
                    if not w.pertinentRoots:
                        break

                if w.pertinentRoots:
                    merge_stack.append((w, win, current_b_id))
                    w_prime_id = w.pertinentRoots[0]

                    current_b_id = w_prime_id
                    key_w = get_actual_key(w, current_b_id)
                    x = w.left_link.get(key_w)
                    y = w.right_link.get(key_w)

                    if is_active_or_pertinent(x, v):
                        w, win = x, w
                    elif is_active_or_pertinent(y, v):
                        w, win = y, w
                    else:
                        break
                else:
                    key_w = get_actual_key(w, current_b_id)
                    next_w = w.right_link.get(key_w) if w.left_link.get(key_w) == win else w.left_link.get(key_w)
                    win = w
                    w = next_w


def MergeBiconnectedComponent(merge_stack, v):
    w, win, parent_b_id = merge_stack.pop()
    b_child = w.pertinentRoots.pop(0)

    key_win = get_actual_key(win, parent_b_id)
    key_w_parent = get_actual_key(w, parent_b_id)
    key_w_child = get_actual_key(w, b_child)

    ch1 = w.left_link.get(key_w_child)
    ch2 = w.right_link.get(key_w_child)

    if ch1 == ch2:
        x = y = ch1
    else:
        if ch2 and (ch2.pertinent or ch2.backedgeFlag == v or ch2.pertinentRoots):
            x, y = ch2, ch1
        else:
            x, y = ch1, ch2

    key_x = get_actual_key(x, b_child)

    if win.left_link.get(key_win) == w:
        win.left_link[key_win] = x
    else:
        win.right_link[key_win] = x

    if x.left_link.get(key_x) == w:
        x.left_link[key_x] = win
    else:
        x.right_link[key_x] = win

    if w.left_link.get(key_w_parent) == win:
        w.left_link[key_w_parent] = y
    else:
        w.right_link[key_w_parent] = y

    if x != y and y is not None:
        key_y = get_actual_key(y, b_child)
        if y.left_link.get(key_y) == w:
            y.left_link[key_y] = w
        else:
            y.right_link[key_y] = w

    parent_block[b_child] = find_block(parent_b_id)
    block_root[find_block(parent_b_id)] = block_root.get(find_block(parent_b_id), w.parent)


def EmbedBackEdge(v, v_out, w, win, current_b_id):
    key_v = get_actual_key(v, current_b_id)
    key_w = get_actual_key(w, current_b_id)

    if (1 ^ v_out) == 0:
        v.left_link[key_v] = w
    else:
        v.right_link[key_v] = w

    if w.left_link.get(key_w) == win:
        w.left_link[key_w] = v
    else:
        w.right_link[key_w] = v

    v.embedded_back_edges_count += 1


def planarity_testing_loop(vertices):
    for v in vertices:
        v.visited_walkup = -1
        v.pertinentRoots = []
        v.backedgeFlag = None
        v.embedded_back_edges_count = 0
    for i in range(len(vertices) - 1, -1, -1):
        if not vertices[i].back_edges_list:
            continue

        vertices[i].embedded_back_edges_count = 0
        for b in vertices[i].back_edges_list:
            if b.vertex_a.id == vertices[i].id:
                descendant = b.vertex_b
            else:
                descendant = b.vertex_a
            walkup(descendant, vertices[i])

        walkdown(vertices[i])
        if vertices[i].embedded_back_edges_count != len(vertices[i].back_edges_list):
            print("Didnt pass main planarity test - graph is not planar")
            return False

    print("Graph is planar")
    return True


file_name = "test.txt"
vert_id =[]
with open(file_name,"r") as f:
    for line in f:
        line = line.split()
        e = Edge(line[0],line[1],line[2],float(line[3]))
        edges.append(e)
        if e.vertex_a_id not in vert_id:
            vert_id.append(e.vertex_a_id)
        if e.vertex_b_id not in vert_id:
            vert_id.append(e.vertex_b_id)
f.close()

if not euler_test(edges,vert_id):
    print("Didnt pass Euler's test - not planar")
    exit()
root = Vertex(edges[0].vertex_a_id)
dfi_counter = 0
root.set_vertex_dfi(dfi_counter)
vertices.append(root)
dfs_graph(edges,root,dfi_counter)

buckets = [[] for _ in range(len(vertices))]
print(len(buckets))

sort_children(vertices,buckets)
for v in vertices:
    if v.parent is not None:
        p = v.parent

        block_root[v.id] = p
        v.left_link[v.id] = p
        v.right_link[v.id] = p

        p.left_link[v.id] = v
        p.right_link[v.id] = v
planarity_testing_loop(vertices)







for i in vertices:
    print(i.id,i.dfi,i.lowpoint,i.leastAncestor)
for e in edges:
    print(e.name, e.vertex_a.id, e.vertex_b.id)