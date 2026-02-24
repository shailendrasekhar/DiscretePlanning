"""
Dijkstra's Algorithm on a Grid
================================
Finds the shortest path in a weighted graph.  On a uniform-cost grid
(all edge weights = 1) it behaves like BFS but generalises to
non-uniform costs.
"""

from __future__ import annotations

import heapq
from math import inf
from typing import Dict, Generator, List, Optional, Set, Tuple

from grid_planner import Grid
from visualiser import SearchState


def dijkstra(grid: Grid) -> Optional[List[Tuple[int, int]]]:
    """Run Dijkstra and return the path (or None)."""
    result = None
    for state in dijkstra_gen(grid):
        if state.path is not None:
            result = state.path
    return result


def dijkstra_gen(grid: Grid) -> Generator[SearchState, None, None]:
    """Generator that yields a ``SearchState`` after every expansion."""
    start, goal = grid.start, grid.goal

    dist: Dict[Tuple[int, int], float] = {start: 0}
    came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}

    counter = 0
    open_list: List[Tuple[float, int, Tuple[int, int]]] = [(0, counter, start)]
    closed: Set[Tuple[int, int]] = set()
    in_open: Set[Tuple[int, int]] = {start}

    while open_list:
        d, _cnt, current = heapq.heappop(open_list)

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
            new_dist = d + 1
            if new_dist < dist.get(neighbour, inf):
                dist[neighbour] = new_dist
                came_from[neighbour] = current
                counter += 1
                heapq.heappush(open_list, (new_dist, counter, neighbour))
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
