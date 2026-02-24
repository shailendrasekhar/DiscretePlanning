"""
Depth-First Search (DFS) on a Grid
====================================
Explores as deep as possible along each branch before backtracking.
Does **not** guarantee the shortest path.
"""

from __future__ import annotations

from typing import Dict, Generator, List, Optional, Set, Tuple

from grid_planner import Grid
from visualiser import SearchState


def dfs(grid: Grid) -> Optional[List[Tuple[int, int]]]:
    """Run DFS and return the path (or None)."""
    result = None
    for state in dfs_gen(grid):
        if state.path is not None:
            result = state.path
    return result


def dfs_gen(grid: Grid) -> Generator[SearchState, None, None]:
    """Generator that yields a ``SearchState`` after every expansion."""
    start, goal = grid.start, grid.goal

    stack: List[Tuple[int, int]] = [start]
    came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
    visited: Set[Tuple[int, int]] = set()

    while stack:
        current = stack.pop()
        visited.add(current)

        frontier_set = set(stack)
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
                stack.append(neighbour)

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
