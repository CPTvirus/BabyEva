# PRODUCTION PIPELINE

**Proposed 6 October 2026. Draft for Percy and Brendon to decide on.** Prices below were read from each vendor's own pricing page on that date. The bibles are unchanged by this document; it only changes how shots are made and in what order the show is released.

---

## 1. Why the lip sync drifted

`episodes/ep01-hello-im-eva/shots/sh01-eva-hello.mp4` has no audio stream. The mouth motion in it was invented by the video model from the prompt, and a voice line recorded afterwards can only ever be dubbed over it. That is the whole lip sync problem, and it is independent of which video model made the clip.

The fix is the order of operations: the voice line is generated first, and the talking shot is generated from a still plus that audio, so the mouth is driven by the words.

Which tools accept a still plus audio and say in writing that they handle non human faces:

| Tool | Non human faces | Price (720p) |
|---|---|---|
| Hedra Character-3 | Yes: "cartoons, 3D characters, stop-motion puppets" | 5 US cents a second |
| Wan 2.5 image to video with `audio_url` (fal.ai, Alibaba) | "Cartoon characters" | 10 US cents a second |
| OmniHuman 1.5 (BytePlus) | "Cartoon and anime characters, animals" | 12 US cents a second |
| Sync Labs lipsync-2, Luma | No: "don't support animals or non-humanoid characters" | ruled out |
| Kling lip sync | No: "not for animal characters" | ruled out |
| Veo 3.1 native speech | Cannot take our audio, voices the line itself | fallback only |

Default for every dialogue shot: approved still → ElevenLabs line → Hedra Character-3.

## 2. The stack, direct instead of through Artlist

Artlist resells these models. On the AI Starter plan, 20 USD is 16,500 credits, so a credit is about 0.12 US cents. Credits expire at month end, do not roll over, are charged on failed generations, and Starter cannot top up.

| Job | Artlist | Direct | Where |
|---|---|---|---|
| Still, Nano Banana 2, 2K | 130 credits, about 0.16 USD | 0.08 USD | fal.ai, or Google AI Studio |
| Silent motion clip from an approved still, 6 to 8 s | Hailuo 2.3 Fast 600 credits, about 0.73 USD | Hailuo 2.3 Fast 0.19 USD per 6 s on MiniMax or fal; Veo 3.1 Lite 0.03 USD a second on fal | fal.ai |
| Talking shot from still plus audio | not offered | 0.05 USD a second, Hedra Character-3 | hedra.com |
| Four locked character voices | not offered | ElevenLabs Starter, 6 USD a month, 10 voice slots, commercial licence | elevenlabs.io |
| 30 s song cue | Lyria 3, 150 credits, about 0.18 USD | 0.04 USD, Lyria 3 Clip on Google's API; 0.08 USD a full song on Lyria 3 Pro | Google AI Studio |
| Assembly, Ken Burns on stills, pauses, music ducking, captions, 16:9 and 9:16 | not offered | free, ffmpeg | local |

Not worth it: open-generative-ai is a front end over one paid gateway (Muapi) and does not lower the per clip price. Renting a GPU for Wan 2.2 only beats the APIs when a season's worth of shots is batched and the card is kept busy.

## 3. Cost per piece on the direct stack

Every generation rolled twice, because about half get rejected against the visual bible. Plan on the "with rerolls" column.

| Piece | Stills | Motion | Talking or singing | Music, voice | Clean | With rerolls |
|---|---|---|---|---|---|---|
| 60 s routine song, both ratios | 10 = 0.80 | 3 x 6 s Veo Lite = 0.54 | 2 x 10 s Hedra = 1.00 | 0.04 | about 2.40 USD | about 5 USD |
| 2:30 routine song, long form | 20 = 1.60 | 6 x 6 s = 1.08 | 4 x 10 s = 2.00 | 0.08 | about 4.80 USD | about 10 USD |
| 5:00 Episode 1 as planned in `shot-plan.md` | 30 = 2.40 | 5 x 8 s = 1.20 | about 100 s dialogue = 5.00 | 0.56 | about 9.20 USD | about 20 USD |

For comparison the shot plan's 6,300 credits is about 7.60 USD on Artlist, with no talking shots at all.

## 4. Release order: routine songs first

The bible's 5:00 story episode stays the format. What changes is what gets made first.

| Phase | What | Why |
|---|---|---|
| 1 | Eight routine songs, 2 to 3 minutes, long form 16:9, each with a 30 to 60 second 9:16 cut | Songs are the proven preschool format (eight of the nine kids videos in YouTube's all time top 30 are songs), a sung mouth tolerates far more than a spoken line, and eight songs compile into one 20 minute video |
| 2 | Episode 1, "Hello, I'm Eva!" | The pipeline is proven by then, and the pilot's job is attachment |
| 3 | Compilations, 20 to 30 minutes | What a parent puts on at the same time every day, and what earns the 4,000 YouTube Partner Program watch hours |

Shorts are marketing to parents, never the product: TikTok, Instagram and Facebook are 13 plus, so the viewer of a vertical cut is the parent, and from 1 February 2027 a channel needs 10 million Shorts views every 90 days to share the Shorts revenue pool at all.

Song slate, one concept each, Eva gets it wrong first:

| # | Topic | Format | Length |
|---|---|---|---|
| 1 | Brushing teeth | Song | 2:30 |
| 2 | Bath time | Song | 2:30 |
| 3 | Packing away toys | Song | 2:30 |
| 4 | Colours | Song | 2:00 |
| 5 | Counting 1 to 5 | Song | 2:00 |
| 6 | Shoes on the right feet | Story | 3:00 |
| 7 | The rainbow plate | Song | 2:30 |
| 8 | Please and thank you | Story | 3:00 |
| 9 | Cooking together | LEARNING episode | 5:00 |
| 10 | Alphabet A to E | Song | 2:00 |
| 11 | Being understanding | LEARNING episode | 5:00 |
| 12 | Respect | LEARNING episode | 5:00 |

## 5. Rules that keep the channel on YouTube

YouTube terminated 16 templated AI channels in January 2026 under its inauthentic content policy, and in April 2026 said it limits AI content in the YouTube Kids app to a small set of channels. The channels that survived had varied stories, consistent characters and a human voice in the writing.

1. Say the show is AI made in the channel description and the about card, and name the people who make it.
2. Vary structure between videos. The ten beats are the skeleton, no two videos may be mistaken for each other.
3. A person writes and directs every script and voice line, and the credits say so.
4. Keep the bible's pacing rules. The 2.5 second minimum cut and the pause protocol are what the research on preschool attention asks for, and what parents check.
5. Every lesson correct, reviewed by someone who works with small children.
6. Mark every video made for kids honestly.
7. Upload at a human rate, two a week.
8. Plan for the main YouTube app on a TV through a parent's account. Do not plan on the Kids app or on Shorts revenue in year one.

## 6. Bible amendments this would need

- Delivery resolution back to 1080p from 768p. The drop saved Artlist credits; on the direct stack it saves a few cents and the audience watches on a TV.
- A `voice-guide.md` with the four ElevenLabs voice IDs once they are designed and locked, since the bible already references the file.
- The Adventure Star's face, faceless or sleeping, decided before the nine blocked shots are generated.

## 7. Decisions taken 6 October 2026

Brendon's answers the same day:

1. Songs first, Episode 1 second. **Yes.**
2. Delivery **1080p**. Bibles amended to v1.3.
3. The Adventure Star's face: **faceless**, decided later the same day. Visual bible §4 now says so.
4. The direct stack: **approved.**
5. The remaining Artlist credits: **spend them on stills before they lapse.** The stills list is section 8.
6. The show stays in **this repo**, Percy's.

The assembler is built and verified, see `pipeline/README.md`. The generation half follows the accounts.

## 8. Spending the remaining Artlist credits

Artlist's credits expire at the end of each monthly cycle and go to zero when the subscription ends, and the downloads already in this repo prove generated files can be kept. Stills are the only thing worth buying there, at 130 credits for 2K against 8 cents direct. At roughly one rejection per approval, 13,000 credits is about 50 approved stills. In this order, through the Artlist MCP with the style kit and both reference sheets on every call, every prompt following the standing rules in `episodes/ep01-hello-im-eva/shots/README.md`:

| Priority | Stills | Count | Why first |
|---|---|---|---|
| 1 | Talking portraits: each of the four characters, chest up, centred, mouth closed, neutral and happy, 16:9 at 2K | 8 | These are the start frames for every Hedra talking shot in every song and episode. Mouth closed matters, the audio opens it |
| 2 | Eva's Bathroom, the new location for song 1, wide and at the sink | 2 | Added to the visual bible as a standing location in v1.3 |
| 3 | The three cast stills the shot plan names: 5.2 Little Bunny, 5.3 Mr Rabit, 2.2 Danny | 3 | Proves the cast holds at 16:9 and the Mr Rabit and Little Bunny silhouette rule |
| 4 | The rest of the Episode 1 shot plan stills, beat by beat | 27 | The pilot, once the songs have proven the pipeline |

Then cancel Artlist. Anything left over after the list goes on song 2's bathroom and garden stills.
