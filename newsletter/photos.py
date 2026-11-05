"""Real photos from Pexels (free API, free to use, photographer credited).

Set PEXELS_API_KEY (free at https://www.pexels.com/api/). Without it, photo visuals are
skipped and covers fall back to the halftone panel.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

import requests

log = logging.getLogger(__name__)


@dataclass
class Photo:
    path: Path
    credit: str      # "Photo: Jane Doe / Pexels"
    page_url: str


def find_photo(query: str, dest_stem: Path, orientation: str = "landscape") -> Photo | None:
    key = os.getenv("PEXELS_API_KEY")
    if not key or not query:
        return None
    resp = requests.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": key},
        params={"query": query, "orientation": orientation, "per_page": 8, "size": "large"},
        timeout=20,
    )
    resp.raise_for_status()
    photos = resp.json().get("photos", [])
    if not photos:
        log.info("No Pexels photo for %r", query)
        return None
    p = max(photos[:5], key=lambda x: x.get("width", 0))  # the sharpest of the top results
    img = requests.get(p["src"].get("large2x") or p["src"]["original"], timeout=30)
    img.raise_for_status()
    path = dest_stem.with_suffix(".jpg")
    path.write_bytes(img.content)
    return Photo(path=path, credit=f"Photo: {p.get('photographer', 'Unknown')} / Pexels", page_url=p.get("url", ""))
