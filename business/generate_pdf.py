#!/usr/bin/env python3
"""Compile all docs/business/*.md into a single PDF.

Usage:
    pixi run python docs/business/generate_pdf.py [--out PATH]

Builds a single styled HTML from every business-model markdown (README + all
<type>/ option docs) and prints it to PDF via headless Chrome.

Requirements:
    python -m pip install markdown
    google-chrome or chromium available on PATH (or set CHROME_BIN).
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

BASE = Path(__file__).resolve().parent

# Ordered list of (type_label, [relative files]) preserving folder grouping.
ORDER: list[tuple[str, list[str]]] = [
    ("Business Models - Overview", ["README.md"]),
    ("Market Research", ["MARKET_RESEARCH.md"]),
    ("Subscription", ["subscription/personal-trainer-tiers.md", "subscription/coach-gym-saas.md", "subscription/deep-report-upgrade.md"]),
    ("API / Usage-based", ["api/pay-per-query-chatbot.md", "api/b2b-video-analysis-api.md"]),
    ("Per-service", ["per-service/pay-per-video-credits.md", "per-service/grade-assessment.md"]),
    ("Licensing", ["licensing/white-label-license.md", "licensing/dataset-library-license.md"]),
    ("Marketplace", ["marketplace/coach-leadgen.md", "marketplace/verified-athlete-profiles.md"]),
    ("Events", ["events/virtual-challenges.md"]),
]

CSS = """
@page { size: A4; margin: 1.6cm 1.6cm 1.8cm 1.6cm; }
body { font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; font-size: 10.5pt;
       line-height: 1.5; color: #1f2328; }
h1 { font-size: 17pt; color: #0d4f8b; border-bottom: 2px solid #0d4f8b;
     padding-bottom: 4pt; margin: 0 0 10pt 0; }
h2 { font-size: 13.5pt; color: #0d4f8b; margin-top: 14pt; }
h3 { font-size: 12pt; color: #333; }
table { border-collapse: collapse; width: 100%; margin: 8pt 0; page-break-inside: avoid; }
th, td { border: 1px solid #c5cdd5; padding: 4pt 6pt; text-align: left; font-size: 9.5pt; }
th { background: #eef3f8; }
code { background: #f2f4f6; padding: 0 3pt; border-radius: 3pt; font-size: 9pt; }
blockquote { border-left: 3px solid #0d4f8b; margin: 6pt 0; padding: 2pt 10pt;
             color: #556; background: #f8fafc; }
.doc { page-break-before: always; }
.doc:first-of-type { page-break-before: auto; }
.toc-type { margin: 8pt 0 2pt 0; color: #0d4f8b; font-size: 11pt; }
ul { margin: 4pt 0; }
li { margin: 2pt 0; }
a { color: #0d4f8b; text-decoration: none; }
hr { border: none; border-top: 1px solid #d5dbe2; margin: 12pt 0; }
"""


def slug(path: str) -> str:
    return path.split("/")[-1].replace(".md", "")


def split_title(raw: str) -> tuple[str | None, str]:
    m = re.search(r"^# (.+)$", raw, flags=re.M)
    title = m.group(1).strip() if m else ""
    if " — " in title:
        code, rest = title.split(" — ", 1)
        return code, rest
    return None, title


def find_chrome() -> str:
    env = os.environ.get("CHROME_BIN")
    if env and Path(env).exists():
        return env
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        found = shutil.which(name)
        if found:
            return found
    raise SystemExit("No Chrome/Chromium found. Install one or set CHROME_BIN.")


def render_html(only: str | None = None) -> str:
    toc: list[str] = []
    body: list[str] = []
    for label, files in ORDER:
        if only is not None:
            files = [f for f in files if slug(f) == only or f == only]
            if not files:
                continue
            label = "Market Research" if only == "MARKET_RESEARCH.md" else label
        toc.append(f"<h3 class='toc-type'>{label}</h3>")
        for f in files:
            raw = (BASE / f).read_text(encoding="utf-8")
            code, title = split_title(raw)
            sid = slug(f)
            label_text = f"[{code}] {title}" if code else title
            toc.append(f"<li><a href='#{sid}'>{label_text}</a></li>")
            body_md = re.sub(r"^# .+\n", "", raw, count=1, flags=re.M)
            html = markdown.markdown(
                body_md,
                extensions=["tables", "fenced_code", "sane_lists", "nl2br"],
            )
            body.append(f"<div class='doc' id='{sid}'><h1>{label_text}</h1>{html}</div>")

    cover_title = "pole-ai — Business Model Options"
    if only is not None and len(body) == 1:
        cover_title = "pole-ai — Market Research" if only == "MARKET_RESEARCH.md" else label_text

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>{cover_title}</title>
<style>{CSS}</style></head>
<body>
<div id='toc'>
<h1 style='font-size:20pt'>{cover_title}</h1>
<p style='color:#556;font-size:10pt'>Monetization strategies for the Athlete Trick Identification System.<br>
Compiled from <code>docs/business/</code> &middot; {len(body)} document{'s' if len(body) != 1 else ''}.</p>
{'<br>'.join(toc)}
<hr>
</div>
{''.join(body)}
</body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Build docs/business PDF.")
    parser.add_argument("--out", default=str(BASE / "pole-ai-business-models.pdf"))
    parser.add_argument(
        "--only",
        help="Build a single-doc PDF for one file (e.g. MARKET_RESEARCH.md).",
    )
    args = parser.parse_args()

    chrome = find_chrome()
    with tempfile.TemporaryDirectory() as tmp:
        html_path = Path(tmp) / "business.html"
        html_path.write_text(render_html(args.only), encoding="utf-8")
        subprocess.run(
            [
                chrome, "--headless", "--disable-gpu", "--no-sandbox",
                "--no-pdf-header-footer",
                f"--print-to-pdf={args.out}",
                html_path.as_uri(),
            ],
            check=True,
        )
    print(f"PDF written to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())