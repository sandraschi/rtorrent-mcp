"""
filename_normalizer.py - Advanced media filename and directory path normalization.

Parses torrent titles and file paths for Anime, TV shows, and Movies, removing scene tags,
release group tags, resolution/codec indicators, and CRC hashes. Generates clean,
Plex-compliant destination paths.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

NOISE_PATTERNS = [
    r"\[(SubsPlease|ASW|Erai-raws|MeGusta|RARBG|EZTV|YIFY|YTS|NOGRP|VXT|Judas|Golumpa|EMBER|HorribleSubs)\]",
    r"-\s*(SubsPlease|ASW|Erai-raws|MeGusta|RARBG|EZTV|YIFY|YTS|NOGRP|VXT|Judas|Golumpa|EMBER|HorribleSubs)\b",
    r"\b(1080p|720p|2160p|4k|uhd|hdr|hevc|x264|x265|h264|h265|h\.264|h\.265|aac2?[\._]?0?|aac5\.1|dts|web-dl|webrip|bluray|hdtv|remux)\b",
    r"\[[A-F0-9]{8}\]",  # CRC32 hashes like [C5819381]
]


class FilenameNormalizer:
    """Normalize media filenames and generate Plex-compliant directory structures."""

    @staticmethod
    def extract_season_episode(text: str) -> dict[str, int | str | None]:
        """Extract Season and Episode numbers from filename string."""
        # Standard S01E02 or S1E2
        match = re.search(r"\bS(\d{1,2})E(\d{1,3})\b", text, re.IGNORECASE)
        if match:
            s, e = int(match.group(1)), int(match.group(2))
            return {"season": s, "episode": e, "formatted": f"S{s:02d}E{e:02d}"}

        # 1x02 format
        match = re.search(r"\b(\d{1,2})x(\d{1,3})\b", text, re.IGNORECASE)
        if match:
            s, e = int(match.group(1)), int(match.group(2))
            return {"season": s, "episode": e, "formatted": f"S{s:02d}E{e:02d}"}

        # Anime standalone episode count: "Show Name - 05" or "Show Name - 139"
        match = re.search(r"-\s*(\d{1,3})\b", text)
        if match:
            e = int(match.group(1))
            return {"season": 1, "episode": e, "formatted": f"S01E{e:02d}"}

        return {"season": None, "episode": None, "formatted": None}

    @staticmethod
    def extract_year(text: str) -> int | None:
        """Extract 4-digit release year (e.g. 1999, 2024)."""
        match = re.search(r"\b(19\d{2}|20\d{2})\b", text)
        if match:
            return int(match.group(1))
        return None

    @classmethod
    def clean_title(cls, filename: str) -> str:
        """Clean noise tags, brackets, and clutter from a filename."""
        stem = Path(filename).stem
        ext = Path(filename).suffix

        cleaned = stem
        # Strip noise patterns
        for pattern in NOISE_PATTERNS:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

        # Replace dots, underscores with spaces
        cleaned = re.sub(r"[\._]", " ", cleaned)

        # Clean multiple whitespace & trailing hyphens
        cleaned = re.sub(r"\s+", " ", cleaned).strip(" -.")

        return f"{cleaned}{ext}" if ext else cleaned

    @classmethod
    def normalize(cls, original_name: str, category: str = "anime") -> dict[str, Any]:
        """Normalize filename and construct Plex-compliant structure.

        Args:
            original_name: Original file or torrent name.
            category: Category (anime, tv, movies).

        Returns:
            Dict containing normalized filename, show/movie title, season, episode, year, and relative Plex path.
        """
        path_obj = Path(original_name)
        stem = path_obj.stem
        ext = path_obj.suffix.lower()
        if not ext and original_name.endswith((".mkv", ".mp4", ".avi", ".m4v")):
            ext = Path(original_name).suffix.lower()

        cat = category.lower()
        ep_info = cls.extract_season_episode(stem)
        year = cls.extract_year(stem)

        # Base title extraction: remove SXXEXX / year / noise
        base_title = stem
        for pattern in NOISE_PATTERNS:
            base_title = re.sub(pattern, "", base_title, flags=re.IGNORECASE)

        # Remove SXXEXX / episode numbers from title
        base_title = re.sub(r"\bS\d{1,2}E\d{1,3}\b", "", base_title, flags=re.IGNORECASE)
        base_title = re.sub(r"\b\d{1,2}x\d{1,3}\b", "", base_title, flags=re.IGNORECASE)
        base_title = re.sub(r"-\s*\d{1,3}\b", "", base_title)
        if year:
            base_title = re.sub(r"\b(19\d{2}|20\d{2})\b", "", base_title)

        # Remove empty parentheses or brackets left behind after noise removal
        base_title = re.sub(r"\(\s*\)", "", base_title)
        base_title = re.sub(r"\[\s*\]", "", base_title)

        base_title = re.sub(r"[\._]", " ", base_title)
        base_title = re.sub(r"\s+", " ", base_title).strip(" -.")

        if cat == "movies":
            year_str = f" ({year})" if year else ""
            clean_movie = f"{base_title}{year_str}"
            normalized_filename = f"{clean_movie}{ext}"
            relative_plex_path = f"Movies/{clean_movie}/{normalized_filename}"
            return {
                "original_name": original_name,
                "normalized_filename": normalized_filename,
                "title": base_title,
                "year": year,
                "category": "movies",
                "relative_plex_path": relative_plex_path,
            }
        else:  # TV or Anime
            season = ep_info["season"] or 1
            ep_formatted = ep_info["formatted"] or "S01E01"
            season_folder = f"Season {season:02d}"

            normalized_filename = f"{base_title} - {ep_formatted}{ext}"
            top_folder = "Anime" if cat == "anime" else "TV Shows"
            relative_plex_path = f"{top_folder}/{base_title}/{season_folder}/{normalized_filename}"

            return {
                "original_name": original_name,
                "normalized_filename": normalized_filename,
                "title": base_title,
                "season": season,
                "episode": ep_info["episode"],
                "formatted_episode": ep_formatted,
                "category": cat,
                "relative_plex_path": relative_plex_path,
            }
