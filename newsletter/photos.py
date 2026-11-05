"""Real photos for covers and articles, credited, from whichever provider is available.

Tried in order:
  1. Pexels    (PEXELS_API_KEY)    free licence, credit the photographer
  2. Pixabay   (PIXABAY_API_KEY)   free licence, key at https://pixabay.com/api/docs/ after signing up
  3. Openverse (no key needed)     Creative Commons photos (Flickr, Wikimedia, ...), limited to licences
                                   that allow commercial use and modification; creator + licence credited
Set PHOTO_PROVIDERS (e.g. "pixabay,openverse") to change the order or turn providers off.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterator

import requests

log = logging.getLogger(__name__)
UA = {"User-Agent": "newsletter-automation/1.0 (newsletter photo search)"}


@dataclass
class Photo:
    path: Path
    credit: str      # e.g. "Photo: Jane Doe / Pixabay" or "Photo: Jane Doe, CC BY 2.0, via Openverse"
    page_url: str
    url: str = ""    # direct image URL, so the choice can be pinned in photos.json


def _download(url: str, dest_stem: Path) -> Path:
    img = requests.get(url, headers=UA, timeout=30)
    img.raise_for_status()
    if not img.headers.get("content-type", "").startswith("image/") or len(img.content) < 20_000:
        raise ValueError("not a usable photo")
    path = dest_stem.with_suffix(".jpg" if "jpeg" in img.headers["content-type"] else ".png")
    path.write_bytes(img.content)
    return path


def _pexels(query: str) -> Iterator[tuple[str, str, str]]:
    key = os.getenv("PEXELS_API_KEY")
    if not key:
        return
    r = requests.get("https://api.pexels.com/v1/search", headers={"Authorization": key},
                     params={"query": query, "orientation": "landscape", "per_page": 8, "size": "large"}, timeout=20)
    r.raise_for_status()
    for p in r.json().get("photos", []):
        yield (p["src"].get("large2x") or p["src"]["original"], f"Photo: {p.get('photographer', 'Unknown')} / Pexels",
               p.get("url", ""))


def _pixabay(query: str) -> Iterator[tuple[str, str, str]]:
    key = os.getenv("PIXABAY_API_KEY")
    if not key:
        return
    r = requests.get("https://pixabay.com/api/", params={
        "key": key, "q": query[:100], "image_type": "photo", "orientation": "horizontal",
        "safesearch": "true", "per_page": 10, "min_width": 1200}, timeout=20)
    r.raise_for_status()
    for p in r.json().get("hits", []):
        yield (p.get("largeImageURL") or p["webformatURL"], f"Photo: {p.get('user', 'Unknown')} / Pixabay",
               p.get("pageURL", ""))


def _openverse(query: str) -> Iterator[tuple[str, str, str]]:
    words, seen = query.split(), set()
    for q in dict.fromkeys([" ".join(words), " ".join(words[:4]), " ".join(words[:2])]):  # broaden if needed
        r = requests.get("https://api.openverse.org/v1/images/", headers=UA, params={
            "q": q[:200], "license_type": "commercial,modification", "aspect_ratio": "wide",
            "mature": "false", "page_size": 20}, timeout=25)
        r.raise_for_status()
        for p in r.json().get("results", []):
            if (p.get("width") or 0) < 900 or p["url"] in seen:
                continue
            seen.add(p["url"])
            lic = f"CC {p.get('license', '').upper()} {p.get('license_version', '')}".strip()
            if p.get("license") in ("cc0", "pdm"):
                lic = "public domain"
            yield (p["url"], f"Photo: {p.get('creator') or 'Unknown'}, {lic}, via Openverse",
                   p.get("foreign_landing_url", ""))


PROVIDERS = {"pexels": _pexels, "pixabay": _pixabay, "openverse": _openverse}
MAX_CANDIDATES = 8


def find_photo(query: str, dest_stem: Path, approve: Callable[[Path, str], bool] | None = None) -> Photo | None:
    """First candidate that downloads cleanly and (if `approve` is given) passes the photo review."""
    if not query:
        return None
    order = os.getenv("PHOTO_PROVIDERS", "pexels,pixabay,openverse")
    tried = 0
    for name in [n.strip() for n in order.split(",") if n.strip() in PROVIDERS]:
        try:
            for url, credit, page in PROVIDERS[name](query):
                if tried >= MAX_CANDIDATES:
                    return None
                tried += 1
                try:
                    path = _download(url, dest_stem)
                except Exception:
                    continue
                if approve is not None and not approve(path, query):
                    log.info("Photo rejected by review (%s): %s", name, page or url)
                    path.unlink(missing_ok=True)
                    continue
                log.info("Photo for %r from %s: %s", query, name, page or url)
                return Photo(path, credit, page, url)
        except Exception as exc:
            log.warning("Photo provider %s failed for %r: %s", name, query, exc)
    return None


def from_pin(pin: dict, dest_stem: Path) -> Photo:
    """Download a photo that was already chosen (pinned in an issue's photos.json)."""
    return Photo(_download(pin["url"], dest_stem), pin["credit"], pin.get("page", ""), pin["url"])


def candidates(query: str, n: int = 6) -> list[tuple[str, str, str]]:
    """First n (url, credit, page) candidates across providers, for manual review."""
    out = []
    order = os.getenv("PHOTO_PROVIDERS", "pexels,pixabay,openverse")
    for name in [x.strip() for x in order.split(",") if x.strip() in PROVIDERS]:
        try:
            for c in PROVIDERS[name](query):
                out.append(c)
                if len(out) >= n:
                    return out
        except Exception as exc:
            log.warning("Photo provider %s failed: %s", name, exc)
    return out


if __name__ == "__main__":  # python -m newsletter.photos "query" out_dir  -> contact sheet + candidates.json
    import json
    import sys

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    query, out = sys.argv[1], Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    found = []
    for i, (url, credit, page) in enumerate(candidates(query, int(sys.argv[3]) if len(sys.argv) > 3 else 6)):
        try:
            found.append({"i": i, "path": str(_download(url, out / f"cand{i}")), "url": url, "credit": credit, "page": page})
        except Exception:
            pass
    (out / "candidates.json").write_text(json.dumps(found, indent=1))
    if found:
        cols = 3
        rows = (len(found) + cols - 1) // cols
        fig, axs = plt.subplots(rows, cols, figsize=(5 * cols, 3.4 * rows), squeeze=False)
        for ax in axs.flat:
            ax.axis("off")
        for ax, f in zip(axs.flat, found):
            ax.imshow(plt.imread(f["path"]))
            ax.set_title(f"#{f['i']}", fontsize=14)
        fig.savefig(out / "contact.png", dpi=60, bbox_inches="tight")
    print(f"{len(found)} candidates -> {out / 'contact.png'}")
