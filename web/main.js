/* ===================================================================
   Main – wires up the UI controls, grid, algorithms, and visualiser
   =================================================================== */

(function () {
  "use strict";

  // ── DOM refs ───────────────────────────────────────────────────────
  const $algorithm    = document.getElementById("algorithm");
  const $rows         = document.getElementById("rows");
  const $cols         = document.getElementById("cols");
  const $startRow     = document.getElementById("startRow");
  const $startCol     = document.getElementById("startCol");
  const $goalRow      = document.getElementById("goalRow");
  const $goalCol      = document.getElementById("goalCol");
  const $obstaclePct  = document.getElementById("obstaclePct");
  const $seed         = document.getElementById("seed");
  const $delay        = document.getElementById("delay");
  const $stepsPerFrame = document.getElementById("stepsPerFrame");
  const $pathDelay    = document.getElementById("pathDelay");
  const $btnRun       = document.getElementById("btnRun");
  const $btnStop      = document.getElementById("btnStop");
  const $btnReset     = document.getElementById("btnReset");
  const $status       = document.getElementById("status");
  const $canvas       = document.getElementById("gridCanvas");

  let animationId = null;   // requestAnimationFrame id
  let stopFlag = false;
  let vis = null;

  // ── Helpers ────────────────────────────────────────────────────────
  function readParams() {
    const rows = parseInt($rows.value, 10) || 20;
    const cols = parseInt($cols.value, 10) || 20;
    return {
      algorithm:    $algorithm.value,
      rows,
      cols,
      start:        [parseInt($startRow.value, 10) || 0,
                     parseInt($startCol.value, 10) || 0],
      goal:         [parseInt($goalRow.value, 10)  ?? (rows - 1),
                     parseInt($goalCol.value, 10)  ?? (cols - 1)],
      obstaclePct:  parseFloat($obstaclePct.value) || 0.2,
      seed:         $seed.value === "" ? null : parseInt($seed.value, 10),
      delay:        parseInt($delay.value, 10)          ?? 30,
      stepsPerFrame: parseInt($stepsPerFrame.value, 10) ?? 1,
      pathDelay:    parseInt($pathDelay.value, 10)      ?? 50,
    };
  }

  function setStatus(msg) { $status.textContent = msg; }

  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // ── Goal auto-update when rows/cols change ─────────────────────────
  function syncGoalDefaults() {
    const rows = parseInt($rows.value, 10) || 20;
    const cols = parseInt($cols.value, 10) || 20;
    $goalRow.value = rows - 1;
    $goalCol.value = cols - 1;
  }
  $rows.addEventListener("change", syncGoalDefaults);
  $cols.addEventListener("change", syncGoalDefaults);

  // ── Draw initial empty grid ────────────────────────────────────────
  function drawInitialGrid() {
    const p = readParams();
    const grid = new Grid(p.rows, p.cols, p.start, p.goal, p.obstaclePct, p.seed);
    vis = new Visualiser($canvas, grid);
    vis.drawBase();
    setStatus(grid.summary());
  }

  // ── Run ────────────────────────────────────────────────────────────
  async function run() {
    stop();                       // cancel any running animation

    const p = readParams();
    const algInfo = ALGORITHMS[p.algorithm];
    if (!algInfo) { setStatus("Unknown algorithm!"); return; }

    let grid;
    try {
      grid = new Grid(p.rows, p.cols, p.start, p.goal, p.obstaclePct, p.seed);
    } catch (e) {
      setStatus(`Error: ${e.message}`);
      return;
    }

    vis = new Visualiser($canvas, grid);
    vis.drawBase();
    setStatus(`Running ${algInfo.label}…`);

    const gen = algInfo.fn(grid);
    stopFlag = false;
    let lastState = { current: null, visited: new Set(), frontier: new Set() };
    let stepsTotal = 0;

    // ── Search animation ──
    while (!stopFlag) {
      let exhausted = false;
      for (let i = 0; i < p.stepsPerFrame; i++) {
        const { value, done } = gen.next();
        if (done) { exhausted = true; break; }
        lastState = value;
        stepsTotal++;
      }

      vis.drawState(lastState);

      if (lastState.path || exhausted) break;

      // Yield to browser
      await sleep(p.delay);
    }

    if (stopFlag) { setStatus("Stopped."); return; }

    // ── Path animation ──
    if (lastState.path) {
      const partial = [];
      for (const cell of lastState.path) {
        if (stopFlag) break;
        partial.push(cell);
        vis.drawState(lastState, partial);
        await sleep(p.pathDelay);
      }
      setStatus(`${algInfo.label} | Path length: ${lastState.path.length} | Expanded: ${stepsTotal} nodes`);
    } else {
      setStatus(`${algInfo.label} | No path found! | Expanded: ${stepsTotal} nodes`);
    }
  }

  function stop() {
    stopFlag = true;
    if (animationId) { cancelAnimationFrame(animationId); animationId = null; }
  }

  function reset() {
    stop();
    drawInitialGrid();
  }

  // ── Bind buttons ───────────────────────────────────────────────────
  $btnRun.addEventListener("click", run);
  $btnStop.addEventListener("click", stop);
  $btnReset.addEventListener("click", reset);

  // ── Keyboard shortcut: Enter to run ────────────────────────────────
  document.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && document.activeElement.tagName !== "BUTTON") run();
    if (e.key === "Escape") stop();
  });

  // ── Initial draw ───────────────────────────────────────────────────
  drawInitialGrid();
})();
