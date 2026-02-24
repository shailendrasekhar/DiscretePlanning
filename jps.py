"""
Jump Point Search (JPS) on a Grid
====================================
An optimisation of A* for **uniform-cost 8-connected** grids.  Instead
of adding every visible neighbour to the open list, JPS *jumps* along
straight lines and diagonals, pruning symmetric paths.

Uses Chebyshev distance as the heuristic, which is admissible and
consistent for 8-connected movement with uniform cost.
"""

from __future__ import annotations

import heapq
from math import inf
from typing import Dict, Generator, List, Optional, Set, Tuple

from grid_planner import Grid, OBSTACLE
from visualiser import SearchState


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def _heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def _in_bounds(grid: Grid, r: int, c: int) -> bool:
    return 0 <= r < grid.rows and 0 <= c < grid.cols


def _walkable(grid: Grid, r: int, c: int) -> bool:
    return _in_bounds(grid, r, c) and grid.grid[r, c] != OBSTACLE


# -------------------------------------------------------------------
# Jumping logic
# -------------------------------------------------------------------

def _jump(grid, r, c, dr, dc, goal):
    nr, nc = r + dr, c + dc
    if not _walkable(grid, nr, nc):
        return None
    if (nr, nc) == goal:
        return (nr, nc)

    if dr != 0 and dc != 0:
        if (not _walkable(grid, nr - dr, nc) and _walkable(grid, nr - dr, nc + dc)):
            return (nr, nc)
        if (not _walkable(grid, nr, nc - dc) and _walkable(grid, nr + dr, nc - dc)):
            return (nr, nc)
        if _jump(grid, nr, nc, dr, 0, goal) is not None:
            return (nr, nc)
        if _jump(grid, nr, nc, 0, dc, goal) is not None:
            return (nr, nc)
    else:
        if dr != 0:
            if (not _walkable(grid, nr, nc - 1) and _walkable(grid, nr + dr, nc - 1)):
                return (nr, nc)
            if (not _walkable(grid, nr, nc + 1) and _walkable(grid, nr + dr, nc + 1)):
                return (nr, nc)
        else:
            if (not _walkable(grid, nr - 1, nc) and _walkable(grid, nr - 1, nc + dc)):
                return (nr, nc)
            if (not _walkable(grid, nr + 1, nc) and _walkable(grid, nr + 1, nc + dc)):
                return (nr, nc)

    if dr != 0 and dc != 0:
        if not (_walkable(grid, nr + dr, nc) or _walkable(grid, nr, nc + dc)):
            return None

    return _jump(grid, nr, nc, dr, dc, goal)


def _identify_successors(grid, current, came_from, goal):
    successors = []
    r, c = current
    parent = came_from.get(current)

    if parent is not None:
        pr, pc = parent
        dr = _sign(r - pr)
        dc = _sign(c - pc)
        directions = _pruned_directions(grid, r, c, dr, dc)
    else:
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1),
        ]

    for dr, dc in directions:
        jp = _jump(grid, r, c, dr, dc, goal)
        if jp is not None:
            successors.append(jp)

    return successors


def _pruned_directions(grid, r, c, dr, dc):
    dirs = []
    if dr != 0 and dc != 0:
        dirs.append((dr, dc))
        dirs.append((dr, 0))
        dirs.append((0, dc))
        if not _walkable(grid, r - dr, c):
            dirs.append((-dr, dc))
        if not _walkable(grid, r, c - dc):
            dirs.append((dr, -dc))
    elif dr != 0:
        dirs.append((dr, 0))
        if not _walkable(grid, r, c - 1):
            dirs.append((dr, -1))
        if not _walkable(grid, r, c + 1):
            dirs.append((dr, 1))
    else:
        dirs.append((0, dc))
        if not _walkable(grid, r - 1, c):
            dirs.append((-1, dc))
        if not _walkable(grid, r + 1, c):
            dirs.append((1, dc))
    return dirs


def _sign(x):
    return (x > 0) - (x < 0)


def _octile_dist(a, b):
    dr = abs(a[0] - b[0])
    dc = abs(a[1] - b[1])
    return max(dr, dc)


# -------------------------------------------------------------------
# Main search
# -------------------------------------------------------------------

def jps(grid: Grid) -> Optional[List[Tuple[int, int]]]:
    """Run JPS and return the path (or None)."""
    result = None
    for state in jps_gen(grid):
        if state.path is not None:
            result = state.path
    return result


def jps_gen(grid: Grid) -> Generator[SearchState, None, None]:
    """Generator that yields a ``SearchState`` after every expansion."""
    start, goal = grid.start, grid.goal

    g_score: Dict[Tuple[int, int], float] = {start: 0}
    came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}

    counter = 0
    open_list: List[Tuple[float, int, Tuple[int, int]]] = [
        (_heuristic(start, goal), counter, start)
    ]
    closed: Set[Tuple[int, int]] = set()
    in_open: Set[Tuple[int, int]] = {start}

    while open_list:
        _f, _cnt, current = heapq.heappop(open_list)

        if current in closed:
            continue
        closed.add(current)
        in_open.discard(current)

        yield SearchState(
            current=current,
            visited=set(closed),
            frontier=set(in_open),
        )

        if current == goal:
            yield SearchState(
                current=current,
                visited=set(closed),
                frontier=set(in_open),
                path=_build_full_path(came_from, goal),
            )
            return

        for jp in _identify_successors(grid, current, came_from, goal):
            if jp in closed:
                continue
            tentative_g = g_score[current] + _octile_dist(current, jp)
            if tentative_g < g_score.get(jp, inf):
                g_score[jp] = tentative_g
                came_from[jp] = current
                f = tentative_g + _heuristic(jp, goal)
                counter += 1
                heapq.heappush(open_list, (f, counter, jp))
                in_open.add(jp)

    # No path found
    yield SearchState(current=None, visited=set(closed), frontier=set())


# -------------------------------------------------------------------
# Path reconstruction
# -------------------------------------------------------------------

def _build_full_path(came_from, goal):
    jp_chain = []
    node = goal
    while node is not None:
        jp_chain.append(node)
        node = came_from[node]
    jp_chain.reverse()

    if len(jp_chain) <= 1:
        return jp_chain

    full_path = [jp_chain[0]]
    for i in range(1, len(jp_chain)):
        a, b = jp_chain[i - 1], jp_chain[i]
        r, c = a
        while (r, c) != b:
            dr = _sign(b[0] - r)
            dc = _sign(b[1] - c)
            r += dr
            c += dc
            full_path.append((r, c))

    return full_path
