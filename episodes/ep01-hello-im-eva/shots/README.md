# EPISODE 1 — SHOTS

Generated against [visual-bible.md](../../../bible/visual-bible.md) **v1.1** (16:9) using style kit
`1be17cde-4267-48df-94df-46cdb2a8cbd1`. Shot list: [shot-plan.md](../shot-plan.md).

**Pipeline, always in this order:** generate the still → check it against the rejection criteria →
only then animate the approved still. Never animate an unchecked frame; a flaw in the still becomes
a flaw in every frame of the video, at 7.7× the cost.

| Shot | Beat | File | Status |
|---|---|---|---|
| 3.1 | 3 — INTRODUCTION | [sh01-eva-hello.mp4](sh01-eva-hello.mp4) | Approved · 16:9 |

*Shot numbering follows [shot-plan.md](../shot-plan.md). This was "shot 01" before the v1.1
restructure; it is now beat 3, shot 1.*

---

## Shot 3.1 — "Hello! I'm Eva."

Eva alone in her room, waving down the lens. The show's signature framing and the first shot of her
a viewer will ever see.

**Still:** [sh01-eva-hello.png](sh01-eva-hello.png) · 2752×1536 · Nano Banana 2 · 130 credits
`generationId` `01a0df20-d1b4-7987-8ea7-116ae61d577c`

**Video:** [sh01-eva-hello.mp4](sh01-eva-hello.mp4) · 8s · 1920×1080 · Veo 3.1 Fast (`modelId` 1037)
· 1,000 credits
`generationId` `01a0df21-709b-7da8-a107-b5c8c9cb0a6e`

Settings: `aspect_ratio` 16:9, `duration` 8, `generate_audio` false, `resolution` 1080p.
Audio is off deliberately — the show carries its own score and sound design per master bible §8–9.

### Version history

- **9:16 vertical originals** (still, rejected still and video) were generated under bibles v1.0 and
  superseded by the v1.1 format change. They are preserved in git at commit `8c3c931` and are not
  carried in the working tree.

### The rejection that taught us the prompt rules

The first attempt under v1.0 failed three rejection criteria and was **not** animated:

1. **Whiskers** — three per side. Banned in visual bible §1 and §6 and listed in the standard
   negative prompt, but the model added them anyway because "mouse" overrides a text instruction.
2. **Visible teeth** — two front teeth. Master bible §6: teeth on no one but Danny.
3. **Framing too wide** — face at ~14% of frame height against a ≥25% requirement.

**What fixed it:** moving the bans out of the trailing negative list and into the body of the prompt
as emphatic positive statements — "her cheeks and muzzle are completely smooth, no whisker strands",
"NO TEETH ARE VISIBLE AT ALL" — plus stating the framing as a shot type ("chest-up close portrait")
rather than as a percentage. **A negative prompt does not beat a strong semantic prior.**

The 16:9 version added a third rule: **landscape needs an explicit negative-space instruction**
("soft empty defocused room to left and right, do not fill the width") or the model fills the extra
width with clutter that competes with her face.

All three rules are now standing requirements in [shot-plan.md](../shot-plan.md).

---

## Open design question — the Adventure Star's face

The original rejected still rendered the Adventure Star on the shelf with a **sleeping face** —
closed eyes, blush, a small smile. It's charming and it fits the bible's "settles back to a soft,
sleepy dim", but **it is not in the locked spec**, which describes only "a soft plush five-pointed
star, `#FFCE5A`, roughly the size of Eva's head, with a gentle inner glow."

The bibles are locked, so this cannot be adopted silently. It needs either a deliberate amendment to
[visual-bible.md §4](../../../bible/visual-bible.md) or a decision to keep the star faceless.

**Still open. Decide before the star appears in any approved shot** — it is a merchandisable
franchise object and a face changes what it is. The star appears in shots 1.1, 1.2, 3.4, 3.5, 3.6,
5.8, 10.8, 10.9, 12.1, 13.1 and 13.4, so this blocks a meaningful chunk of the episode.

---

## Costs

| Item | Credits |
|---|---|
| 9:16 still v1 (rejected, superseded) | 130 |
| 9:16 still v2 (superseded by format change) | 130 |
| 9:16 video (superseded by format change) | 1,000 |
| **16:9 still (current)** | **130** |
| **16:9 video (current)** | **1,000** |
| **Total spent on this shot** | **2,390** |

The 1,260 spent on the 9:16 version was lost to the format change, not to error. Worth noting as the
cost of settling format before generating rather than after — the full-episode equivalent of that
mistake would have been ~43,000 credits.
