# MAIN THEME — v1 demo

**File:** [theme-main-v1.mp3](theme-main-v1.mp3) · 29.8s · 192 kbps · 44.1 kHz
**Status:** demo for approval — not locked

Generated 2026-09-26. Once a version is approved it becomes the locked main theme, and per
[master-bible.md §8](../bible/master-bible.md) the melody never changes again — only arrangements do.

---

## Generation parameters

Recorded so the theme can be regenerated or varied without drifting off the locked identity.

| | |
|---|---|
| Service | Artlist MCP |
| Model | Lyria 3 — T2M Custom (`modelId` 2238, `modelGroupId` 375) |
| Generation ID | `01a0defe-78b1-7db7-b75a-620ba9e627d4` |
| Cost | 150 credits |

### Settings

```json
{
  "duration": 30,
  "song_type": "custom_lyrics",
  "song_genre": "children",
  "song_mood": "happy",
  "song_theme": "auto",
  "song_tempo": "slow_med",
  "prompt_enhance_mode": "artlist_sound"
}
```

`song_tempo` is deliberately `slow_med`, not `medium` — the bible sets a hard 108 BPM ceiling because
anything faster overstimulates the 1–4 age group.

### Prompt

```
Opening title theme for a preschool children's television show called "Baby Eva Adventures", aimed
at toddlers aged 1 to 4. Bright, warm, gentle and extremely singable, built on a simple repetitive
melody a two-year-old could hum back after one listen. Lead instrumentation: soft ukulele strumming
and sparkling glockenspiel, with celesta, light hand percussion, soft claps and a warm upright bass.
Sweet, friendly single child-like female vocal, clear and unhurried, never shrieky or manic. Key of
C major, around 100 BPM — unhurried and comforting, never frantic. Clean, premium, professionally
produced children's TV theme quality with a warm analogue softness. No harsh or sharp sounds, no
aggressive drums, no electronic elements, no dark or minor-key turns. Cheerful, cosy and reassuring
throughout, ending on a warm resolved major chord.
```

### Lyrics

```
Baby Eva, Baby Eva!
Come on, little adventurers!
Baby Eva, Baby Eva!
Adventure starts with you!

Mr Rabit, Little Bunny,
Danny's here to play!
Stop... Think... Look!
We'll find the way today!

Baby Eva, Baby Eva!
Adventure starts with YOU!
```

Both locked phrases are load-bearing here: **"Come on, little adventurers!"** (the call to begin) and
**"Adventure starts with YOU!"** (the theme hook and end-of-episode button). Mr Rabit's
**"Stop… Think… Look!"** is seeded in verse 2 so children meet the method before the first episode
teaches it.

---

## What to check before approving

- [ ] Could a two-year-old hum the hook back after one listen?
- [ ] Is "Adventure starts with YOU!" the most memorable four seconds in the track?
- [ ] Tempo comfortable, not driving — no sense of hurry
- [ ] Vocal warm and clear, no shriek, no vocal fry, no baby-talk
- [ ] "Mr Rabit" sung clearly enough to register as a name
- [ ] Nothing sharp, no sudden loud transient
- [ ] Ends resolved and warm, not on a cliff
- [ ] The opening ~20s works as the title cut (master bible §11 beat 1)

## Open items

- Theme is 30s; the title beat is **0:20**. Needs a trim point chosen, or a 20s edit.
- The **goodbye song** (§8, ~15s, same melodic family, slower and tenderer) is not yet generated —
  it must be derived from whichever theme version is approved, not composed independently.
- The four character cues (Eva motif, Mr Rabit, Danny, Little Bunny) are still to do.
