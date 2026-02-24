"""
A* Search Algorithm on a Grid
================================
Combines the actual cost g(n) with a heuristic estimate h(n) to
efficiently find the optimal shortest path.  Uses Manhattan distance
as the heuristic for 4-connected movement.
"""

from __future__ import annotations

import heapq
from math import inf
from typing import Dict, Generator, List, Optional, Set, Tuple

from grid_planner import Grid
from visualiser import SearchState


def _heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    """Manhattan distance -- admissible and consistent for 4-connected grids."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(grid: Grid) -> Optional[List[Tuple[int, int]]]:
    """Run A* and return the path (or None)."""
    result = None
    for state in astar_gen(grid):
        if state.path is not None:
            result = state.path
    return result


def astar_gen(grid: Grid) -> Generator[SearchState, None, None]:
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
                path=_reconstruct(came_from, goal),
            )
            return

        for neighbour in grid.neighbours(current):
            if neighbour in closed:
                continue
            tentative_g = g_score[current] + 1
            if tentative_g < g_score.get(neighbour, inf):
                g_score[neighbour] = tentative_g
                came_from[neighbour] = current
                f = tentative_g + _heuristic(neighbour, goal)
                counter += 1
                heapq.heappush(open_list, (f, counter, neighbour))
                in_open.add(neighbour)

    # No path found
    yield SearchState(current=None, visited=set(closed), frontier=set())


def _reconstruct(
    came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]],
    goal: Tuple[int, int],
) -> List[Tuple[int, int]]:
    path: List[Tuple[int, int]] = []
    node: Optional[Tuple[int, int]] = goal
    while node is not None:
        path.append(node)
        node = came_from[node]
    path.reverse()
    return path
