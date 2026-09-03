import math
import random
from multiprocessing.shared_memory import SharedMemory
from multiprocessing.pool import Pool
import numpy as np

ADJACENCY = None
POS_OLD = None
POS_NEW = None
ID_TO_IDX = None


def init_worker(adj, shm_old_name, shm_new_name, n, id_to_idx):
    global ADJACENCY, POS_OLD, POS_NEW, ID_TO_IDX
    ADJACENCY = adj
    ID_TO_IDX = id_to_idx

    shm_old = SharedMemory(name=shm_old_name)
    shm_new = SharedMemory(name=shm_new_name)

    POS_OLD = np.ndarray((n, 2), dtype=np.float64, buffer=shm_old.buf)
    POS_NEW = np.ndarray((n, 2), dtype=np.float64, buffer=shm_new.buf)


def worker_step(vertex_ids):
    local_max_delta = 0.0
    for vertex_id in vertex_ids:
        idx = ID_TO_IDX[vertex_id]
        neighbors = ADJACENCY.get(vertex_id, set())

        if not neighbors:
            new_x, new_y = POS_OLD[idx, 0], POS_OLD[idx, 1]
        else:
            sum_x = 0.0
            sum_y = 0.0
            for n_id in neighbors:
                n_idx = ID_TO_IDX[n_id]
                sum_x += POS_OLD[n_idx, 0]
                sum_y += POS_OLD[n_idx, 1]
            count = float(len(neighbors))
            new_x, new_y = sum_x / count, sum_y / count

        POS_NEW[idx, 0] = new_x
        POS_NEW[idx, 1] = new_y

        delta = abs(new_x - POS_OLD[idx, 0]) + abs(new_y - POS_OLD[idx, 1])
        if delta > local_max_delta:
            local_max_delta = delta

    return local_max_delta


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
        for v in vertices.values():
            v.is_boundary = True
        return

    ordered = sorted(vertices.values(), key=lambda item: len(adjacency.get(item.id, set())), reverse=True)
    auto_boundary = ordered[:3]
    for i, v in enumerate(auto_boundary):
        angle = (2.0 * math.pi * i) / 3.0
        v.x = math.cos(angle)
        v.y = math.sin(angle)
        v.is_boundary = True


def compute_internal_positions_parallel(vertices, edges, fixed_positions=None, max_iter=300, tol=1e-5, workers=4,):
    if fixed_positions is None:
        fixed_positions = {}

    adjacency = build_adjacency(edges)
    initialize_boundary_positions(vertices, adjacency, fixed_positions)

    positions = {v_id: (v.x, v.y) for v_id, v in vertices.items()}
    boundary_ids = {v for v in vertices if vertices.get(v).is_boundary}
    internal_ids = [v for v in vertices if v not in boundary_ids]

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

    for _ in range(max_iter):
        max_delta = 0.0
        new_positions = {}
        for v_id in internal_ids:
            neighbors = adjacency.get(v_id, set())
            if not neighbors:
                new_positions[v_id] = positions[v_id]
                continue
            sum_x = sum(positions[n_id][0] for n_id in neighbors)
            sum_y = sum(positions[n_id][1] for n_id in neighbors)
            count = float(len(neighbors))
            new_x, new_y = sum_x / count, sum_y / count
            new_positions[v_id] = (new_x, new_y)

            old_x, old_y = positions[v_id]
            delta = abs(new_x - old_x) + abs(new_y - old_y)
            if delta > max_delta:
                max_delta = delta

        positions.update(new_positions)
        if max_delta < tol:
            break
        return positions
    all_vertex_ids = list(vertices.keys())
    id_to_idx = {v_id: idx for idx, v_id in enumerate(all_vertex_ids)}
    n = len(all_vertex_ids)

    bytes_size = n * 2 * np.dtype(np.float64).itemsize
    shm_old = SharedMemory(create=True, size=bytes_size)
    shm_new = SharedMemory(create=True, size=bytes_size)

    try:
        arr_old = np.ndarray((n, 2), dtype=np.float64, buffer=shm_old.buf)
        arr_new = np.ndarray((n, 2), dtype=np.float64, buffer=shm_new.buf)

        for v_id, (x, y) in positions.items():
            idx = id_to_idx[v_id]
            arr_old[idx] = [x, y]
            arr_new[idx] = [x, y]

        chunk_size = math.ceil(len(internal_ids) / workers)
        chunks = [internal_ids[i:i + chunk_size] for i in range(0, len(internal_ids), chunk_size)]

        with Pool(workers, initializer=init_worker,
                  initargs=(adjacency, shm_old.name, shm_new.name, n, id_to_idx)) as p:
            for _ in range(max_iter):
                deltas = p.map(worker_step, chunks)

                max_delta = max(deltas) if deltas else 0.0

                arr_old, arr_new = arr_new, arr_old
                shm_old, shm_new = shm_new, shm_old

                if max_delta < tol:
                    break


        final_positions = {}
        for v_id in vertices:
            idx = id_to_idx[v_id]
            final_positions[v_id] = (float(arr_old[idx, 0]), float(arr_old[idx, 1]))

        return final_positions

    finally:

        shm_old.close()
        shm_old.unlink()
        shm_new.close()
        shm_new.unlink()


def assign_positions(vertices, positions):
    for v in vertices:
        if v in positions:
            vertices.get(v).x, vertices.get(v).y = positions[v]
