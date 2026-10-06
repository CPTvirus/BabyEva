#!/usr/bin/env python3
"""Assemble a Baby Eva piece from a shot manifest, with ffmpeg only.

    python pipeline/assemble.py episodes/ep01-hello-im-eva/edit.json
    python pipeline/assemble.py edit.json --only 16x9

Reads a manifest (see pipeline/README.md), renders every shot to the target
size, puts the voice lines on a timeline, ducks the music bed under them, burns
optional captions, and writes <output>-16x9.mp4 and <output>-9x16.mp4.

Stills get a slow Ken Burns move (push, pull, pan_left, pan_right, static).
Video clips are centre cropped to the target ratio and frozen on their last
frame if they are shorter than the shot. Nothing here calls a generation API;
every input is a file already approved against the visual bible.

Needs Python 3.10+ and ffmpeg/ffprobe on PATH. No other dependencies.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

SIZES = {"16x9": (1920, 1080), "9x16": (1080, 1920)}
VIDEO_EXT = {".mp4", ".mov", ".webm", ".mkv"}


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def probe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    return float(out)


def has_audio(path: Path) -> bool:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_type",
         "-of", "csv=p=0", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    return bool(out)


def ff_path(path: Path) -> str:
    """Escape a path for use inside an ffmpeg filter option (Windows colons and backslashes)."""
    return str(path.resolve()).replace("\\", "/").replace(":", "\\:")


def kenburns(motion: str, duration: float, w: int, h: int) -> str:
    """Slow move over a 2x oversampled still, as a scale (per frame) plus a centre crop.

    ffmpeg evaluates crop's width and height once, so the zoom lives in scale with
    eval=frame, where t is allowed, and crop only animates its x and y.
    """
    big_w, big_h = w * 2, h * 2
    amount = 0.10  # ten percent over the shot, slow by design (bible: slow pushes only)
    d = f"{duration:.3f}"
    if motion == "push":
        z = f"(1+{amount}*t/{d})"
        return f"scale=w='{big_w}*{z}':h='{big_h}*{z}':eval=frame,crop={big_w}:{big_h}:x=(iw-ow)/2:y=(ih-oh)/2"
    if motion == "pull":
        z = f"(1+{amount}-{amount}*t/{d})"
        return f"scale=w='{big_w}*{z}':h='{big_h}*{z}':eval=frame,crop={big_w}:{big_h}:x=(iw-ow)/2:y=(ih-oh)/2"
    if motion in ("pan_left", "pan_right"):
        x = f"(iw-ow)*(1-t/{d})" if motion == "pan_left" else f"(iw-ow)*t/{d}"
        return f"scale={int(big_w*1.08)}:{int(big_h*1.08)},crop={big_w}:{big_h}:x='{x}':y=(ih-oh)/2"
    return f"scale={int(big_w*1.04)}:{int(big_h*1.04)},crop={big_w}:{big_h}:x=(iw-ow)/2:y=(ih-oh)/2"


def caption_filters(shot: dict, manifest: dict, w: int, h: int, tmp: Path, idx: int) -> list[str]:
    if not manifest.get("captions", True):
        return []
    font = manifest.get("font", "C:/Windows/Fonts/arialbd.ttf")
    filters = []
    for n, line in enumerate(shot.get("lines", [])):
        text = line.get("caption")
        if not text:
            continue
        # Size off the shorter side so 9:16 and 16:9 get the same reading size, and wrap so a
        # caption never runs past the frame in the vertical cut.
        size = int(min(w, h) * 0.05)
        per_line = max(12, int(w * 0.9 / (size * 0.56)))
        rows = textwrap.wrap(text, width=per_line) or [text]
        # A talking clip carries its own line from frame zero, so its caption starts at zero too.
        start = 0.0 if (shot.get("_embedded") and n == 0) else float(line.get("at", 0.5))
        end = start + probe_duration(Path(line["file"]))
        # One drawtext per row, stacked upward from the same baseline, so no newline ever
        # reaches drawtext (ffmpeg 8 draws a missing glyph box for it).
        for r, row in enumerate(rows):
            textfile = tmp / f"cap-{idx}-{n}-{r}.txt"
            textfile.write_text(row, encoding="utf-8")
            y = f"h*0.84-{(len(rows) - r) * int(size * 1.3)}"
            filters.append(
                "drawtext=fontfile='{font}':textfile='{tf}':fontsize={size}:fontcolor=white:"
                "borderw={bw}:bordercolor=0x2E2640:x=(w-tw)/2:y={y}:"
                "enable='between(t,{s:.3f},{e:.3f})'".format(
                    font=ff_path(Path(font)), tf=ff_path(textfile), size=size,
                    bw=max(2, size // 12), y=y, s=start, e=end
                )
            )
    return filters


CACHE_VERSION = "1"  # bump when the way a shot is rendered changes


def shot_key(shot: dict, manifest: dict, w: int, h: int, fps: int) -> str:
    """Everything that decides what a rendered shot looks like. Same key, same pixels."""
    def stamp(p: str) -> list:
        st = Path(p).stat()
        return [p, st.st_mtime_ns, st.st_size]
    spec = {
        "v": CACHE_VERSION, "src": stamp(shot["file"]), "duration": float(shot["duration"]),
        "motion": shot.get("motion", "push"), "size": [w, h, fps],
        "captions": bool(manifest.get("captions", True)), "font": manifest.get("font", ""),
        "embedded": bool(shot.get("_embedded")),
        "lines": [[l.get("caption"), l.get("at", 0.5), stamp(l["file"])] for l in shot.get("lines", [])],
    }
    return hashlib.sha1(json.dumps(spec, sort_keys=True).encode("utf-8")).hexdigest()[:20]


def render_shot(shot: dict, manifest: dict, w: int, h: int, fps: int, tmp: Path, idx: int) -> Path:
    src = Path(shot["file"])
    # Captions are rendered per ratio, so the wrap width above is recomputed on every call.
    duration = float(shot["duration"])
    # Rendered shots are kept beside the output, keyed by everything that shapes them, so a
    # second render only redoes the shots that changed. A one shot fix takes a minute, not twenty.
    cache = Path(manifest["output"]).resolve().parent / ".cache" / f"{w}x{h}"
    cache.mkdir(parents=True, exist_ok=True)
    out = cache / f"{shot_key(shot, manifest, w, h, fps)}.mp4"
    if out.exists() and out.stat().st_size > 0:
        return out
    part = out.with_suffix(".part.mp4")
    vf: list[str]
    cmd = ["ffmpeg", "-v", "error", "-y"]
    if src.suffix.lower() in VIDEO_EXT:
        clip_len = probe_duration(src)
        cmd += ["-i", str(src)]
        vf = [
            f"scale={w}:{h}:force_original_aspect_ratio=increase",
            f"crop={w}:{h}",
            f"fps={fps}",
        ]
        if clip_len < duration:
            vf.append(f"tpad=stop_mode=clone:stop_duration={duration - clip_len:.3f}")
    else:
        cmd += ["-loop", "1", "-framerate", str(fps), "-i", str(src)]
        vf = [
            f"scale={w * 2}:{h * 2}:force_original_aspect_ratio=increase",
            f"crop={w * 2}:{h * 2}",
            kenburns(shot.get("motion", "push"), duration, w, h),
            f"scale={w}:{h}",
        ]
    vf += caption_filters(shot, manifest, w, h, tmp, idx)
    vf += ["format=yuv420p"]
    cmd += ["-t", f"{duration:.3f}", "-vf", ",".join(vf), "-an",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", str(fps), str(part)]
    run(cmd)
    part.replace(out)  # only a finished render ever gets the cache name
    return out


def build_audio_graph(manifest: dict, starts: list[float], total: float) -> tuple[list[str], str, str]:
    """Return (extra ffmpeg inputs, filter_complex, output label)."""
    inputs: list[str] = []
    parts: list[str] = []
    n_in = 1  # input 0 is the concatenated video
    line_labels = []
    for shot, start in zip(manifest["shots"], starts):
        if shot.get("_embedded"):
            # The clip was generated from its line, so the clip's own audio is the line, in sync
            # by construction. Use it, trimmed to the shot, and skip the separate line file.
            ms = int(start * 1000)
            inputs += ["-i", str(Path(shot["file"]))]
            label = f"l{len(line_labels)}"
            parts.append(f"[{n_in}:a]aresample=48000,aformat=channel_layouts=stereo,"
                         f"atrim=0:{float(shot['duration']):.3f},adelay={ms}|{ms}[{label}]")
            line_labels.append(label)
            n_in += 1
        for k, line in enumerate(shot.get("lines", [])):
            if shot.get("_embedded") and k == 0:
                continue
            at = start + float(line.get("at", 0.5))
            ms = int(at * 1000)
            inputs += ["-i", str(Path(line["file"]))]
            label = f"l{len(line_labels)}"
            gain = float(line.get("gain_db", 0))
            parts.append(f"[{n_in}:a]aresample=48000,aformat=channel_layouts=stereo,"
                         f"volume={gain}dB,adelay={ms}|{ms}[{label}]")
            line_labels.append(label)
            n_in += 1
    music = manifest.get("music")
    if music:
        inputs += ["-stream_loop", "-1", "-i", str(Path(music["file"]))]
        bed = float(music.get("bed_db", -16))
        fade = float(music.get("fade_out", 2.0))
        parts.append(f"[{n_in}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{total:.3f},"
                     f"afade=t=out:st={max(0.0, total - fade):.3f}:d={fade},volume={bed}dB[mus]")
        n_in += 1
    if line_labels:
        joined = "".join(f"[{l}]" for l in line_labels)
        parts.append(f"{joined}amix=inputs={len(line_labels)}:normalize=0:dropout_transition=0[dlg]")
        if music:
            duck = float(music.get("duck_db", -18))
            # Sidechain compression pulls the bed down whenever a voice line is playing.
            parts.append("[dlg]asplit=2[dlgA][dlgB]")
            parts.append(f"[mus][dlgA]sidechaincompress=threshold=0.015:ratio=20:attack=40:release=700:"
                         f"makeup=1[musd]")
            parts.append(f"[musd][dlgB]amix=inputs=2:normalize=0:dropout_transition=0,"
                         f"apad=whole_dur={total:.3f}[aout]")
        else:
            parts.append(f"[dlg]apad=whole_dur={total:.3f}[aout]")
        return inputs, ";".join(parts), "aout"
    if music:
        return inputs, ";".join(parts), "mus"
    return [], "", ""


def render(manifest: dict, ratio: str, keep_tmp: bool) -> Path:
    w, h = SIZES[ratio]
    fps = int(manifest.get("fps", 24))
    out = Path(manifest["output"]).with_name(Path(manifest["output"]).name + f"-{ratio}.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix=f"babyeva-{ratio}-"))
    try:
        segments, starts, t = [], [], 0.0
        for shot in manifest["shots"]:
            src = Path(shot["file"])
            shot["_embedded"] = bool(shot.get("lines")) and src.suffix.lower() in VIDEO_EXT and has_audio(src)
        for i, shot in enumerate(manifest["shots"]):
            print(f"  [{ratio}] shot {shot.get('id', i)}  {shot['duration']}s  {Path(shot['file']).name}")
            segments.append(render_shot(shot, manifest, w, h, fps, tmp, i))
            starts.append(t)
            t += float(shot["duration"])
        total = t
        concat_list = tmp / "concat.txt"
        concat_list.write_text("".join(f"file '{s.as_posix()}'\n" for s in segments), encoding="utf-8")
        video_all = tmp / "video.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
             "-c", "copy", str(video_all)])
        inputs, graph, label = build_audio_graph(manifest, starts, total)
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(video_all)] + inputs
        if graph:
            cmd += ["-filter_complex", graph, "-map", "0:v", "-map", f"[{label}]",
                    "-c:a", "aac", "-b:a", "192k"]
        else:
            cmd += ["-map", "0:v"]
        cmd += ["-c:v", "copy", "-t", f"{total:.3f}", "-movflags", "+faststart", str(out)]
        run(cmd)
        print(f"  [{ratio}] wrote {out}  ({total:.1f}s)")
        return out
    finally:
        if not keep_tmp:
            for p in tmp.iterdir():
                p.unlink()
            tmp.rmdir()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manifest", type=Path)
    ap.add_argument("--only", choices=sorted(SIZES), help="render one ratio only")
    ap.add_argument("--keep-tmp", action="store_true", help="keep the per shot segments for inspection")
    args = ap.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    missing = [s["file"] for s in manifest["shots"] if not Path(s["file"]).exists()]
    missing += [l["file"] for s in manifest["shots"] for l in s.get("lines", []) if not Path(l["file"]).exists()]
    if manifest.get("music") and not Path(manifest["music"]["file"]).exists():
        missing.append(manifest["music"]["file"])
    if missing:
        print("missing inputs:\n  " + "\n  ".join(missing), file=sys.stderr)
        return 2
    total = sum(float(s["duration"]) for s in manifest["shots"])
    print(f"{len(manifest['shots'])} shots, {total:.1f}s total")
    for ratio in ([args.only] if args.only else sorted(SIZES)):
        render(manifest, ratio, args.keep_tmp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
