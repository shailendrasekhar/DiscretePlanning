/* ===================================================================
   Search Algorithms – Generator-based for live animation
   ===================================================================
   Each algorithm is a JS generator function (function*) that yields
   { current, visited, frontier, path } state snapshots.
   Sets are encoded as JS Set of "r,c" strings for fast lookup.
   =================================================================== */

// ── Helpers ──────────────────────────────────────────────────────────

function key(r, c) { return `${r},${c}`; }

function reconstructPath(cameFrom, goal) {
  const path = [];
  let k = key(goal[0], goal[1]);
  while (k != null) {
    const [r, c] = k.split(",").map(Number);
    path.push([r, c]);
    k = cameFrom.get(k) ?? null;
  }
  path.reverse();
  return path;
}

/**
 * Manhattan distance.
 */
function manhattan(a, b) {
  return Math.abs(a[0] - b[0]) + Math.abs(a[1] - b[1]);
}

/**
 * Chebyshev distance (for 8-connected).
 */
function chebyshev(a, b) {
  return Math.max(Math.abs(a[0] - b[0]), Math.abs(a[1] - b[1]));
}

// ── Simple min-heap (priority queue) ─────────────────────────────────

class MinHeap {
  constructor() { this.data = []; }
  get size() { return this.data.length; }
  push(priority, item) {
    this.data.push({ p: priority, v: item });
    this._up(this.data.length - 1);
  }
  pop() {
    const top = this.data[0];
    const last = this.data.pop();
    if (this.data.length > 0) { this.data[0] = last; this._down(0); }
    return top.v;
  }
  _up(i) {
    while (i > 0) {
      const parent = (i - 1) >> 1;
      if (this.data[i].p >= this.data[parent].p) break;
      [this.data[i], this.data[parent]] = [this.data[parent], this.data[i]];
      i = parent;
    }
  }
  _down(i) {
    const n = this.data.length;
    while (true) {
      let smallest = i;
      const l = 2 * i + 1, r = 2 * i + 2;
      if (l < n && this.data[l].p < this.data[smallest].p) smallest = l;
      if (r < n && this.data[r].p < this.data[smallest].p) smallest = r;
      if (smallest === i) break;
      [this.data[i], this.data[smallest]] = [this.data[smallest], this.data[i]];
      i = smallest;
    }
  }
}

// =====================================================================
// 1. BFS
// =====================================================================

function* bfsGen(grid) {
  const start = grid.start, goal = grid.goal;
  const sk = key(...start), gk = key(...goal);
  const queue = [start];
  const cameFrom = new Map([[sk, undefined]]);
  const visited = new Set();
  let head = 0;

  while (head < queue.length) {
    const current = queue[head++];
    const ck = key(...current);
    visited.add(ck);

    const frontier = new Set();
    for (let i = head; i < queue.length; i++) frontier.add(key(...queue[i]));

    yield { current, visited: new Set(visited), frontier };

    if (ck === gk) {
      yield { current, visited: new Set(visited), frontier, path: reconstructPath(cameFrom, goal) };
      return;
    }

    for (const [nr, nc] of grid.neighbours4(...current)) {
      const nk = key(nr, nc);
      if (!cameFrom.has(nk)) {
        cameFrom.set(nk, ck);
        queue.push([nr, nc]);
      }
    }
  }

  yield { current: null, visited: new Set(visited), frontier: new Set() };
}

// =====================================================================
// 2. DFS
// =====================================================================

function* dfsGen(grid) {
  const start = grid.start, goal = grid.goal;
  const sk = key(...start), gk = key(...goal);
  const stack = [start];
  const cameFrom = new Map([[sk, undefined]]);
  const visited = new Set();

  while (stack.length > 0) {
    const current = stack.pop();
    const ck = key(...current);
    visited.add(ck);

    const frontier = new Set();
    for (const s of stack) frontier.add(key(...s));

    yield { current, visited: new Set(visited), frontier };

    if (ck === gk) {
      yield { current, visited: new Set(visited), frontier, path: reconstructPath(cameFrom, goal) };
      return;
    }

    for (const [nr, nc] of grid.neighbours4(...current)) {
      const nk = key(nr, nc);
      if (!cameFrom.has(nk)) {
        cameFrom.set(nk, ck);
        stack.push([nr, nc]);
      }
    }
  }

  yield { current: null, visited: new Set(visited), frontier: new Set() };
}

// =====================================================================
// 3. Best-First Search (Greedy)
// =====================================================================

function* bestFirstGen(grid) {
  const start = grid.start, goal = grid.goal;
  const sk = key(...start), gk = key(...goal);

  const heap = new MinHeap();
  heap.push(manhattan(start, goal), start);
  const cameFrom = new Map([[sk, undefined]]);
  const visited = new Set();
  const inOpen = new Set([sk]);

  while (heap.size > 0) {
    const current = heap.pop();
    const ck = key(...current);
    inOpen.delete(ck);
    visited.add(ck);

    yield { current, visited: new Set(visited), frontier: new Set(inOpen) };

    if (ck === gk) {
      yield { current, visited: new Set(visited), frontier: new Set(inOpen), path: reconstructPath(cameFrom, goal) };
      return;
    }

    for (const [nr, nc] of grid.neighbours4(...current)) {
      const nk = key(nr, nc);
      if (!cameFrom.has(nk)) {
        cameFrom.set(nk, ck);
        heap.push(manhattan([nr, nc], goal), [nr, nc]);
        inOpen.add(nk);
      }
    }
  }

  yield { current: null, visited: new Set(visited), frontier: new Set() };
}

// =====================================================================
// 4. Dijkstra
// =====================================================================

function* dijkstraGen(grid) {
  const start = grid.start, goal = grid.goal;
  const sk = key(...start), gk = key(...goal);

  const dist = new Map([[sk, 0]]);
  const cameFrom = new Map([[sk, undefined]]);
  const heap = new MinHeap();
  heap.push(0, start);
  const closed = new Set();
  const inOpen = new Set([sk]);

  while (heap.size > 0) {
    const current = heap.pop();
    const ck = key(...current);
    if (closed.has(ck)) continue;
    closed.add(ck);
    inOpen.delete(ck);

    yield { current, visited: new Set(closed), frontier: new Set(inOpen) };

    if (ck === gk) {
      yield { current, visited: new Set(closed), frontier: new Set(inOpen), path: reconstructPath(cameFrom, goal) };
      return;
    }

    const d = dist.get(ck);
    for (const [nr, nc] of grid.neighbours4(...current)) {
      const nk = key(nr, nc);
      if (closed.has(nk)) continue;
      const nd = d + 1;
      if (nd < (dist.get(nk) ?? Infinity)) {
        dist.set(nk, nd);
        cameFrom.set(nk, ck);
        heap.push(nd, [nr, nc]);
        inOpen.add(nk);
      }
    }
  }

  yield { current: null, visited: new Set(closed), frontier: new Set() };
}

// =====================================================================
// 5. A*
// =====================================================================

function* astarGen(grid) {
  const start = grid.start, goal = grid.goal;
  const sk = key(...start), gk = key(...goal);

  const gScore = new Map([[sk, 0]]);
  const cameFrom = new Map([[sk, undefined]]);
  const heap = new MinHeap();
  heap.push(manhattan(start, goal), start);
  const closed = new Set();
  const inOpen = new Set([sk]);

  while (heap.size > 0) {
    const current = heap.pop();
    const ck = key(...current);
    if (closed.has(ck)) continue;
    closed.add(ck);
    inOpen.delete(ck);

    yield { current, visited: new Set(closed), frontier: new Set(inOpen) };

    if (ck === gk) {
      yield { current, visited: new Set(closed), frontier: new Set(inOpen), path: reconstructPath(cameFrom, goal) };
      return;
    }

    const g = gScore.get(ck);
    for (const [nr, nc] of grid.neighbours4(...current)) {
      const nk = key(nr, nc);
      if (closed.has(nk)) continue;
      const ng = g + 1;
      if (ng < (gScore.get(nk) ?? Infinity)) {
        gScore.set(nk, ng);
        cameFrom.set(nk, ck);
        heap.push(ng + manhattan([nr, nc], goal), [nr, nc]);
        inOpen.add(nk);
      }
    }
  }

  yield { current: null, visited: new Set(closed), frontier: new Set() };
}

// =====================================================================
// 6. Jump Point Search (JPS) – 8-connected
// =====================================================================

function _sign(x) { return (x > 0) - (x < 0); }

function _jump(grid, r, c, dr, dc, goal) {
  const nr = r + dr, nc = c + dc;
  if (!grid.walkable(nr, nc)) return null;
  if (nr === goal[0] && nc === goal[1]) return [nr, nc];

  if (dr !== 0 && dc !== 0) {
    // Diagonal
    if ((!grid.walkable(nr - dr, nc)) && grid.walkable(nr - dr, nc + dc)) return [nr, nc];
    if ((!grid.walkable(nr, nc - dc)) && grid.walkable(nr + dr, nc - dc)) return [nr, nc];
    if (_jump(grid, nr, nc, dr, 0, goal) !== null) return [nr, nc];
    if (_jump(grid, nr, nc, 0, dc, goal) !== null) return [nr, nc];
  } else if (dr !== 0) {
    // Vertical
    if ((!grid.walkable(nr, nc - 1)) && grid.walkable(nr + dr, nc - 1)) return [nr, nc];
    if ((!grid.walkable(nr, nc + 1)) && grid.walkable(nr + dr, nc + 1)) return [nr, nc];
  } else {
    // Horizontal
    if ((!grid.walkable(nr - 1, nc)) && grid.walkable(nr - 1, nc + dc)) return [nr, nc];
    if ((!grid.walkable(nr + 1, nc)) && grid.walkable(nr + 1, nc + dc)) return [nr, nc];
  }

  // Diagonal: must be able to continue
  if (dr !== 0 && dc !== 0) {
    if (!grid.walkable(nr + dr, nc) && !grid.walkable(nr, nc + dc)) return null;
  }

  return _jump(grid, nr, nc, dr, dc, goal);
}

function _prunedDirs(grid, r, c, dr, dc) {
  const dirs = [];
  if (dr !== 0 && dc !== 0) {
    dirs.push([dr, dc], [dr, 0], [0, dc]);
    if (!grid.walkable(r - dr, c)) dirs.push([-dr, dc]);
    if (!grid.walkable(r, c - dc)) dirs.push([dr, -dc]);
  } else if (dr !== 0) {
    dirs.push([dr, 0]);
    if (!grid.walkable(r, c - 1)) dirs.push([dr, -1]);
    if (!grid.walkable(r, c + 1)) dirs.push([dr, 1]);
  } else {
    dirs.push([0, dc]);
    if (!grid.walkable(r - 1, c)) dirs.push([-1, dc]);
    if (!grid.walkable(r + 1, c)) dirs.push([1, dc]);
  }
  return dirs;
}

function _identifySuccessors(grid, current, cameFrom, goal) {
  const [r, c] = current;
  const ck = key(r, c);
  const parentKey = cameFrom.get(ck);
  let directions;

  if (parentKey != null) {
    const [pr, pc] = parentKey.split(",").map(Number);
    const dr = _sign(r - pr), dc = _sign(c - pc);
    directions = _prunedDirs(grid, r, c, dr, dc);
  } else {
    directions = [
      [-1, 0], [1, 0], [0, -1], [0, 1],
      [-1, -1], [-1, 1], [1, -1], [1, 1],
    ];
  }

  const successors = [];
  for (const [dr, dc] of directions) {
    const jp = _jump(grid, r, c, dr, dc, goal);
    if (jp !== null) successors.push(jp);
  }
  return successors;
}

function _buildFullPath(cameFrom, goal) {
  const jpChain = [];
  let k = key(goal[0], goal[1]);
  while (k != null) {
    const [r, c] = k.split(",").map(Number);
    jpChain.push([r, c]);
    k = cameFrom.get(k) ?? null;
  }
  jpChain.reverse();

  if (jpChain.length <= 1) return jpChain;

  const fullPath = [jpChain[0]];
  for (let i = 1; i < jpChain.length; i++) {
    let [r, c] = jpChain[i - 1];
    const [tr, tc] = jpChain[i];
    while (r !== tr || c !== tc) {
      r += _sign(tr - r);
      c += _sign(tc - c);
      fullPath.push([r, c]);
    }
  }
  return fullPath;
}

function* jpsGen(grid) {
  const start = grid.start, goal = grid.goal;
  const sk = key(...start), gk = key(...goal);

  const gScore = new Map([[sk, 0]]);
  const cameFrom = new Map([[sk, undefined]]);
  const heap = new MinHeap();
  heap.push(chebyshev(start, goal), start);
  const closed = new Set();
  const inOpen = new Set([sk]);

  while (heap.size > 0) {
    const current = heap.pop();
    const ck = key(...current);
    if (closed.has(ck)) continue;
    closed.add(ck);
    inOpen.delete(ck);

    yield { current, visited: new Set(closed), frontier: new Set(inOpen) };

    if (ck === gk) {
      yield { current, visited: new Set(closed), frontier: new Set(inOpen), path: _buildFullPath(cameFrom, goal) };
      return;
    }

    const g = gScore.get(ck);
    for (const jp of _identifySuccessors(grid, current, cameFrom, goal)) {
      const jk = key(...jp);
      if (closed.has(jk)) continue;
      const tentG = g + chebyshev(current, jp);
      if (tentG < (gScore.get(jk) ?? Infinity)) {
        gScore.set(jk, tentG);
        cameFrom.set(jk, ck);
        heap.push(tentG + chebyshev(jp, goal), jp);
        inOpen.add(jk);
      }
    }
  }

  yield { current: null, visited: new Set(closed), frontier: new Set() };
}

// ── Dispatch ─────────────────────────────────────────────────────────

const ALGORITHMS = {
  bfs:        { fn: bfsGen,      label: "BFS" },
  dfs:        { fn: dfsGen,      label: "DFS" },
  best_first: { fn: bestFirstGen, label: "Best-First" },
  dijkstra:   { fn: dijkstraGen, label: "Dijkstra" },
  astar:      { fn: astarGen,    label: "A*" },
  jps:        { fn: jpsGen,      label: "JPS" },
};
