// Shared helper for moving elements along the knot centerline path.
// Keeps Follow/Sub/Raid from each reimplementing path-walking.

export function makePathSampler(pathEl) {
  const len = pathEl.getTotalLength();
  const eps = Math.max(1, len * 0.002);
  return function sample(frac) {
    const f = ((frac % 1) + 1) % 1;
    const d = f * len;
    const p = pathEl.getPointAtLength(d);
    const p2 = pathEl.getPointAtLength((d + eps) % len);
    const angle = Math.atan2(p2.y - p.y, p2.x - p.x) * 180 / Math.PI;
    return { x: p.x, y: p.y, angle, len };
  };
}

// Positions `el` (expects transform-origin center) at path fraction `frac`,
// facing the direction of travel, with an optional squash pulse near corners.
export function placeOnPath(el, sampler, frac, { scale = 1, flip = false, squash = 0, w = 0, h = 0, rotate = true } = {}) {
  const { x, y, angle } = sampler(frac);
  const faceFlip = flip ? 180 : 0;
  const sx = scale * (1 + squash);
  const sy = scale * (1 - squash * 0.6);
  const cx = x - w / 2;
  const cy = y - h / 2;
  const rot = rotate ? `rotate(${angle}deg)` : '';
  el.style.transform =
    `translate(${cx}px, ${cy}px) ${rot} scaleX(${sx}) scaleY(${sy}) rotate(${faceFlip}deg)`;
}

// Drives a requestAnimationFrame loop for `durationMs`, calling onFrame(t) each tick
// where t goes 0 -> 1 linearly across the whole duration. Returns a cancel function.
export function runTimeline(durationMs, onFrame, onDone) {
  let start = null;
  let raf;
  function frame(ts) {
    if (start === null) start = ts;
    const t = Math.min((ts - start) / durationMs, 1);
    onFrame(t, ts - start);
    if (t < 1) {
      raf = requestAnimationFrame(frame);
    } else if (onDone) {
      onDone();
    }
  }
  raf = requestAnimationFrame(frame);
  return () => cancelAnimationFrame(raf);
}

// A small deterministic wobble (sum of two off-ratio sines) for "alive" motion
// on top of clean path tracking. Call with elapsed ms; returns offsets in [-1,1].
export function makeJitter(seed = 1) {
  const a = 2.1 + seed * 0.37;
  const b = 1.3 + seed * 0.21;
  const pa = seed * 1.7;
  const pb = seed * 2.9;
  return function jitter(elapsedMs) {
    const s = elapsedMs / 1000;
    const nx = Math.sin(s * a + pa) * 0.6 + Math.sin(s * b * 1.9 + pb) * 0.4;
    const ny = Math.cos(s * b + pb) * 0.6 + Math.cos(s * a * 1.3 + pa) * 0.4;
    return { nx, ny };
  };
}

// Builds N trailing "ghost" ancestors of a moving element for a motion-blur trail.
// Returns an array of { el, phaseOffset, opacity } to update each frame alongside the lead.
export function makeTrail(sourceEl, count, { spacingFrac = 0.015, opacityFalloff = 0.55 } = {}) {
  const parent = sourceEl.parentElement;
  const ghosts = [];
  for (let i = 1; i <= count; i++) {
    const ghost = sourceEl.cloneNode(true);
    ghost.removeAttribute('id');
    ghost.style.opacity = String(Math.pow(opacityFalloff, i));
    ghost.style.filter = (ghost.style.filter || '') + ' blur(1.5px)';
    parent.insertBefore(ghost, sourceEl);
    ghosts.push({ el: ghost, phaseOffset: -spacingFrac * i });
  }
  return ghosts;
}
