# EPISODE 1 — SHOTS

5:00 · 16:9 · 768p · against [shot-plan.md](../shot-plan.md) and bibles v1.2.
Style kit `1be17cde-4267-48df-94df-46cdb2a8cbd1` + both reference sheets on every generation.

**Pipeline:** generate the still → check it against the rejection criteria → only then animate.
Never animate an unchecked frame.

## Approved

| Shot | Beat | File | Type | Credits |
|---|---|---|---|---|
| 1.1 | 1 Cold open | [sh1-1-evas-room-dawn.png](sh1-1-evas-room-dawn.png) | Still | 130 |
| 3.1 | 3 Introduction | [sh01-eva-hello.mp4](sh01-eva-hello.mp4) | Video (Veo, reused) | 1,130 |
| 5.1 | 5 Adventure | [sh5-1-garden-wide.png](sh5-1-garden-wide.png) | Still | 130 |
| 10.3 | 10 Goodbye | [sh10-3-cosy-corner.png](sh10-3-cosy-corner.png) | Still | 130 |

Locations are now locked. Every subsequent shot in Eva's Room, the Garden or the Cosy Corner must
match these three frames.

### What the location stills established

- **Eva's Room** — shelf height and position for the star, yellow curtains camera left, round pastel
  rug, honey-wood floor, bunting line.
- **The Garden** — the low stone-and-wood wall sits centre-foreground and reads clearly at a glance.
  This matters: shots 5.4 (Eva sets the star down), 5.5 (Danny takes it) and the held empty-wall beat
  all depend on the audience reading that surface instantly. Fence with gate behind, watering can
  camera right, terracotta pots both sides.
- **Cosy Corner** — green armchair centred, bookshelf camera left, table lamp camera right as the
  warm key.

The Adventure Star is **faceless** in all three, per the locked spec. See the open question below.

## Standing prompt rules

Learned from the shot 3.1 rejection. Every prompt, no exceptions:

- **Whiskers and teeth get an explicit positive sentence in the prompt body**, not just the negative
  list. A negative prompt does not beat the semantic prior of "mouse".
- **Framing is stated as a shot type**, not a percentage.
- **16:9 needs an explicit negative-space instruction**, or the model fills the width with clutter.
- Paste the character lock **verbatim** from the visual bible.
- Generate stills at **2K** — they cost 130 at every resolution, so there is no reason to go smaller,
  and the extra pixels give room to push and crop in the edit.

## Decided 6 October 2026: the Adventure Star has no face

Brendon's call, recorded in the visual bible §4 at v1.3. The nine shots below generate faceless.
The history, for the record:

An early rejected still rendered the star with a **sleeping face** (closed eyes, blush, small smile).
Charming, and it fits "settles back to a soft, sleepy dim" — but **not in the locked spec**, which
describes only "a soft plush five-pointed star, `#FFCE5A`, with a gentle inner glow."

Generating faceless by default. Changing it now means re-rolling the star in every shot it appears
in — 1.1, 1.2, 3.2, 3.3, 4.3, 5.4, 9.4, 10.1 and 10.3 — so decide before those are generated.

## Budget

Cap **6,755**. Spent **390** on locations. **6,365** remaining, against a planned **5,910** for the
27 outstanding shots (26 stills + 4 video, less the 3 done) — leaving ~455 for rejections.
