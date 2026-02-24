"""
Best-First Search (Greedy) on a Grid
======================================
Expands the node that appears closest to the goal according to a
heuristic (Manhattan distance).  Does **not** guarantee the shortest
path -- it is greedy and can be misled by obstacles.
"""

from __future__ import annotations

import heapq
from typing import Dict, Generator, List, Optional, Set, Tuple

from grid_planner import Grid
from visualiser import SearchState


def _heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    """Manhattan distance between two cells."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def best_first_search(grid: Grid) -> Optional[List[Tuple[int, int]]]:
    """Run greedy best-first search and return the path (or None)."""
    result = None
    for state in best_first_search_gen(grid):
        if state.path is not None:
            result = state.path
    return result


def best_first_search_gen(grid: Grid) -> Generator[SearchState, None, None]:
    """Generator that yields a ``SearchState`` after every expansion."""
    start, goal = grid.start, grid.goal

    counter = 0
    open_list: List[Tuple[int, int, Tuple[int, int]]] = []
    heapq.heappush(open_list, (_heuristic(start, goal), counter, start))

    came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
    visited: Set[Tuple[int, int]] = set()
    in_open: Set[Tuple[int, int]] = {start}

    while open_list:
        _h, _cnt, current = heapq.heappop(open_list)
        in_open.discard(current)
        visited.add(current)

        yield SearchState(
            current=current,
            visited=set(visited),
            frontier=set(in_open),
        )

        if current == goal:
            yield SearchState(
                current=current,
                visited=set(visited),
                frontier=set(in_open),
                path=_reconstruct(came_from, goal),
            )
            return

        for neighbour in grid.neighbours(current):
            if neighbour not in came_from:
                came_from[neighbour] = current
                counter += 1
                heapq.heappush(
                    open_list,
                    (_heuristic(neighbour, goal), counter, neighbour),
                )
                in_open.add(neighbour)

    # No path found
    yield SearchState(current=None, visited=set(visited), frontier=set())


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
