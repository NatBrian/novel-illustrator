---
name: epub-novel-illustrator
description: >-
  Use when transforming an EPUB novel into an illustrated EPUB with per-chapter
  multi-panel artwork, source-grounded scene briefs, spoiler-free visual
  continuity, E-Ink grayscale optimization, and dedicated fullscreen
  illustration pages.
---

# EPUB Novel Illustrator

Transform an EPUB novel into a source-faithful illustrated EPUB with **one 4-panel illustration per chapter or meaningful narrative section**, placed on its own dedicated fullscreen page after each unit.

**Core priority:** Narrative accuracy and source fidelity take precedence over visual spectacle. **Do not begin image generation before inspecting the EPUB and planning the full workflow.**

## Non-Negotiable Rules

1. **Source fidelity & no unsupported invention:** Classify every visual detail as `CONFIRMED` (explicitly in text), `INTERPRETED` (conservative choice consistent with text), or `UNKNOWN` (do not invent). Never substitute generic genre clichés (spaceships, holograms, castles, neon, monsters) for actual story events.
2. **Strict spoiler prevention & agent isolation:** Chapter *N* briefs may use details established in Chapters `1..N` only. Simply telling subagents to ignore future chapters is insufficient—pass **only** the isolated chapter excerpt and the progressive visual reference log up to `N-1`.
3. **Original content immutability:** Never rewrite, shorten, summarize, translate, reorder, or alter original chapter text, formatting, CSS, metadata, or TOC navigation. Only add illustration images, dedicated illustration XHTML pages, and OPF `<manifest>`/`<spine>` entries.
4. **Zero extraneous text in artwork:** Unless required by the story, panels must contain **no speech bubbles, dialogue, caption boxes, sound effects, labels, or watermarks**.

## Workflow

### Phase 1: EPUB Inspection & Production Manifest
Run [inspect_epub.py](./scripts/inspect_epub.py) on the input `.epub`:
```bash
python scripts/inspect_epub.py "<input.epub>" --out-dir ./work
```
Examine EPUB version, OPF metadata/manifest/spine, TOC navigation, CSS, headings, and reading order. Do not assume 1 XHTML file = 1 chapter.
Build a production manifest tracking every unit:
`Unit ID | Chapter/Section | Reading Order | Source Boundaries | Summary | Characters & Locations | Key Events | Assigned Agents | Status`

### Phase 2: Art Direction & Confirmation Gate
1. **Infer style & medium from the novel** (genre, tone, era, setting, realism, narrative voice) or user preference—choosing the fitting visual style (e.g., realistic, anime/manga, stylized/cartoon, gritty dystopian, gothic horror ink, painterly, etc.) rather than forcing a single default style or generic genre clichés.
2. **Confirm scope & target with the user** before generating images:
   - Target chapters (all units or specific range/skips).
   - Output profile: **Kindle Paperwhite / E-Ink** (`1072x1448` 3:4 portrait, 8-bit grayscale high-contrast ink & wash — see [art-direction-eink.md](./references/art-direction-eink.md)) or **Standard Color EPUB** (`--color` in `compile_epub.py`).
   - **Pilot gate:** Generate and get user approval on the first **3** target chapters before scaling to the full book.

### Phase 3: Narrative Analysis, 4-Scene Selection & Quote Verification
For each unit (in isolated chapter context):
1. Select **4 complementary visual beats** representing actual events, character interactions, discoveries, objects, or setting shifts (never repeat the same scene; never invent events for short chapters).
2. Vary **layout** (do not force every page into a rigid 2×2 grid—use `1 large + 3 small`, `2 large + 2 small`, mixed horizontal/vertical, or asymmetric editorial layouts) and **camera framing** (wide, medium, close-up, over-the-shoulder, action, environmental).
3. Produce a per-panel evidence record (`Panel | Scene | Supporting source passage | Confirmed details | Unknown details`) and update the progressive visual reference guide (characters, clothing, physical state, locations, objects).
4. Compile `work/image_briefs.json` and verify **0 quote mismatches** before generating images:
```bash
python scripts/verify_quotes.py --chapters work/chapters_raw.json --briefs work/image_briefs.json
```

### Phase 4–6: Batched Image Generation & Independent QC
- Respect delegation/subagent concurrency limits (e.g., max **3** `image-generator` subagents in parallel; wait for all 3 to finish before launching the next batch).
- Assign **1 illustration per `image-generator` subagent** with only its approved brief, layout, and progressive references up to chapter `N`.
- **Inspect every generated image directly** against the chapter text and [qc-checklist.md](./references/qc-checklist.md).
- **Regeneration loop on FAIL:** Identify the exact error and source passage, fix the brief (remove unsupported details/text/spoilers), regenerate, and re-QC. Never insert rejected images.
- **Quota (`429 RESOURCE_EXHAUSTED`) handling:** Never retry immediately. Log completed/failed units and the reset timestamp, then pause or schedule a one-shot wakeup past reset.

### Phase 7: Fullscreen EPUB Compilation, Validation & Delivery
Compile and structurally validate the EPUB with [compile_epub.py](./scripts/compile_epub.py):
```bash
python scripts/compile_epub.py "<input.epub>" \
  --briefs work/image_briefs.json \
  --images-map work/approved_images.json \
  --out "<output_illustrated.epub>"
```
(Add `--color` for color EPUBs; default converts to 8-bit grayscale `1072x1448` JPEG for E-Ink.)

Before delivering:
- Run `epubcheck` if installed and report actual errors/warnings.
- Verify **content preservation** (original chapter count, text, metadata, and TOC intact) and **visual rendering** (all 4 panels visible, aspect ratio preserved, clean chapter transitions).
- Deliver the `.epub` directly in chat (never external cloud links) with a completion report:

| Metric | Result |
|---|---|
| Chapters/sections identified | Count |
| Illustration units completed | Count |
| Images generated / approved / regenerated | Counts |
| Panels per image | 4 |
| EPUB insertion & original content preserved | Verified status |
| EPUB validation | Actual tool/check result |

## Common Mistakes

| Mistake | Fix |
|---|---|
| Rigid 2×2 grid and identical medium shots every chapter | Vary panel proportions and camera angles (wide, close-up, OTS) per beat |
| Subagent adds speech bubbles, captions, or color LEDs | Explicitly forbid text/color in prompt; inspect every image and regenerate on violation |
| Passing future chapter context to analysts/artists | Pass only chapter `N` text + progressive references `1..N` |
| Inserting `<img>` inside Calibre chapter HTML breaks page breaks | Keep original chapter HTML untouched; insert a dedicated XHTML page immediately after the chapter in `<spine>` |
| Subagent saves images to root artifact dir instead of subdirs | Record exact returned file paths in `approved_images.json` |
