# PIPELINE

The tools that turn approved assets into a finished piece. Added 6 October 2026 with the
production pipeline proposal. Nothing in here generates an image, a clip or a voice yet; that half
arrives once the accounts in `PRODUCTION-PIPELINE.md` exist. This half is the part that was missing
from every attempt so far: the assembly, with the pauses, the ducking and both aspect ratios,
done by a script instead of by hand.

## assemble.py

```
python pipeline/assemble.py episodes/ep01-hello-im-eva/edit.json
python pipeline/assemble.py edit.json --only 9x16
python pipeline/assemble.py edit.json --keep-tmp      # keep the per shot segments to inspect
```

Needs Python 3.10 or newer and ffmpeg and ffprobe on PATH. No other dependencies, nothing to
install. Verified 6 October 2026 on Windows with ffmpeg 8 and Python 3.13 against the three approved
location stills, the approved Eva clip and the theme: 27 seconds, both ratios, voice lines placed
on the timeline, captions burnt in, music ducked under speech.

What it does, in order:

1. Renders every shot to the target size. A still gets a slow move (`push`, `pull`, `pan_left`,
   `pan_right`, `static`), ten percent over the shot, from a 2x oversampled frame so there is no
   jitter. A video clip is centre cropped to the ratio and frozen on its last frame if it is
   shorter than the shot. This is why every hero shot must survive a 9:16 centre crop (master bible
   §6): the vertical cut is the same shot list cropped, never reframed.
2. Concatenates the shots with hard cuts. No dissolves, on purpose. The bible's minimum shot
   length does the pacing.
3. Places each voice line at `shot start + at` on one timeline and mixes them.
4. Loops the music under the whole piece at `bed_db`, fades it out, and pulls it down under every
   voice line with a sidechain compressor. The bible's rule is music never competes with dialogue.
5. Burns captions for any line that has one, centred, in the bottom fifth, so they survive the
   vertical crop.
6. Writes `<output>-16x9.mp4` (1920x1080) and `<output>-9x16.mp4` (1080x1920), H.264, AAC.

## The manifest

One `edit.json` per piece, beside its shots. Paths are relative to where you run the script, or
absolute.

```json
{
  "output": "episodes/ep01-hello-im-eva/renders/ep01",
  "fps": 24,
  "captions": true,
  "font": "C:/Windows/Fonts/arialbd.ttf",
  "music": {
    "file": "audio/theme-v2b-call-response.mp3",
    "bed_db": -14,
    "duck_db": -18,
    "fade_out": 2.5
  },
  "shots": [
    {
      "id": "1.1",
      "file": "episodes/ep01-hello-im-eva/shots/sh1-1-evas-room-dawn.png",
      "duration": 7,
      "motion": "push"
    },
    {
      "id": "3.1",
      "file": "episodes/ep01-hello-im-eva/shots/sh3-1-eva-hello-talking.mp4",
      "duration": 8,
      "lines": [
        { "file": "episodes/ep01-hello-im-eva/voice/3-1-eva-hello.mp3", "at": 0.8,
          "caption": "Hello! I'm Eva." }
      ]
    }
  ]
}
```

| Field | Meaning |
|---|---|
| `output` | Base path, the ratio suffix is added |
| `fps` | 24 unless there is a reason |
| `captions` | `false` to skip burning captions |
| `font` | A TrueType file for captions. The default is Windows Arial Bold, set it on a Mac |
| `music.file` | Any audio ffmpeg can read. It loops |
| `music.bed_db` | Level of the bed under the piece. Start at -14 |
| `music.duck_db` | Reserved for a fixed duck; the sidechain does the work today |
| `music.fade_out` | Seconds of fade at the end |
| `shots[].file` | A still (png, jpg) or a clip (mp4, mov, webm) |
| `shots[].duration` | Seconds on screen. A pause is simply a longer duration on a held shot |
| `shots[].motion` | Stills only. `push` is the default |
| `shots[].lines[]` | Voice lines in this shot, `file`, `at` seconds from the shot start, optional `caption` and `gain_db` |

The pause protocol (master bible §12) is a manifest decision, not a code one: a question line at
`at: 0.5` on a shot whose `duration` is the line length plus three seconds is a pause. The script
holds the frame. Nothing cuts.

## generate.py

```
python pipeline/generate.py episodes/ep01-hello-im-eva/edit.json --dry-run
python pipeline/generate.py episodes/ep01-hello-im-eva/edit.json                  # lines and stills
python pipeline/generate.py episodes/ep01-hello-im-eva/edit.json --kinds motion,talking
python pipeline/generate.py edit.json --only 5.5 --force                           # reroll one shot
```

Reads the same manifest and makes whatever file is missing. The approval gate is the file
system: a pass makes lines and stills, a person looks at every still against the visual bible and
deletes the ones that fail, the script is run again until every still on disk is approved, and
only then `--kinds motion,talking` turns approved stills into clips. The default kinds exclude
motion and talking for exactly that reason. `--force` on one id is a reroll.

| Kind | Provider, 6 October 2026 | Input | Price on the Baby Eva fal account |
|---|---|---|---|
| line | ElevenLabs text to speech, `eleven_v3` | `voice` and `text` on the line, voice ids in `pipeline/voices.json` | inside the plan |
| still | `fal-ai/nano-banana-2/edit` | `gen.prompt` plus the reference images (`gen.refs`, else the manifest `refs`), 2K | 8 US cents |
| motion | `fal-ai/veo3.1/lite/image-to-video`, silent | an approved still in `gen.from`, 4, 6 or 8 seconds | 5 cents a second |
| talking | `fal-ai/wan-25-preview/image-to-video` | an approved still in `gen.from` plus the first line's audio | 5 cents a second |

Prompts can use `{EVA}`, `{RABIT}`, `{DANNY}`, `{BUNNY}`, `{STAR}` and `{EVAFACE}`, filled from the
manifest's `locks` so the character blocks are pasted verbatim everywhere, as the visual bible
requires. The manifest's `style_suffix` is appended to every still and motion prompt and
`negative` goes to the video models. A motion or talking shot carries `from_gen`, the recipe for
the still it starts from, so the still is generated in the still pass and the clip in the next.

Keys come from `BABYEVA_FAL_KEY` and `BABYEVA_ELEVENLABS_API_KEY`, read from the environment or
from a `.env` file passed with `--env`. Never from this repo.

## design_voices.py

Auditions the four voices on ElevenLabs, three previews each from the casting notes in the master
bible, then creates the chosen ones on the account and prints the voice ids for
`pipeline/voices.json`. ElevenLabs refuses a voice design described by a child's age, so the cast
is described as cartoon characters performed by adults.
