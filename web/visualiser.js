/* ===================================================================
   Canvas Visualiser – draws the grid and animates search state
   =================================================================== */

class Visualiser {
  /**
   * @param {HTMLCanvasElement} canvas
   * @param {Grid} grid
   * @param {object} opts – { cellSize, colours }
   */
  constructor(canvas, grid, opts = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.grid = grid;

    this.cell = opts.cellSize ?? 30;

    this.colours = Object.assign({
      free:      "#ffffff",
      obstacle:  "#282828",
      start:     "#32cd32",
      goal:      "#ff6347",
      visited:   "#add8e6",
      frontier:  "#ffa500",
      current:   "#ffff00",
      path:      "#1e90ff",
      gridLine:  "#c8c8c8",
      text:      "#ffffff",
    }, opts.colours ?? {});

    // Compute cell size to fit wrapper if needed
    this._fitToWrapper();

    this.width = grid.cols * this.cell;
    this.height = grid.rows * this.cell;
    canvas.width = this.width;
    canvas.height = this.height;
  }

  /** Auto-shrink cell size so canvas fits within its parent. */
  _fitToWrapper() {
    const wrapper = this.canvas.parentElement;
    if (!wrapper) return;
    const maxW = wrapper.clientWidth - 32;
    const maxH = wrapper.clientHeight - 32;
    const maxCellW = Math.floor(maxW / this.grid.cols);
    const maxCellH = Math.floor(maxH / this.grid.rows);
    this.cell = Math.max(4, Math.min(this.cell, maxCellW, maxCellH));
  }

  /** Draw the static base grid (obstacles, start, goal). */
  drawBase() {
    const ctx = this.ctx;
    const g = this.grid;
    const s = this.cell;

    ctx.clearRect(0, 0, this.width, this.height);

    for (let r = 0; r < g.rows; r++) {
      for (let c = 0; c < g.cols; c++) {
        const v = g.get(r, c);
        if (v === OBSTACLE) ctx.fillStyle = this.colours.obstacle;
        else if (v === START) ctx.fillStyle = this.colours.start;
        else if (v === GOAL) ctx.fillStyle = this.colours.goal;
        else ctx.fillStyle = this.colours.free;
        ctx.fillRect(c * s, r * s, s, s);
      }
    }

    // Grid lines
    ctx.strokeStyle = this.colours.gridLine;
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let r = 0; r <= g.rows; r++) {
      ctx.moveTo(0, r * s);
      ctx.lineTo(this.width, r * s);
    }
    for (let c = 0; c <= g.cols; c++) {
      ctx.moveTo(c * s, 0);
      ctx.lineTo(c * s, this.height);
    }
    ctx.stroke();

    // Labels
    this._drawLabel(g.start, "S");
    this._drawLabel(g.goal, "G");
  }

  /** Draw a single search-state overlay on top of the base grid. */
  drawState(state, pathPartial) {
    this.drawBase();

    const ctx = this.ctx;
    const s = this.cell;
    const g = this.grid;
    const sk = key(...g.start), gk = key(...g.goal);

    // Visited
    if (state.visited) {
      ctx.fillStyle = this.colours.visited;
      for (const k of state.visited) {
        if (k === sk || k === gk) continue;
        const [r, c] = k.split(",").map(Number);
        ctx.fillRect(c * s, r * s, s, s);
      }
    }

    // Frontier
    if (state.frontier) {
      ctx.fillStyle = this.colours.frontier;
      for (const k of state.frontier) {
        if (k === sk || k === gk) continue;
        const [r, c] = k.split(",").map(Number);
        ctx.fillRect(c * s, r * s, s, s);
      }
    }

    // Current
    if (state.current) {
      const ck = key(...state.current);
      if (ck !== sk && ck !== gk) {
        ctx.fillStyle = this.colours.current;
        ctx.fillRect(state.current[1] * s, state.current[0] * s, s, s);
      }
    }

    // Path
    const drawPath = pathPartial ?? state.path;
    if (drawPath) {
      ctx.fillStyle = this.colours.path;
      for (const [r, c] of drawPath) {
        const pk = key(r, c);
        if (pk === sk || pk === gk) continue;
        ctx.fillRect(c * s, r * s, s, s);
      }
    }

    // Re-draw start & goal on top
    ctx.fillStyle = this.colours.start;
    ctx.fillRect(g.start[1] * s, g.start[0] * s, s, s);
    ctx.fillStyle = this.colours.goal;
    ctx.fillRect(g.goal[1] * s, g.goal[0] * s, s, s);

    // Grid lines again
    ctx.strokeStyle = this.colours.gridLine;
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let r = 0; r <= g.rows; r++) {
      ctx.moveTo(0, r * s);
      ctx.lineTo(this.width, r * s);
    }
    for (let c = 0; c <= g.cols; c++) {
      ctx.moveTo(c * s, 0);
      ctx.lineTo(c * s, this.height);
    }
    ctx.stroke();

    // Labels
    this._drawLabel(g.start, "S");
    this._drawLabel(g.goal, "G");
  }

  _drawLabel(cell, text) {
    const ctx = this.ctx;
    const s = this.cell;
    const fontSize = Math.max(10, Math.floor(s * 0.55));
    ctx.fillStyle = this.colours.text;
    ctx.font = `bold ${fontSize}px monospace`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(text, cell[1] * s + s / 2, cell[0] * s + s / 2);
  }
}
