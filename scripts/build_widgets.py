"""
Assembles StreamElements-custom-widget-ready HTML/CSS/JS bundles from the
local dev alert files.

Why this exists: the local alert .html files use ES module <script
type="module"> + import/export to share code (theme/path-motion.js,
theme/knot-border.js, etc.) and reference assets via relative paths
(../assets/...). That's correct for how OBS loads a local file directly, but
a StreamElements custom widget runs your pasted HTML/CSS/JS inside THEIR
page, with no access to our local files and (per their docs/examples) no
indication they evaluate the JS tab as a module -- so imports and relative
paths would both break. This script inlines the shared theme JS (stripping
`export`) and rewrites every relative asset path to its public GitHub Pages
URL, producing one self-contained HTML/CSS/JS bundle per alert ready to
paste into StreamElements' three code tabs.

Run after any change to alerts/*.html or theme/*.js and re-paste into SE.
"""
import re
from pathlib import Path

ROOT = Path("/home/ndot/Work/twitch-alerts")
BASE_URL = "https://imndot.github.io/twitch-alerts"
OUT_DIR = ROOT / "widget"
OUT_DIR.mkdir(exist_ok=True)

def strip_exports(src: str) -> str:
    return re.sub(r"^export (function|const)", r"\1", src, flags=re.MULTILINE)

def rewrite_paths(src: str) -> str:
    # ../assets/x -> https://.../assets/x , ../theme/x -> https://.../theme/x
    src = re.sub(r"\.\./(assets|theme)/", f"{BASE_URL}/\\1/", src)
    return src

TOKENS_CSS = (ROOT / "theme/tokens.css").read_text()
PATH_MOTION = strip_exports((ROOT / "theme/path-motion.js").read_text())
KNOT_BORDER = strip_exports(rewrite_paths((ROOT / "theme/knot-border.js").read_text()))
KNOT_PATH_DATA = strip_exports((ROOT / "theme/knot-path-data.js").read_text())

ALERTS = {
    "follow": {"needs_knot": True},
    "sub": {"needs_knot": True},
    "raid": {"needs_knot": True},
    "gift": {"needs_knot": False},
}

def extract(html: str, tag: str) -> str:
    m = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", html, re.DOTALL)
    return m.group(1).strip() if m else ""

def build(name: str, needs_knot: bool):
    html = (ROOT / f"alerts/{name}.html").read_text()

    # tokens.css is normally pulled in via a <link> in <head>, which this
    # script never looks at -- without inlining it here, every var(--teal)
    # etc. in the alert's own CSS would resolve to nothing in the widget.
    css = TOKENS_CSS + "\n\n" + extract(html, "style")

    # Body content minus the script tag itself (HTML tab).
    body_full = extract(html, "body")
    body_html = re.sub(r"<script.*?</script>", "", body_full, flags=re.DOTALL).strip()
    body_html = rewrite_paths(body_html)

    # Inline script: drop the import lines, rewrite remaining asset paths.
    m = re.search(r'<script type="module">(.*?)</script>', html, re.DOTALL)
    script = m.group(1).strip() if m else ""
    script_lines = [
        line for line in script.splitlines()
        if not re.match(r"\s*import ", line)
    ]
    script = "\n".join(script_lines)
    script = rewrite_paths(script)

    js_parts = [PATH_MOTION]
    if needs_knot:
        js_parts += [KNOT_BORDER, KNOT_PATH_DATA]
    js_parts.append(script.strip())
    js = "\n\n".join(js_parts)

    (OUT_DIR / f"{name}.css.txt").write_text(css + "\n")
    (OUT_DIR / f"{name}.html.txt").write_text(body_html + "\n")
    (OUT_DIR / f"{name}.js.txt").write_text(js + "\n")
    print(f"built widget/{name}.{{css,html,js}}.txt")

for name, cfg in ALERTS.items():
    build(name, cfg["needs_knot"])
