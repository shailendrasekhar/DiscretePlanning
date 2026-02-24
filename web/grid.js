/* ===================================================================
   Grid – 2-D occupancy grid with random obstacles
   =================================================================== */

const FREE = 0;
const OBSTACLE = 1;
const START = 2;
const GOAL = 3;

/**
 * Seeded pseudo-random number generator (Mulberry32).
 * If seed is null/undefined, uses Math.random instead.
 */
function makeRng(seed) {
  if (seed == null) return Math.random;
  let s = seed | 0;
  return function () {
    s |= 0;
    s = (s + 0x6d2b79f5) | 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/**
 * Fisher-Yates shuffle using supplied rng.
 */
function shuffle(arr, rng) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

class Grid {
  /**
   * @param {number} rows
   * @param {number} cols
   * @param {[number,number]} start
   * @param {[number,number]} goal
   * @param {number} obstaclePct
   * @param {number|null} seed
   */
  constructor(rows, cols, start, goal, obstaclePct, seed) {
    this.rows = rows;
    this.cols = cols;
    this.start = start;
    this.goal = goal;
    this.cells = new Uint8Array(rows * cols); // all FREE

    const rng = makeRng(seed);
    const total = rows * cols;
    const nObstacles = Math.floor(total * obstaclePct);

    // Build candidate list (skip start & goal)
    const candidates = [];
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        if ((r === start[0] && c === start[1]) ||
            (r === goal[0] && c === goal[1])) continue;
        candidates.push(r * cols + c);
      }
    }
    shuffle(candidates, rng);
    for (let i = 0; i < Math.min(nObstacles, candidates.length); i++) {
      this.cells[candidates[i]] = OBSTACLE;
    }

    // Mark start & goal
    this.cells[start[0] * cols + start[1]] = START;
    this.cells[goal[0] * cols + goal[1]] = GOAL;
  }

  get(r, c) {
    return this.cells[r * this.cols + c];
  }

  isObstacle(r, c) {
    return this.cells[r * this.cols + c] === OBSTACLE;
  }

  inBounds(r, c) {
    return r >= 0 && r < this.rows && c >= 0 && c < this.cols;
  }

  walkable(r, c) {
    return this.inBounds(r, c) && !this.isObstacle(r, c);
  }

  /** 4-connected walkable neighbours */
  neighbours4(r, c) {
    const nbrs = [];
    for (const [dr, dc] of [[-1, 0], [1, 0], [0, -1], [0, 1]]) {
      const nr = r + dr, nc = c + dc;
      if (this.walkable(nr, nc)) nbrs.push([nr, nc]);
    }
    return nbrs;
  }

  /** 8-connected walkable neighbours (no corner-cutting) */
  neighbours8(r, c) {
    const nbrs = [];
    for (const [dr, dc] of [
      [-1, 0], [1, 0], [0, -1], [0, 1],
      [-1, -1], [-1, 1], [1, -1], [1, 1],
    ]) {
      const nr = r + dr, nc = c + dc;
      if (!this.walkable(nr, nc)) continue;
      // diagonal: require both cardinal neighbours free
      if (dr !== 0 && dc !== 0) {
        if (this.isObstacle(r + dr, c) || this.isObstacle(r, c + dc)) continue;
      }
      nbrs.push([nr, nc]);
    }
    return nbrs;
  }

  summary() {
    let nObs = 0;
    for (let i = 0; i < this.cells.length; i++) {
      if (this.cells[i] === OBSTACLE) nObs++;
    }
    const total = this.rows * this.cols;
    return `Grid ${this.rows}×${this.cols} | Start (${this.start}) | Goal (${this.goal}) | Obstacles ${nObs}/${total} (${(100 * nObs / total).toFixed(1)}%)`;
  }
}
