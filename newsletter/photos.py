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

import requests

log = logging.getLogger(__name__)
UA = {"User-Agent": "newsletter-automation/1.0 (newsletter photo search)"}


@dataclass
class Photo:
    path: Path
    credit: str      # e.g. "Photo: Jane Doe / Pixabay" or "Photo: Jane Doe, CC BY 2.0, via Openverse"
    page_url: str


def _download(url: str, dest_stem: Path) -> Path:
    img = requests.get(url, headers=UA, timeout=30)
    img.raise_for_status()
    if not img.headers.get("content-type", "").startswith("image/") or len(img.content) < 20_000:
        raise ValueError("not a usable photo")
    path = dest_stem.with_suffix(".jpg" if "jpeg" in img.headers["content-type"] else ".png")
    path.write_bytes(img.content)
    return path


def _pexels(query: str, dest_stem: Path) -> Photo | None:
    key = os.getenv("PEXELS_API_KEY")
    if not key:
        return None
    r = requests.get("https://api.pexels.com/v1/search", headers={"Authorization": key},
                     params={"query": query, "orientation": "landscape", "per_page": 8, "size": "large"}, timeout=20)
    r.raise_for_status()
    hits = r.json().get("photos", [])
    if not hits:
        return None
    p = max(hits[:5], key=lambda x: x.get("width", 0))
    path = _download(p["src"].get("large2x") or p["src"]["original"], dest_stem)
    return Photo(path, f"Photo: {p.get('photographer', 'Unknown')} / Pexels", p.get("url", ""))


def _pixabay(query: str, dest_stem: Path) -> Photo | None:
    key = os.getenv("PIXABAY_API_KEY")
    if not key:
        return None
    r = requests.get("https://pixabay.com/api/", params={
        "key": key, "q": query[:100], "image_type": "photo", "orientation": "horizontal",
        "safesearch": "true", "per_page": 10, "min_width": 1200}, timeout=20)
    r.raise_for_status()
    hits = r.json().get("hits", [])
    if not hits:
        return None
    p = hits[0]  # Pixabay ranks by relevance
    path = _download(p.get("largeImageURL") or p["webformatURL"], dest_stem)
    return Photo(path, f"Photo: {p.get('user', 'Unknown')} / Pixabay", p.get("pageURL", ""))


def _openverse(query: str, dest_stem: Path) -> Photo | None:
    r = requests.get("https://api.openverse.org/v1/images/", headers=UA, params={
        "q": query[:200], "license_type": "commercial,modification", "category": "photograph",
        "aspect_ratio": "wide", "size": "large", "mature": "false", "page_size": 10}, timeout=25)
    r.raise_for_status()
    for p in r.json().get("results", []):
        try:
            path = _download(p["url"], dest_stem)
        except Exception:
            continue
        lic = f"CC {p.get('license', '').upper()} {p.get('license_version', '')}".strip()
        if p.get("license") in ("cc0", "pdm"):
            lic = "public domain"
        return Photo(path, f"Photo: {p.get('creator') or 'Unknown'}, {lic}, via Openverse", p.get("foreign_landing_url", ""))
    return None


PROVIDERS = {"pexels": _pexels, "pixabay": _pixabay, "openverse": _openverse}


def find_photo(query: str, dest_stem: Path) -> Photo | None:
    if not query:
        return None
    order = os.getenv("PHOTO_PROVIDERS", "pexels,pixabay,openverse")
    for name in [n.strip() for n in order.split(",") if n.strip() in PROVIDERS]:
        try:
            photo = PROVIDERS[name](query, dest_stem)
        except Exception as exc:
            log.warning("Photo provider %s failed for %r: %s", name, query, exc)
            continue
        if photo:
            log.info("Photo for %r from %s", query, name)
            return photo
    return None
