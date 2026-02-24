# Discrete Planning – Grid Path-Finding

A configurable 2-D grid world with six classic search algorithms and
**live animated visualisation**.  Available as both a **Python desktop app**
(Pygame) and a **static website** (HTML5 Canvas) deployable to GitHub Pages.

---

## Quick Start

### Option A – Web version (GitHub Pages)

Open [**the live demo**](https://YOUR_USERNAME.github.io/YOUR_REPO/web/)
or serve locally:

```bash
cd web
python -m http.server 8000
# open http://localhost:8000
```

Everything runs in the browser — no install needed.

### Option B – Python desktop app

```bash
# Install dependencies
pip install numpy pygame pyyaml

# Run with defaults from config.yaml (A* on a 20×20 grid)
python grid_planner.py

# Override algorithm on the fly
python grid_planner.py --algorithm bfs

# Override grid size, start, goal, obstacles, seed
python grid_planner.py --rows 30 --cols 30 --start 0,0 --goal 29,29 \
    --obstacle_pct 0.25 --seed 42
```

> **Only `grid_planner.py` needs to be run.**
> Algorithm choice and every tunable parameter live in `config.yaml`.

---

## Live Visualisation

When you run `grid_planner.py`, a Pygame window opens and animates the
search **step by step**:

1. **Search phase** – the algorithm expands nodes one at a time.
   Visited cells, the current cell, and the frontier are drawn in
   distinct colours so you can see the search wave propagate.
2. **Path phase** – once the goal is found, the final path is drawn
   cell by cell.
3. **Pause** – the window stays open for a configurable duration (or
   until you press **Esc** / close the window).

### Colour Legend

| Colour | Meaning |
|---|---|
| White | Free cell |
| Black | Obstacle |
| Green | Start |
| Red | Goal |
| Light blue | Visited (closed set) |
| Orange | Frontier (open set) |
| Yellow | Currently expanding |
| Blue | Final path |

### Controls

| Key | Action |
|---|---|
| **Esc** | Quit immediately |
| Window close (×) | Quit immediately |

### Animation Tuning (`config.yaml`)

```yaml
visualisation:
  cell_size: 30               # pixels per cell
  steps_per_frame: 1          # search steps before redraw (↑ = faster)
  delay_ms: 30                # pause between frames (↓ = faster)
  path_delay_ms: 50           # pause between path cells
  pause_before_close_ms: 3000 # how long the result stays on screen
```

---

## Files

| File | Purpose |
|---|---|
| `grid_planner.py` | **Entry point (Python).** Builds the grid, dispatches to the selected algorithm, and launches the Pygame visualisation. |
| `config.yaml` | All configurable parameters (grid size, start/goal, obstacles, algorithm, visualisation). |
| `visualiser.py` | Pygame rendering engine — consumes algorithm generators and draws each frame. |
| `bfs.py` | Breadth-First Search (+ generator variant). |
| `dfs.py` | Depth-First Search (+ generator variant). |
| `best_first_search.py` | Greedy Best-First Search (+ generator variant). |
| `dijkstra.py` | Dijkstra's algorithm (+ generator variant). |
| `astar.py` | A\* algorithm (+ generator variant). |
| `jps.py` | Jump Point Search (+ generator variant). |
| `web/` | **Static website version** — self-contained HTML/CSS/JS, no server needed. |
| `web/index.html` | Main page with control panel and canvas. |
| `web/style.css` | Dark-theme responsive styles. |
| `web/grid.js` | Grid class with seeded RNG and obstacle generation. |
| `web/algorithms.js` | All 6 search algorithms as JS generators. |
| `web/visualiser.js` | Canvas-based renderer. |
| `web/main.js` | Wires UI controls to grid + algorithms + visualiser. |

---

## Configuration (`config.yaml`)

```yaml
# Algorithm to use
algorithm: astar          # bfs | dfs | best_first | dijkstra | astar | jps

# Grid dimensions
grid:
  rows: 20
  cols: 20

# Start and goal cells [row, col]
start: [0, 0]
goal: null                # null → bottom-right corner

# Obstacles
obstacles:
  percentage: 0.20        # fraction of cells [0, 1)
  seed: null              # null = random each run

# Visualisation (Pygame)
visualisation:
  cell_size: 30
  colours:
    free: [255, 255, 255]
    obstacle: [40, 40, 40]
    start: [0, 200, 0]
    goal: [200, 0, 0]
    visited: [173, 216, 230]
    frontier: [255, 165, 0]
    current: [255, 255, 0]
    path: [30, 144, 255]
    grid_line: [200, 200, 200]
  steps_per_frame: 1
  delay_ms: 30
  path_delay_ms: 50
  pause_before_close_ms: 3000
```

Every value can also be overridden from the command line:

```
python grid_planner.py --algorithm dijkstra --rows 25 --cols 25 --seed 7
```

---

## Algorithms

### Breadth-First Search (BFS)
- **File:** `bfs.py`
- **Movement:** 4-connected (up, down, left, right)
- **Optimal?** Yes (on unweighted grids)
- **Strategy:** Explores all cells at depth *d* before depth *d + 1*.
  Uses a FIFO queue.

### Depth-First Search (DFS)
- **File:** `dfs.py`
- **Movement:** 4-connected
- **Optimal?** No
- **Strategy:** Explores as deep as possible along each branch before
  backtracking. Uses a LIFO stack.

### Greedy Best-First Search
- **File:** `best_first_search.py`
- **Movement:** 4-connected
- **Optimal?** No
- **Strategy:** Expands the node with the lowest heuristic value
  *h(n)* (Manhattan distance to goal).

### Dijkstra's Algorithm
- **File:** `dijkstra.py`
- **Movement:** 4-connected
- **Optimal?** Yes
- **Strategy:** Expands the node with the lowest accumulated cost
  *g(n)*. Uses a min-heap priority queue.

### A\* Algorithm
- **File:** `astar.py`
- **Movement:** 4-connected
- **Optimal?** Yes (with an admissible heuristic)
- **Strategy:** Combines *g(n) + h(n)* (Manhattan distance). Expands
  fewer nodes than Dijkstra while still finding the optimal path.

### Jump Point Search (JPS)
- **File:** `jps.py`
- **Movement:** 8-connected (cardinal + diagonal)
- **Optimal?** Yes
- **Strategy:** An optimisation of A\* that jumps along straight and
  diagonal lines, pruning symmetric paths. Uses Chebyshev distance.

---

## Dependencies

### Web version
None — runs in any modern browser (Chrome, Firefox, Safari, Edge).

### Python version
- Python 3.10+
- `numpy`
- `pygame`
- `pyyaml`

```bash
pip install numpy pygame pyyaml
```

---

## Deploying to GitHub Pages

1. Push this repo to GitHub.
2. Go to **Settings → Pages**.
3. Set **Source** to the branch (e.g. `main`) and folder to `/ (root)`.
4. The site will be available at
   `https://<username>.github.io/<repo>/web/`.

Alternatively, set the folder to `/web` to serve the web app at the
repo root URL.

---

## CLI Reference

```
usage: grid_planner.py [-h] [--algorithm {bfs,dfs,best_first,dijkstra,astar,jps}]
                       [--rows ROWS] [--cols COLS] [--start ROW,COL]
                       [--goal ROW,COL] [--obstacle_pct PCT] [--seed SEED]

options:
  --algorithm, -a   Search algorithm (default: from config.yaml)
  --rows            Number of rows
  --cols            Number of columns
  --start           Start cell as row,col
  --goal            Goal cell as row,col (default: bottom-right corner)
  --obstacle_pct    Fraction of obstacle cells [0, 1)
  --seed            Random seed for obstacle placement
```
