"""
Discrete Planning – Custom Grid with Start, Goal, and Random Obstacles
======================================================================
Single entry point: reads algorithm choice + all parameters from
config.yaml (overridable via CLI flags).

Usage:
    python grid_planner.py                        # uses config.yaml defaults
    python grid_planner.py --algorithm bfs        # override algorithm
    python grid_planner.py --rows 30 --cols 40    # override grid size
    python grid_planner.py --rows 10 --cols 10 --start 0,0 --goal 9,9 --obstacle_pct 0.25
    python grid_planner.py --seed 42              # reproducible obstacle layout
"""

from __future__ import annotations

import argparse
import os
import random
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import yaml


# ---------------------------------------------------------------------------
# Configuration loader
# ---------------------------------------------------------------------------

_CONFIG_PATH = Path(__file__).parent / "config.yaml"


def load_config(path: Path = _CONFIG_PATH) -> Dict[str, Any]:
    """Load configuration from a YAML file."""
    with open(path, "r") as f:
        return yaml.safe_load(f)


CFG = load_config()

# ---------------------------------------------------------------------------
# Grid world representation
# ---------------------------------------------------------------------------

FREE = 0
OBSTACLE = 1
START = 2
GOAL = 3

CELL_LABELS = {FREE: "Free", OBSTACLE: "Obstacle", START: "Start", GOAL: "Goal"}


class Grid:
    """A 2-D occupancy grid with a start cell, goal cell, and obstacles."""

    def __init__(
        self,
        rows: int = CFG["grid"]["rows"],
        cols: int = CFG["grid"]["cols"],
        start: Tuple[int, int] = tuple(CFG["start"]),
        goal: Tuple[int, int] | None = (
            tuple(CFG["goal"]) if CFG["goal"] is not None else None
        ),
        obstacle_pct: float = CFG["obstacles"]["percentage"],
        seed: int | None = CFG["obstacles"]["seed"],
    ) -> None:
        if rows < 2 or cols < 2:
            raise ValueError("Grid must be at least 2×2.")
        if not (0.0 <= obstacle_pct < 1.0):
            raise ValueError("obstacle_pct must be in [0, 1).")

        self.rows = rows
        self.cols = cols
        self.start = start
        self.goal = goal if goal is not None else (rows - 1, cols - 1)

        self._validate_cell(self.start, "start")
        self._validate_cell(self.goal, "goal")
        if self.start == self.goal:
            raise ValueError("Start and goal must be different cells.")

        self.grid = np.zeros((rows, cols), dtype=np.int8)

        # --- Place random obstacles -------------------------------------------
        rng = random.Random(seed)
        total_cells = rows * cols
        n_obstacles = int(total_cells * obstacle_pct)

        # All cells except start and goal are candidates
        candidates = [
            (r, c)
            for r in range(rows)
            for c in range(cols)
            if (r, c) not in (self.start, self.goal)
        ]
        obstacles = rng.sample(candidates, min(n_obstacles, len(candidates)))
        for r, c in obstacles:
            self.grid[r, c] = OBSTACLE

        # Mark start and goal (overwrite even if they somehow got an obstacle)
        self.grid[self.start] = START
        self.grid[self.goal] = GOAL

    # ------------------------------------------------------------------
    def _validate_cell(self, cell: Tuple[int, int], name: str) -> None:
        r, c = cell
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            raise ValueError(
                f"{name} cell {cell} is out of bounds for a {self.rows}×{self.cols} grid."
            )

    # ------------------------------------------------------------------
    def neighbours(self, cell: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Return walkable 4-connected neighbours of *cell*."""
        r, c = cell
        nbrs = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                if self.grid[nr, nc] != OBSTACLE:
                    nbrs.append((nr, nc))
        return nbrs

    # ------------------------------------------------------------------
    def neighbours8(self, cell: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Return walkable 8-connected neighbours (including diagonals).

        Diagonal movement is only allowed when both adjacent cardinal
        cells are free (no corner-cutting through obstacles).
        """
        r, c = cell
        nbrs = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1),
                        (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                if self.grid[nr, nc] == OBSTACLE:
                    continue
                # For diagonals, require both cardinal neighbours to be free
                if dr != 0 and dc != 0:
                    if (self.grid[r + dr, c] == OBSTACLE or
                            self.grid[r, c + dc] == OBSTACLE):
                        continue
                nbrs.append((nr, nc))
        return nbrs

    # ------------------------------------------------------------------
    def is_free(self, r: int, c: int) -> bool:
        return self.grid[r, c] != OBSTACLE

    # ------------------------------------------------------------------
    def summary(self) -> str:
        total = self.rows * self.cols
        n_obs = int((self.grid == OBSTACLE).sum())
        return (
            f"Grid {self.rows}×{self.cols}  |  "
            f"Start {self.start}  |  Goal {self.goal}  |  "
            f"Obstacles {n_obs}/{total} ({100*n_obs/total:.1f}%)"
        )




# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def parse_pair(s: str) -> Tuple[int, int]:
    """Parse 'row,col' string into a tuple."""
    parts = s.split(",")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError(f"Expected row,col but got '{s}'")
    return int(parts[0]), int(parts[1])


ALGORITHM_CHOICES = ["bfs", "dfs", "best_first", "dijkstra", "astar", "jps"]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Generate and visualise a custom planning grid."
    )
    _alg = CFG.get("algorithm", "astar")
    p.add_argument(
        "--algorithm", "-a",
        type=str,
        choices=ALGORITHM_CHOICES,
        default=_alg,
        help=f"Search algorithm to use (default: {_alg})",
    )
    _g = CFG["grid"]
    _s = CFG["start"]
    _o = CFG["obstacles"]
    p.add_argument("--rows", type=int, default=_g["rows"],
                   help=f"Number of rows (default: {_g['rows']})")
    p.add_argument("--cols", type=int, default=_g["cols"],
                   help=f"Number of columns (default: {_g['cols']})")
    p.add_argument(
        "--start",
        type=parse_pair,
        default=f"{_s[0]},{_s[1]}",
        help=f"Start cell as row,col (default: {_s[0]},{_s[1]})",
    )
    _goal_default = None
    _goal_help = "Goal cell as row,col (default: bottom-right corner)"
    if CFG["goal"] is not None:
        _gv = CFG["goal"]
        _goal_default = f"{_gv[0]},{_gv[1]}"
        _goal_help = f"Goal cell as row,col (default: {_gv[0]},{_gv[1]})"
    p.add_argument(
        "--goal",
        type=parse_pair,
        default=_goal_default,
        help=_goal_help,
    )
    p.add_argument(
        "--obstacle_pct",
        type=float,
        default=_o["percentage"],
        help=f"Fraction of cells that are obstacles (default: {_o['percentage']})",
    )
    p.add_argument(
        "--seed",
        type=int,
        default=_o["seed"],
        help="Random seed for reproducible obstacle placement",
    )
    return p


# ---------------------------------------------------------------------------
# Algorithm dispatch  (returns generator version)
# ---------------------------------------------------------------------------

def _get_algorithm_gen(name: str):
    """Lazily import and return the *generator* search function for *name*."""
    if name == "bfs":
        from bfs import bfs_gen
        return bfs_gen
    elif name == "dfs":
        from dfs import dfs_gen
        return dfs_gen
    elif name == "best_first":
        from best_first_search import best_first_search_gen
        return best_first_search_gen
    elif name == "dijkstra":
        from dijkstra import dijkstra_gen
        return dijkstra_gen
    elif name == "astar":
        from astar import astar_gen
        return astar_gen
    elif name == "jps":
        from jps import jps_gen
        return jps_gen
    else:
        raise ValueError(f"Unknown algorithm: {name!r}")


_ALGORITHM_LABELS = {
    "bfs": "BFS",
    "dfs": "DFS",
    "best_first": "Best-First",
    "dijkstra": "Dijkstra",
    "astar": "A*",
    "jps": "JPS",
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    args = build_parser().parse_args()
    grid = Grid(
        rows=args.rows,
        cols=args.cols,
        start=args.start,
        goal=args.goal,
        obstacle_pct=args.obstacle_pct,
        seed=args.seed,
    )

    alg_name = args.algorithm
    label = _ALGORITHM_LABELS.get(alg_name, alg_name)
    gen_fn = _get_algorithm_gen(alg_name)

    print(f"{label}  |  {grid.summary()}")

    from visualiser import PygameVisualiser
    vis = PygameVisualiser(grid, title=f"{label} – {grid.summary()}")
    path = vis.run(gen_fn(grid))

    if path:
        print(f"Path length: {len(path)}")
    else:
        print("No path found!")


if __name__ == "__main__":
    main()
