#!/usr/bin/env python3
"""Generate first-frame thumbnails for demo videos.

Output thumbnails mirror the source tree:
  website/assets/demo_videos/.../*.mp4 -> website/assets/demo_thumbs/.../*.jpg
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


VIDEO_EXTS = {".mp4", ".webm", ".mov", ".m4v", ".ogg"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate thumbnails from demo videos.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate thumbnails even when output exists and is newer.",
    )
    parser.add_argument(
        "--source",
        default=None,
        help="Source video root directory (default: assets/demo_videos under website root).",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output thumbnail root directory (default: assets/demo_thumbs under website root).",
    )
    parser.add_argument(
        "--seek-seconds",
        default="0.10",
        help="Seek time before extracting frame (default: 0.10).",
    )
    parser.add_argument(
        "--thumb-width",
        type=int,
        default=240,
        help="Thumbnail width in pixels, preserving aspect ratio (default: 240).",
    )
    return parser.parse_args()


def has_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


def iter_video_files(source_root: Path):
    for path in source_root.rglob("*"):
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue
        if path.suffix.lower() not in VIDEO_EXTS:
            continue
        yield path


def thumb_path_for(video_path: Path, source_root: Path, output_root: Path) -> Path:
    rel = video_path.relative_to(source_root)
    return (output_root / rel).with_suffix(".jpg")


def generate_thumbnail(video_path: Path, thumb_path: Path, seek_seconds: str, thumb_width: int) -> bool:
    thumb_path.parent.mkdir(parents=True, exist_ok=True)
    scale_filter = f"scale={thumb_width}:-1"
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-ss",
        seek_seconds,
        "-i",
        str(video_path),
        "-frames:v",
        "1",
        "-vf",
        scale_filter,
        "-q:v",
        "3",
        str(thumb_path),
    ]
    result = subprocess.run(command)
    return result.returncode == 0


def main() -> int:
    args = parse_args()
    website_root = Path(__file__).resolve().parent.parent
    source_root = (Path(args.source).expanduser().resolve() if args.source else (website_root / "assets" / "demo_videos"))
    output_root = (Path(args.output).expanduser().resolve() if args.output else (website_root / "assets" / "demo_thumbs"))

    if not source_root.exists():
        print(f"Source directory not found: {source_root}")
        return 1
    if not has_ffmpeg():
        print("ffmpeg not found. Please install ffmpeg first.")
        return 1

    videos = sorted(iter_video_files(source_root))
    if not videos:
        print(f"No videos found under: {source_root}")
        return 0

    generated = 0
    skipped = 0
    failed = 0

    for video_path in videos:
        thumb_path = thumb_path_for(video_path, source_root, output_root)
        if (
            not args.force
            and thumb_path.exists()
            and thumb_path.stat().st_mtime >= video_path.stat().st_mtime
        ):
            skipped += 1
            continue

        ok = generate_thumbnail(video_path, thumb_path, args.seek_seconds, args.thumb_width)
        if ok:
            generated += 1
        else:
            failed += 1
            print(f"[FAILED] {video_path}")

    print(
        f"Thumbnail generation done. generated={generated}, skipped={skipped}, failed={failed}, "
        f"output={output_root}"
    )
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
