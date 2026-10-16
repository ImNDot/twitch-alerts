const SVG_NS = 'http://www.w3.org/2000/svg';

function el(tag, attrs) {
  const node = document.createElementNS(SVG_NS, tag);
  for (const k in attrs) node.setAttribute(k, attrs[k]);
  return node;
}

// Places the real Celtic N-knot artwork at its computed position/scale and
// returns the invisible centerline <path> that traces its outer silhouette
// (with a halo margin) — use with makePathSampler() to walk characters and
// shapes around the actual knot, not an abstract border shape.
//
// `data` is one of the generated knot-path-data modules (KNOT_CENTERLINE_D +
// EMBLEM_PLACEMENT) — pass theme/knot-path-data.js for the compact alert
// placement, or theme/scene-knot-path-data.js for the bigger scene placement.
export function buildEmblem(root, svgEl, data, { glow = true, imgSrc = '../assets/celtic-n-knot.png' } = {}) {
  const { KNOT_CENTERLINE_D, EMBLEM_PLACEMENT } = data;
  const img = document.createElement('img');
  img.src = imgSrc;
  img.alt = '';
  img.style.position = 'absolute';
  img.style.left = `${EMBLEM_PLACEMENT.left}px`;
  img.style.top = `${EMBLEM_PLACEMENT.top}px`;
  img.style.width = `${EMBLEM_PLACEMENT.width}px`;
  img.style.height = `${EMBLEM_PLACEMENT.height}px`;
  if (glow) img.style.filter = 'drop-shadow(0 0 14px rgba(47,217,201,0.35))';
  root.appendChild(img);

  const centerline = el('path', { d: KNOT_CENTERLINE_D, fill: 'none', stroke: 'none' });
  svgEl.appendChild(centerline);
  return centerline;
}
