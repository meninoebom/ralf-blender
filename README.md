# Blender

Turn any song into categorized musical samples with a `.perf.json` config.

**Pipeline:** Song → Demucs stem separation → BPM detection → bar-aligned slicing → 7-category selection → config generation

## Install

```bash
pip install -e .
```

## Usage

```bash
blender song.mp3
blender song.mp3 --output-dir ~/my-samples --bpm 120 --stems drums,bass --verbose
```

Output goes to the **current working directory** by default (like most CLI tools). Use `--output-dir` to write elsewhere. Creates a `samples/` directory with categorized WAV files and a `.perf.json` config.

## Categories

| Category | Source | Mode |
|----------|--------|------|
| Foundation | Drums (highest energy) | Loop |
| Groove | Drums (brightest) | Loop |
| Bass | Bass (diverse phrases) | Loop |
| Harmonic Bed | Other (longest sections) | Loop |
| Hook | Vocals (highest energy) | Oneshot |
| Texture | All (lowest energy) | Loop |
| Accent | All (punchiest) | Oneshot |
