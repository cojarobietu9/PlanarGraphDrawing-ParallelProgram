import math
import random
from concurrent.futures import ThreadPoolExecutor


def build_adjacency(edges):
    adjacency = {}
    for e in edges:
        adjacency.setdefault(e.vertex_a_id, set()).add(e.vertex_b_id)
        adjacency.setdefault(e.vertex_b_id, set()).add(e.vertex_a_id)
    return adjacency

def initialize_boundary_positions(vertices, adjacency, fixed_positions):
    for vertex_id, (x, y) in fixed_positions.items():
        if vertex_id in vertices:
            vertices[vertex_id].x = x
            vertices[vertex_id].y = y
            vertices[vertex_id].is_boundary = True

    if any(vertices.get(v).is_boundary for v in vertices):
        return

    if len(vertices) < 3:
        for v in vertices:
            v.is_boundary = True
        return

    ordered = sorted(vertices.values(), key=lambda item: len(adjacency.get(item.id, set())), reverse=True)
    auto_boundary = ordered[:3]
    for i, v in enumerate(auto_boundary):
        angle = (2.0 * math.pi * i) / 3.0
        v.x = math.cos(angle)
        v.y = math.sin(angle)
        v.is_boundary = True

def _next_position(vertex_id, adjacency, positions):
    neighbors = adjacency.get(vertex_id, set())
    if not neighbors:
        return vertex_id, positions[vertex_id]

    sum_x = 0.0
    sum_y = 0.0
    for n_id in neighbors:
        nx, ny = positions[n_id]

        sum_x += nx
        sum_y += ny
    count = float(len(neighbors))
    return vertex_id, (sum_x / count, sum_y / count)


def compute_internal_positions_parallel(vertices, edges, fixed_positions=None, max_iter=300, tol=1e-5, workers=32):
    if fixed_positions is None:
        fixed_positions = {}

    adjacency = build_adjacency(edges)
    initialize_boundary_positions(vertices, adjacency, fixed_positions)

    positions = {v_id: (v.x, v.y) for v_id, v in vertices.items()}
    boundary_ids = {v for v in vertices if vertices.get(v).is_boundary}
    internal_ids = [v for v in vertices if v not in boundary_ids]

    #print("boundry:", boundary_ids, "| internal:", internal_ids)

    if boundary_ids:
        bx = sum(positions[v_id][0] for v_id in boundary_ids) / len(boundary_ids)
        by = sum(positions[v_id][1] for v_id in boundary_ids) / len(boundary_ids)
    else:
        bx = by = 0.0

    boundary_list = list(boundary_ids)

    for v_id in internal_ids:
        if boundary_list:
            rand_boundary_id = random.choice(boundary_list)
            bound_x, bound_y = positions[rand_boundary_id]


            w = random.uniform(0.05, 0.4)

            start_x = bx * (1 - w) + bound_x * w
            start_y = by * (1 - w) + bound_y * w

            positions[v_id] = (start_x, start_y)
        else:
            positions[v_id] = (bx, by)

#    print("initial positions, before thread pool: ", positions)
 #   print("adjecencies:", adjacency)

    for abctest in range(max_iter):
        max_delta = 0.0
        with ThreadPoolExecutor(max_workers=min(workers, max(1, len(internal_ids)))) as executor:
            futures = [
                executor.submit(_next_position, v_id, adjacency, positions)
                for v_id in internal_ids
            ]
            updates = [f.result() for f in futures]

        for v_id, (new_x, new_y) in updates:
            old_x, old_y = positions[v_id]
            delta = abs(new_x - old_x) + abs(new_y - old_y)
            if delta > max_delta:
                max_delta = delta
            positions[v_id] = (new_x, new_y)

        if max_delta < tol:
            break

    return positions

def assign_positions(vertices, positions):
    for v in vertices:
        if v in positions:
            vertices.get(v).x, vertices.get(v).y = positions[v]

            AREA = 1000.0 * 1000.0
            K = math.sqrt(AREA / 100)  

