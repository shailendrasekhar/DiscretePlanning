"""
Pygame-based live visualiser for grid search algorithms.
=========================================================
Consumes a *generator* that yields ``SearchState`` snapshots and
renders each step in real time.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Generator, List, Optional, Set, Tuple

import pygame

from grid_planner import CFG, FREE, OBSTACLE, START, GOAL, Grid


# -------------------------------------------------------------------
# Search state snapshot (yielded by algorithm generators)
# -------------------------------------------------------------------

@dataclass
class SearchState:
    """One snapshot of a running search algorithm."""
    current: Optional[Tuple[int, int]] = None
    visited: Set[Tuple[int, int]] = field(default_factory=set)
    frontier: Set[Tuple[int, int]] = field(default_factory=set)
    path: Optional[List[Tuple[int, int]]] = None   # set when goal is found


# -------------------------------------------------------------------
# Renderer
# -------------------------------------------------------------------

class PygameVisualiser:
    """Renders a ``Grid`` and animates search progress via a generator."""

    def __init__(self, grid: Grid, title: str = "Grid Planner") -> None:
        self.grid = grid
        self.title = title

        v = CFG["visualisation"]
        self.cell = v["cell_size"]
        self.lw = v["grid_line_width"]

        c = v["colours"]
        self.col_bg       = tuple(c["background"])
        self.col_obstacle = tuple(c["obstacle"])
        self.col_start    = tuple(c["start"])
        self.col_goal     = tuple(c["goal"])
        self.col_visited  = tuple(c["visited"])
        self.col_frontier = tuple(c["frontier"])
        self.col_current  = tuple(c["current"])
        self.col_path     = tuple(c["path"])
        self.col_grid     = tuple(c["grid_line"])
        self.col_text     = tuple(c["text"])

        self.start_label = v["start_label"]
        self.goal_label  = v["goal_label"]

        anim = v["animation"]
        self.steps_per_frame   = anim["steps_per_frame"]
        self.delay_ms          = anim["delay_ms"]
        self.path_delay_ms     = anim["path_delay_ms"]
        self.pause_ms          = anim["pause_before_close_ms"]

        # Window dimensions
        self.width  = grid.cols * self.cell
        self.height = grid.rows * self.cell

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)

        font_size = max(12, int(self.cell * 0.6))
        self.font = pygame.font.SysFont("monospace", font_size, bold=True)

    # ----------------------------------------------------------------
    # Drawing helpers
    # ----------------------------------------------------------------

    def _cell_rect(self, r: int, c: int) -> pygame.Rect:
        return pygame.Rect(c * self.cell, r * self.cell, self.cell, self.cell)

    def _draw_base_grid(self) -> None:
        """Draw the static grid: background, obstacles, start, goal."""
        self.screen.fill(self.col_bg)
        g = self.grid
        for r in range(g.rows):
            for c in range(g.cols):
                rect = self._cell_rect(r, c)
                val = g.grid[r, c]
                if val == OBSTACLE:
                    pygame.draw.rect(self.screen, self.col_obstacle, rect)
                elif val == START:
                    pygame.draw.rect(self.screen, self.col_start, rect)
                elif val == GOAL:
                    pygame.draw.rect(self.screen, self.col_goal, rect)

        # Grid lines
        for r in range(g.rows + 1):
            y = r * self.cell
            pygame.draw.line(self.screen, self.col_grid, (0, y), (self.width, y), self.lw)
        for c in range(g.cols + 1):
            x = c * self.cell
            pygame.draw.line(self.screen, self.col_grid, (x, 0), (x, self.height), self.lw)

    def _draw_overlay(self, state: SearchState, path_so_far: List[Tuple[int, int]] | None = None) -> None:
        """Draw visited / frontier / current / path on top of the base grid."""
        g = self.grid

        # Visited cells
        for (r, c) in state.visited:
            if (r, c) not in (g.start, g.goal):
                pygame.draw.rect(self.screen, self.col_visited, self._cell_rect(r, c))

        # Frontier cells
        for (r, c) in state.frontier:
            if (r, c) not in (g.start, g.goal):
                pygame.draw.rect(self.screen, self.col_frontier, self._cell_rect(r, c))

        # Current cell
        if state.current and state.current not in (g.start, g.goal):
            pygame.draw.rect(self.screen, self.col_current, self._cell_rect(*state.current))

        # Path (animated or final)
        draw_path = path_so_far if path_so_far is not None else state.path
        if draw_path:
            for (r, c) in draw_path:
                if (r, c) not in (g.start, g.goal):
                    pygame.draw.rect(self.screen, self.col_path, self._cell_rect(r, c))

        # Re-draw start/goal on top so they stay visible
        pygame.draw.rect(self.screen, self.col_start, self._cell_rect(*g.start))
        pygame.draw.rect(self.screen, self.col_goal, self._cell_rect(*g.goal))

        # Labels
        sr, sc = g.start
        gr, gc = g.goal
        s_surf = self.font.render(self.start_label, True, self.col_text)
        g_surf = self.font.render(self.goal_label, True, self.col_text)
        self.screen.blit(
            s_surf,
            s_surf.get_rect(center=self._cell_rect(sr, sc).center),
        )
        self.screen.blit(
            g_surf,
            g_surf.get_rect(center=self._cell_rect(gr, gc).center),
        )

    # ----------------------------------------------------------------
    # Main animation loop
    # ----------------------------------------------------------------

    def run(self, gen: Generator[SearchState, None, None]) -> Optional[List[Tuple[int, int]]]:
        """Consume *gen* and animate.  Returns the final path (or None)."""
        clock = pygame.time.Clock()
        last_state = SearchState()
        running = True

        # --- Animate search expansion -----------------------------------
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return None

            # Advance the generator by steps_per_frame
            exhausted = False
            for _ in range(self.steps_per_frame):
                try:
                    last_state = next(gen)
                except StopIteration:
                    exhausted = True
                    break

            self._draw_base_grid()
            self._draw_overlay(last_state)
            pygame.display.flip()
            pygame.time.delay(self.delay_ms)

            if exhausted:
                break

        # --- Animate the final path cell-by-cell -------------------------
        if last_state.path:
            path_partial: List[Tuple[int, int]] = []
            for cell in last_state.path:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return last_state.path
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return last_state.path

                path_partial.append(cell)
                self._draw_base_grid()
                self._draw_overlay(last_state, path_so_far=path_partial)
                pygame.display.flip()
                pygame.time.delay(self.path_delay_ms)

        # --- Pause then close (or wait for user) -------------------------
        end_tick = pygame.time.get_ticks() + self.pause_ms
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    running = False
            if pygame.time.get_ticks() >= end_tick:
                running = False

        pygame.quit()
        return last_state.path
