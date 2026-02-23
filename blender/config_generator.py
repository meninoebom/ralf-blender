"""Generate .perf.json from musical primitives."""

import json
from pathlib import Path

from .slicer import Slice
from .defaults import (
    CATEGORY_MODES, CATEGORY_COLORS, CATEGORY_VOLUMES,
    DEFAULT_REVERB_SEND_DB, DEFAULT_DELAY_SEND_DB,
    DENSITY_SCENES, STARTING_SCENE,
)


def _infer_interval(duration_ms: float, bpm: float, default: str) -> str:
    """Snap slice duration to nearest musical interval."""
    beat_ms = 60000 / bpm
    bar_ms = beat_ms * 4
    bars = duration_ms / bar_ms

    if bars <= 1.5:
        return "1m"
    elif bars <= 3:
        return "2m"
    elif bars <= 6:
        return "4m"
    else:
        return "8m"


def generate_config(
    primitives: dict[str, list[Slice]],
    bpm: float,
    song_name: str,
    samples_dir: Path,
) -> dict:
    """Generate a .perf.json from categorized musical primitives."""
    sample_tracks = []
    category_indices: dict[str, list[int]] = {}
    track_idx = 0

    category_order = ["foundation", "groove", "bass", "harmonic_bed", "hook", "texture", "accent"]

    for category in category_order:
        slices = primitives.get(category, [])
        if not slices:
            continue

        category_indices[category] = []
        mode_def = CATEGORY_MODES[category]
        color = CATEGORY_COLORS.get(category, "#aaa")
        volume = CATEGORY_VOLUMES.get(category, -8)

        for i, sl in enumerate(slices):
            display_name = f"{category.replace('_', ' ').title()} {i + 1}"
            mode = mode_def["mode"]

            track = {
                "name": display_name,
                "file": sl.path.name,
                "color": color,
                "category": category,
                "volume": volume,
                "sends": {
                    "reverb": DEFAULT_REVERB_SEND_DB,
                    "delay": DEFAULT_DELAY_SEND_DB,
                },
                "mode": mode,
            }

            if mode == "loop":
                default_interval = mode_def["interval"] or "2m"
                track["interval"] = _infer_interval(sl.duration_ms, bpm, default_interval)

            # Muted-in-scenes: muted in any scene where this category is NOT active
            if category not in ("hook", "accent"):
                muted_scenes = []
                for scene_idx, scene in enumerate(DENSITY_SCENES):
                    if category not in scene["active"]:
                        muted_scenes.append(scene_idx)
                if muted_scenes:
                    track["muted_in_scenes"] = muted_scenes

            sample_tracks.append(track)
            category_indices[category].append(track_idx)
            track_idx += 1

    scenes = []
    for scene in DENSITY_SCENES:
        scenes.append({
            "name": scene["name"],
            "desc": f"Active: {', '.join(scene['active'])}",
        })

    config = {
        "version": "0.2",
        "name": f"{song_name} (Blended)",
        "bpm": bpm,
        "sample_tracks": sample_tracks,
        "scenes": scenes,
        "category_indices": {k: v for k, v in category_indices.items() if v},
        "starting_scene": STARTING_SCENE,
    }

    return config


def write_config(config: dict, output_path: Path) -> None:
    """Write .perf.json to disk."""
    with open(output_path, "w") as f:
        json.dump(config, f, indent=2)
