#!/usr/bin/env python3
"""Make a music cue, bed or song on Eleven Music and save it as mp3.

    python pipeline/make_music.py --out audio/cue-danny.mp3 --seconds 8 --instrumental \
        --prompt "Comic staccato bassoon with woodblock and a slide whistle, ..."
    python pipeline/make_music.py --out audio/song-brush.mp3 --seconds 150 --prompt "..." --lyrics lyrics.txt

Eleven Music, read from elevenlabs.io/pricing on 6 October 2026: 900 credits a minute of music,
commercial use included on Starter and above, 3 seconds to 5 minutes a track. It shares the plan's
credit pool with text to speech. The key is BABYEVA_ELEVENLABS_API_KEY, from the environment or
the .env file passed with --env.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from generate import DEFAULT_ENV, load_env, need  # noqa: E402

API = "https://api.elevenlabs.io/v1/music"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--prompt", required=True, help="what the music is, instruments, mood, tempo, key")
    ap.add_argument("--seconds", type=float, required=True, help="3 to 300")
    ap.add_argument("--instrumental", action="store_true", help="no vocals, guaranteed")
    ap.add_argument("--lyrics", type=Path, help="a text file of lyrics to sing, appended to the prompt")
    ap.add_argument("--model", default="music_v2_5")
    ap.add_argument("--env", type=Path, default=DEFAULT_ENV)
    args = ap.parse_args()

    load_env(args.env)
    key = need("BABYEVA_ELEVENLABS_API_KEY")
    prompt = args.prompt.strip()
    if args.lyrics:
        prompt += "\n\nLyrics, sing these exactly:\n" + args.lyrics.read_text(encoding="utf-8").strip()
    body = {
        "prompt": prompt,
        "music_length_ms": int(args.seconds * 1000),
        "model_id": args.model,
        "force_instrumental": bool(args.instrumental),
    }
    credits = int(round(args.seconds / 60 * 900))
    print(f"composing {args.seconds:.0f}s on {args.model}, about {credits} credits ...", flush=True)
    r = requests.post(API, headers={"xi-api-key": key, "Content-Type": "application/json"},
                      params={"output_format": "mp3_44100_192"}, json=body, timeout=600)
    if r.status_code != 200:
        print(f"ElevenLabs {r.status_code}: {r.text[:500]}", file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(r.content)
    print(f"wrote {args.out} ({len(r.content) // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
