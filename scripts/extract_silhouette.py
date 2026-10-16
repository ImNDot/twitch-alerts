import math
import numpy as np
from PIL import Image

SRC = "/home/ndot/Work/twitch-alerts/assets/source/celtic-n-knot.png"
im = Image.open(SRC).convert("RGB")
W0, H0 = im.size
DS = 420  # working resolution for the scan (downsampled for speed/smoothing)
small = im.resize((DS, DS), Image.BILINEAR)
arr = np.asarray(small).astype(np.float32)
brightness = arr.max(axis=2)  # per-pixel max(R,G,B)

THRESH = 55  # ignore faint sparkle/flare streaks, keep the solid knotwork
mask = brightness > THRESH

ys, xs = np.nonzero(mask)
cx, cy = xs.mean(), ys.mean()
print("centroid (downsampled px):", cx, cy, "of", DS)

N_ANGLES = 360
R_MAX = DS * 0.75
R_STEPS = 500
angles = np.linspace(0, 2*math.pi, N_ANGLES, endpoint=False)
radii = np.zeros(N_ANGLES)

r_samples = np.linspace(R_MAX, 1, R_STEPS)
for i, a in enumerate(angles):
    dx, dy = math.cos(a), math.sin(a)
    xs_r = (cx + r_samples*dx).round().astype(int)
    ys_r = (cy + r_samples*dy).round().astype(int)
    valid = (xs_r >= 0) & (xs_r < DS) & (ys_r >= 0) & (ys_r < DS)
    hit_r = 0.0
    xs_v = xs_r[valid]; ys_v = ys_r[valid]; r_v = r_samples[valid]
    hits = mask[ys_v, xs_v]
    if hits.any():
        hit_r = r_v[hits.argmax()]  # r_v is descending, argmax of bool finds first True
    radii[i] = hit_r

# circular smoothing (moving average) to remove pixel/flare noise, keep the 4-point star shape
def circ_smooth(a, win):
    k = win // 2
    out = np.zeros_like(a)
    n = len(a)
    for i in range(n):
        idx = [(i + j) % n for j in range(-k, k+1)]
        out[i] = a[idx].mean()
    return out

radii_smooth = circ_smooth(radii, 7)

# scale back up to full-res image coordinates
scale_to_full = W0 / DS
radii_full = radii_smooth * scale_to_full
cx_full, cy_full = cx * scale_to_full, cy * scale_to_full

MARGIN = 20  # px halo outside the art, in full-res image space
radii_path = radii_full + MARGIN

pts_image_space = []
for a, r in zip(angles, radii_path):
    x = cx_full + r*math.cos(a)
    y = cy_full + r*math.sin(a)
    pts_image_space.append((x, y))

maxr = max(radii_path)
print("centroid full-res:", cx_full, cy_full, "max radius (with margin):", maxr)

with open("/tmp/silhouette_debug.txt", "w") as f:
    f.write(f"{cx_full} {cy_full} {maxr}\n")
    for x, y in pts_image_space:
        f.write(f"{x} {y}\n")
