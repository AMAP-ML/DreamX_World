#!/usr/bin/env python3
"""Build demo video manifest for static hosting (e.g., GitHub Pages)."""

import json
import re
from pathlib import Path
from typing import Dict, List


VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov", ".m4v", ".ogg"}


def natural_key(value: str):
    """Natural sort key, e.g. 2 before 10."""
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", value)]


def sorted_video_paths(directory: Path, root: Path) -> List[str]:
    if not directory.exists():
        return []
    videos = [
        path for path in directory.iterdir()
        if path.is_file()
        and not path.name.startswith(".")
        and path.suffix.lower() in VIDEO_EXTENSIONS
    ]
    videos.sort(key=lambda p: natural_key(p.name))
    return [p.relative_to(root).as_posix() for p in videos]


def sorted_scene_entries(scene_root: Path, root: Path) -> List[Dict[str, object]]:
    if not scene_root.exists():
        return []
    scene_dirs = [d for d in scene_root.iterdir() if d.is_dir() and not d.name.startswith(".")]
    scene_dirs.sort(key=lambda d: natural_key(d.name))

    entries: List[Dict[str, object]] = []
    for scene_dir in scene_dirs:
        videos = sorted_video_paths(scene_dir, root)
        if not videos:
            continue
        entries.append({
            "name": scene_dir.name,
            "videos": videos,
        })
    return entries


def build_manifest(website_root: Path) -> Dict[str, object]:
    demo_root = website_root / "assets" / "demo_videos"
    return {
        "realVideos": sorted_video_paths(demo_root / "real_video", website_root),
        "dreamVideos": sorted_video_paths(demo_root / "dream_video", website_root),
        "thirdVideos": sorted_video_paths(demo_root / "third_video", website_root),
        "longVideos": sorted_video_paths(demo_root / "long_video", website_root),
        "memoryVideos": sorted_video_paths(demo_root / "memory_video", website_root),
        "singleEventScenes": sorted_scene_entries(demo_root / "event_video" / "single", website_root),
        "multipleEventScenes": sorted_scene_entries(demo_root / "event_video" / "multiple", website_root),
    }


def main():
    script_path = Path(__file__).resolve()
    website_root = script_path.parent.parent
    manifest_path = website_root / "assets" / "demo_videos" / "manifest.json"

    manifest = build_manifest(website_root)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Manifest generated: {manifest_path}")


if __name__ == "__main__":
    main()
