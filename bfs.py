"""
Breadth-First Search (BFS) on a Grid
=====================================
Explores all neighbours at the current depth before moving deeper.
Guarantees the shortest path in an unweighted grid (all moves cost 1).
"""

from __future__ import annotations

from collections import deque
from typing import Dict, Generator, List, Optional, Set, Tuple

from grid_planner import Grid
from visualiser import SearchState


def bfs(grid: Grid) -> Optional[List[Tuple[int, int]]]:
    """Run BFS and return the path (or None)."""
    result = None
    for state in bfs_gen(grid):
        if state.path is not None:
            result = state.path
    return result


def bfs_gen(grid: Grid) -> Generator[SearchState, None, None]:
    """Generator that yields a ``SearchState`` after every expansion."""
    start, goal = grid.start, grid.goal

    queue: deque[Tuple[int, int]] = deque([start])
    came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
    visited: Set[Tuple[int, int]] = set()

    while queue:
        current = queue.popleft()
        visited.add(current)

        frontier_set = set(queue)
        yield SearchState(
            current=current,
            visited=set(visited),
            frontier=frontier_set,
        )

        if current == goal:
            yield SearchState(
                current=current,
                visited=set(visited),
                frontier=frontier_set,
                path=_reconstruct(came_from, goal),
            )
            return

        for neighbour in grid.neighbours(current):
            if neighbour not in came_from:
                came_from[neighbour] = current
                queue.append(neighbour)

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
