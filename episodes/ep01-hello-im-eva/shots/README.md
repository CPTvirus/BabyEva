# EPISODE 1 — SHOTS

Generated against [visual-bible.md](../../../bible/visual-bible.md) v1.0 (locked) using style kit
`1be17cde-4267-48df-94df-46cdb2a8cbd1`.

**Pipeline, always in this order:** generate the still → check it against the rejection criteria →
only then animate the approved still. Never animate an unchecked frame; a flaw in the still becomes
a flaw in every frame of the video, at 5–15× the cost.

| Shot | Beat | File | Status |
|---|---|---|---|
| 01 | 2 — INTRODUCTION | [sh01-eva-hello.mp4](sh01-eva-hello.mp4) | Approved |

---

## Shot 01 — "Hello! I'm Eva."

Eva alone in her room, waving down the lens. The show's signature framing and the first shot a
viewer will ever see.

**Still:** [sh01-eva-hello-v2.png](sh01-eva-hello-v2.png) · 1536×2752 · Nano Banana 2 · 130 credits
`generationId` `01a0df0e-e779-7f3e-aaec-aaca647a39f0`

**Video:** [sh01-eva-hello.mp4](sh01-eva-hello.mp4) · 8s · 1080p · 9:16 · Veo 3.1 Fast (`modelId`
1037) · 1,000 credits
`generationId` `01a0df13-c9a7-76be-b4a4-7e74ec72765d`

Settings: `aspect_ratio` 9:16, `duration` 8, `generate_audio` false, `resolution` 1080p.
Audio is off deliberately — the show carries its own score and sound design per master bible §8–9.

### First attempt was rejected

[sh01-eva-hello.png](sh01-eva-hello.png) (`01a0df0d-cac8-7cbb-b448-eebd6d814d5a`, 130 credits) failed
three rejection criteria and was **not** animated:

1. **Whiskers** — three per side. Banned in visual bible §1 and §6 and listed in the standard
   negative prompt, but the model added them anyway because "mouse" overrides a text instruction.
2. **Visible teeth** — two front teeth. Master bible §6: teeth on no one but Danny.
3. **Framing too wide** — face at ~14% of frame height against a ≥25% requirement for direct address.

**What fixed it:** moving the bans out of the trailing negative list and into the body of the prompt
as emphatic positive statements — "her cheeks and muzzle are completely smooth, no whisker strands",
"her mouth is a warm closed-lip smile, NO TEETH ARE VISIBLE AT ALL" — plus stating the framing as a
shot type ("CLOSE-UP PORTRAIT FRAMING… chest-up") rather than as a percentage. A negative prompt
alone does not beat a strong semantic prior like "mouse ⇒ whiskers".

**Apply to every future prompt:** whiskers and teeth get an explicit positive sentence in the prompt
body, every time. Do not rely on the negative prompt for them.

---

## Open design question — the Adventure Star's face

The rejected first still rendered the Adventure Star on the shelf with a sleeping face — closed eyes,
blush, a small smile. It's charming and it fits the bible's "settles back to a soft, sleepy dim", but
**it is not in the locked spec**, which describes only "a soft plush five-pointed star, `#FFCE5A`,
roughly the size of Eva's head, with a gentle inner glow."

The bibles are locked, so this cannot be adopted silently. It needs either a deliberate amendment to
[visual-bible.md §4](../../../bible/visual-bible.md) or a decision to keep the star faceless. Flagged
for Brendon — worth deciding before the star appears in any approved shot, because it is a
merchandisable franchise object and a face changes what it is.

---

## Costs so far

| Item | Credits |
|---|---|
| Still v1 (rejected) | 130 |
| Still v2 (approved) | 130 |
| Video, Veo 3.1 Fast 8s 1080p | 1,000 |
| **Shot 01 total** | **1,260** |

At this rate a ~30-shot episode runs roughly 30,000 credits against a 16,500/month plan — about 1.8
months per episode. Cheaper models quoted: Kling 2.5 Turbo 750 (5s, 1080p), Hailuo 2.3 Fast 600 (6s,
768p), Seedance 2.0 Mini 480 (4s, 480p). Full Veo 3.1 is 2,000 for the same 8s.

**This is unresolved and gates the season plan.** Decide after judging motion quality on this shot.
