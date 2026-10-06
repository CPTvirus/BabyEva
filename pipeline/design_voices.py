#!/usr/bin/env python3
"""Design the four Baby Eva voices on ElevenLabs and save the previews to listen to.

    python pipeline/design_voices.py --out <folder>            # 3 previews per character
    python pipeline/design_voices.py --create eva=<generated_voice_id> rabit=<id> danny=<id> bunny=<id>

Step one writes <folder>/<character>-<n>.mp3 and <folder>/previews.json (the generated_voice_id
for each preview). Step two turns the chosen previews into saved voices on the account and prints
the voice ids to put in pipeline/voices.json. The casting notes come from master-bible.md section 7.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from generate import DEFAULT_ENV, load_env, need  # noqa: E402

API = "https://api.elevenlabs.io/v1"

CAST = {
    "eva": {
        # ElevenLabs blocks voice designs described by age, so the cast is described as cartoon
        # characters performed by adults, which is what every preschool show actually does.
        "description": (
            "A warm, gentle, youthful cartoon character voice for an animated plush mouse, performed by an adult "
            "female voice actor, light and high pitched, bright mid range and soft, speaking slowly with real pauses "
            "and an audible smile, breathy warmth, clear simple words, never shrieky, never sarcastic. "
            "Neutral clear English accent. Brave and a little unsure at the same time."
        ),
        "text": (
            "Hello! I'm Eva. I'm so happy you came. Look, this is my Adventure Star. It sleeps on my shelf, "
            "and when it glows, it means an adventure is starting! Can you wave hello? ... I saw that! "
            "Then come on, little adventurers! Can you help me? Where should we look?"
        ),
    },
    "rabit": {
        "description": (
            "A kind grandfatherly male voice in his sixties, low to mid range, warm and unhurried, slow and patient, "
            "with gentle amusement in it, the sound of a grown up kneeling down to a child's height. Never stern, "
            "never lecturing. Neutral clear English accent, soft and reassuring."
        ),
        "text": (
            "Good morning, you two. And good morning to all our friends watching. When something is lost, Eva, "
            "what do we do? We stop... we think... and we look! Can you do it with me? Well done. "
            "I knew you would find the way."
        ),
    },
    "danny": {
        "description": (
            "A playful, boisterous cartoon character voice for a big friendly plush dinosaur, performed by an adult "
            "male voice actor doing a youthful, mid range, rounded voice, bouncy and a little irregular, with a big "
            "grin in the voice and comic timing, secretly soft and shy underneath. Never scary, never mean. "
            "Neutral clear English accent."
        ),
        "text": (
            "Hello. ... I just wanted you to come and find me. Really? Can I play too? I'm the biggest, so I'll hide "
            "behind this tiny flowerpot! Nobody will ever see me. Shh! Together? Yes! Together!"
        ),
    },
    "bunny": {
        "description": (
            "A sweet, bubbly cartoon character voice for a tiny plush bunny, performed by an adult female voice "
            "actor, very high and bright, quick and giggly with upward inflections, loyal and encouraging, full of "
            "energy, never shrieky. Clearly higher, faster and brighter than the gentle mouse character. "
            "Neutral clear English accent."
        ),
        "text": (
            "Eva! You're here! It was right here! Eva... I think it's wiggling. Let's look together! "
            "Together! Hooray, we did it! Can we do it again tomorrow? I'll bring my carrots!"
        ),
    },
}


def design(key: str, who: str, out: Path) -> list[dict]:
    body = {
        "voice_description": CAST[who]["description"],
        "text": CAST[who]["text"],
        "model_id": "eleven_ttv_v3",
        "auto_generate_text": False,
    }
    r = requests.post(f"{API}/text-to-voice/design", headers={"xi-api-key": key}, json=body, timeout=180)
    if r.status_code == 404:  # older route name
        r = requests.post(f"{API}/text-to-voice/create-previews", headers={"xi-api-key": key}, json=body, timeout=180)
    if r.status_code != 200:
        raise RuntimeError(f"{who}: ElevenLabs {r.status_code}: {r.text[:400]}")
    previews = r.json().get("previews", [])
    saved = []
    for n, p in enumerate(previews, 1):
        path = out / f"{who}-{n}.mp3"
        path.write_bytes(base64.b64decode(p["audio_base_64"]))
        saved.append({"file": str(path), "generated_voice_id": p["generated_voice_id"],
                      "duration": p.get("duration_secs")})
        print(f"  {who} preview {n}: {path.name}  ({p.get('duration_secs', '?')}s)")
    return saved


def create(key: str, who: str, generated_voice_id: str) -> str:
    body = {
        "voice_name": f"Baby Eva - {who}",
        "voice_description": CAST[who]["description"],
        "generated_voice_id": generated_voice_id,
    }
    r = requests.post(f"{API}/text-to-voice", headers={"xi-api-key": key}, json=body, timeout=120)
    if r.status_code == 404:
        r = requests.post(f"{API}/text-to-voice/create-voice-from-preview", headers={"xi-api-key": key},
                          json=body, timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"{who}: ElevenLabs {r.status_code}: {r.text[:400]}")
    return r.json()["voice_id"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--env", type=Path, default=DEFAULT_ENV)
    ap.add_argument("--out", type=Path, help="folder for the preview mp3s")
    ap.add_argument("--only", choices=sorted(CAST), nargs="*")
    ap.add_argument("--create", nargs="*", metavar="who=generated_voice_id")
    args = ap.parse_args()
    load_env(args.env)
    key = need("BABYEVA_ELEVENLABS_API_KEY")

    if args.create:
        ids = {}
        for pair in args.create:
            who, gid = pair.split("=", 1)
            ids[who] = create(key, who, gid)
            print(f"  {who}: voice_id {ids[who]}")
        print(json.dumps(ids, indent=2))
        return 0

    out = args.out or Path("voice-previews")
    out.mkdir(parents=True, exist_ok=True)
    result = {}
    for who in (args.only or list(CAST)):
        print(f"designing {who} ...", flush=True)
        result[who] = design(key, who, out)
    (out / "previews.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"wrote {out / 'previews.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
