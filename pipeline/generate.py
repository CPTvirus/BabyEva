#!/usr/bin/env python3
"""Generate the missing pieces of a Baby Eva manifest, then hand over to assemble.py.

    python pipeline/generate.py episodes/ep01-hello-im-eva/edit.json --dry-run
    python pipeline/generate.py episodes/ep01-hello-im-eva/edit.json
    python pipeline/generate.py edit.json --only 5.5          # one shot (or one line id)
    python pipeline/generate.py edit.json --only 5.5 --force  # reroll it

Reads the same edit.json that assemble.py reads. Anything whose file already exists is left
alone, so the approval gate is simply the file system: look at what landed, delete what fails
the visual bible, run again. Nothing is ever animated from a still that is not on disk, so a
still is always approved by a person before it moves.

Providers, chosen 6 October 2026 (prices from the vendors' pages that day):
  still    fal-ai/nano-banana-2/edit            reference images in, 2K out, about 8 US cents
  motion   fal-ai/veo3.1/lite/image-to-video    approved still in, silent clip out, 3c a second 720p, 5c 1080p
  talking  fal-ai/wan-25-preview/image-to-video approved still plus the voice line in, 10c a second 720p, 15c 1080p
  line     ElevenLabs text to speech            voice ids from pipeline/voices.json

Keys come from the environment, or from a .env file passed with --env (default: the Breazy
.claude/.env). Never from this repo.
  BABYEVA_FAL_KEY, BABYEVA_ELEVENLABS_API_KEY

Manifest fields this script adds on top of assemble.py's (everything else is unchanged):

  "style_suffix": "...",            appended to every still and motion prompt
  "negative": "...",                negative prompt for motion and talking
  "refs": ["reference/eva-model-sheet.jpg", "reference/cast-sheet.jpg"],   default references

  shot.gen = { "kind": "still",   "prompt": "...", "refs": [...], "resolution": "2K" }
  shot.gen = { "kind": "motion",  "prompt": "...", "from": "<approved still>", "seconds": 8, "resolution": "1080p" }
  shot.gen = { "kind": "talking", "prompt": "...", "from": "<approved still>", "audio": "<line file>", "resolution": "1080p" }
  line     = { "file": "...", "at": 0.8, "caption": "...", "voice": "eva", "text": "Hello! I'm Eva." }
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import requests

RATES_USD = {  # for --dry-run estimates only. fal's own get_pricing on the Baby Eva account, 6 October 2026
    "still": 0.08,
    "motion_720p": 0.05, "motion_1080p": 0.05,     # per second, Veo 3.1 Lite image to video
    "talking_720p": 0.05, "talking_1080p": 0.05,   # per second, Wan 2.5 image to video with audio
    "line": 0.0,                                   # inside the ElevenLabs plan
}
DEFAULT_ENV = Path(r"C:\Users\mapin\OneDrive\Documents\Brendon\.claude\.env")


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def need(var: str) -> str:
    val = os.environ.get(var)
    if not val:
        sys.exit(f"{var} is not set. Put it in the .env file or the environment.")
    return val


def probe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    return float(out)


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=300) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(1 << 16):
                f.write(chunk)


# ---------------------------------------------------------------- fal.ai

def fal():
    import fal_client  # installed with: python -m pip install --user fal-client
    os.environ["FAL_KEY"] = need("BABYEVA_FAL_KEY")
    return fal_client


def fal_upload(client, path: Path) -> str:
    return client.upload_file(str(path))


def gen_still(client, shot: dict, manifest: dict, dest: Path) -> None:
    g = shot["gen"]
    refs = [Path(p) for p in g.get("refs", manifest.get("refs", []))]
    prompt = expand(g["prompt"].strip(), manifest)
    if manifest.get("style_suffix"):
        prompt += "\n\n" + manifest["style_suffix"].strip()
    args = {
        "prompt": prompt,
        "num_images": 1,
        "aspect_ratio": g.get("aspect", "16:9"),
        "resolution": g.get("resolution", "2K"),
        "output_format": "png",
    }
    if refs:
        args["image_urls"] = [fal_upload(client, p) for p in refs]
        endpoint = "fal-ai/nano-banana-2/edit"
    else:
        endpoint = "fal-ai/nano-banana-2"
    result = client.subscribe(endpoint, arguments=args)
    download(result["images"][0]["url"], dest)


def gen_motion(client, shot: dict, manifest: dict, dest: Path) -> None:
    g = shot["gen"]
    src = Path(g["from"])
    if not src.exists():
        raise FileNotFoundError(f"approved still missing for motion shot {shot.get('id')}: {src}")
    seconds = int(g.get("seconds", 8))
    if seconds not in (4, 6, 8):
        raise ValueError(f"shot {shot.get('id')}: Veo Lite takes 4, 6 or 8 seconds, not {seconds}")
    prompt = expand(g["prompt"].strip(), manifest)
    if manifest.get("style_suffix"):
        prompt += "\n\n" + manifest["style_suffix"].strip()
    args = {
        "prompt": prompt,
        "image_url": fal_upload(client, src),
        "duration": f"{seconds}s",
        "resolution": g.get("resolution", "1080p"),
        "aspect_ratio": "16:9",
        "generate_audio": False,
    }
    if manifest.get("negative"):
        args["negative_prompt"] = manifest["negative"]
    result = client.subscribe("fal-ai/veo3.1/lite/image-to-video", arguments=args)
    download(result["video"]["url"], dest)


def gen_talking(client, shot: dict, manifest: dict, dest: Path) -> None:
    g = shot["gen"]
    src = Path(g["from"])
    audio = Path(g.get("audio") or shot["lines"][0]["file"])
    for p in (src, audio):
        if not p.exists():
            raise FileNotFoundError(f"talking shot {shot.get('id')} needs {p}")
    length = probe_duration(audio)
    if length < 3.2:
        # Wan wants at least 3 seconds of audio. A short line gets silence after it, which is
        # also exactly what the pause protocol wants: the character keeps listening.
        padded = audio.with_name(audio.stem + ".padded.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(audio), "-af",
                        "apad=whole_dur=3.5", str(padded)], check=True)
        audio, length = padded, 3.5
    if length > 10:
        print(f"  warning: line is {length:.1f}s, Wan keeps the first 10 seconds only", file=sys.stderr)
    duration = 5 if length <= 5 else 10
    args = {
        "prompt": expand(g["prompt"].strip(), manifest),
        "image_url": fal_upload(client, src),
        "audio_url": fal_upload(client, audio),
        "resolution": g.get("resolution", "720p"),
        "duration": duration,
        "enable_prompt_expansion": False,
    }
    if manifest.get("negative"):
        args["negative_prompt"] = manifest["negative"][:500]
    result = client.subscribe("fal-ai/wan-25-preview/image-to-video", arguments=args)
    download(result["video"]["url"], dest)


# ---------------------------------------------------------------- ElevenLabs

def gen_line(line: dict, voices: dict, dest: Path) -> None:
    key = need("BABYEVA_ELEVENLABS_API_KEY")
    voice = voices.get(line["voice"])
    if not voice:
        raise KeyError(f"no voice named {line['voice']!r} in voices.json")
    body = {
        "text": line["text"],
        "model_id": voice.get("model_id", "eleven_v3"),
        "voice_settings": voice.get("settings", {"stability": 0.5, "similarity_boost": 0.8, "style": 0.3}),
    }
    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice['voice_id']}",
        params={"output_format": "mp3_44100_128"},
        headers={"xi-api-key": key, "Accept": "audio/mpeg", "Content-Type": "application/json"},
        json=body, timeout=120,
    )
    if r.status_code != 200:
        raise RuntimeError(f"ElevenLabs {r.status_code}: {r.text[:300]}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(r.content)


# ---------------------------------------------------------------- plan and run

def expand(text: str, manifest: dict) -> str:
    """Fill {EVA}, {RABIT}, {DANNY}, {BUNNY} and any other manifest-level lock into a prompt."""
    locks = manifest.get("locks", {})
    try:
        return text.format_map(locks)
    except KeyError as e:
        raise KeyError(f"prompt uses {{{e.args[0]}}} but manifest.locks has no such entry") from e


def plan(manifest: dict, only: str | None, force: bool) -> list[dict]:
    jobs = []
    seen_stills: set[str] = set()
    for shot in manifest["shots"]:
        sid = str(shot.get("id"))
        for n, line in enumerate(shot.get("lines", [])):
            lid = f"{sid}.line{n + 1}"
            if "text" in line and (force or not Path(line["file"]).exists()) and (only in (None, sid, lid)):
                jobs.append({"id": lid, "kind": "line", "shot": shot, "line": line, "dest": Path(line["file"])})
        g = shot.get("gen")
        if not g:
            continue
        # A motion or talking shot can carry the recipe for the still it starts from. The still
        # is generated first and must be approved on disk before the clip is made.
        if g.get("from_gen") and g["from"] not in seen_stills and (only in (None, sid)) \
                and not Path(g["from"]).exists():
            seen_stills.add(g["from"])
            jobs.append({"id": f"{sid}.still", "kind": "still", "shot": {"id": sid, "gen": g["from_gen"]},
                         "dest": Path(g["from"])})
        if force or not Path(shot["file"]).exists():
            if only in (None, sid):
                jobs.append({"id": sid, "kind": g["kind"], "shot": shot, "dest": Path(shot["file"])})
    return jobs


def estimate(job: dict) -> float:
    g = job["shot"].get("gen", {})
    res = g.get("resolution", "1080p")
    if job["kind"] == "still":
        return RATES_USD["still"]
    if job["kind"] == "motion":
        return RATES_USD[f"motion_{res}"] * int(g.get("seconds", 8))
    if job["kind"] == "talking":
        audio = Path(g.get("audio") or job["shot"]["lines"][0]["file"])
        secs = 10 if audio.exists() and probe_duration(audio) > 5 else 5
        return RATES_USD[f"talking_{res}"] * secs
    return RATES_USD["line"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manifest", type=Path)
    ap.add_argument("--env", type=Path, default=DEFAULT_ENV, help="a .env file with the keys")
    ap.add_argument("--voices", type=Path, default=Path(__file__).with_name("voices.json"))
    ap.add_argument("--only", help="a shot id, or <shot id>.line<n>")
    ap.add_argument("--force", action="store_true", help="regenerate even if the file exists (a reroll)")
    ap.add_argument("--dry-run", action="store_true", help="list what would be generated and the estimated cost")
    args = ap.parse_args()

    load_env(args.env)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    voices = json.loads(args.voices.read_text(encoding="utf-8")) if args.voices.exists() else {}
    jobs = plan(manifest, args.only, args.force)
    if not jobs:
        print("nothing to generate, every file is on disk")
        return 0

    # Lines first, then stills, then anything that needs a still or a line on disk.
    order = {"line": 0, "still": 1, "motion": 2, "talking": 2}
    jobs.sort(key=lambda j: order[j["kind"]])
    total = sum(estimate(j) for j in jobs)
    for j in jobs:
        print(f"  {j['kind']:8} {j['id']:10} -> {j['dest']}   ~{estimate(j):.2f} USD")
    print(f"{len(jobs)} jobs, about {total:.2f} USD before rerolls")
    if args.dry_run:
        return 0

    client = fal() if any(j["kind"] != "line" for j in jobs) else None
    failed = 0
    for j in jobs:
        print(f"generating {j['kind']} {j['id']} ...", flush=True)
        try:
            if j["kind"] == "line":
                gen_line(j["line"], voices, j["dest"])
            elif j["kind"] == "still":
                gen_still(client, j["shot"], manifest, j["dest"])
            elif j["kind"] == "motion":
                gen_motion(client, j["shot"], manifest, j["dest"])
            elif j["kind"] == "talking":
                gen_talking(client, j["shot"], manifest, j["dest"])
            print(f"  wrote {j['dest']}")
        except Exception as e:  # keep going, report at the end
            failed += 1
            print(f"  FAILED {j['id']}: {e}", file=sys.stderr)
    print(f"done, {len(jobs) - failed} ok, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
